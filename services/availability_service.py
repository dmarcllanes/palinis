from datetime import date, time, timedelta
from repositories import booking_repo, cleaner_repo

TIME_SLOTS: list[time] = [
    time(8, 0), time(10, 0), time(12, 0), time(14, 0), time(16, 0)
]

_SLOT_LABELS = {
    time(8, 0): "8:00 AM",
    time(10, 0): "10:00 AM",
    time(12, 0): "12:00 PM",
    time(14, 0): "2:00 PM",
    time(16, 0): "4:00 PM",
}


def format_slot(t: time) -> str:
    return _SLOT_LABELS.get(t, t.strftime("%I:%M %p").lstrip("0"))


async def get_available_slots(pool, service_date: date) -> list[time]:
    """Returns time slots that still have capacity on the given date."""
    active_cleaner_count = await cleaner_repo.count_active(pool)
    if active_cleaner_count == 0:
        return []
    booked_counts = await booking_repo.count_by_date_and_times(pool, service_date)
    return [
        slot for slot in TIME_SLOTS
        if booked_counts.get(slot, 0) < active_cleaner_count
    ]


async def validate_slot(pool, service_date: date, service_time: time) -> None:
    """Raises ValueError if slot is full, with alternatives in message."""
    available = await get_available_slots(pool, service_date)
    if service_time not in available:
        alternatives = await _find_alternatives(pool, service_date, service_time)
        raise ValueError(f"That time slot is fully booked. {alternatives}")


async def _find_alternatives(pool, service_date: date, service_time: time) -> str:
    """Build a human-readable suggestion string with alternative slots."""
    # Other available slots on the same day
    same_day = await get_available_slots(pool, service_date)
    # Exclude the requested slot from suggestions (it's full)
    same_day = [s for s in same_day if s != service_time]

    if same_day:
        labels = ", ".join(format_slot(s) for s in same_day)
        return f"Other available times today: {labels}."

    # Scan forward up to 7 days for next available date
    for delta in range(1, 8):
        next_date = service_date + timedelta(days=delta)
        slots = await get_available_slots(pool, next_date)
        if slots:
            labels = ", ".join(format_slot(s) for s in slots)
            return f"Next available: {next_date.strftime('%A, %d %B')} at {labels}."

    return "No availability in the next 7 days. Please contact us directly."
