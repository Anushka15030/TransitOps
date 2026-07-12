from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.driver import Driver
from app.models.enums import DriverStatus
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    def __init__(self, db: Session):
        super().__init__(Driver, db)

    def get_by_id_with_user(self, driver_id) -> Driver | None:
        return (
            self.db.query(Driver)
            .options(joinedload(Driver.user))
            .filter(Driver.id == driver_id)
            .first()
        )

    def get_by_license_number(self, license_number: str) -> Driver | None:
        return self.db.query(Driver).filter(Driver.license_number == license_number).first()

    def get_by_user_id(self, user_id) -> Driver | None:
        return self.db.query(Driver).filter(Driver.user_id == user_id).first()

    def search_and_filter(
        self,
        search: str | None,
        status: DriverStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Driver], int]:
        """
        Joins User because search spans both tables (name/email live on
        User, license lives on Driver). joinedload eager-loads User so the
        service doesn't trigger N+1 queries when flattening the DTO.
        """
        query = self.db.query(Driver).join(User, Driver.user_id == User.id).options(joinedload(Driver.user))

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(pattern),
                    User.email.ilike(pattern),
                    Driver.license_number.ilike(pattern),
                )
            )

        if status:
            query = query.filter(Driver.status == status)

        total = query.with_entities(func.count(Driver.id)).scalar() or 0

        items = (
            query.order_by(Driver.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def has_active_trips(self, driver_id) -> bool:
        from app.models.trip import Trip

        return self.db.query(Trip.id).filter(Trip.driver_id == driver_id).first() is not None