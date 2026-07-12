"""initial schema: roles, users, drivers, vehicles, routes, route_stops, trips, bookings

Revision ID: 0001
Revises:
Create Date: 2026-07-12
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Extension for gen_random_uuid() on managed PG providers that need it explicitly ---
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # --- Native ENUM types (created once, reused across tables via create_type=False) ---
    driver_status_enum = postgresql.ENUM(
        "available", "on_trip", "off_duty", "suspended", name="driver_status_enum"
    )
    vehicle_type_enum = postgresql.ENUM("bus", "mini_bus", "van", name="vehicle_type_enum")
    vehicle_status_enum = postgresql.ENUM("active", "maintenance", "inactive", name="vehicle_status_enum")
    route_status_enum = postgresql.ENUM("active", "inactive", name="route_status_enum")
    trip_status_enum = postgresql.ENUM(
        "scheduled", "ongoing", "completed", "cancelled", name="trip_status_enum"
    )
    booking_status_enum = postgresql.ENUM(
        "pending", "confirmed", "cancelled", "completed", name="booking_status_enum"
    )

    bind = op.get_bind()
    driver_status_enum.create(bind, checkfirst=True)
    vehicle_type_enum.create(bind, checkfirst=True)
    vehicle_status_enum.create(bind, checkfirst=True)
    route_status_enum.create(bind, checkfirst=True)
    trip_status_enum.create(bind, checkfirst=True)
    booking_status_enum.create(bind, checkfirst=True)

    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"])

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_users_role_id", "users", ["role_id"])

    # --- drivers ---
    op.create_table(
        "drivers",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("license_number", sa.String(50), nullable=False),
        sa.Column("license_expiry", sa.Date(), nullable=False),
        sa.Column("status", driver_status_enum, server_default="available", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_drivers_user_id"),
        sa.UniqueConstraint("license_number", name="uq_drivers_license_number"),
    )
    op.create_index("ix_drivers_user_id", "drivers", ["user_id"])
    op.create_index("ix_drivers_license_number", "drivers", ["license_number"])
    op.create_index("ix_drivers_status", "drivers", ["status"])

    # --- vehicles ---
    op.create_table(
        "vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("registration_number", sa.String(20), nullable=False),
        sa.Column("vehicle_type", vehicle_type_enum, nullable=False),
        sa.Column("manufacturer", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("status", vehicle_status_enum, server_default="active", nullable=False),
        sa.UniqueConstraint("registration_number", name="uq_vehicles_registration_number"),
        sa.CheckConstraint("capacity > 0", name="ck_vehicles_capacity_positive"),
        sa.CheckConstraint("year >= 1990", name="ck_vehicles_year_valid"),
    )
    op.create_index("ix_vehicles_registration_number", "vehicles", ["registration_number"])
    op.create_index("ix_vehicles_status", "vehicles", ["status"])

    # --- routes ---
    op.create_table(
        "routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("origin", sa.String(150), nullable=False),
        sa.Column("destination", sa.String(150), nullable=False),
        sa.Column("distance_km", sa.Numeric(6, 2), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("status", route_status_enum, server_default="active", nullable=False),
        sa.CheckConstraint("distance_km > 0", name="ck_routes_distance_positive"),
        sa.CheckConstraint("estimated_duration_minutes > 0", name="ck_routes_duration_positive"),
    )
    op.create_index("ix_routes_origin", "routes", ["origin"])
    op.create_index("ix_routes_destination", "routes", ["destination"])
    op.create_index("ix_routes_status", "routes", ["status"])

    # --- route_stops ---
    op.create_table(
        "route_stops",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stop_name", sa.String(150), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("arrival_offset_minutes", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("route_id", "sequence_order", name="uq_route_stop_sequence"),
    )
    op.create_index("ix_route_stops_route_id", "route_stops", ["route_id"])

    # --- trips ---
    op.create_table(
        "trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_seats", sa.Integer(), nullable=False),
        sa.Column("fare", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", trip_status_enum, server_default="scheduled", nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("arrival_time > departure_time", name="ck_trips_arrival_after_departure"),
        sa.CheckConstraint("available_seats >= 0", name="ck_trips_seats_non_negative"),
        sa.CheckConstraint("fare >= 0", name="ck_trips_fare_non_negative"),
    )
    op.create_index("ix_trips_route_id", "trips", ["route_id"])
    op.create_index("ix_trips_vehicle_id", "trips", ["vehicle_id"])
    op.create_index("ix_trips_driver_id", "trips", ["driver_id"])
    op.create_index("ix_trips_departure_time", "trips", ["departure_time"])
    op.create_index("ix_trips_status", "trips", ["status"])
    # Composite index: the most common query is "find scheduled trips on a route
    # around a given date" — a composite index serves this directly instead of
    # combining two single-column indexes at query time.
    op.create_index("ix_trips_route_status_departure", "trips", ["route_id", "status", "departure_time"])

    # --- bookings ---
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seat_number", sa.Integer(), nullable=False),
        sa.Column("booking_reference", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", booking_status_enum, server_default="pending", nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("booking_reference", name="uq_bookings_reference"),
        sa.CheckConstraint("seat_number > 0", name="ck_bookings_seat_positive"),
        sa.CheckConstraint("amount >= 0", name="ck_bookings_amount_non_negative"),
    )
    op.create_index("ix_bookings_trip_id", "bookings", ["trip_id"])
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])
    op.create_index("ix_bookings_reference", "bookings", ["booking_reference"])
    op.create_index("ix_bookings_status", "bookings", ["status"])

    # Partial unique index: a seat can be double-booked ONLY if the previous
    # booking for that seat was cancelled. Plain UniqueConstraint can't express
    # a WHERE clause, so this is done via raw index creation.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_bookings_active_seat_per_trip
        ON bookings (trip_id, seat_number)
        WHERE status IN ('pending', 'confirmed', 'completed')
        """
    )


def downgrade() -> None:
    op.drop_index("uq_bookings_active_seat_per_trip", table_name="bookings")
    op.drop_table("bookings")
    op.drop_table("trips")
    op.drop_table("route_stops")
    op.drop_table("routes")
    op.drop_table("vehicles")
    op.drop_table("drivers")
    op.drop_table("users")
    op.drop_table("roles")

    postgresql.ENUM(name="booking_status_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="trip_status_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="route_status_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="vehicle_status_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="vehicle_type_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="driver_status_enum").drop(op.get_bind(), checkfirst=True)