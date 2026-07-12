"""rename trip statuses to draft/dispatched, add overlap-check indexes

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-12
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL 12+ allows RENAME VALUE inside a transaction — this is a
    # zero-downtime, zero-data-loss rename (existing rows are relabeled
    # automatically by Postgres, no UPDATE needed).
    op.execute("ALTER TYPE trip_status_enum RENAME VALUE 'scheduled' TO 'draft'")
    op.execute("ALTER TYPE trip_status_enum RENAME VALUE 'ongoing' TO 'dispatched'")

    # These composite indexes are what make the overlap-check query (the
    # hottest query in the dispatch transaction) fast even with thousands
    # of trips — without them, every dispatch would force a sequential
    # scan of the trips table while holding a row lock, which would
    # serialize ALL dispatches system-wide, not just conflicting ones.
    op.create_index(
        "ix_trips_vehicle_status_window", "trips",
        ["vehicle_id", "status", "departure_time", "arrival_time"],
    )
    op.create_index(
        "ix_trips_driver_status_window", "trips",
        ["driver_id", "status", "departure_time", "arrival_time"],
    )


def downgrade() -> None:
    op.drop_index("ix_trips_driver_status_window", table_name="trips")
    op.drop_index("ix_trips_vehicle_status_window", table_name="trips")
    op.execute("ALTER TYPE trip_status_enum RENAME VALUE 'draft' TO 'scheduled'")
    op.execute("ALTER TYPE trip_status_enum RENAME VALUE 'dispatched' TO 'ongoing'")