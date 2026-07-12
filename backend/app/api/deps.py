"""
FastAPI dependencies: DB session, current-user extraction, and the RBAC
permission gate. Routes declare requirements declaratively —
`current_user = Depends(require_permission(Permission.VEHICLE_WRITE))` —
and never write authorization logic inline. This is the "Permission
Middleware" requirement, implemented as a composable dependency rather
than global middleware, because per-route granularity is what real RBAC
needs (global middleware can only do coarse allow/deny).
"""

from collections.abc import Generator

from fastapi import Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InactiveUserException,
    InsufficientPermissionsException,
    InvalidTokenException,
)
from app.core.permissions import Permission, role_has_permission
from app.core.security import decode_access_token
from app.database.session import SessionLocal
from app.models.enums import RoleName
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if token is None:
        raise InvalidTokenException("Not authenticated")

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise InvalidTokenException()

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenException()

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise InvalidTokenException("User no longer exists")

    if not user.is_active:
        raise InactiveUserException()

    return user


def require_permission(permission: Permission):
    """
    Returns a FastAPI dependency that enforces a single permission.
    Usage: Depends(require_permission(Permission.TRIP_WRITE))
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        role_name = RoleName(current_user.role.name)
        if not role_has_permission(role_name, permission):
            raise InsufficientPermissionsException(
                f"Role '{role_name.value}' lacks permission '{permission.value}'"
            )
        return current_user

    return dependency


def require_role(*allowed_roles: RoleName):
    """Coarser guard for cases where the check is simply role identity."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if RoleName(current_user.role.name) not in allowed_roles:
            raise InsufficientPermissionsException()
        return current_user

    return dependency