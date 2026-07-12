import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel


class RouteStop(Base, BaseModel):
    """
    Ordered stop belonging to a route. `sequence_order` defines the
    physical order stops occur along the route (1, 2, 3...).
    """
    __tablename__ = "route_stops"
    __table_args__ = (
        # A route can't have two stops at the same position in the sequence.
        UniqueConstraint("route_id", "sequence_order", name="uq_route_stop_sequence"),
    )

    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stop_name: Mapped[str] = mapped_column(String(150), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    arrival_offset_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )  # minutes from trip departure to reach this stop

    route: Mapped["Route"] = relationship(back_populates="stops")