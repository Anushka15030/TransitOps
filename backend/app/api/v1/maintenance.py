import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.core.permissions import Permission
from app.models.enums import MaintenanceStatus
from app.schemas.common_schema import PaginatedResponse
from app.schemas.maintenance_schema import (
    MaintenanceCloseRequest,
    MaintenanceFilterParams,
    MaintenanceOpenRequest,
    MaintenanceResponse,
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.VEHICLE_WRITE))],
)
def open_maintenance(payload: MaintenanceOpenRequest, db: Session = Depends(get_db)):
    return MaintenanceService(db).open_maintenance(payload)


@router.post(
    "/{record_id}/close",
    response_model=MaintenanceResponse,
    dependencies=[Depends(require_permission(Permission.VEHICLE_WRITE))],
)
def close_maintenance(record_id: uuid.UUID, payload: MaintenanceCloseRequest, db: Session = Depends(get_db)):
    return MaintenanceService(db).close_maintenance(record_id, payload)


@router.get(
    "",
    response_model=PaginatedResponse[MaintenanceResponse],
    dependencies=[Depends(require_permission(Permission.VEHICLE_READ))],
)
def list_maintenance(
    status_filter: MaintenanceStatus | None = Query(default=None, alias="status"),
    vehicle_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = MaintenanceFilterParams(status=status_filter, vehicle_id=vehicle_id)
    return MaintenanceService(db).list_records(filters, page, page_size)


@router.get(
    "/{record_id}",
    response_model=MaintenanceResponse,
    dependencies=[Depends(require_permission(Permission.VEHICLE_READ))],
)
def get_maintenance(record_id: uuid.UUID, db: Session = Depends(get_db)):
    return MaintenanceService(db).get_by_id(record_id)