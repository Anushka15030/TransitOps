"""
Seeds the four fixed roles the RBAC system depends on.
Idempotent: safe to run multiple times (checks existence first).
"""

from sqlalchemy.orm import Session

from app.models.enums import RoleName
from app.models.role import Role

DEFAULT_ROLES = [
    (RoleName.ADMIN, "Full system access — manages users, vehicles, routes"),
    (RoleName.DISPATCHER, "Schedules trips, assigns drivers/vehicles"),
    (RoleName.DRIVER, "Operates assigned trips"),
    (RoleName.CUSTOMER, "Books and manages own trips"),
]


def seed_roles(db: Session) -> None:
    for role_name, description in DEFAULT_ROLES:
        exists = db.query(Role).filter(Role.name == role_name.value).first()
        if not exists:
            db.add(Role(name=role_name.value, description=description))
    db.commit()