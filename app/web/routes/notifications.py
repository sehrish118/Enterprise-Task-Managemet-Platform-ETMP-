"""Web routes for notifications — reuses NotificationService."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.notification_service import NotificationService
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter(tags=["web-notifications"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/notifications")
async def list_notifications(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = NotificationService(db)
    notifications = await service.list_my_notifications(current_user.id)
    return templates.TemplateResponse(
        request, "notifications.html", {"notifications": notifications}
    )


@router.post("/notifications/{notification_id}/mark-read")
async def mark_read(
    notification_id: str,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = NotificationService(db)
    await service.mark_read(
        notification_id=uuid.UUID(notification_id), requesting_user_id=current_user.id
    )
    await db.commit()
    return RedirectResponse(url="/notifications", status_code=303)
