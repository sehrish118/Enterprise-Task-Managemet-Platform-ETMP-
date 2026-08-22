"""Web-specific auth dependency — reads JWT from cookie instead of
Authorization header (browsers can't easily attach custom headers
from plain HTML/forms)."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.rbac_repository import RBACRepository
from fastapi import HTTPException, status
import uuid


async def get_current_user_from_cookie(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    try:
        user_id = decode_token(access_token, TokenType.ACCESS)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    return user


def require_permission_web(permission_code: str):
    """
    Cookie-based equivalent of api/dependencies.py's require_permission().
    Used by web routes since they authenticate via cookie, not header.
    """

    async def dependency(
        organization_id: str,
        current_user: Annotated[User, Depends(get_current_user_from_cookie)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        rbac_repo = RBACRepository(db)
        has_permission = await rbac_repo.user_has_permission(
            user_id=current_user.id,
            organization_id=uuid.UUID(organization_id),
            permission_code=permission_code,
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have the '{permission_code}' permission in this organization.",
            )

    return dependency
