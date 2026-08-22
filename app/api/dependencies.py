# app/api/dependencies.py
"""
Shared FastAPI dependencies — DB session and current-user extraction.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

import uuid
from typing import Callable

from app.core.exceptions import InvalidCredentialsError  # already ho sakta hai
from app.repositories.rbac_repository import RBACRepository

from app.core.security import TokenType, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# tokenUrl is just for Swagger UI's "Authorize" button — doesn't affect
# actual token verification logic below.
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials  # extracts the raw token string after "Bearer "

    try:
        user_id = decode_token(token, TokenType.ACCESS)
    except ValueError:
        raise credentials_exception

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_permission(permission_code: str) -> Callable:
    """
    Dependency factory — returns a FastAPI dependency that checks
    whether the current user has the given permission within the
    organization specified in the URL path.

    Usage in a router:
        @router.post("/organizations/{organization_id}/tasks")
        async def create_task(
            organization_id: uuid.UUID,
            current_user: Annotated[User, Depends(get_current_user)],
            _: Annotated[None, Depends(require_permission(Permissions.TASK_CREATE))],
        ):
            ...
    """

    async def dependency(
        organization_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        rbac_repo = RBACRepository(db)
        has_permission = await rbac_repo.user_has_permission(
            user_id=current_user.id,
            organization_id=organization_id,
            permission_code=permission_code,
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have the '{permission_code}' permission in this organization.",
            )

    return dependency
