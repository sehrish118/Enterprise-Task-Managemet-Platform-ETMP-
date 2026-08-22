import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_permission
from app.db.session import get_db
from app.enums.permissions import Permissions
from app.schemas.activity_log import ActivityLogRead
from app.services.activity_log_service import ActivityLogService

router = APIRouter(
    prefix="/organizations/{organization_id}/activity-logs", tags=["activity-logs"]
)


@router.get("", response_model=list[ActivityLogRead])
async def list_activity_logs(
    organization_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[None, Depends(require_permission(Permissions.ORG_MANAGE_SETTINGS))],
) -> list[ActivityLogRead]:
    service = ActivityLogService(db)
    logs = await service.list_for_organization(organization_id)
    return [ActivityLogRead.model_validate(l) for l in logs]
