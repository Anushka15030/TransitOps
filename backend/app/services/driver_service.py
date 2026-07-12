"""
Orchestrates User + Driver creation as one transaction, plus license and
status business rules. This is a direct parallel to VehicleService but
one layer deeper because a driver's identity lives in a different table
than its operational data.
"""

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateResourceException, ResourceNotFoundException
from app.core.permissions import Permission
from app.core.security import hash_password
from app.models.driver import Driver
from app.models.enums import RoleName
from app.models.user import User
from app.repositories.driver_repository import DriverRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common_schema import PaginatedResponse
from app.schemas.driver_schema import (
    DriverCreateRequest,
    DriverFilterParams,
    DriverResponse,
    DriverUpdateRequest,
)


class DriverAlreadyReferencedException(DuplicateResourceException):
    status_code = 409
    detail = "Driver cannot be deleted because they have associated trip history"


class DriverService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DriverRepository(db)
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def create(self, payload: DriverCreateRequest) -> DriverResponse:
        if self.user_repo.exists_by_email_or_phone(payload.email, payload.phone):
            raise DuplicateResourceException("An account with this email or phone already exists")

        if self.repo.get_by_license_number(payload.license_number):
            raise DuplicateResourceException(
                f"A driver with license number '{payload.license_number}' already exists"
            )

        driver_role = self.role_repo.get_by_name(RoleName.DRIVER.value)
        if driver_role is None:
            raise ResourceNotFoundException("Driver role not seeded — contact administrator")

        # Single transaction: both rows commit together or neither does.
        # If Driver creation fails after User is added, the whole session
        # rolls back — we never end up with an orphan login-only account.
        user = User(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            role_id=driver_role.id,
            is_active=True,
        )
        self.user_repo.create(user)  # flush only, no commit yet

        driver = Driver(
            user_id=user.id,
            license_number=payload.license_number,
            license_expiry=payload.license_expiry,
        )
        self.repo.create(driver)

        self.db.commit()
        self.db.refresh(driver)

        return self._to_response(driver, user)

    def get_by_id(self, driver_id: uuid.UUID) -> DriverResponse:
        driver = self.repo.get_by_id_with_user(driver_id)
        if driver is None:
            raise ResourceNotFoundException("Driver not found")
        return self._to_response(driver, driver.user)

    def list_drivers(
        self, filters: DriverFilterParams, page: int, page_size: int
    ) -> PaginatedResponse[DriverResponse]:
        offset = (page - 1) * page_size
        items, total = self.repo.search_and_filter(
            search=filters.search, status=filters.status, offset=offset, limit=page_size
        )
        return PaginatedResponse.build(
            items=[self._to_response(d, d.user) for d in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, driver_id: uuid.UUID, payload: DriverUpdateRequest) -> DriverResponse:
        driver = self.repo.get_by_id_with_user(driver_id)
        if driver is None:
            raise ResourceNotFoundException("Driver not found")

        update_data = payload.model_dump(exclude_unset=True)

        if "license_number" in update_data:
            existing = self.repo.get_by_license_number(update_data["license_number"])
            if existing and existing.id != driver.id:
                raise DuplicateResourceException(
                    f"License number '{update_data['license_number']}' is already registered"
                )

        # full_name lives on User, not Driver — route the field to the right table.
        if "full_name" in update_data:
            driver.user.full_name = update_data.pop("full_name")

        for field, value in update_data.items():
            setattr(driver, field, value)

        self.db.commit()
        self.db.refresh(driver)
        return self._to_response(driver, driver.user)

    def delete(self, driver_id: uuid.UUID) -> None:
        driver = self.repo.get_by_id(driver_id)
        if driver is None:
            raise ResourceNotFoundException("Driver not found")

        if self.repo.has_active_trips(driver_id):
            raise DriverAlreadyReferencedException()

        # Deleting the Driver profile does NOT delete the User account —
        # a driver being removed from operations doesn't have to lose
        # their login/identity record. Cascade direction is deliberate
        # (Module 1): User -> Driver cascades, not the other way.
        self.repo.delete(driver)
        self.db.commit()

    @staticmethod
    def _to_response(driver: Driver, user: User) -> DriverResponse:
        return DriverResponse(
            id=driver.id,
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            license_number=driver.license_number,
            license_expiry=driver.license_expiry,
            status=driver.status,
            created_at=driver.created_at,
            updated_at=driver.updated_at,
        )