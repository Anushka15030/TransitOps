import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel
from app.models.enums import TripStatus


class Trip(Base, BaseModel):
    """
    A single scheduled instance of a route, on a specific vehicle,
    with a specific driver, at a specific time.
    """
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("arrival_time > departure_time", name="ck_trips_arrival_after_departure"),
        CheckConstraint("available_seats >= 0", name="ck_trips_seats_non_negative"),
        CheckConstraint("fare >= 0", name="ck_trips_fare_non_negative"),
    )

    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    fare: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[TripStatus] = mapped_column(
        PG_ENUM(TripStatus, name="trip_status_enum", create_type=False),
        default=TripStatus.SCHEDULED,
        nullable=False,
        index=True,
    )

    # Relationships
    route: Mapped["Route"] = relationship(back_populates="trips")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="trips")
    driver: Mapped["Driver"] = relationship(back_populates="trips")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="trip")

    # app/models/trip.py — change the default
    status: Mapped[TripStatus] = mapped_column(
    PG_ENUM(TripStatus, name="trip_status_enum", create_type=False),
    default=TripStatus.DRAFT,
    nullable=False,
    index=True,
)

 