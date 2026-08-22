import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.notification_type import NotificationType


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_type_by_code(self, code: str) -> NotificationType | None:
        result = await self.session.execute(
            select(NotificationType).where(NotificationType.code == code)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        type_id: uuid.UUID,
        title: str,
        message: str,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> Notification:
        notification = Notification(
            organization_id=organization_id,
            user_id=user_id,
            type_id=type_id,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        await self.session.flush()
        return notification

    async def list_for_user(self, user_id: uuid.UUID) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())
