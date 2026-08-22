import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationRead
from app.services.notification_service import NotificationService
from app.core.exceptions import NotificationNotFoundError, NotYourNotificationError

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
async def list_my_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[NotificationRead]:
    service = NotificationService(db)
    notifications = await service.list_my_notifications(current_user.id)
    return [NotificationRead.model_validate(n) for n in notifications]


@router.post("/{notification_id}/mark-read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationRead:
    service = NotificationService(db)
    try:
        notification = await service.mark_read(
            notification_id=notification_id, requesting_user_id=current_user.id
        )
        await db.commit()
    except NotificationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except NotYourNotificationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e

    return NotificationRead.model_validate(notification)
