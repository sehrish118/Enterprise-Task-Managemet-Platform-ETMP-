from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter(tags=["web-dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def show_dashboard(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = DashboardService(db)
    dashboard = await service.get_my_dashboard(current_user.id)
    return templates.TemplateResponse(
        request, "dashboard.html", {"user": current_user, "dashboard": dashboard}
    )


@router.get("/logout")
async def logout():
    from fastapi.responses import RedirectResponse

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response
