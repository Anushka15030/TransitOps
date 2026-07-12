"""
All vehicle queries live here — search, filter, and pagination logic.
The service layer calls these methods with plain arguments; it never
constructs a SQLAlchemy query itself.
"""

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.enums import VehicleStatus, VehicleType
from app.models.vehicle import Vehicle
from app.repositories.base_repository import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    def __init__(self, db: Session):
        super().__init__(Vehicle, db)

    def get_by_registration_number(self, registration_number: str) -> Vehicle | None:
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.registration_number == registration_number)
            .first()
        )

    def search_and_filter(
        self,
        search: str | None,
        vehicle_type: VehicleType | None,
        status: VehicleStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Vehicle], int]:
        """
        Returns (page_of_results, total_matching_count). The count query
        uses the SAME filter predicate as the page query, so pagination
        totals are always consistent with what's actually returned.
        """
        query = self.db.query(Vehicle)

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Vehicle.registration_number.ilike(pattern),
                    Vehicle.manufacturer.ilike(pattern),
                    Vehicle.model.ilike(pattern),
                )
            )

        if vehicle_type:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)

        if status:
            query = query.filter(Vehicle.status == status)

        total = query.with_entities(func.count(Vehicle.id)).scalar() or 0

        items = (
            query.order_by(Vehicle.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def has_active_trips(self, vehicle_id) -> bool:
        """
        Used by the service to block deletion of a vehicle that's referenced
        by trip history — the DB FK is RESTRICT so this would fail anyway,
        but checking here lets us return a clean 409 with a helpful message
        instead of a raw IntegrityError bubbling up.
        """
        from app.models.trip import Trip  # local import avoids circular import at module load

        return (
            self.db.query(Trip.id)
            .filter(Trip.vehicle_id == vehicle_id)
            .first()
            is not None
        )