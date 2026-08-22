"""Web routes for organizations — reuses OrganizationService."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    RoleNotFoundError,
    SlugAlreadyExistsError,
    UserAlreadyMemberError,
    UserNotFoundError,
)
import uuid
from app.enums.permissions import Permissions
from app.db.session import get_db
from app.models.user import User
from app.services.organization_service import OrganizationService
from app.web.dependencies import get_current_user_from_cookie, require_permission_web
from app.core.exceptions import InvalidCredentialsError, UserNotFoundError
from app.services.user_service import UserService


router = APIRouter(tags=["web-organizations"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations")
async def list_organizations(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = OrganizationService(db)
    orgs = await service.list_my_organizations(current_user.id)
    return templates.TemplateResponse(
        request, "organizations.html", {"organizations": orgs}
    )


@router.post("/organizations")
async def create_organization(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
    slug: Annotated[str, Form()],
):
    service = OrganizationService(db)
    try:
        await service.create_organization(
            name=name, slug=slug, creator_user_id=current_user.id
        )
    except SlugAlreadyExistsError:
        orgs = await service.list_my_organizations(current_user.id)
        return templates.TemplateResponse(
            request,
            "organizations.html",
            {"organizations": orgs, "error": "Slug already taken"},
        )
    return RedirectResponse(url="/organizations", status_code=303)


@router.get("/organizations/{organization_id}")
async def organization_detail(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_service = OrganizationService(db)
    user_service = UserService(db)
    org_uuid = uuid.UUID(organization_id)
    org = await org_service.get_organization(org_uuid)
    members = await user_service.list_organization_users(organization_id=org_uuid)
    return templates.TemplateResponse(
        request,
        "organization_detail.html",
        {"organization": org, "members": members, "current_user_id": current_user.id},
    )


@router.post("/organizations/{organization_id}/members")
async def add_member(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Form()],
    role_name: Annotated[str, Form()],
    _: Annotated[None, Depends(require_permission_web(Permissions.ORG_MANAGE_MEMBERS))],
):
    import uuid

    org_uuid = uuid.UUID(organization_id)
    service = OrganizationService(db)
    try:
        await service.add_member(
            organization_id=org_uuid, email=email, role_name=role_name
        )
    except (UserNotFoundError, UserAlreadyMemberError, RoleNotFoundError) as e:
        org = await service.get_organization(org_uuid)
        return templates.TemplateResponse(
            request, "organization_detail.html", {"organization": org, "error": str(e)}
        )
    return RedirectResponse(url=f"/organizations/{organization_id}", status_code=303)


@router.post("/organizations/{organization_id}/users/{user_id}/deactivate")
async def deactivate_user(
    organization_id: str,
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission_web(Permissions.ORG_MANAGE_MEMBERS))],
):
    user_service = UserService(db)
    try:
        await user_service.deactivate_user(
            target_user_id=uuid.UUID(user_id), requesting_user_id=current_user.id
        )
    except (UserNotFoundError, InvalidCredentialsError):
        pass
    return RedirectResponse(url=f"/organizations/{organization_id}", status_code=303)
