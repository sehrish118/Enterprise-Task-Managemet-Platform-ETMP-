"""Web routes for user profile — reuses UserService."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.db.session import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.web.dependencies import get_current_user_from_cookie

router = APIRouter(tags=["web-profile"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/profile")
async def show_profile(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
):
    return templates.TemplateResponse(request, "profile.html", {"user": current_user})


@router.post("/profile")
async def update_profile(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    full_name: Annotated[str, Form()],
):
    service = UserService(db)
    updated_user = await service.update_profile(
        current_user=current_user, full_name=full_name
    )
    return templates.TemplateResponse(
        request, "profile.html", {"user": updated_user, "success": "Profile updated"}
    )


@router.post("/profile/change-password")
async def change_password(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
):
    service = UserService(db)
    try:
        await service.change_password(
            current_user=current_user,
            current_password=current_password,
            new_password=new_password,
        )
    except InvalidCredentialsError:
        return templates.TemplateResponse(
            request,
            "profile.html",
            {"user": current_user, "error": "Current password is incorrect"},
        )
    return templates.TemplateResponse(
        request,
        "profile.html",
        {"user": current_user, "success": "Password changed successfully"},
    )
