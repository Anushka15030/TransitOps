"""
Shared mixin for all ORM models.
- UUID primary keys instead of auto-increment integers: prevents ID
  enumeration attacks (a competitor can't guess /vehicles/2, /vehicles/3...)
  and makes IDs safe to expose in URLs — a security requirement, not just style.
- created_at / updated_at give every table a free audit trail, which is
  expected in any enterprise schema for debugging and compliance.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )