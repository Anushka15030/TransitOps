"""
Thin controller. Every route: parse input -> call service -> return.
Permission checks are declared per-route via `require_permission`, not
written as inline `if` checks — this is the RBAC system from Module 2
now doing real work.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.core.permissions import Permission
from app.models.enums import VehicleStatus, VehicleType
from app.schemas.common_schema import PaginatedResponse
from app.schemas.vehicle_schema import (
    VehicleCreateRequest,
    VehicleFilterParams,
    VehicleResponse,
    VehicleUpdateRequest,
)
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.VEHICLE_WRITE))],
)
def create_vehicle(payload: VehicleCreateRequest, db: Session = Depends(get_db)):
    return VehicleService(db).create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[VehicleResponse],
    dependencies=[Depends(require_permission(Permission.VEHICLE_READ))],
)
def list_vehicles(
    search: str | None = Query(default=None, max_length=100),
    vehicle_type: VehicleType | None = Query(default=None),
    status_filter: VehicleStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = VehicleFilterParams(search=search, vehicle_type=vehicle_type, status=status_filter)
    return VehicleService(db).list_vehicles(filters, page, page_size)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    dependencies=[Depends(require_permission(Permission.VEHICLE_READ))],
)
def get_vehicle(vehicle_id: uuid.UUID, db: Session = Depends(get_db)):
    return VehicleService(db).get_by_id(vehicle_id)


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    dependencies=[Depends(require_permission(Permission.VEHICLE_WRITE))],
)
def update_vehicle(vehicle_id: uuid.UUID, payload: VehicleUpdateRequest, db: Session = Depends(get_db)):
    return VehicleService(db).update(vehicle_id, payload)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.VEHICLE_WRITE))],
)
def delete_vehicle(vehicle_id: uuid.UUID, db: Session = Depends(get_db)):
    VehicleService(db).delete(vehicle_id)
    return None