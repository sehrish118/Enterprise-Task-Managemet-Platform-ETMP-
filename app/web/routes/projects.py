"""Web routes for projects — reuses ProjectService."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ProjectNameAlreadyExistsError,
    UserAlreadyProjectMemberError,
    UserNotFoundError,
    UserNotOrganizationMemberError,
)
from app.db.session import get_db
from app.models.user import User
from app.services.project_service import ProjectService
from app.web.dependencies import get_current_user_from_cookie, require_permission_web
from app.enums.permissions import Permissions

router = APIRouter(tags=["web-projects"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/projects")
async def list_projects(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_uuid = uuid.UUID(organization_id)
    service = ProjectService(db)
    projects = await service.list_projects(
        organization_id=org_uuid, requesting_user_id=current_user.id
    )
    return templates.TemplateResponse(
        request,
        "projects.html",
        {"projects": projects, "organization_id": organization_id},
    )


@router.post("/organizations/{organization_id}/projects")
async def create_project(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
    _: Annotated[None, Depends(require_permission_web(Permissions.PROJECT_CREATE))],
):
    org_uuid = uuid.UUID(organization_id)
    service = ProjectService(db)
    try:
        await service.create_project(
            organization_id=org_uuid, name=name, created_by=current_user.id
        )
    except ProjectNameAlreadyExistsError:
        projects = await service.list_projects(
            organization_id=org_uuid, requesting_user_id=current_user.id
        )  # <-- FIX 2
        return templates.TemplateResponse(
            request,
            "projects.html",
            {
                "projects": projects,
                "organization_id": organization_id,
                "error": "Project name already exists",
            },
        )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects", status_code=303
    )


@router.get("/organizations/{organization_id}/projects/{project_id}")
async def project_detail(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = ProjectService(db)
    project_uuid = uuid.UUID(project_id)
    project = await service.get_project(
        project_uuid,
        requesting_user_id=current_user.id,
        organization_id=uuid.UUID(organization_id),
    )
    members = await service.list_members_with_names(
        project_uuid,
        requesting_user_id=current_user.id,
        organization_id=uuid.UUID(organization_id),
    )
    return templates.TemplateResponse(
        request, "project_detail.html", {"project": project, "members": members}
    )


@router.post("/organizations/{organization_id}/projects/{project_id}/update")
async def update_project(
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
    status: Annotated[str, Form()],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.PROJECT_MANAGE_MEMBERS))
    ],
):
    service = ProjectService(db)
    await service.update_project(
        project_id=uuid.UUID(project_id),
        name=name,
        status=status,
        is_archived=None,
        requesting_user_id=current_user.id,
        organization_id=uuid.UUID(organization_id),
    )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{project_id}", status_code=303
    )


@router.post("/organizations/{organization_id}/projects/{project_id}/delete")
async def delete_project(
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission_web(Permissions.PROJECT_DELETE))],
):
    service = ProjectService(db)
    await service.delete_project(
        uuid.UUID(project_id),
        requesting_user_id=current_user.id,
        organization_id=uuid.UUID(organization_id),
    )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects", status_code=303
    )


@router.post("/organizations/{organization_id}/projects/{project_id}/members")
async def add_project_member(
    request: Request,
    organization_id: str,
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Form()],
    role: Annotated[str, Form()],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.PROJECT_MANAGE_MEMBERS))
    ],
):
    org_uuid = uuid.UUID(organization_id)
    project_uuid = uuid.UUID(project_id)
    service = ProjectService(db)
    try:
        await service.add_member(
            organization_id=org_uuid,
            project_id=project_uuid,
            email=email,
            role=role,
            requesting_user_id=current_user.id,
        )
    except (
        UserNotFoundError,
        UserAlreadyProjectMemberError,
        UserNotOrganizationMemberError,
    ) as e:
        project = await service.get_project(
            project_uuid,
            requesting_user_id=current_user.id,
            organization_id=uuid.UUID(organization_id),
        )
        members = await service.list_members_with_names(
            project_uuid,
            requesting_user_id=current_user.id,
            organization_id=uuid.UUID(organization_id),
        )

        return templates.TemplateResponse(
            request,
            "project_detail.html",
            {"project": project, "members": members, "error": str(e)},
        )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/projects/{project_id}", status_code=303
    )
