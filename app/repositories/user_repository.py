# app/repositories/user_repository.py
"""
User data access layer — pure DB queries, no business logic.

Note: methods never call session.commit() — that's the Service layer's
responsibility, since a single service operation might involve multiple
repository calls that need to commit together as one transaction.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization_member import OrganizationMember
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, *, email: str, password_hash: str, full_name: str) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name)
        self.session.add(user)
        await self.session.flush()  # assigns user.id without committing
        return user

    async def update(self, user: User, *, full_name: str | None = None) -> User:
        if full_name is not None:
            user.full_name = full_name
        await self.session.flush()
        return user

    async def update_password(self, user: User, *, new_password_hash: str) -> User:
        user.password_hash = new_password_hash
        await self.session.flush()
        return user

    async def deactivate(self, user: User) -> User:
        user.is_active = False
        await self.session.flush()
        return user

    async def activate(self, user: User) -> User:
        user.is_active = True
        await self.session.flush()
        return user

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[User]:
        stmt = (
            select(User)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
                User.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_organization_with_roles(
        self, organization_id: uuid.UUID
    ) -> list[tuple[User, str]]:
        from app.models.organization_member import OrganizationMember
        from app.models.role import Role

        stmt = (
            select(User, Role.name)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .join(Role, Role.id == OrganizationMember.role_id)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.deleted_at.is_(None),
                User.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return [(user, role_name) for user, role_name in result.all()]
