import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog


class ActivityLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> ActivityLog:
        log = ActivityLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_for_organization(
        self, organization_id: uuid.UUID
    ) -> list[ActivityLog]:
        result = await self.session.execute(
            select(ActivityLog)
            .where(ActivityLog.organization_id == organization_id)
            .order_by(ActivityLog.created_at.desc())
        )
        return list(result.scalars().all())
