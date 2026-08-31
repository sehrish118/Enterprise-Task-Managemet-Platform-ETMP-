# import uuid
# from datetime import datetime, timezone

# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.project import Project, ProjectStatus
# from app.models.project_member import ProjectMember, ProjectMemberRole


# class ProjectRepository:
#     def __init__(self, session: AsyncSession) -> None:
#         self.session = session

#     async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
#         result = await self.session.execute(
#             select(Project).where(
#                 Project.id == project_id, Project.deleted_at.is_(None)
#             )
#         )
#         return result.scalar_one_or_none()

#     async def get_by_name(
#         self, *, organization_id: uuid.UUID, name: str
#     ) -> Project | None:
#         result = await self.session.execute(
#             select(Project).where(
#                 Project.organization_id == organization_id,
#                 Project.name == name,
#                 Project.deleted_at.is_(None),
#             )
#         )
#         return result.scalar_one_or_none()

#     async def create(
#         self, *, organization_id: uuid.UUID, name: str, created_by: uuid.UUID
#     ) -> Project:
#         project = Project(
#             organization_id=organization_id, name=name, created_by=created_by
#         )
#         self.session.add(project)
#         await self.session.flush()
#         return project

#     async def update(
#         self,
#         project: Project,
#         *,
#         name: str | None = None,
#         status: str | None = None,
#         is_archived: bool | None = None,
#     ) -> Project:
#         if name is not None:
#             project.name = name
#         if status is not None:
#             project.status = ProjectStatus(status)
#         if is_archived is not None:
#             project.is_archived = is_archived
#         await self.session.flush()
#         return project

#     async def soft_delete(self, project: Project) -> None:
#         project.deleted_at = datetime.now(timezone.utc)
#         await self.session.flush()

#     async def list_by_organization(self, organization_id: uuid.UUID) -> list[Project]:
#         result = await self.session.execute(
#             select(Project).where(
#                 Project.organization_id == organization_id, Project.deleted_at.is_(None)
#             )
#         )
#         return list(result.scalars().all())

#     async def list_for_member(
#         self, *, organization_id: uuid.UUID, user_id: uuid.UUID
#     ) -> list[Project]:
#         """Projects where the user is an explicit project member."""
#         from app.models.project_member import ProjectMember

#         stmt = (
#             select(Project)
#             .join(ProjectMember, ProjectMember.project_id == Project.id)
#             .where(
#                 Project.organization_id == organization_id,
#                 Project.deleted_at.is_(None),
#                 ProjectMember.user_id == user_id,
#             )
#         )
#         result = await self.session.execute(stmt)
#         return list(result.scalars().all())

#     async def add_member(
#         self,
#         *,
#         organization_id: uuid.UUID,
#         project_id: uuid.UUID,
#         user_id: uuid.UUID,
#         role: ProjectMemberRole,
#     ) -> ProjectMember:
#         member = ProjectMember(
#             organization_id=organization_id,
#             project_id=project_id,
#             user_id=user_id,
#             role=role,
#         )
#         self.session.add(member)
#         await self.session.flush()
#         return member

#     async def get_membership(
#         self, *, project_id: uuid.UUID, user_id: uuid.UUID
#     ) -> ProjectMember | None:
#         result = await self.session.execute(
#             select(ProjectMember).where(
#                 ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
#             )
#         )
#         return result.scalar_one_or_none()

#     async def list_members(self, project_id: uuid.UUID) -> list[ProjectMember]:
#         result = await self.session.execute(
#             select(ProjectMember).where(ProjectMember.project_id == project_id)
#         )
#         return list(result.scalars().all())

#     async def list_members_with_names(
#         self, project_id: uuid.UUID
#     ) -> list[tuple[ProjectMember, str]]:
#         from sqlalchemy import select as sa_select
#         from app.models.user import User

#         stmt = (
#             sa_select(ProjectMember, User.full_name)
#             .join(User, User.id == ProjectMember.user_id)
#             .where(ProjectMember.project_id == project_id)
#         )
#         result = await self.session.execute(stmt)
#         return [(member, name) for member, name in result.all()]

#     async def get_member_role(
#         self, *, project_id: uuid.UUID, user_id: uuid.UUID
#     ) -> ProjectMemberRole | None:
#         membership = await self.get_membership(project_id=project_id, user_id=user_id)
#         return membership.role if membership else None

#     async def remove_member(self, *, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
#         membership = await self.get_membership(project_id=project_id, user_id=user_id)
#         if membership:
#             await self.session.delete(membership)
#             return True
#         return False


import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.models.task import Task
from app.models.task_assignee import TaskAssignee


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        result = await self.session.execute(
            select(Project).where(
                Project.id == project_id, Project.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self, *, organization_id: uuid.UUID, name: str
    ) -> Project | None:
        result = await self.session.execute(
            select(Project).where(
                Project.organization_id == organization_id,
                Project.name == name,
                Project.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self, *, organization_id: uuid.UUID, name: str, created_by: uuid.UUID
    ) -> Project:
        project = Project(
            organization_id=organization_id, name=name, created_by=created_by
        )
        self.session.add(project)
        await self.session.flush()
        return project

    async def update(
        self,
        project: Project,
        *,
        name: str | None = None,
        status: str | None = None,
        is_archived: bool | None = None,
    ) -> Project:
        if name is not None:
            project.name = name
        if status is not None:
            project.status = ProjectStatus(status)
        if is_archived is not None:
            project.is_archived = is_archived
        await self.session.flush()
        return project

    async def soft_delete(self, project: Project) -> None:
        project.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def soft_delete_project_tasks(self, project_id: uuid.UUID) -> None:
        """Project soft delete hone par uske sare tasks ko bhi soft-delete karta hai."""
        stmt = (
            update(Task)
            .where(Task.project_id == project_id, Task.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def unassign_user_from_project_tasks(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Member remove hone par project tasks se uski assignees remove karta hai."""
        task_ids_stmt = select(Task.id).where(Task.project_id == project_id)
        stmt = delete(TaskAssignee).where(
            TaskAssignee.user_id == user_id,
            TaskAssignee.task_id.in_(task_ids_stmt),
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[Project]:
        result = await self.session.execute(
            select(Project).where(
                Project.organization_id == organization_id, Project.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())

    async def list_for_member(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[Project]:
        """Projects where the user is an explicit project member."""
        from app.models.project_member import ProjectMember

        stmt = (
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                Project.organization_id == organization_id,
                Project.deleted_at.is_(None),
                ProjectMember.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_member(
        self,
        *,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        role: ProjectMemberRole,
    ) -> ProjectMember:
        member = ProjectMember(
            organization_id=organization_id,
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        self.session.add(member)
        await self.session.flush()
        return member

    async def get_membership(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectMember | None:
        result = await self.session.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_members(self, project_id: uuid.UUID) -> list[ProjectMember]:
        result = await self.session.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        return list(result.scalars().all())

    async def list_members_with_names(
        self, project_id: uuid.UUID
    ) -> list[tuple[ProjectMember, str]]:
        from sqlalchemy import select as sa_select
        from app.models.user import User

        stmt = (
            sa_select(ProjectMember, User.full_name)
            .join(User, User.id == ProjectMember.user_id)
            .where(ProjectMember.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return [(member, name) for member, name in result.all()]

    async def get_member_role(
        self, *, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> ProjectMemberRole | None:
        membership = await self.get_membership(project_id=project_id, user_id=user_id)
        return membership.role if membership else None

    async def remove_member(self, *, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        membership = await self.get_membership(project_id=project_id, user_id=user_id)
        if membership:
            await self.session.delete(membership)
            return True
        return False
