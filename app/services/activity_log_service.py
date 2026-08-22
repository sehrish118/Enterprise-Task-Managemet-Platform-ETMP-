import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog
from app.repositories.activity_log_repository import ActivityLogRepository


class ActivityLogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.log_repo = ActivityLogRepository(session)

    async def log(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> ActivityLog:
        return await self.log_repo.create(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def list_for_organization(
        self, organization_id: uuid.UUID
    ) -> list[ActivityLog]:
        return await self.log_repo.list_for_organization(organization_id)
