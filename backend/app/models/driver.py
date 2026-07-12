import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel
from app.models.enums import DriverStatus


class Driver(Base, BaseModel):
    """
    Operational profile for a user with role=DRIVER.
    Separated from `users` because license/status data changes for
    completely different reasons than auth data (SRP).
    """
    __tablename__ = "drivers"

    # unique=True enforces the 1:1 relationship at the DB level, not just in code.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    license_expiry: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[DriverStatus] = mapped_column(
        PG_ENUM(DriverStatus, name="driver_status_enum", create_type=False),
        default=DriverStatus.AVAILABLE,
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="driver_profile")
    trips: Mapped[list["Trip"]] = relationship(back_populates="driver")