import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel
from app.models.enums import MaintenanceStatus


class MaintenanceRecord(Base, BaseModel):
    """
    An open maintenance record is what DRIVES a vehicle's status to
    MAINTENANCE — the vehicle's `status` field is a derived/synced value,
    not independently editable while maintenance is open (enforced in
    VehicleService going forward: block direct status edits to a vehicle
    with an open maintenance record).
    """
    __tablename__ = "maintenance_records"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    reported_issue: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MaintenanceStatus] = mapped_column(
        PG_ENUM(MaintenanceStatus, name="maintenance_status_enum", create_type=False),
        default=MaintenanceStatus.OPEN,
        nullable=False,
        index=True,
    )
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    vehicle: Mapped["Vehicle"] = relationship()