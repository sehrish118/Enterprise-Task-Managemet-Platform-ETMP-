"""
Simple in-memory sliding-window rate limiter, keyed by client IP.
Adequate for a single-process dev/portfolio deployment. When Redis is
introduced later in the roadmap, this should move to a Redis-backed
counter so limits are shared across multiple app instances.
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 100

_request_log: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        window_start = now - WINDOW_SECONDS
        _request_log[client_ip] = [
            t for t in _request_log[client_ip] if t > window_start
        ]

        if len(_request_log[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        _request_log[client_ip].append(now)
        return await call_next(request)
