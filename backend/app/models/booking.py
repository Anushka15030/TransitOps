import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel
from app.models.enums import BookingStatus


class Booking(Base, BaseModel):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("seat_number > 0", name="ck_bookings_seat_positive"),
        CheckConstraint("amount >= 0", name="ck_bookings_amount_non_negative"),
        # A seat can only be actively held once per trip. Cancelled bookings
        # free the seat back up for re-booking (enforced via partial index
        # in the migration, since UniqueConstraint alone can't add a WHERE clause).
        UniqueConstraint("trip_id", "seat_number", "booking_reference", name="uq_booking_trip_seat_ref"),
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_reference: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        PG_ENUM(BookingStatus, name="booking_status_enum", create_type=False),
        default=BookingStatus.PENDING,
        nullable=False,
        index=True,
    )

    trip: Mapped["Trip"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship(back_populates="bookings")