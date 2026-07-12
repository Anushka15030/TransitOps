"""
Central definition of all domain enums.
These map 1:1 to PostgreSQL ENUM types created in the Alembic migration.
Kept separate from individual model files so services/schemas can import
enums without importing the full ORM model (avoids circular imports).
"""

import enum


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    DRIVER = "driver"
    CUSTOMER = "customer"


class VehicleType(str, enum.Enum):
    BUS = "bus"
    MINI_BUS = "mini_bus"
    VAN = "van"


class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class DriverStatus(str, enum.Enum):
    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    OFF_DUTY = "off_duty"
    SUSPENDED = "suspended"


class RouteStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TripStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class TripStatus(str, enum.Enum):
    DRAFT = "draft"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"