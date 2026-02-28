from domain.booking import CreateBookingRequest, Booking
from services import pricing_service, service_area_service, email_service
from repositories import booking_repo


async def create_booking(pool, request: CreateBookingRequest) -> Booking:
    # 1. Validate postcode against DB
    await service_area_service.validate_postcode(pool, request.postcode)

    # 2. Calculate price server-side (source of truth)
    price = pricing_service.calculate_price(
        request.service_type,
        request.bedrooms,
        request.bathrooms,
    )

    # 3. Persist to DB
    booking = await booking_repo.create(pool, request, price)

    # 4. Send email confirmation (stub)
    await email_service.send_booking_confirmation(booking)

    return booking
