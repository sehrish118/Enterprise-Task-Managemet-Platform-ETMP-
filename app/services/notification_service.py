import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotificationNotFoundError, NotYourNotificationError
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    """
    Called BOTH by the notifications router (list/mark-read) AND
    internally by other services (e.g. TaskService) to fire
    notifications on events like task assignment.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.notif_repo = NotificationRepository(session)

    async def notify(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        type_code: str,
        title: str,
        message: str,
        entity_type: str,
        entity_id: uuid.UUID,
    ) -> Notification | None:
        """
        Fire-and-forget style: if the notification type isn't seeded,
        logs nothing loudly and just skips rather than blocking the
        calling action (a missing notification type should never break
        task assignment, for example).
        """
        notif_type = await self.notif_repo.get_type_by_code(type_code)
        if notif_type is None:
            return None
        return await self.notif_repo.create(
            organization_id=organization_id,
            user_id=user_id,
            type_id=notif_type.id,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def list_my_notifications(self, user_id: uuid.UUID) -> list[Notification]:
        return await self.notif_repo.list_for_user(user_id)

    async def mark_read(
        self, *, notification_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> Notification:
        notification = await self.notif_repo.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFoundError(f"Notification {notification_id} not found")
        if notification.user_id != requesting_user_id:
            raise NotYourNotificationError(
                "You cannot mark another user's notification as read"
            )
        return await self.notif_repo.mark_read(notification)
