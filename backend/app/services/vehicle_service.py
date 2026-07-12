"""
Business rules for vehicle management: uniqueness checks, deletion guards,
and translating repository results into paginated response DTOs.
"""

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateResourceException, ResourceNotFoundException
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.common_schema import PaginatedResponse
from app.schemas.vehicle_schema import (
    VehicleCreateRequest,
    VehicleFilterParams,
    VehicleResponse,
    VehicleUpdateRequest,
)


class VehicleAlreadyReferencedException(DuplicateResourceException):
    status_code = 409
    detail = "Vehicle cannot be deleted because it has associated trip history"


class VehicleService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VehicleRepository(db)

    def create(self, payload: VehicleCreateRequest) -> VehicleResponse:
        if self.repo.get_by_registration_number(payload.registration_number):
            raise DuplicateResourceException(
                f"A vehicle with registration number '{payload.registration_number}' already exists"
            )

        vehicle = Vehicle(**payload.model_dump())
        self.repo.create(vehicle)
        self.db.commit()
        return VehicleResponse.model_validate(vehicle)

    def get_by_id(self, vehicle_id: uuid.UUID) -> VehicleResponse:
        vehicle = self.repo.get_by_id(vehicle_id)
        if vehicle is None:
            raise ResourceNotFoundException("Vehicle not found")
        return VehicleResponse.model_validate(vehicle)

    def list_vehicles(
        self, filters: VehicleFilterParams, page: int, page_size: int
    ) -> PaginatedResponse[VehicleResponse]:
        offset = (page - 1) * page_size
        items, total = self.repo.search_and_filter(
            search=filters.search,
            vehicle_type=filters.vehicle_type,
            status=filters.status,
            offset=offset,
            limit=page_size,
        )
        return PaginatedResponse.build(
            items=[VehicleResponse.model_validate(v) for v in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, vehicle_id: uuid.UUID, payload: VehicleUpdateRequest) -> VehicleResponse:
        vehicle = self.repo.get_by_id(vehicle_id)
        if vehicle is None:
            raise ResourceNotFoundException("Vehicle not found")

        update_data = payload.model_dump(exclude_unset=True)  # only touch fields the client sent
        for field, value in update_data.items():
            setattr(vehicle, field, value)

        self.db.commit()
        self.db.refresh(vehicle)
        return VehicleResponse.model_validate(vehicle)

    def delete(self, vehicle_id: uuid.UUID) -> None:
        vehicle = self.repo.get_by_id(vehicle_id)
        if vehicle is None:
            raise ResourceNotFoundException("Vehicle not found")

        if self.repo.has_active_trips(vehicle_id):
            raise VehicleAlreadyReferencedException()

        self.repo.delete(vehicle)
        self.db.commit()