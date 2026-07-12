"""
Central RBAC permission matrix. Adding a new role or permission means
editing ONE dict here — never scattered `if role == "admin"` checks
throughout route handlers (that pattern doesn't scale and is impossible
to audit).
"""

from enum import Enum

from app.models.enums import RoleName


class Permission(str, Enum):
    # Users
    USER_MANAGE = "user:manage"
    # Vehicles
    VEHICLE_READ = "vehicle:read"
    VEHICLE_WRITE = "vehicle:write"
    # Drivers
    DRIVER_READ = "driver:read"
    DRIVER_WRITE = "driver:write"
    # Routes
    ROUTE_READ = "route:read"
    ROUTE_WRITE = "route:write"
    # Trips
    TRIP_READ = "trip:read"
    TRIP_WRITE = "trip:write"
    TRIP_ASSIGN = "trip:assign"          # assign driver/vehicle to a trip
    TRIP_UPDATE_STATUS = "trip:update_status"   # driver marks ongoing/completed
    # Bookings
    BOOKING_READ_OWN = "booking:read_own"
    BOOKING_READ_ALL = "booking:read_all"
    BOOKING_CREATE = "booking:create"
    BOOKING_CANCEL_OWN = "booking:cancel_own"
    # Dashboard
    DASHBOARD_VIEW = "dashboard:view"


ROLE_PERMISSIONS: dict[RoleName, set[Permission]] = {
    RoleName.ADMIN: {p for p in Permission},  # full access

    RoleName.DISPATCHER: {
        Permission.VEHICLE_READ, Permission.VEHICLE_WRITE,
        Permission.DRIVER_READ, Permission.DRIVER_WRITE,
        Permission.ROUTE_READ, Permission.ROUTE_WRITE,
        Permission.TRIP_READ, Permission.TRIP_WRITE, Permission.TRIP_ASSIGN,
        Permission.BOOKING_READ_ALL,
        Permission.DASHBOARD_VIEW,
    },

    RoleName.DRIVER: {
        Permission.TRIP_READ, Permission.TRIP_UPDATE_STATUS,
        Permission.VEHICLE_READ, Permission.ROUTE_READ,
    },

    RoleName.CUSTOMER: {
        Permission.TRIP_READ, Permission.ROUTE_READ,
        Permission.BOOKING_READ_OWN, Permission.BOOKING_CREATE, Permission.BOOKING_CANCEL_OWN,
    },
}


def role_has_permission(role: RoleName, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())