# app/core/rate_limit.py
"""
Per-user rate limiting for the chatbot specifically. Separate from the
IP-based RateLimitMiddleware because:
1. LLM calls are expensive — need a tighter limit than general API traffic.
2. Keyed by user_id, not IP — multiple employees on the same office
   network shouldn't share one limit.
"""

import redis.asyncio as redis
from fastapi import HTTPException, status

from app.core.config import settings

_redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

CHAT_RATE_LIMIT = 15  # messages
CHAT_RATE_WINDOW_SECONDS = 60


async def enforce_chat_rate_limit(user_id: str) -> None:
    key = f"chat_rate_limit:{user_id}"
    current = await _redis_client.incr(key)
    if current == 1:
        await _redis_client.expire(key, CHAT_RATE_WINDOW_SECONDS)

    if current > CHAT_RATE_LIMIT:
        ttl = await _redis_client.ttl(key)
        wait_seconds = ttl if ttl > 0 else CHAT_RATE_WINDOW_SECONDS
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"You're sending messages too quickly. Please wait "
                f"{wait_seconds} seconds and try again."
            ),
        )
