"""
The trip lifecycle state machine and every safety check around dispatch.

TRANSACTION BOUNDARY: every method here that mutates state (create, dispatch,
complete, cancel) performs its full read-check-write sequence against the
SAME SQLAlchemy session, and commits exactly once at the end. If ANY
validation raises partway through, the session is never committed and
FastAPI's request teardown (`db.close()` in get_db) discards the
uncommitted transaction — Postgres rolls it back automatically. There is
no scenario where a partially-applied dispatch can persist.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ResourceNotFoundException
from app.models.enums import DriverStatus, TripStatus, VehicleStatus
from app.models.trip import Trip
from app.repositories.driver_repository import DriverRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.common_schema import PaginatedResponse
from app.schemas.trip_schema import (
    TripCreateRequest,
    TripFilterParams,
    TripResponse,
    TripStatusChangeResponse,
    TripUpdateRequest,
)


class InvalidTripTransitionException(AppException):
    status_code = 409
    detail = "This status change is not allowed from the trip's current state"


class DriverUnavailableException(AppException):
    status_code = 409
    detail = "Driver is not available for this trip"


class VehicleUnavailableException(AppException):
    status_code = 409
    detail = "Vehicle is not available for this trip"


class ScheduleConflictException(AppException):
    status_code = 409
    detail = "This assignment overlaps with another dispatched trip"


class CapacityExceededException(AppException):
    status_code = 422
    detail = "Requested seat capacity exceeds vehicle capacity"


# Explicit transition table. This is the single source of truth for what
# moves are legal — no state logic is scattered across route handlers.
ALLOWED_TRANSITIONS: dict[TripStatus, set[TripStatus]] = {
    TripStatus.DRAFT: {TripStatus.DISPATCHED, TripStatus.CANCELLED},
    TripStatus.DISPATCHED: {TripStatus.COMPLETED, TripStatus.CANCELLED},
    TripStatus.COMPLETED: set(),   # terminal
    TripStatus.CANCELLED: set(),   # terminal
}


class TripService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TripRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.driver_repo = DriverRepository(db)
        self.route_repo = RouteRepository(db)

    # ---------- Create (Draft) ----------

    def create_draft(self, payload: TripCreateRequest) -> TripResponse:
        route = self.route_repo.get_by_id(payload.route_id)
        if route is None:
            raise ResourceNotFoundException("Route not found")

        vehicle = self.vehicle_repo.get_by_id(payload.vehicle_id)
        if vehicle is None:
            raise ResourceNotFoundException("Vehicle not found")

        driver = self.driver_repo.get_by_id(payload.driver_id)
        if driver is None:
            raise ResourceNotFoundException("Driver not found")

        self._validate_capacity(payload.available_seats, vehicle.capacity)

        trip = Trip(
            route_id=payload.route_id,
            vehicle_id=payload.vehicle_id,
            driver_id=payload.driver_id,
            departure_time=payload.departure_time,
            arrival_time=payload.arrival_time,
            available_seats=payload.available_seats,
            fare=payload.fare,
            status=TripStatus.DRAFT,
        )
        self.repo.create(trip)
        self.db.commit()
        return self._to_response(self.repo.get_by_id_with_relations(trip.id))

    # ---------- Update (Draft only) ----------

    def update_draft(self, trip_id: uuid.UUID, payload: TripUpdateRequest) -> TripResponse:
        trip = self.repo.get_by_id(trip_id)
        if trip is None:
            raise ResourceNotFoundException("Trip not found")
        if trip.status != TripStatus.DRAFT:
            raise InvalidTripTransitionException("Only draft trips can be edited")

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(trip, field, value)

        if trip.arrival_time <= trip.departure_time:
            raise AppException("Arrival time must be after departure time")

        vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
        self._validate_capacity(trip.available_seats, vehicle.capacity)

        self.db.commit()
        self.db.refresh(trip)
        return self._to_response(self.repo.get_by_id_with_relations(trip.id))

    # ---------- Dispatch: the critical path ----------

    def dispatch(self, trip_id: uuid.UUID) -> TripStatusChangeResponse:
        """
        The core operation. Order of operations matters:
          1. Load the trip (no lock needed yet — its status hasn't changed).
          2. Validate the transition is legal (DRAFT -> DISPATCHED).
          3. Lock driver row, THEN vehicle row (always same order across the
             codebase to prevent deadlocks between concurrent dispatches
             that reference the same pair in reverse order).
          4. Re-validate driver/vehicle business state under the lock — a
             value read before locking could be stale by the time we hold
             the lock, so we read status fields fresh from the locked rows.
          5. Check for schedule overlap against other DISPATCHED trips.
          6. Mutate + commit — single atomic unit.
        """
        trip = self.repo.get_by_id(trip_id)
        if trip is None:
            raise ResourceNotFoundException("Trip not found")

        self._assert_transition_allowed(trip.status, TripStatus.DISPATCHED)

        # --- Acquire locks in a fixed global order: driver, then vehicle ---
        driver = self.repo.lock_driver(trip.driver_id)
        vehicle = self.repo.lock_vehicle(trip.vehicle_id)

        if driver is None or vehicle is None:
            raise ResourceNotFoundException("Assigned driver or vehicle no longer exists")

        # --- Driver validations (fresh, under lock) ---
        if driver.status != DriverStatus.AVAILABLE:
            raise DriverUnavailableException(
                f"Driver is currently '{driver.status.value}' and cannot be dispatched"
            )
        if driver.license_expiry <= date.today():
            raise DriverUnavailableException("Driver's license has expired")
        if driver.license_expiry <= trip.arrival_time.date():
            raise DriverUnavailableException(
                "Driver's license expires before this trip's arrival date"
            )

        # --- Vehicle validations (fresh, under lock) ---
        if vehicle.status != VehicleStatus.ACTIVE:
            raise VehicleUnavailableException(
                f"Vehicle is currently '{vehicle.status.value}' and cannot be dispatched"
            )

        # --- Cargo / seat capacity re-check (defense in depth) ---
        self._validate_capacity(trip.available_seats, vehicle.capacity)

        # --- Schedule overlap check — safe now because both rows are locked,
        #     so no concurrent transaction can insert a conflicting
        #     DISPATCHED trip for this driver/vehicle until we commit ---
        if self.repo.has_overlapping_dispatched_trip_for_vehicle(
            vehicle.id, trip.departure_time, trip.arrival_time, exclude_trip_id=trip.id
        ):
            raise ScheduleConflictException("Vehicle is already assigned to an overlapping trip")

        if self.repo.has_overlapping_dispatched_trip_for_driver(
            driver.id, trip.departure_time, trip.arrival_time, exclude_trip_id=trip.id
        ):
            raise ScheduleConflictException("Driver is already assigned to an overlapping trip")

        # --- All checks passed: mutate and commit atomically ---
        trip.status = TripStatus.DISPATCHED
        driver.status = DriverStatus.ON_TRIP

        self.db.commit()
        self.db.refresh(trip)

        return TripStatusChangeResponse(id=trip.id, status=trip.status, updated_at=trip.updated_at)

    # ---------- Complete ----------

    def complete(self, trip_id: uuid.UUID) -> TripStatusChangeResponse:
        trip = self.repo.get_by_id(trip_id)
        if trip is None:
            raise ResourceNotFoundException("Trip not found")

        self._assert_transition_allowed(trip.status, TripStatus.COMPLETED)

        driver = self.repo.lock_driver(trip.driver_id)

        trip.status = TripStatus.COMPLETED
        if driver is not None and driver.status == DriverStatus.ON_TRIP:
            driver.status = DriverStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(trip)
        return TripStatusChangeResponse(id=trip.id, status=trip.status, updated_at=trip.updated_at)

    # ---------- Cancel ----------

    def cancel(self, trip_id: uuid.UUID, reason: str | None = None) -> TripStatusChangeResponse:
        trip = self.repo.get_by_id(trip_id)
        if trip is None:
            raise ResourceNotFoundException("Trip not found")

        self._assert_transition_allowed(trip.status, TripStatus.CANCELLED)

        was_dispatched = trip.status == TripStatus.DISPATCHED
        driver = self.repo.lock_driver(trip.driver_id) if was_dispatched else None

        trip.status = TripStatus.CANCELLED
        if was_dispatched and driver is not None and driver.status == DriverStatus.ON_TRIP:
            driver.status = DriverStatus.AVAILABLE

        # Note: cancelling a dispatched trip with existing confirmed bookings
        # is a cross-module concern — the Bookings module (when built) should
        # subscribe to this transition and cancel/refund affected bookings.
        # Flagged here rather than silently ignored.

        self.db.commit()
        self.db.refresh(trip)
        return TripStatusChangeResponse(id=trip.id, status=trip.status, updated_at=trip.updated_at)

    # ---------- Read ----------

    def get_by_id(self, trip_id: uuid.UUID) -> TripResponse:
        trip = self.repo.get_by_id_with_relations(trip_id)
        if trip is None:
            raise ResourceNotFoundException("Trip not found")
        return self._to_response(trip)

    def list_trips(self, filters: TripFilterParams, page: int, page_size: int) -> PaginatedResponse[TripResponse]:
        offset = (page - 1) * page_size
        items, total = self.repo.search_and_filter(
            status=filters.status,
            route_id=filters.route_id,
            vehicle_id=filters.vehicle_id,
            driver_id=filters.driver_id,
            departure_from=filters.departure_from,
            departure_to=filters.departure_to,
            offset=offset,
            limit=page_size,
        )
        return PaginatedResponse.build(
            items=[self._to_response(t) for t in items], total=total, page=page, page_size=page_size
        )

    def delete_draft(self, trip_id: uuid.UUID) -> None:
        trip = self.repo.get_by_id(trip_id)
        if trip is None:
            raise ResourceNotFoundException("Trip not found")
        if trip.status != TripStatus.DRAFT:
            raise InvalidTripTransitionException("Only draft trips can be deleted; cancel dispatched trips instead")
        self.repo.delete(trip)
        self.db.commit()

    # ---------- Internal helpers ----------

    @staticmethod
    def _assert_transition_allowed(current: TripStatus, target: TripStatus) -> None:
        if target not in ALLOWED_TRANSITIONS.get(current, set()):
            raise InvalidTripTransitionException(
                f"Cannot move trip from '{current.value}' to '{target.value}'"
            )

    @staticmethod
    def _validate_capacity(requested_seats: int, vehicle_capacity: int) -> None:
        if requested_seats > vehicle_capacity:
            raise CapacityExceededException(
                f"Requested {requested_seats} seats but vehicle capacity is {vehicle_capacity}"
            )

    @staticmethod
    def _to_response(trip: Trip) -> TripResponse:
        return TripResponse(
            id=trip.id,
            route_id=trip.route_id,
            route_name=trip.route.name,
            vehicle_id=trip.vehicle_id,
            vehicle_registration=trip.vehicle.registration_number,
            driver_id=trip.driver_id,
            driver_name=trip.driver.user.full_name,
            departure_time=trip.departure_time,
            arrival_time=trip.arrival_time,
            available_seats=trip.available_seats,
            fare=trip.fare,
            status=trip.status,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )