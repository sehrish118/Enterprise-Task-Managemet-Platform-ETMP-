"""Web routes for organization-level dashboard and activity logs."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.services.activity_log_service import ActivityLogService
from app.services.dashboard_service import DashboardService
from app.services.organization_service import OrganizationService
from app.web.dependencies import get_current_user_from_cookie
from app.web.dependencies import get_current_user_from_cookie, require_permission_web

router = APIRouter(tags=["web-org-dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/organizations/{organization_id}/dashboard")
async def organization_dashboard(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.ORG_MANAGE_SETTINGS))
    ],
):
    org_uuid = uuid.UUID(organization_id)
    org_service = OrganizationService(db)
    dash_service = DashboardService(db)
    organization = await org_service.get_organization(org_uuid)
    dashboard = await dash_service.get_organization_dashboard(org_uuid)
    return templates.TemplateResponse(
        request,
        "organization_dashboard.html",
        {"organization": organization, "dashboard": dashboard},
    )


@router.get("/organizations/{organization_id}/activity-logs")
async def activity_logs(
    request: Request,
    organization_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        None, Depends(require_permission_web(Permissions.ORG_MANAGE_SETTINGS))
    ],
):
    service = ActivityLogService(db)
    logs = await service.list_for_organization(uuid.UUID(organization_id))
    return templates.TemplateResponse(
        request,
        "activity_logs.html",
        {"logs": logs, "organization_id": organization_id},
    )
