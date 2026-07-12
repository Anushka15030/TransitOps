import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import MaintenanceStatus
from app.schemas.base_schema import BaseSchema


class MaintenanceOpenRequest(BaseModel):
    vehicle_id: uuid.UUID
    reported_issue: str = Field(min_length=5, max_length=2000)
    estimated_cost: float | None = Field(default=None, ge=0)


class MaintenanceCloseRequest(BaseModel):
    resolution_notes: str = Field(min_length=5, max_length=2000)
    actual_cost: float | None = Field(default=None, ge=0)


class MaintenanceResponse(BaseSchema):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    vehicle_registration: str
    reported_issue: str
    status: MaintenanceStatus
    opened_at: datetime
    closed_at: datetime | None
    resolution_notes: str | None
    estimated_cost: float | None
    created_at: datetime


class MaintenanceFilterParams(BaseModel):
    status: MaintenanceStatus | None = None
    vehicle_id: uuid.UUID | None = None