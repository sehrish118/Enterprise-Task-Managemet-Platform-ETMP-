# # app/api/v1/auth.py
# """
# Authentication routes — thin layer, delegates everything to AuthService.
# """

# import uuid
# from app.api.dependencies import require_permission
# from app.enums.permissions import Permissions

# from typing import Annotated

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.exceptions import (
#     EmailAlreadyExistsError,
#     InvalidCredentialsError,
#     InvalidTokenError,
# )
# from app.db.session import get_db
# from app.schemas.user import Token, TokenRefreshRequest, UserCreate, UserLogin, UserRead
# from app.services.auth_service import AuthService

# # app/api/v1/auth.py mein imports mein add karo:
# from app.api.dependencies import get_current_user
# from app.models.user import User


# router = APIRouter(prefix="/auth", tags=["auth"])


# @router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
# async def register(
#     payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
# ) -> UserRead:
#     service = AuthService(db)
#     try:
#         user = await service.register(
#             email=payload.email, password=payload.password, full_name=payload.full_name
#         )
#     except EmailAlreadyExistsError as e:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
#     return UserRead.model_validate(user)


# @router.post("/login", response_model=Token)
# async def login(
#     payload: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]
# ) -> Token:
#     service = AuthService(db)

#     try:
#         access_token, refresh_token = await service.login(
#             email=payload.email, password=payload.password
#         )
#     except InvalidCredentialsError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
#         ) from e
#     return Token(access_token=access_token, refresh_token=refresh_token)


# @router.post("/refresh", response_model=Token)
# async def refresh(
#     payload: TokenRefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]
# ) -> Token:
#     service = AuthService(db)
#     try:
#         access_token = await service.refresh_access_token(
#             refresh_token=payload.refresh_token
#         )
#     except InvalidTokenError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
#         ) from e
#     return Token(access_token=access_token, refresh_token=payload.refresh_token)


# # file ke end mein naya endpoint add karo:
# @router.get("/me", response_model=UserRead)
# async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
#     return UserRead.model_validate(current_user)


# # Endpoints add karo:
# @router.get("/organizations/{organization_id}/test-member-permission")
# async def test_member_permission(
#     organization_id: uuid.UUID,
#     _: Annotated[None, Depends(require_permission(Permissions.TASK_CREATE))],
# ) -> dict:
#     return {
#         "message": "You have task:create permission — Member role should ALLOW this."
#     }


# @router.get("/organizations/{organization_id}/test-owner-only-permission")
# async def test_owner_only_permission(
#     organization_id: uuid.UUID,
#     _: Annotated[None, Depends(require_permission(Permissions.ORG_DELETE))],
# ) -> dict:
#     return {"message": "You have organization:delete — this should FAIL for a Member."}


"""
Authentication routes — thin layer, delegates everything to AuthService.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.user import (
    AcceptInviteRequest,
    Token,
    TokenRefreshRequest,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRead:
    service = AuthService(db)
    try:
        user = await service.register(
            email=payload.email, password=payload.password, full_name=payload.full_name
        )
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    service = AuthService(db)

    try:
        access_token, refresh_token = await service.login(
            email=payload.email, password=payload.password
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(
    payload: TokenRefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    service = AuthService(db)
    try:
        access_token = await service.refresh_access_token(
            refresh_token=payload.refresh_token
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    return Token(access_token=access_token, refresh_token=payload.refresh_token)


@router.post("/accept-invite", response_model=UserRead, status_code=status.HTTP_200_OK)
async def accept_invite(
    payload: AcceptInviteRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRead:
    service = AuthService(db)
    try:
        user = await service.accept_invitation(
            token=payload.token,
            full_name=payload.full_name,
            password=payload.password,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("/organizations/{organization_id}/test-member-permission")
async def test_member_permission(
    organization_id: uuid.UUID,
    _: Annotated[None, Depends(require_permission(Permissions.TASK_CREATE))],
) -> dict:
    return {
        "message": "You have task:create permission — Member role should ALLOW this."
    }


@router.get("/organizations/{organization_id}/test-owner-only-permission")
async def test_owner_only_permission(
    organization_id: uuid.UUID,
    _: Annotated[None, Depends(require_permission(Permissions.ORG_DELETE))],
) -> dict:
    return {"message": "You have organization:delete — this should FAIL for a Member."}
