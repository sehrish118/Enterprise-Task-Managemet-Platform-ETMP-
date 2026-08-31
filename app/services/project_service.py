import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.exceptions import (
    ProjectNameAlreadyExistsError,
    ProjectNotFoundError,
    UserAlreadyProjectMemberError,
    UserNotFoundError,
    UserNotOrganizationMemberError,
    ProjectMemberNotFoundError,
)
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.rbac_repository import RBACRepository


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.rbac_repo = RBACRepository(session)

    async def create_project(
        self, *, organization_id: uuid.UUID, name: str, created_by: uuid.UUID
    ) -> Project:
        existing = await self.project_repo.get_by_name(
            organization_id=organization_id, name=name
        )
        if existing is not None:
            raise ProjectNameAlreadyExistsError(
                f"Project '{name}' already exists in this organization"
            )
        project = await self.project_repo.create(
            organization_id=organization_id, name=name, created_by=created_by
        )
        # Creator is automatically added as a project member with elevated role
        await self.project_repo.add_member(
            organization_id=organization_id,
            project_id=project.id,
            user_id=created_by,
            role=ProjectMemberRole.PROJECT_MANAGER,
        )
        await self.session.commit()
        return project

    async def get_project(
        self,
        project_id: uuid.UUID,
        *,
        requesting_user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        is_admin = await self.rbac_repo.user_is_org_admin_or_owner(
            user_id=requesting_user_id, organization_id=organization_id
        )
        if is_admin:
            return project

        membership = await self.project_repo.get_membership(
            project_id=project_id, user_id=requesting_user_id
        )
        if membership is None:
            raise ProjectNotFoundError(
                f"Project {project_id} not found"
            )  # 404, not 403 — don't reveal existence

        return project

    async def update_project(
        self,
        *,
        project_id: uuid.UUID,
        name: str | None,
        status: str | None,
        is_archived: bool | None,
        requesting_user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Project:
        project = await self.get_project(
            project_id,
            requesting_user_id=requesting_user_id,
            organization_id=organization_id,
        )
        project = await self.project_repo.update(
            project, name=name, status=status, is_archived=is_archived
        )
        await self.session.commit()
        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
        *,
        requesting_user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> None:
        project = await self.get_project(
            project_id,
            requesting_user_id=requesting_user_id,
            organization_id=organization_id,
        )
        # 1. Project soft delete karein
        await self.project_repo.soft_delete(project)

        # 2. Project ke tamam tasks ko bhi soft-delete karein
        await self.project_repo.soft_delete_project_tasks(project_id)

        await self.session.commit()

    async def list_projects(
        self, *, organization_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> list[Project]:
        is_admin = await self.rbac_repo.user_is_org_admin_or_owner(
            user_id=requesting_user_id, organization_id=organization_id
        )
        if is_admin:
            return await self.project_repo.list_by_organization(organization_id)
        return await self.project_repo.list_for_member(
            organization_id=organization_id, user_id=requesting_user_id
        )

    async def add_member(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        requesting_user_id: uuid.UUID,
    ) -> ProjectMember:
        await self.get_project(
            project_id,
            requesting_user_id=requesting_user_id,
            organization_id=organization_id,
        )

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID '{user_id}' not found")

        org_membership = await self.org_repo.get_membership(
            organization_id=organization_id, user_id=user.id
        )
        if org_membership is None:
            raise UserNotOrganizationMemberError(
                f"User '{user.full_name}' must be a member of the organization before joining a project"
            )

        existing = await self.project_repo.get_membership(
            project_id=project_id, user_id=user.id
        )
        if existing is not None:
            raise UserAlreadyProjectMemberError(
                f"User '{user.full_name}' is already a member of this project"
            )

        member = await self.project_repo.add_member(
            organization_id=organization_id,
            project_id=project_id,
            user_id=user.id,
            role=ProjectMemberRole(role),
        )
        await self.session.commit()
        return member

    async def remove_member(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
    ) -> None:
        # 1. Fetch Project Members
        members = await self.project_repo.list_members(project_id)

        # 2. Request bhejne wale ka role check karein
        requester = next((m for m in members if m.user_id == requesting_user_id), None)

        if not requester:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project",
            )

        # AUTHORIZATION CHECK: Sirf PROJECT_MANAGER ya OWNER hi remove kar sakta hai
        is_manager = requester.role in ["PROJECT_MANAGER", "OWNER", "LEAD"]
        if not is_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied. Only Project Managers can remove members.",
            )

        # 3. Target member verification
        target_member = next((m for m in members if m.user_id == user_id), None)
        if not target_member:
            raise ProjectMemberNotFoundError(f"User is not a member of this project")

        # 4. Rules Guard
        if len(members) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last member. Delete project instead.",
            )

        if (
            target_member.role in ["PROJECT_MANAGER", "OWNER"]
            and target_member.user_id != requesting_user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot remove another Manager/Owner.",
            )

        # 5. Member ke project tasks se assignments remove karein
        await self.project_repo.unassign_user_from_project_tasks(
            project_id=project_id, user_id=user_id
        )

        # 6. DB se Delete execute karein
        await self.project_repo.remove_member(project_id=project_id, user_id=user_id)
        await self.session.commit()

    async def list_members_with_names(
        self,
        project_id: uuid.UUID,
        *,
        requesting_user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[tuple]:
        await self.get_project(
            project_id,
            requesting_user_id=requesting_user_id,
            organization_id=organization_id,
        )
        return await self.project_repo.list_members_with_names(project_id)
