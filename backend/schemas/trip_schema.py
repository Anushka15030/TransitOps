import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import TripStatus
from app.schemas.base_schema import BaseSchema


class TripCreateRequest(BaseModel):
    """
    Creating a trip = DRAFT state. Vehicle and driver are assigned here,
    but nothing is locked/committed as "in service" until dispatch —
    a draft can be edited or discarded freely with zero operational impact.
    """
    route_id: uuid.UUID
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    departure_time: datetime
    arrival_time: datetime
    available_seats: int = Field(gt=0)
    fare: float = Field(ge=0)

    @model_validator(mode="after")
    def arrival_after_departure(self) -> "TripCreateRequest":
        if self.arrival_time <= self.departure_time:
            raise ValueError("Arrival time must be after departure time")
        return self


class TripUpdateRequest(BaseModel):
    """
    Only allowed while a trip is still DRAFT — enforced in the service,
    not here, because "is this trip editable" is a state-dependent
    business rule, not a shape-validation rule.
    """
    route_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    departure_time: datetime | None = None
    arrival_time: datetime | None = None
    available_seats: int | None = Field(default=None, gt=0)
    fare: float | None = Field(default=None, ge=0)


class TripResponse(BaseSchema):
    id: uuid.UUID
    route_id: uuid.UUID
    route_name: str
    vehicle_id: uuid.UUID
    vehicle_registration: str
    driver_id: uuid.UUID
    driver_name: str
    departure_time: datetime
    arrival_time: datetime
    available_seats: int
    fare: float
    status: TripStatus
    created_at: datetime
    updated_at: datetime


class TripFilterParams(BaseModel):
    status: TripStatus | None = None
    route_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    departure_from: datetime | None = None
    departure_to: datetime | None = None


class TripStatusChangeResponse(BaseSchema):
    """Lightweight response for dispatch/complete/cancel actions."""
    id: uuid.UUID
    status: TripStatus
    updated_at: datetime