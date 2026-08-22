"""
User business logic — profile updates, password changes, org-scoped
listing, and deactivation.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError, UserNotFoundError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def update_profile(
        self, *, current_user: User, full_name: str | None
    ) -> User:
        user = await self.user_repo.update(current_user, full_name=full_name)
        await self.session.commit()
        return user

    async def change_password(
        self, *, current_user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, current_user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")

        new_hash = hash_password(new_password)
        await self.user_repo.update_password(current_user, new_password_hash=new_hash)
        await self.session.commit()

    async def list_organization_users(
        self, *, organization_id: uuid.UUID
    ) -> list[tuple]:
        return await self.user_repo.list_by_organization_with_roles(organization_id)

    async def deactivate_user(
        self, *, target_user_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> User:
        if target_user_id == requesting_user_id:
            raise InvalidCredentialsError("You cannot deactivate your own account")

        user = await self.user_repo.get_by_id(target_user_id)
        if user is None:
            raise UserNotFoundError(f"User {target_user_id} not found")

        user = await self.user_repo.deactivate(user)
        await self.session.commit()
        return user

    async def activate_user(self, target_user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(target_user_id)
        if user is None:
            raise UserNotFoundError(f"User {target_user_id} not found")
        user = await self.user_repo.activate(user)
        await self.session.commit()
        return user
