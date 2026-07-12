"""
Owns the vehicle-status sync rule: opening maintenance forces the vehicle
into MAINTENANCE; closing it restores ACTIVE. Both are one transaction —
a maintenance record can never exist "open" while its vehicle shows any
status other than MAINTENANCE, and vice versa for closed.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, DuplicateResourceException, ResourceNotFoundException
from app.models.enums import TripStatus, VehicleStatus
from app.models.maintenance_record import MaintenanceRecord
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.common_schema import PaginatedResponse
from app.schemas.maintenance_schema import (
    MaintenanceCloseRequest,
    MaintenanceFilterParams,
    MaintenanceOpenRequest,
    MaintenanceResponse,
)


class VehicleAlreadyInMaintenanceException(DuplicateResourceException):
    status_code = 409
    detail = "This vehicle already has an open maintenance record"


class VehicleOnActiveTripException(AppException):
    status_code = 409
    detail = "Cannot open maintenance while the vehicle is on a dispatched trip"


class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaintenanceRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.trip_repo = TripRepository(db)

    def open_maintenance(self, payload: MaintenanceOpenRequest) -> MaintenanceResponse:
        # Lock the vehicle row — prevents a concurrent dispatch() call and
        # this open_maintenance() call from racing each other (same
        # pattern as Module 5's dispatch locking).
        vehicle = self.trip_repo.lock_vehicle(payload.vehicle_id)
        if vehicle is None:
            raise ResourceNotFoundException("Vehicle not found")

        if self.repo.get_open_for_vehicle(payload.vehicle_id):
            raise VehicleAlreadyInMaintenanceException()

        # Block opening maintenance on a vehicle mid-trip — operationally,
        # you can't pull a bus into the shop while it's out on a route.
        active_trip_exists = (
            self.db.query(TripRepository(self.db).model)
            .filter_by(vehicle_id=payload.vehicle_id, status=TripStatus.DISPATCHED)
            .first()
            is not None
        )
        if active_trip_exists:
            raise VehicleOnActiveTripException()

        record = MaintenanceRecord(
            vehicle_id=payload.vehicle_id,
            reported_issue=payload.reported_issue,
            estimated_cost=payload.estimated_cost,
            opened_at=datetime.now(timezone.utc),
            status="open",
        )
        self.repo.create(record)

        # The auto-transition: opening maintenance drives vehicle status.
        vehicle.status = VehicleStatus.MAINTENANCE

        self.db.commit()
        self.db.refresh(record)
        return self._to_response(self.repo.get_by_id_with_vehicle(record.id))

    def close_maintenance(self, record_id: uuid.UUID, payload: MaintenanceCloseRequest) -> MaintenanceResponse:
        record = self.repo.get_by_id_with_vehicle(record_id)
        if record is None:
            raise ResourceNotFoundException("Maintenance record not found")
        if record.status != "open":
            raise AppException("This maintenance record is already closed")

        vehicle = self.trip_repo.lock_vehicle(record.vehicle_id)

        record.status = "closed"
        record.closed_at = datetime.now(timezone.utc)
        record.resolution_notes = payload.resolution_notes
        if payload.actual_cost is not None:
            record.estimated_cost = payload.actual_cost

        # The auto-transition back: closing maintenance restores the
        # vehicle to service. If OTHER open maintenance records somehow
        # exist for this vehicle (shouldn't, given the partial unique
        # index), we conservatively leave it in MAINTENANCE rather than
        # risk releasing a vehicle that still has unresolved issues.
        if vehicle is not None and self.repo.get_open_for_vehicle(vehicle.id) is None:
            vehicle.status = VehicleStatus.ACTIVE

        self.db.commit()
        self.db.refresh(record)
        return self._to_response(self.repo.get_by_id_with_vehicle(record.id))

    def get_by_id(self, record_id: uuid.UUID) -> MaintenanceResponse:
        record = self.repo.get_by_id_with_vehicle(record_id)
        if record is None:
            raise ResourceNotFoundException("Maintenance record not found")
        return self._to_response(record)

    def list_records(self, filters: MaintenanceFilterParams, page: int, page_size: int) -> PaginatedResponse[MaintenanceResponse]:
        offset = (page - 1) * page_size
        items, total = self.repo.search_and_filter(filters.status, filters.vehicle_id, offset, page_size)
        return PaginatedResponse.build(
            items=[self._to_response(r) for r in items], total=total, page=page, page_size=page_size
        )

    @staticmethod
    def _to_response(record: MaintenanceRecord) -> MaintenanceResponse:
        return MaintenanceResponse(
            id=record.id,
            vehicle_id=record.vehicle_id,
            vehicle_registration=record.vehicle.registration_number,
            reported_issue=record.reported_issue,
            status=record.status,
            opened_at=record.opened_at,
            closed_at=record.closed_at,
            resolution_notes=record.resolution_notes,
            estimated_cost=float(record.estimated_cost) if record.estimated_cost is not None else None,
            created_at=record.created_at,
        )