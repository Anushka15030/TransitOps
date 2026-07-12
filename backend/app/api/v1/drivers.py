import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.core.permissions import Permission
from app.models.enums import DriverStatus
from app.schemas.common_schema import PaginatedResponse
from app.schemas.driver_schema import (
    DriverCreateRequest,
    DriverFilterParams,
    DriverResponse,
    DriverUpdateRequest,
)
from app.services.driver_service import DriverService

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post(
    "",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.DRIVER_WRITE))],
)
def create_driver(payload: DriverCreateRequest, db: Session = Depends(get_db)):
    return DriverService(db).create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[DriverResponse],
    dependencies=[Depends(require_permission(Permission.DRIVER_READ))],
)
def list_drivers(
    search: str | None = Query(default=None, max_length=100),
    status_filter: DriverStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = DriverFilterParams(search=search, status=status_filter)
    return DriverService(db).list_drivers(filters, page, page_size)


@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
    dependencies=[Depends(require_permission(Permission.DRIVER_READ))],
)
def get_driver(driver_id: uuid.UUID, db: Session = Depends(get_db)):
    return DriverService(db).get_by_id(driver_id)


@router.patch(
    "/{driver_id}",
    response_model=DriverResponse,
    dependencies=[Depends(require_permission(Permission.DRIVER_WRITE))],
)
def update_driver(driver_id: uuid.UUID, payload: DriverUpdateRequest, db: Session = Depends(get_db)):
    return DriverService(db).update(driver_id, payload)


@router.delete(
    "/{driver_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.DRIVER_WRITE))],
)
def delete_driver(driver_id: uuid.UUID, db: Session = Depends(get_db)):
    DriverService(db).delete(driver_id)
    return None