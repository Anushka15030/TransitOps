from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base_schema import BaseSchema


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """
        Enforced server-side, never trust client-side validation alone —
        the API is the real security boundary.
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds, so the frontend knows when to proactively refresh


class AuthUserResponse(BaseSchema):
    id: str
    full_name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    user: AuthUserResponse
    tokens: TokenResponse