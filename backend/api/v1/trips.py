import uuid

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.core.permissions import Permission
from app.models.enums import TripStatus
from app.schemas.common_schema import PaginatedResponse
from app.schemas.trip_schema import (
    TripCreateRequest,
    TripFilterParams,
    TripResponse,
    TripStatusChangeResponse,
    TripUpdateRequest,
)
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.TRIP_WRITE))],
)
def create_trip(payload: TripCreateRequest, db: Session = Depends(get_db)):
    return TripService(db).create_draft(payload)


@router.get(
    "",
    response_model=PaginatedResponse[TripResponse],
    dependencies=[Depends(require_permission(Permission.TRIP_READ))],
)
def list_trips(
    status_filter: TripStatus | None = Query(default=None, alias="status"),
    route_id: uuid.UUID | None = Query(default=None),
    vehicle_id: uuid.UUID | None = Query(default=None),
    driver_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = TripFilterParams(status=status_filter, route_id=route_id, vehicle_id=vehicle_id, driver_id=driver_id)
    return TripService(db).list_trips(filters, page, page_size)


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    dependencies=[Depends(require_permission(Permission.TRIP_READ))],
)
def get_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return TripService(db).get_by_id(trip_id)


@router.patch(
    "/{trip_id}",
    response_model=TripResponse,
    dependencies=[Depends(require_permission(Permission.TRIP_WRITE))],
)
def update_trip(trip_id: uuid.UUID, payload: TripUpdateRequest, db: Session = Depends(get_db)):
    return TripService(db).update_draft(trip_id, payload)


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.TRIP_WRITE))],
)
def delete_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    TripService(db).delete_draft(trip_id)
    return None


# ---------- State transitions: distinct endpoints, not a generic PATCH ----------
# Each is a verb-shaped action with its own permission and its own set of
# validations — collapsing these into "PATCH status" would hide the very
# different business rules (and locking) each transition requires.

@router.post(
    "/{trip_id}/dispatch",
    response_model=TripStatusChangeResponse,
    dependencies=[Depends(require_permission(Permission.TRIP_ASSIGN))],
)
def dispatch_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return TripService(db).dispatch(trip_id)


@router.post(
    "/{trip_id}/complete",
    response_model=TripStatusChangeResponse,
    dependencies=[Depends(require_permission(Permission.TRIP_UPDATE_STATUS))],
)
def complete_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return TripService(db).complete(trip_id)


@router.post(
    "/{trip_id}/cancel",
    response_model=TripStatusChangeResponse,
    dependencies=[Depends(require_permission(Permission.TRIP_WRITE))],
)
def cancel_trip(trip_id: uuid.UUID, reason: str | None = Body(default=None, embed=True), db: Session = Depends(get_db)):
    return TripService(db).cancel(trip_id, reason)