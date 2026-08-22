"""
Organization business logic — creation (atomic with Owner membership),
updates, member management.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    OrganizationNotFoundError,
    RoleNotFoundError,
    SlugAlreadyExistsError,
    UserAlreadyMemberError,
    UserNotFoundError,
)
from app.models.organization import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
import uuid
from typing import Optional


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.org_repo = OrganizationRepository(session)
        self.user_repo = UserRepository(session)

    async def create_organization(
        self, *, name: str, slug: str, creator_user_id: uuid.UUID
    ) -> Organization:
        existing = await self.org_repo.get_by_slug(slug)
        if existing is not None:
            raise SlugAlreadyExistsError(f"Slug '{slug}' is already in use")

        owner_role = await self.org_repo.get_role_by_name(
            organization_id=None,  # type: ignore[arg-type]
            role_name="Owner",
        )
        if owner_role is None:
            raise RoleNotFoundError(
                "System role 'Owner' not found — run the seed script"
            )

        org = await self.org_repo.create(name=name, slug=slug)
        await self.org_repo.add_member(
            organization_id=org.id, user_id=creator_user_id, role_id=owner_role.id
        )
        # Both the org and its owner membership commit together — if
        # either insert had failed, both roll back. An org can never
        # exist without an owner, and vice versa.
        await self.session.commit()
        return org

    async def update_organization(
        self, *, organization_id: uuid.UUID, name: str | None
    ) -> Organization:
        org = await self.org_repo.get_by_id(organization_id)
        if org is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")

        org = await self.org_repo.update(org, name=name)
        await self.session.commit()
        return org

    async def get_organization(self, organization_id: uuid.UUID) -> Organization:
        org = await self.org_repo.get_by_id(organization_id)
        if org is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        return org

    async def list_my_organizations(self, user_id: uuid.UUID) -> list[Organization]:
        return await self.org_repo.list_for_user(user_id)

    async def add_member(
        self, *, organization_id: uuid.UUID, email: str, role_name: str
    ) -> None:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UserNotFoundError(f"No user registered with email '{email}'")

        existing_membership = await self.org_repo.get_membership(
            organization_id=organization_id, user_id=user.id
        )
        if existing_membership is not None:
            raise UserAlreadyMemberError(
                f"'{email}' is already a member of this organization"
            )

        role = await self.org_repo.get_role_by_name(
            organization_id=organization_id, role_name=role_name
        )
        if role is None:
            raise RoleNotFoundError(f"Role '{role_name}' not found")

        await self.org_repo.add_member(
            organization_id=organization_id, user_id=user.id, role_id=role.id
        )
        await self.session.commit()

    async def get_organization_for_member(
        self, organization_id: uuid.UUID, *, requesting_user_id: uuid.UUID
    ) -> Organization:
        """
        Like get_organization(), but only requires the requester to be
        an organization member — not ORG_MANAGE_SETTINGS. Used for
        basic org info (name/slug) so any member can navigate to
        Teams/Projects without hitting an RBAC wall meant for settings.
        """
        org = await self.org_repo.get_by_id(organization_id)
        if org is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")

        membership = await self.org_repo.get_membership(
            organization_id=organization_id, user_id=requesting_user_id
        )
        if membership is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")

        return org

    async def delete_organization(self, organization_id: uuid.UUID) -> None:
        org = await self.org_repo.get_by_id(organization_id)
        if org is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        from datetime import datetime, timezone

        org.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
