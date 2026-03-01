from domain.booking import CreateBookingRequest, Booking
from domain.enums import BookingStatus
from services import pricing_service, service_area_service, email_service, status_transition_service, availability_service
from repositories import booking_repo, cleaner_repo
from uuid import UUID


async def create_booking(pool, request: CreateBookingRequest) -> Booking:
    # 1. Validate postcode against DB
    await service_area_service.validate_postcode(pool, request.postcode)

    # 2. Validate time slot availability
    await availability_service.validate_slot(pool, request.service_date, request.service_time)

    # 3. Calculate price server-side (source of truth)
    price = pricing_service.calculate_price(
        request.service_type,
        request.bedrooms,
        request.bathrooms,
    )

    # 4. Persist to DB
    booking = await booking_repo.create(pool, request, price)

    # 4. Send email confirmation (stub)
    await email_service.send_booking_confirmation(booking)

    return booking


async def update_booking_status(pool, booking_id: UUID, new_status: str) -> Booking:
    """
    Validate the transition then persist. Raises ValueError on invalid
    booking ID or disallowed transition.
    """
    booking = await booking_repo.get_by_id(pool, booking_id)
    if booking is None:
        raise ValueError("Booking not found.")

    new_status_enum = BookingStatus(new_status)

    # No-op: already in this state (e.g. back-button resubmit)
    if booking.status == new_status_enum:
        return booking

    # Enforce state machine — raises ValueError on invalid transition
    status_transition_service.validate_transition(booking.status, new_status_enum)

    return await booking_repo.update_status(pool, booking_id, new_status)


async def assign_cleaner_to_booking(pool, booking_id: UUID, cleaner_id: UUID) -> Booking:
    """
    Assign an active cleaner to a confirmed booking and transition it to 'assigned'.
    Raises ValueError if booking or cleaner is invalid.
    """
    booking = await booking_repo.get_by_id(pool, booking_id)
    if booking is None:
        raise ValueError("Booking not found.")

    # Only confirmed (or already assigned for reassignment) bookings can be assigned
    allowed = {BookingStatus.confirmed, BookingStatus.assigned}
    if booking.status not in allowed:
        raise ValueError(
            f"Cannot assign a cleaner to a booking with status '{booking.status.value}'."
        )

    cleaner = await cleaner_repo.get_by_id(pool, cleaner_id)
    if cleaner is None:
        raise ValueError("Cleaner not found.")
    if not cleaner.is_active:
        raise ValueError(f"Cleaner '{cleaner.name}' is not currently active.")

    return await booking_repo.assign_cleaner(pool, booking_id, cleaner_id)
