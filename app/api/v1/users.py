"""
User routes. Self-service (/users/me/*) acts on current_user only.
Admin-scoped routes require organization RBAC permissions.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.core.exceptions import InvalidCredentialsError, UserNotFoundError
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.user import PasswordUpdate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserRead)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/users/me", response_model=UserRead)
async def update_my_profile(
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    service = UserService(db)
    user = await service.update_profile(
        current_user=current_user, full_name=payload.full_name
    )
    return UserRead.model_validate(user)


@router.post("/users/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    payload: PasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = UserService(db)
    try:
        await service.change_password(
            current_user=current_user,
            current_password=payload.current_password,
            new_password=payload.new_password,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.get("/organizations/{organization_id}/users", response_model=list[UserRead])
async def list_organization_users(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    # _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_MEMBERS))],
) -> list[UserRead]:
    service = UserService(db)
    users_with_roles = await service.list_organization_users(
        organization_id=organization_id
    )
    return [
        UserRead(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            is_active=u.is_active,
            created_at=u.created_at,
            role=role_name,
        )
        for u, role_name in users_with_roles
    ]


@router.post(
    "/organizations/{organization_id}/users/{user_id}/deactivate",
    response_model=UserRead,
)
async def deactivate_user(
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_MEMBERS))],
) -> UserRead:
    service = UserService(db)
    try:
        user = await service.deactivate_user(
            target_user_id=user_id, requesting_user_id=current_user.id
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    return UserRead.model_validate(user)


@router.post(
    "/organizations/{organization_id}/users/{user_id}/activate",
    response_model=UserRead,
)
async def activate_user(
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_MEMBERS))],
) -> UserRead:
    service = UserService(db)
    try:
        user = await service.activate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return UserRead.model_validate(user)
