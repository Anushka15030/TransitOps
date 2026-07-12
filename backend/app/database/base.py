"""
Declarative base + a single import point that pulls in every model.
Alembic's autogenerate needs every model imported somewhere it can see
before it diffs metadata — this file is that single source of truth,
so we never forget to register a new table in migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Base.metadata is fully populated for Alembic.
from app.models.role import Role          # noqa: E402, F401
from app.models.user import User          # noqa: E402, F401
from app.models.driver import Driver      # noqa: E402, F401
from app.models.vehicle import Vehicle    # noqa: E402, F401
from app.models.route import Route        # noqa: E402, F401
from app.models.route_stop import RouteStop   # noqa: E402, F401
from app.models.trip import Trip          # noqa: E402, F401
from app.models.booking import Booking    # noqa: E402, F401
from app.models.refresh_token import RefreshToken  # noqa: E402, F401