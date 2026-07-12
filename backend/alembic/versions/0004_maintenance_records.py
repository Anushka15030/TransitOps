"""add maintenance_records table

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-12
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    maintenance_status_enum = postgresql.ENUM("open", "closed", name="maintenance_status_enum")
    maintenance_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "maintenance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reported_issue", sa.Text(), nullable=False),
        sa.Column("status", maintenance_status_enum, server_default="open", nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(10, 2), nullable=True),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_maintenance_vehicle_id", "maintenance_records", ["vehicle_id"])
    op.create_index("ix_maintenance_status", "maintenance_records", ["status"])

    # Only ONE open maintenance record per vehicle at a time — this is the
    # DB-level guarantee that backs the service-layer check, same pattern
    # as the active-seat-per-trip partial index from Module 1.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_maintenance_open_per_vehicle
        ON maintenance_records (vehicle_id)
        WHERE status = 'open'
        """
    )


def downgrade() -> None:
    op.drop_index("uq_maintenance_open_per_vehicle", table_name="maintenance_records")
    op.drop_table("maintenance_records")
    postgresql.ENUM(name="maintenance_status_enum").drop(op.get_bind(), checkfirst=True)