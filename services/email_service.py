from domain.booking import Booking


async def send_booking_confirmation(booking: Booking) -> None:
    # TODO: replace with real email provider (Resend, SendGrid, etc.)
    print(f"[EMAIL] Booking confirmation sent to {booking.email}")
    print(f"  Booking ID : {booking.id}")
    print(f"  Customer   : {booking.customer_name}")
    print(f"  Service    : {booking.service_type.value}")
    print(f"  Date       : {booking.service_date}")
    print(f"  Total      : ${booking.total_price}")
