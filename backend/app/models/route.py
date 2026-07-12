from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel
from app.models.enums import RouteStatus


class Route(Base, BaseModel):
    __tablename__ = "routes"
    __table_args__ = (
        CheckConstraint("distance_km > 0", name="ck_routes_distance_positive"),
        CheckConstraint("estimated_duration_minutes > 0", name="ck_routes_duration_positive"),
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    origin: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    distance_km: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[RouteStatus] = mapped_column(
        PG_ENUM(RouteStatus, name="route_status_enum", create_type=False),
        default=RouteStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    stops: Mapped[list["RouteStop"]] = relationship(
        back_populates="route", cascade="all, delete-orphan", order_by="RouteStop.sequence_order"
    )
    trips: Mapped[list["Trip"]] = relationship(back_populates="route")