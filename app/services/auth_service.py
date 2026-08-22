# # app/services/auth_service.py
# """
# Authentication business logic — register, login, token refresh.

# This is where hashing utilities (core/security.py) and data access
# (repositories/user_repository.py) come together. Routers will call
# these methods; routers never talk to the repository or security.py
# directly — that would leak business logic into the API layer.
# """

# import uuid

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.exceptions import (
#     EmailAlreadyExistsError,
#     InvalidCredentialsError,
#     InvalidTokenError,
# )
# from app.core.security import (
#     TokenType,
#     create_access_token,
#     create_refresh_token,
#     decode_token,
#     hash_password,
#     verify_password,
# )
# from app.models.user import User
# from app.repositories.user_repository import UserRepository
# from app.core.security import decode_invite_token
# from app.models.team_member import TeamMemberRole
# from app.repositories.organization_repository import OrganizationRepository
# from app.repositories.team_repository import TeamRepository


# class AuthService:
#     def __init__(self, session: AsyncSession) -> None:
#         self.session = session
#         self.user_repo = UserRepository(session)

#     async def register(self, *, email: str, password: str, full_name: str) -> User:
#         existing = await self.user_repo.get_by_email(email)
#         if existing is not None:
#             raise EmailAlreadyExistsError(f"Email '{email}' is already registered")

#         password_hash = hash_password(password)
#         user = await self.user_repo.create(
#             email=email, password_hash=password_hash, full_name=full_name
#         )
#         await self.session.commit()
#         return user

#     async def login(self, *, email: str, password: str) -> tuple[str, str]:
#         """Returns (access_token, refresh_token)."""
#         user = await self.user_repo.get_by_email(email)
#         if user is None or not verify_password(password, user.password_hash):
#             # Deliberately identical error for "no such user" and "wrong
#             # password" — distinguishing them lets an attacker enumerate
#             # valid emails.
#             raise InvalidCredentialsError("Incorrect email or password")

#         if not user.is_active:
#             raise InvalidCredentialsError("Incorrect email or password")

#         access_token = create_access_token(user.id)
#         refresh_token = create_refresh_token(user.id)
#         return access_token, refresh_token

#     async def refresh_access_token(self, *, refresh_token: str) -> str:
#         try:
#             user_id: uuid.UUID = decode_token(refresh_token, TokenType.REFRESH)
#         except ValueError as e:
#             raise InvalidTokenError(str(e)) from e

#         user = await self.user_repo.get_by_id(user_id)
#         if user is None or not user.is_active:
#             raise InvalidTokenError("User no longer exists or is inactive")

#         return create_access_token(user.id)


# async def accept_invitation(self, *, token: str, full_name: str, password: str) -> User:
#     # Decode invitation token
#     payload = decode_invite_token(token)
#     if not payload:
#         raise InvalidTokenError("Invalid or expired invitation token.")

#     email = payload["sub"]
#     organization_id = uuid.UUID(payload["org_id"])
#     team_id = uuid.UUID(payload["team_id"])
#     role_str = payload.get("role", "MEMBER")

#     # 1. Register User if account doesn't exist
#     user = await self.user_repo.get_by_email(email)
#     if not user:
#         user = await self.register(email=email, password=password, full_name=full_name)

#     # Initialize variable to prevent UnboundLocalError
#     member_role = None

#     # 2. Add to OrganizationMember if not already added
#     org_repo = OrganizationRepository(self.session)
#     org_member = await org_repo.get_membership(
#         organization_id=organization_id, user_id=user.id
#     )

#     if not org_member:
#         member_role = await org_repo.get_role_by_name(
#             organization_id=organization_id, role_name="Member"
#         )
#         if member_role:
#             await org_repo.add_member(
#                 organization_id=organization_id,
#                 user_id=user.id,
#                 role_id=member_role.id,
#             )

#     # 3. Add to TeamMember if not already added
#     team_repo = TeamRepository(self.session)
#     team_member = await team_repo.get_membership(team_id=team_id, user_id=user.id)

#     if not team_member:
#         # Directly pass string role ("MEMBER" / "TEAM_LEAD") as per schema definition
#         await team_repo.add_member(
#             organization_id=organization_id,
#             team_id=team_id,
#             user_id=user.id,
#             role=role_str,
#         )

#     await self.session.commit()
#     return user


# app/services/auth_service.py
"""
Authentication business logic — register, login, token refresh.

This is where hashing utilities (core/security.py) and data access
(repositories/user_repository.py) come together. Routers will call
these methods; routers never talk to the repository or security.py
directly — that would leak business logic into the API layer.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_invite_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.team_repository import TeamRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, *, email: str, password: str, full_name: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyExistsError(f"Email '{email}' is already registered")

        password_hash = hash_password(password)
        user = await self.user_repo.create(
            email=email, password_hash=password_hash, full_name=full_name
        )
        await self.session.commit()
        return user

    async def login(self, *, email: str, password: str) -> tuple[str, str]:
        """Returns (access_token, refresh_token)."""
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            # Deliberately identical error for "no such user" and "wrong
            # password" — distinguishing them lets an attacker enumerate
            # valid emails.
            raise InvalidCredentialsError("Incorrect email or password")

        if not user.is_active:
            raise InvalidCredentialsError("Incorrect email or password")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return access_token, refresh_token

    async def refresh_access_token(self, *, refresh_token: str) -> str:
        try:
            user_id: uuid.UUID = decode_token(refresh_token, TokenType.REFRESH)
        except ValueError as e:
            raise InvalidTokenError(str(e)) from e

        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidTokenError("User no longer exists or is inactive")

        return create_access_token(user.id)

    async def accept_invitation(
        self, *, token: str, full_name: str, password: str
    ) -> User:
        # Decode invitation token
        payload = decode_invite_token(token)
        if not payload:
            raise InvalidTokenError("Invalid or expired invitation token.")

        email = payload["sub"]
        organization_id = uuid.UUID(payload["org_id"])
        team_id = uuid.UUID(payload["team_id"])
        role_str = payload.get("role", "MEMBER")

        # 1. Register User if account doesn't exist
        user = await self.user_repo.get_by_email(email)
        if not user:
            user = await self.register(
                email=email, password=password, full_name=full_name
            )

        # Initialize variable to prevent UnboundLocalError
        member_role = None

        # 2. Add to OrganizationMember if not already added
        org_repo = OrganizationRepository(self.session)
        org_member = await org_repo.get_membership(
            organization_id=organization_id, user_id=user.id
        )

        if not org_member:
            member_role = await org_repo.get_role_by_name(
                organization_id=organization_id, role_name="Member"
            )
            if member_role:
                await org_repo.add_member(
                    organization_id=organization_id,
                    user_id=user.id,
                    role_id=member_role.id,
                )

        # 3. Add to TeamMember if not already added
        team_repo = TeamRepository(self.session)
        team_member = await team_repo.get_membership(team_id=team_id, user_id=user.id)

        if not team_member:
            # Directly pass string role ("MEMBER" / "TEAM_LEAD") as per schema definition
            await team_repo.add_member(
                organization_id=organization_id,
                team_id=team_id,
                user_id=user.id,
                role=role_str,
            )

        await self.session.commit()
        return user
