# app/repositories/rbac_repository.py

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization_member import OrganizationMember
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission


class RBACRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def user_has_permission(
        self, *, user_id: uuid.UUID, organization_id: uuid.UUID, permission_code: str
    ) -> bool:
        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(OrganizationMember, OrganizationMember.role_id == Role.id)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
                Permission.name == permission_code,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_organization_member(
        self, *, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> bool:
        """Used when we just need membership, not a specific permission
        (e.g. viewing shared resources any member can see)."""
        stmt = select(OrganizationMember.id).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def user_is_org_admin_or_owner(
        self, *, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> bool:
        """Convenience check: does this user have org-management-level
        access? Used to decide 'see all projects' vs 'see only my
        projects' without hardcoding role names."""
        return await self.user_has_permission(
            user_id=user_id,
            organization_id=organization_id,
            permission_code="organization:manage_settings",
        )
