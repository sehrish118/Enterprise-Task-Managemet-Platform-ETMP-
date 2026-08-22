"""
Centralized exception handling. Registers a single handler for
DomainError (and its subclasses) so routers no longer need repetitive
try/except blocks — raise the domain exception in the service, and it
gets translated to the correct HTTP response automatically here.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import EXCEPTION_STATUS_MAP, DomainError
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status_code = EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Catches anything NOT explicitly raised as a DomainError — a
        # genuine bug. Logged with full traceback, but the client only
        # ever sees a generic message (never leak internals like SQL
        # errors or stack traces to API consumers).
        logger.error(
            "Unhandled exception", exc_info=True, extra={"path": request.url.path}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
        )
