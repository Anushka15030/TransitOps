from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.enums import MaintenanceStatus
from app.models.maintenance_record import MaintenanceRecord
from app.repositories.base_repository import BaseRepository


class MaintenanceRepository(BaseRepository[MaintenanceRecord]):
    def __init__(self, db: Session):
        super().__init__(MaintenanceRecord, db)

    def get_open_for_vehicle(self, vehicle_id) -> MaintenanceRecord | None:
        return (
            self.db.query(MaintenanceRecord)
            .filter(MaintenanceRecord.vehicle_id == vehicle_id, MaintenanceRecord.status == MaintenanceStatus.OPEN)
            .first()
        )

    def get_by_id_with_vehicle(self, record_id) -> MaintenanceRecord | None:
        return (
            self.db.query(MaintenanceRecord)
            .options(joinedload(MaintenanceRecord.vehicle))
            .filter(MaintenanceRecord.id == record_id)
            .first()
        )

    def search_and_filter(self, status: MaintenanceStatus | None, vehicle_id, offset: int, limit: int):
        query = self.db.query(MaintenanceRecord).options(joinedload(MaintenanceRecord.vehicle))
        if status:
            query = query.filter(MaintenanceRecord.status == status)
        if vehicle_id:
            query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)

        total = query.with_entities(func.count(MaintenanceRecord.id)).scalar() or 0
        items = query.order_by(MaintenanceRecord.opened_at.desc()).offset(offset).limit(limit).all()
        return items, total