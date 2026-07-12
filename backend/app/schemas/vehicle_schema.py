import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import VehicleStatus, VehicleType
from app.schemas.base_schema import BaseSchema

CURRENT_YEAR_CEILING = 2027  # next model year, avoids importing datetime.now() into validators


class VehicleCreateRequest(BaseModel):
    registration_number: str = Field(min_length=3, max_length=20)
    vehicle_type: VehicleType
    manufacturer: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1990, le=CURRENT_YEAR_CEILING)
    capacity: int = Field(gt=0, le=200)

    @field_validator("registration_number")
    @classmethod
    def normalize_registration(cls, v: str) -> str:
        # Normalize at the API boundary so "mh12ab1234" and "MH12AB1234"
        # can never both exist as distinct rows.
        return v.strip().upper()


class VehicleUpdateRequest(BaseModel):
    """
    All fields optional: this is a PATCH-style partial update.
    `status` is intentionally included here (not a separate endpoint) since
    changing status is a simple field update, unlike Trip status which has
    a real state machine and gets its own service method later.
    """
    manufacturer: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1990, le=CURRENT_YEAR_CEILING)
    capacity: int | None = Field(default=None, gt=0, le=200)
    status: VehicleStatus | None = None


class VehicleResponse(BaseSchema):
    id: uuid.UUID
    registration_number: str
    vehicle_type: VehicleType
    manufacturer: str
    model: str
    year: int
    capacity: int
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime


class VehicleFilterParams(BaseModel):
    """Query-param bundle for GET /vehicles — kept as one schema so the
    route signature stays clean and FastAPI validates types automatically."""
    search: str | None = None                # matches registration_number, manufacturer, model
    vehicle_type: VehicleType | None = None
    status: VehicleStatus | None = None