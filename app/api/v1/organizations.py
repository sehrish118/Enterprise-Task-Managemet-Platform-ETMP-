"""
Organization routes.

POST /organizations has no organization_id in the path (there isn't
one yet) — so it's the one endpoint here NOT gated by
require_permission(). Every other endpoint requires org membership
with the appropriate permission.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission

from app.core.exceptions import (
    OrganizationNotFoundError,
    RoleNotFoundError,
    SlugAlreadyExistsError,
    UserAlreadyMemberError,
    UserNotFoundError,
)
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.organization import (
    AddMemberRequest,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from app.models.role import Role
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationRead:
    service = OrganizationService(db)
    try:
        org = await service.create_organization(
            name=payload.name, slug=payload.slug, creator_user_id=current_user.id
        )
    except SlugAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    return OrganizationRead.model_validate(org)


@router.get("/me", response_model=list[OrganizationRead])
async def list_my_organizations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[OrganizationRead]:
    service = OrganizationService(db)
    orgs = await service.list_my_organizations(current_user.id)
    return [OrganizationRead.model_validate(o) for o in orgs]


@router.get("/{organization_id}", response_model=OrganizationRead)
async def get_organization(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationRead:
    service = OrganizationService(db)
    try:
        org = await service.get_organization_for_member(
            organization_id, requesting_user_id=current_user.id
        )
    except OrganizationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return OrganizationRead.model_validate(org)


@router.patch("/{organization_id}", response_model=OrganizationRead)
async def update_organization(
    organization_id: uuid.UUID,
    payload: OrganizationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_SETTINGS))],
) -> OrganizationRead:
    service = OrganizationService(db)
    try:
        org = await service.update_organization(
            organization_id=organization_id, name=payload.name
        )
    except OrganizationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return OrganizationRead.model_validate(org)


@router.post("/{organization_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    organization_id: uuid.UUID,
    payload: AddMemberRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_MEMBERS))],
) -> dict:
    service = OrganizationService(db)
    try:
        await service.add_member(
            organization_id=organization_id,
            email=payload.email,
            role_name=payload.role_name,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (UserAlreadyMemberError, RoleNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    return {"message": f"'{payload.email}' added to organization"}


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_DELETE))],
) -> None:
    service = OrganizationService(db)
    try:
        await service.delete_organization(organization_id)
    except OrganizationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{organization_id}/my-membership")
async def get_my_membership(
    organization_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    from app.repositories.organization_repository import OrganizationRepository

    repo = OrganizationRepository(db)
    membership = await repo.get_membership(
        organization_id=organization_id, user_id=current_user.id
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not a member"
        )

    role = await db.get(Role, membership.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not valid Person"
        )

    return {"role": role.name}
