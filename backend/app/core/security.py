"""
All cryptographic primitives live here and ONLY here — password hashing
and JWT logic must never be duplicated or reimplemented elsewhere in the
codebase (a common source of security bugs).
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


# ---------- Password Hashing ----------

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT Access Tokens ----------

def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """
    Access token carries `sub` (user id) and `role` as claims so downstream
    dependencies can authorize a request WITHOUT hitting the database on
    every single call — a key performance/scalability decision.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": TokenType.ACCESS.value,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises JWTError on invalid/expired token — caller converts to HTTP 401."""
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != TokenType.ACCESS.value:
        raise JWTError("Invalid token type")
    return payload


# ---------- Opaque Refresh Tokens ----------
# Refresh tokens are NOT JWTs. They're random opaque strings whose hash is
# stored server-side. This is intentional: it lets us revoke a specific
# session instantly (delete/flag the DB row), which a self-contained JWT
# refresh token cannot do without an extra blacklist anyway. Simpler and
# more secure to just not make it a JWT at all.

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)