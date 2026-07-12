from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base_model import BaseModel


class Role(Base, BaseModel):
    """
    Lookup table for RBAC roles.
    Kept as a table (not a hardcoded enum on `users`) so new roles
    (e.g. FLEET_MANAGER) can be added via a data migration, not a schema one.
    """
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # One role -> many users
    users: Mapped[list["User"]] = relationship(back_populates="role")