"""
Thin controller layer: parses HTTP in, calls AuthService, shapes HTTP out.
No business logic lives here — notice login/refresh/logout are one-liners
into the service. Cookie handling (the HTTP-specific concern) is the one
thing that correctly belongs at this layer, not in the service.
"""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.exceptions import InvalidTokenException
from app.middleware.rate_limiter import auth_rate_limiter
from app.models.user import User
from app.schemas.auth_schema import (
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

REFRESH_COOKIE_NAME = "transitops_refresh_token"
REFRESH_COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,                 # inaccessible to JS -> mitigates XSS token theft
        secure=settings.ENVIRONMENT != "development",  # HTTPS-only in prod
        samesite="lax",                # CSRF mitigation for cross-site requests
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/api/v1/auth",           # only sent to auth endpoints, not the whole API
    )


@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(payload)


@router.post("/login", response_model=LoginResponse, dependencies=[Depends(auth_rate_limiter)])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    result, raw_refresh_token = AuthService(db).login(payload.email, payload.password)
    _set_refresh_cookie(response, raw_refresh_token)
    return result


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise InvalidTokenException("No refresh token provided")

    tokens, new_raw_token = AuthService(db).refresh(raw_token)
    _set_refresh_cookie(response, new_raw_token)
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token:
        AuthService(db).logout(raw_token)
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return None


@router.get("/me", response_model=AuthUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return AuthUserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role.name,
    )