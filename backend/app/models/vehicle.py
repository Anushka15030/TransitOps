from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel
from app.models.enums import VehicleStatus, VehicleType


class Vehicle(Base, BaseModel):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_vehicles_capacity_positive"),
        CheckConstraint("year >= 1990", name="ck_vehicles_year_valid"),
    )

    registration_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        PG_ENUM(VehicleType, name="vehicle_type_enum", create_type=False), nullable=False
    )
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[VehicleStatus] = mapped_column(
        PG_ENUM(VehicleStatus, name="vehicle_status_enum", create_type=False),
        default=VehicleStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    trips: Mapped[list["Trip"]] = relationship(back_populates="vehicle")