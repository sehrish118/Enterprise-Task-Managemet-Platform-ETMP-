from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.v1 import (
    auth,
    users,
    organizations,
    teams,
    projects,
    task_statuses,
    tasks,
    attachments,
    comments,
    activity_logs,
    notifications,
    dashboard,
)
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.core.exception_handlers import register_exception_handlers
from app.api.v1 import documents as documents_router
from app.api.v1 import chat as chat_router

# app/main.py
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for err in errors:
        # Invalid UUID format like 'undefined' in path parameters
        if err.get("type") == "uuid_parsing" and "undefined" in str(err.get("input")):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Invalid UUID parameter provided in URL path. Received 'undefined'."
                },
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting aur Request logging
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    # API Routers
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
    app.include_router(users.router, prefix=settings.API_V1_PREFIX)
    app.include_router(organizations.router, prefix=settings.API_V1_PREFIX)
    app.include_router(teams.router, prefix=settings.API_V1_PREFIX)
    app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
    app.include_router(task_statuses.router, prefix=settings.API_V1_PREFIX)
    app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)
    app.include_router(comments.router, prefix=settings.API_V1_PREFIX)
    app.include_router(attachments.router, prefix=settings.API_V1_PREFIX)
    app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
    app.include_router(activity_logs.router, prefix=settings.API_V1_PREFIX)
    app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
    app.include_router(documents_router.router, prefix=settings.API_V1_PREFIX)
    app.include_router(chat_router.router, prefix=settings.API_V1_PREFIX)

    logger.info("Application configured", extra={"env": settings.APP_ENV})
    return app


app = create_app()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME}


# from fastapi.staticfiles import StaticFiles
# # from app.web.routes import auth as web_auth
# from app.web.routes import dashboard as web_dashboard
# from app.web.routes import organizations as web_organizations
# from app.web.routes import teams as web_teams
# from app.web.routes import projects as web_projects
# from app.web.routes import tasks as web_tasks
# from app.web.routes import notifications as web_notifications
# from app.web.routes import profile as web_profile
# from app.web.routes import organization_dashboard as web_org_dashboard


# app.mount("/static", StaticFiles(directory="app/static"), name="static")


# # Web Routers
# app.include_router(web_auth.router)
# app.include_router(web_dashboard.router)
# app.include_router(web_organizations.router)
# app.include_router(web_teams.router)
# app.include_router(web_projects.router)
# app.include_router(web_tasks.router)
# app.include_router(web_notifications.router)
# app.include_router(web_profile.router)
# app.include_router(web_org_dashboard.router)
