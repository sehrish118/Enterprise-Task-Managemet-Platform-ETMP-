from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

import uuid


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


# ── Password Hashing ────────────────────────────────────────────────


def hash_password(plain_password: str) -> str:
    """One-way hash. bcrypt generates its own salt internally — never
    store or handle salts manually."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time comparison under the hood (via passlib) — avoids
    timing attacks that a naive `==` comparison would be vulnerable to."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ───────────────────────────────────────────────────────


def _create_token(
    user_id: UUID, token_type: TokenType, expires_delta: timedelta
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(user_id: UUID) -> str:
    return _create_token(
        user_id,
        TokenType.ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: UUID) -> str:
    return _create_token(
        user_id,
        TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: TokenType) -> UUID:

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e

    if payload.get("type") != expected_type.value:
        raise ValueError(
            f"Expected a {expected_type.value} token, got {payload.get('type')}"
        )

    sub = payload.get("sub")
    if sub is None:
        raise ValueError("Token missing 'sub' claim")

    return UUID(sub)


def create_invite_token(
    email: str,
    organization_id: uuid.UUID,
    team_id: uuid.UUID,
    role: str = "MEMBER",
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=48)
    payload = {
        "sub": email,
        "org_id": str(organization_id),
        "team_id": str(team_id),
        "role": role,
        "type": "invitation",
        "exp": expire,
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_invite_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "invitation":
            return None
        return payload
    except JWTError:
        return None
