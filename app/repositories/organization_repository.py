# # """Organization data access layer — pure DB queries, no business logic."""

# # import uuid

# # from sqlalchemy import select, and_
# # from sqlalchemy.ext.asyncio import AsyncSession

# # from app.models.organization import Organization
# # from app.models.organization_member import OrganizationMember
# # from app.models.role import Role
# # from app.models.user import User
# # from app.models.team_member import TeamMember


# # class OrganizationRepository:
# #     def __init__(self, session: AsyncSession) -> None:
# #         self.session = session

# #     async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
# #         result = await self.session.execute(
# #             select(Organization).where(
# #                 Organization.id == organization_id, Organization.deleted_at.is_(None)
# #             )
# #         )
# #         return result.scalar_one_or_none()

# #     async def get_by_slug(self, slug: str) -> Organization | None:
# #         result = await self.session.execute(
# #             select(Organization).where(
# #                 Organization.slug == slug, Organization.deleted_at.is_(None)
# #             )
# #         )
# #         return result.scalar_one_or_none()

# #     async def create(self, *, name: str, slug: str) -> Organization:
# #         org = Organization(name=name, slug=slug)
# #         self.session.add(org)
# #         await self.session.flush()
# #         return org

# #     async def update(
# #         self, org: Organization, *, name: str | None = None
# #     ) -> Organization:
# #         if name is not None:
# #             org.name = name
# #         await self.session.flush()
# #         return org

# #     async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
# #         stmt = (
# #             select(Organization)
# #             .join(
# #                 OrganizationMember,
# #                 OrganizationMember.organization_id == Organization.id,
# #             )
# #             .where(
# #                 OrganizationMember.user_id == user_id,
# #                 OrganizationMember.deleted_at.is_(None),
# #                 Organization.deleted_at.is_(None),
# #             )
# #         )
# #         result = await self.session.execute(stmt)
# #         return list(result.scalars().all())

# #     async def get_role_by_name(
# #         self, *, organization_id: uuid.UUID, role_name: str
# #     ) -> Role | None:
# #         """
# #         Looks up a role by name — checks org-scoped custom roles first,
# #         falls back to global system roles (Owner/Admin/Member).
# #         """
# #         result = await self.session.execute(
# #             select(Role).where(
# #                 Role.name == role_name,
# #                 (Role.organization_id == organization_id)
# #                 | (Role.organization_id.is_(None)),
# #             )
# #         )
# #         return result.scalar_one_or_none()

# #     async def add_member(
# #         self, *, organization_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID
# #     ) -> OrganizationMember:
# #         membership = OrganizationMember(
# #             organization_id=organization_id, user_id=user_id, role_id=role_id
# #         )
# #         self.session.add(membership)
# #         await self.session.flush()
# #         return membership

# #     async def get_membership(
# #         self, *, organization_id: uuid.UUID, user_id: uuid.UUID
# #     ) -> OrganizationMember | None:
# #         result = await self.session.execute(
# #             select(OrganizationMember).where(
# #                 OrganizationMember.organization_id == organization_id,
# #                 OrganizationMember.user_id == user_id,
# #                 OrganizationMember.deleted_at.is_(None),
# #             )
# #         )
# #         return result.scalar_one_or_none()

# #     async def get_unassigned_team_members(
# #         self, organization_id: uuid.UUID, team_id: uuid.UUID
# #     ):
# #         query = (
# #             select(User)
# #             .join(OrganizationMember, OrganizationMember.user_id == User.id)
# #             .outerjoin(
# #                 TeamMember,
# #                 and_(TeamMember.user_id == User.id, TeamMember.team_id == team_id),
# #             )
# #             .where(
# #                 OrganizationMember.organization_id == organization_id,
# #                 OrganizationMember.deleted_at.is_(None),
# #                 TeamMember.id.is_(None),
# #             )
# #         )

# #         result = await self.session.execute(query)
# #         return result.scalars().all()

# #     async def get_any_membership(
# #         self, *, organization_id: uuid.UUID, user_id: uuid.UUID
# #     ) -> OrganizationMember | None:
# #         result = await self.session.execute(
# #             select(OrganizationMember).where(
# #                 OrganizationMember.organization_id == organization_id,
# #                 OrganizationMember.user_id == user_id,
# #             )
# #         )
# #         return result.scalar_one_or_none()


# """Organization data access layer — pure DB queries, no business logic."""

# import uuid

# from sqlalchemy import and_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.organization import Organization
# from app.models.organization_member import OrganizationMember
# from app.models.role import Role
# from app.models.team_member import TeamMember
# from app.models.user import User


# class OrganizationRepository:
#     def __init__(self, session: AsyncSession) -> None:
#         self.session = session

#     async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
#         result = await self.session.execute(
#             select(Organization).where(
#                 Organization.id == organization_id,
#                 Organization.deleted_at.is_(None),
#             )
#         )
#         return result.scalar_one_or_none()

#     async def get_by_slug(self, slug: str) -> Organization | None:
#         result = await self.session.execute(
#             select(Organization).where(
#                 Organization.slug == slug, Organization.deleted_at.is_(None)
#             )
#         )
#         return result.scalar_one_or_none()

#     async def create(self, *, name: str, slug: str) -> Organization:
#         org = Organization(name=name, slug=slug)
#         self.session.add(org)
#         await self.session.flush()
#         return org

#     async def update(
#         self, org: Organization, *, name: str | None = None
#     ) -> Organization:
#         if name is not None:
#             org.name = name
#         await self.session.flush()
#         return org

#     async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
#         stmt = (
#             select(Organization)
#             .join(
#                 OrganizationMember,
#                 OrganizationMember.organization_id == Organization.id,
#             )
#             .where(
#                 OrganizationMember.user_id == user_id,
#                 OrganizationMember.deleted_at.is_(None),
#                 Organization.deleted_at.is_(None),
#             )
#         )
#         result = await self.session.execute(stmt)
#         return list(result.scalars().all())

#     async def get_role_by_name(
#         self, *, organization_id: uuid.UUID, role_name: str
#     ) -> Role | None:
#         result = await self.session.execute(
#             select(Role).where(
#                 Role.name == role_name,
#                 (Role.organization_id == organization_id)
#                 | (Role.organization_id.is_(None)),
#             )
#         )
#         return result.scalar_one_or_none()

#     async def add_member(
#         self, *, organization_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID
#     ) -> OrganizationMember:
#         membership = OrganizationMember(
#             organization_id=organization_id, user_id=user_id, role_id=role_id
#         )
#         self.session.add(membership)
#         await self.session.flush()
#         return membership

#     # 1. Fetch ONLY ACTIVE Organization Member
#     async def get_membership(
#         self, *, organization_id: uuid.UUID, user_id: uuid.UUID
#     ) -> OrganizationMember | None:
#         result = await self.session.execute(
#             select(OrganizationMember).where(
#                 OrganizationMember.organization_id == organization_id,
#                 OrganizationMember.user_id == user_id,
#                 OrganizationMember.deleted_at.is_(None),
#             )
#         )
#         return result.scalar_one_or_none()

#     # 2. Fetch ANY Organization Member (Active OR Deactivated)
#     async def get_any_membership(
#         self, *, organization_id: uuid.UUID, user_id: uuid.UUID
#     ) -> tuple[OrganizationMember, User] | None:
#         result = await self.session.execute(
#             select(OrganizationMember, User)
#             .join(User, User.id == OrganizationMember.user_id)
#             .where(
#                 OrganizationMember.organization_id == organization_id,
#                 OrganizationMember.user_id == user_id,
#             )
#         )
#         row = result.first()
#         if row:
#             return row[0], row[1]  # returns (OrganizationMember, User)
#         return None

#     # 3. List ONLY Active Organization Members (for Organization Members List API)
#     async def list_members(
#         self, organization_id: uuid.UUID
#     ) -> list[tuple[OrganizationMember, User]]:
#         query = (
#             select(OrganizationMember, User)
#             .join(User, OrganizationMember.user_id == User.id)
#             .where(
#                 OrganizationMember.organization_id == organization_id,
#                 OrganizationMember.deleted_at.is_(None),
#             )
#         )
#         result = await self.session.execute(query)
#         return list(result.tuples().all())

#     # 4. Dropdown List: Unassigned active organization members for a team
#     async def get_unassigned_team_members(
#         self, organization_id: uuid.UUID, team_id: uuid.UUID
#     ) -> list[User]:
#         query = (
#             select(User)
#             .join(OrganizationMember, OrganizationMember.user_id == User.id)
#             .outerjoin(
#                 TeamMember,
#                 and_(
#                     TeamMember.user_id == User.id,
#                     TeamMember.team_id == team_id,
#                     # TeamMember.deleted_at == None,
#                 ),
#             )
#             .where(
#                 OrganizationMember.organization_id == organization_id,
#                 OrganizationMember.deleted_at.is_(None),  # Must be ACTIVE in Org
#                 TeamMember.id.is_(None),  # Must NOT be in Team
#             )
#         )

#         result = await self.session.execute(query)
#         return list(result.scalars().all())


import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.models.project import Project
from app.models.role import Role
from app.models.task import Task
from app.models.team_member import TeamMember
from app.models.user import User


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(
                Organization.slug == slug,
                Organization.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, *, name: str, slug: str) -> Organization:
        org = Organization(name=name, slug=slug)
        self.session.add(org)
        await self.session.flush()
        return org

    async def update(
        self, org: Organization, *, name: str | None = None
    ) -> Organization:
        if name is not None:
            org.name = name
        await self.session.flush()
        return org

    async def soft_delete(self, org: Organization) -> None:
        now = datetime.now(timezone.utc)
        org.deleted_at = now
        await self.session.flush()

    async def soft_delete_cascade_organization_data(
        self, organization_id: uuid.UUID
    ) -> None:
        now = datetime.now(timezone.utc)

        # 1. Soft delete all members inside the organization
        await self.session.execute(
            update(OrganizationMember)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )

        # 2. Soft delete all projects under the organization
        await self.session.execute(
            update(Project)
            .where(
                Project.organization_id == organization_id,
                Project.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )

        # 3. Soft delete all tasks under the organization
        await self.session.execute(
            update(Task)
            .where(
                Task.organization_id == organization_id,
                Task.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )
        await self.session.flush()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(
                OrganizationMember,
                OrganizationMember.organization_id == Organization.id,
            )
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
                Organization.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_role_by_name(
        self, *, organization_id: uuid.UUID, role_name: str
    ) -> Role | None:
        result = await self.session.execute(
            select(Role).where(
                Role.name == role_name,
                (Role.organization_id == organization_id)
                | (Role.organization_id.is_(None)),
            )
        )
        return result.scalar_one_or_none()

    async def add_member(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID, role_id: uuid.UUID
    ) -> OrganizationMember:
        membership = OrganizationMember(
            organization_id=organization_id, user_id=user_id, role_id=role_id
        )
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def get_membership(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> OrganizationMember | None:
        result = await self.session.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_any_membership(
        self, *, organization_id: uuid.UUID, user_id: uuid.UUID
    ) -> tuple[OrganizationMember, User] | None:
        result = await self.session.execute(
            select(OrganizationMember, User)
            .join(User, User.id == OrganizationMember.user_id)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        row = result.first()
        if row:
            return row[0], row[1]
        return None

    async def list_members(
        self, organization_id: uuid.UUID
    ) -> list[tuple[OrganizationMember, User]]:
        query = (
            select(OrganizationMember, User)
            .join(User, OrganizationMember.user_id == User.id)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return list(result.tuples().all())

    async def get_unassigned_team_members(
        self, organization_id: uuid.UUID, team_id: uuid.UUID
    ) -> list[User]:
        query = (
            select(User)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .outerjoin(
                TeamMember,
                and_(
                    TeamMember.user_id == User.id,
                    TeamMember.team_id == team_id,
                ),
            )
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
                TeamMember.id.is_(None),
            )
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())
