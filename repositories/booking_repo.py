from domain.booking import CreateBookingRequest, Booking
from decimal import Decimal
from uuid import UUID


async def create(pool, request: CreateBookingRequest, price: Decimal) -> Booking:
    row = await pool.fetchrow(
        """
        INSERT INTO bookings
            (customer_name, email, phone, address, postcode,
             service_date, service_type, bedrooms, bathrooms, total_price)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
        RETURNING *
        """,
        request.customer_name, request.email, request.phone,
        request.address, request.postcode, request.service_date,
        request.service_type.value, request.bedrooms, request.bathrooms, price,
    )
    return Booking(**dict(row))


async def get_by_id(pool, booking_id: UUID) -> Booking | None:
    row = await pool.fetchrow(
        "SELECT * FROM bookings WHERE id = $1", booking_id
    )
    if row is None:
        return None
    return Booking(**dict(row))


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


async def update_status(pool, booking_id: UUID, new_status: str) -> Booking | None:
    row = await pool.fetchrow(
        "UPDATE bookings SET status = $1 WHERE id = $2 RETURNING *",
        new_status, booking_id,
    )
    if row is None:
        return None
    return Booking(**dict(row))
