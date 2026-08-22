"""Web routes for teams — reuses TeamService."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    TeamNameAlreadyExistsError,
    UserAlreadyTeamMemberError,
    UserNotFoundError,
    UserNotOrganizationMemberError,
)
from app.db.session import get_db
from app.models.user import User
from app.services.team_service import TeamService
from app.enums.permissions import Permissions
from app.web.dependencies import get_current_user_from_cookie, require_permission_web

router = APIRouter(tags=["web-teams"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/teams")
async def list_teams(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = TeamService(db)
    teams = await service.list_teams(uuid.UUID(organization_id))
    return templates.TemplateResponse(
        request, "teams.html", {"teams": teams, "organization_id": organization_id}
    )


@router.post("/organizations/{organization_id}/teams")
async def create_team(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
    _: Annotated[None, Depends(require_permission_web(Permissions.TEAM_CREATE))],
):
    org_uuid = uuid.UUID(organization_id)
    service = TeamService(db)
    try:
        await service.create_team(organization_id=org_uuid, name=name)
    except TeamNameAlreadyExistsError:
        teams = await service.list_teams(org_uuid)
        return templates.TemplateResponse(
            request,
            "teams.html",
            {
                "teams": teams,
                "organization_id": organization_id,
                "error": "Team name already exists",
            },
        )
    return RedirectResponse(
        url=f"/organizations/{organization_id}/teams", status_code=303
    )


@router.get("/organizations/{organization_id}/teams/{team_id}")
async def team_detail(
    request: Request,
    organization_id: str,
    team_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = TeamService(db)
    team = await service.get_team(uuid.UUID(team_id))
    members = await service.list_members_with_names(uuid.UUID(team_id))
    return templates.TemplateResponse(
        request,
        "team_detail.html",
        {"team": team, "members": members, "organization_id": organization_id},
    )


@router.post("/organizations/{organization_id}/teams/{team_id}/update")
async def update_team(
    organization_id: str,
    team_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    name: Annotated[str, Form()],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.TEAM_MANAGE_MEMBERS))
    ],
):
    service = TeamService(db)
    await service.update_team(team_id=uuid.UUID(team_id), name=name)
    return RedirectResponse(
        url=f"/organizations/{organization_id}/teams/{team_id}", status_code=303
    )


@router.post("/organizations/{organization_id}/teams/{team_id}/delete")
async def delete_team(
    organization_id: str,
    team_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission_web(Permissions.TEAM_DELETE))],
):
    service = TeamService(db)
    await service.delete_team(uuid.UUID(team_id))
    return RedirectResponse(
        url=f"/organizations/{organization_id}/teams", status_code=303
    )


@router.post("/organizations/{organization_id}/teams/{team_id}/members")
async def add_team_member(
    request: Request,
    organization_id: str,
    team_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Form()],
    role: Annotated[str, Form()],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.TEAM_MANAGE_MEMBERS))
    ],
):
    org_uuid = uuid.UUID(organization_id)
    team_uuid = uuid.UUID(team_id)
    service = TeamService(db)
    try:
        await service.add_member(
            organization_id=org_uuid, team_id=team_uuid, email=email, role=role
        )
    except (
        UserNotFoundError,
        UserAlreadyTeamMemberError,
        UserNotOrganizationMemberError,
    ) as e:
        team = await service.get_team(team_uuid)
        members = await service.list_members_with_names(uuid.UUID(team_id))
        return templates.TemplateResponse(
            request,
            "team_detail.html",
            {
                "team": team,
                "members": members,
                "organization_id": organization_id,
                "error": str(e),
            },
        )

    return RedirectResponse(
        url=f"/organizations/{organization_id}/teams/{team_id}", status_code=303
    )
