"""
Owns every trip query, including the pessimistic locking primitives the
service needs for safe dispatch. Locking mechanics belong in the
repository (it's a data-access concern) — the service just calls
`lock_driver()` / `lock_vehicle()` without knowing it's a SELECT...FOR UPDATE.
"""

import uuid
from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.driver import Driver
from app.models.enums import TripStatus
from app.models.route import Route
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.repositories.base_repository import BaseRepository


class TripRepository(BaseRepository[Trip]):
    def __init__(self, db: Session):
        super().__init__(Trip, db)

    # ---------- Locking primitives ----------

    def lock_vehicle(self, vehicle_id: uuid.UUID) -> Vehicle | None:
        """
        SELECT ... FOR UPDATE on the vehicle row. Any other transaction
        trying to lock the SAME vehicle row (i.e. dispatching it into
        another trip) blocks here until this transaction commits or
        rolls back. This is what makes double-assignment structurally
        impossible, not just "unlikely."
        """
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.id == vehicle_id)
            .with_for_update()
            .first()
        )

    def lock_driver(self, driver_id: uuid.UUID) -> Driver | None:
        return (
            self.db.query(Driver)
            .filter(Driver.id == driver_id)
            .with_for_update()
            .first()
        )

    # ---------- Overlap detection ----------

    def has_overlapping_dispatched_trip_for_vehicle(
        self, vehicle_id: uuid.UUID, departure: datetime, arrival: datetime, exclude_trip_id: uuid.UUID
    ) -> bool:
        """
        Classic interval-overlap predicate: two ranges [a_start, a_end) and
        [b_start, b_end) overlap iff a_start < b_end AND b_start < a_end.
        Only checks DISPATCHED trips — a DRAFT or CANCELLED trip on the
        same vehicle is not a real conflict.
        """
        return (
            self.db.query(Trip.id)
            .filter(
                Trip.vehicle_id == vehicle_id,
                Trip.status == TripStatus.DISPATCHED,
                Trip.id != exclude_trip_id,
                Trip.departure_time < arrival,
                departure < Trip.arrival_time,
            )
            .first()
            is not None
        )

    def has_overlapping_dispatched_trip_for_driver(
        self, driver_id: uuid.UUID, departure: datetime, arrival: datetime, exclude_trip_id: uuid.UUID
    ) -> bool:
        return (
            self.db.query(Trip.id)
            .filter(
                Trip.driver_id == driver_id,
                Trip.status == TripStatus.DISPATCHED,
                Trip.id != exclude_trip_id,
                Trip.departure_time < arrival,
                departure < Trip.arrival_time,
            )
            .first()
            is not None
        )

    # ---------- Reads ----------

    def get_by_id_with_relations(self, trip_id: uuid.UUID) -> Trip | None:
        return (
            self.db.query(Trip)
            .options(
                joinedload(Trip.route),
                joinedload(Trip.vehicle),
                joinedload(Trip.driver).joinedload(Driver.user),
            )
            .filter(Trip.id == trip_id)
            .first()
        )

    def search_and_filter(
        self,
        status: TripStatus | None,
        route_id: uuid.UUID | None,
        vehicle_id: uuid.UUID | None,
        driver_id: uuid.UUID | None,
        departure_from: datetime | None,
        departure_to: datetime | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Trip], int]:
        query = self.db.query(Trip).options(
            joinedload(Trip.route),
            joinedload(Trip.vehicle),
            joinedload(Trip.driver).joinedload(Driver.user),
        )

        if status:
            query = query.filter(Trip.status == status)
        if route_id:
            query = query.filter(Trip.route_id == route_id)
        if vehicle_id:
            query = query.filter(Trip.vehicle_id == vehicle_id)
        if driver_id:
            query = query.filter(Trip.driver_id == driver_id)
        if departure_from:
            query = query.filter(Trip.departure_time >= departure_from)
        if departure_to:
            query = query.filter(Trip.departure_time <= departure_to)

        total = query.with_entities(func.count(Trip.id)).scalar() or 0
        items = query.order_by(Trip.departure_time.desc()).offset(offset).limit(limit).all()
        return items, total

    def has_active_bookings(self, trip_id: uuid.UUID) -> bool:
        from app.models.booking import Booking
        from app.models.enums import BookingStatus

        return (
            self.db.query(Booking.id)
            .filter(Booking.trip_id == trip_id, Booking.status != BookingStatus.CANCELLED)
            .first()
            is not None
        )