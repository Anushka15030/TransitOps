"""
Driver creation bundles user-account fields (for login) with driver-profile
fields (license). Kept as one request schema since the frontend "Add Driver"
form is one form, not two — the split into User + Driver happens inside
the service, not exposed to the API consumer.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import DriverStatus
from app.schemas.base_schema import BaseSchema


class DriverCreateRequest(BaseModel):
    # User-account fields
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    # Driver-profile fields
    license_number: str = Field(min_length=3, max_length=50)
    license_expiry: date

    @field_validator("license_number")
    @classmethod
    def normalize_license(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("license_expiry")
    @classmethod
    def expiry_must_be_future(cls, v: date) -> date:
        if v <= date.today():
            raise ValueError("License expiry date must be in the future")
        return v


class DriverUpdateRequest(BaseModel):
    """
    Partial update — deliberately does NOT allow updating email/phone here.
    Identity fields go through a dedicated account-management flow (out of
    scope for this module); this endpoint only touches operational fields
    a dispatcher legitimately manages day-to-day.
    """
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    license_number: str | None = Field(default=None, min_length=3, max_length=50)
    license_expiry: date | None = None
    status: DriverStatus | None = None

    @field_validator("license_expiry")
    @classmethod
    def expiry_must_be_future(cls, v: date | None) -> date | None:
        if v is not None and v <= date.today():
            raise ValueError("License expiry date must be in the future")
        return v


class DriverResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: EmailStr
    phone: str
    license_number: str
    license_expiry: date
    status: DriverStatus
    created_at: datetime
    updated_at: datetime


class DriverFilterParams(BaseModel):
    search: str | None = None   # matches full_name, email, license_number
    status: DriverStatus | None = None