import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel


class User(Base, BaseModel):
    """
    Central identity table. Every actor in the system (admin, dispatcher,
    driver, customer) is a row here — drivers get an additional `Driver`
    profile row linked 1:1.
    """
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    # Unique + indexed: primary login lookup path, must be fast and unique.
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users")
    driver_profile: Mapped["Driver | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")