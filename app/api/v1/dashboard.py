import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_permission
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.models.user import User
from app.schemas.dashboard import MyDashboard, OrganizationDashboard
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/me", response_model=MyDashboard)
async def get_my_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MyDashboard:
    service = DashboardService(db)
    return await service.get_my_dashboard(current_user.id)


@router.get(
    "/organizations/{organization_id}/dashboard", response_model=OrganizationDashboard
)
async def get_organization_dashboard(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_SETTINGS))],
) -> OrganizationDashboard:
    service = DashboardService(db)
    return await service.get_organization_dashboard(organization_id)
