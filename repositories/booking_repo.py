from domain.booking import CreateBookingRequest, Booking
from decimal import Decimal
from datetime import date, time
from uuid import UUID


async def create(pool, request: CreateBookingRequest, price: Decimal) -> Booking:
    row = await pool.fetchrow(
        """
        INSERT INTO bookings
            (customer_name, email, phone, address, postcode,
             service_date, service_time, service_type, bedrooms, bathrooms, total_price)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
        RETURNING *
        """,
        request.customer_name, request.email, request.phone,
        request.address, request.postcode, request.service_date,
        request.service_time, request.service_type.value,
        request.bedrooms, request.bathrooms, price,
    )
    return Booking(**dict(row))


async def get_by_id(pool, booking_id: UUID) -> Booking | None:
    row = await pool.fetchrow(
        "SELECT * FROM bookings WHERE id = $1", booking_id
    )
    return Booking(**dict(row)) if row else None


async def get_by_email(pool, email: str) -> list[Booking]:
    rows = await pool.fetch(
        "SELECT * FROM bookings WHERE LOWER(email) = LOWER($1) ORDER BY created_at DESC",
        email,
    )
    return [Booking(**dict(row)) for row in rows]


async def get_all(pool, status: str | None = None) -> list[Booking]:
    if status:
        rows = await pool.fetch(
            "SELECT * FROM bookings WHERE status = $1 ORDER BY created_at DESC", status
        )
    else:
        rows = await pool.fetch(
            "SELECT * FROM bookings ORDER BY created_at DESC"
        )
    return [Booking(**dict(row)) for row in rows]


async def get_by_cleaner_id(pool, cleaner_id: UUID) -> list[Booking]:
    rows = await pool.fetch(
        """
        SELECT * FROM bookings
        WHERE cleaner_id = $1
          AND status != 'cancelled'
        ORDER BY service_date ASC
        """,
        cleaner_id,
    )
    return [Booking(**dict(row)) for row in rows]


async def update_status(pool, booking_id: UUID, new_status: str) -> Booking | None:
    row = await pool.fetchrow(
        "UPDATE bookings SET status = $1 WHERE id = $2 RETURNING *",
        new_status, booking_id,
    )
    return Booking(**dict(row)) if row else None


async def assign_cleaner(pool, booking_id: UUID, cleaner_id: UUID) -> Booking | None:
    row = await pool.fetchrow(
        """
        UPDATE bookings
        SET cleaner_id = $1, status = 'assigned'
        WHERE id = $2
        RETURNING *
        """,
        cleaner_id, booking_id,
    )
    return Booking(**dict(row)) if row else None


async def count_by_date_and_times(pool, service_date: date) -> dict[time, int]:
    """Returns {time_slot: booking_count} for all slots on a date (non-cancelled/flagged)."""
    rows = await pool.fetch(
        """
        SELECT service_time, COUNT(*) AS cnt
        FROM bookings
        WHERE service_date = $1
          AND status IN ('confirmed', 'assigned', 'completed')
        GROUP BY service_time
        """,
        service_date,
    )
    return {row["service_time"]: row["cnt"] for row in rows}
