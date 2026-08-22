"""
Web (HTML) routes for authentication.

Unlike app/api/v1/auth.py (which returns JSON and expects an
Authorization header), these routes render HTML and use an httponly
cookie to persist the JWT — the standard approach for browser-based
form login, since attaching custom headers from plain HTML isn't
possible without JavaScript.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.db.session import get_db
from app.services.auth_service import AuthService

router = APIRouter(tags=["web-auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def show_login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
async def process_login(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    service = AuthService(db)
    try:
        access_token, refresh_token = await service.login(
            email=email, password=password
        )
    except InvalidCredentialsError:
        return templates.TemplateResponse(
            request, "login.html", {"error": "Incorrect email or password"}
        )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, max_age=1800
    )
    return response


from app.core.exceptions import EmailAlreadyExistsError


@router.get("/register")
async def show_register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post("/register")
async def process_register(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    full_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    service = AuthService(db)
    try:
        await service.register(email=email, password=password, full_name=full_name)
    except EmailAlreadyExistsError:
        return templates.TemplateResponse(
            request, "register.html", {"error": "Email already registered"}
        )

    return RedirectResponse(url="/login", status_code=303)