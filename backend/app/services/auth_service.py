"""
Owns every rule around authentication: what makes a password valid,
what happens on login, how tokens are rotated, what logout means.
Nothing here touches SQLAlchemy query syntax directly — that's the
repositories' job. This separation is what lets us unit-test business
rules with a mocked repository instead of a real database.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateResourceException,
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
)
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from app.models.enums import RoleName
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import AuthUserResponse, LoginResponse, RegisterRequest, TokenResponse
from app.core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    # ---------- Registration ----------

    def register(self, payload: RegisterRequest) -> AuthUserResponse:
        if self.user_repo.exists_by_email_or_phone(payload.email, payload.phone):
            raise DuplicateResourceException("An account with this email or phone already exists")

        customer_role = self.role_repo.get_by_name(RoleName.CUSTOMER.value)
        if customer_role is None:
            # Defensive: should never happen post-seed, but fail loudly if it does.
            raise DuplicateResourceException("Default role not seeded — contact administrator")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            role_id=customer_role.id,
            is_active=True,
        )
        self.user_repo.create(user)
        self.db.commit()

        return AuthUserResponse(id=str(user.id), full_name=user.full_name, email=user.email, role=customer_role.name)

    # ---------- Login ----------

    def login(self, email: str, password: str) -> tuple[LoginResponse, str]:
        """Returns (response body, raw refresh token) — the raw refresh
        token is set as an httpOnly cookie by the route, never in JSON."""
        user = self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        access_token = create_access_token(user.id, user.role.name)
        raw_refresh_token, refresh_record = self._issue_refresh_token(user.id)

        self.db.commit()

        response = LoginResponse(
            user=AuthUserResponse(id=str(user.id), full_name=user.full_name, email=user.email, role=user.role.name),
            tokens=TokenResponse(
                access_token=access_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
        )
        return response, raw_refresh_token

    # ---------- Refresh ----------

    def refresh(self, raw_refresh_token: str) -> tuple[TokenResponse, str]:
        """
        Rotates the refresh token on every use (issue a new one, revoke the
        old one). This limits the damage window if a refresh token is ever
        stolen — a replayed old token is immediately detectable as invalid.
        """
        token_hash = hash_refresh_token(raw_refresh_token)
        existing = self.token_repo.get_by_hash(token_hash)

        if existing is None or existing.is_revoked:
            raise InvalidTokenException()

        if existing.expires_at < datetime.now(timezone.utc):
            raise InvalidTokenException()

        user = self.user_repo.get_by_id(existing.user_id)
        if user is None or not user.is_active:
            raise InactiveUserException()

        # Rotate: revoke old, issue new
        self.token_repo.revoke(existing)
        new_raw_token, _ = self._issue_refresh_token(user.id)
        new_access_token = create_access_token(user.id, user.role.name)

        self.db.commit()

        return (
            TokenResponse(access_token=new_access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            new_raw_token,
        )

    # ---------- Logout ----------

    def logout(self, raw_refresh_token: str) -> None:
        token_hash = hash_refresh_token(raw_refresh_token)
        existing = self.token_repo.get_by_hash(token_hash)
        if existing and not existing.is_revoked:
            self.token_repo.revoke(existing)
            self.db.commit()
        # Idempotent by design: logging out with an already-invalid token
        # is not an error — the end state (no valid session) is what matters.

    # ---------- Internal ----------

    def _issue_refresh_token(self, user_id) -> tuple[str, RefreshToken]:
        raw_token = generate_refresh_token()
        record = RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=refresh_token_expiry(),
        )
        self.token_repo.create(record)
        return raw_token, record