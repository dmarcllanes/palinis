from domain.enums import BookingStatus

ALLOWED_TRANSITIONS: dict[BookingStatus, list[BookingStatus]] = {
    BookingStatus.pending_confirmation: [BookingStatus.confirmed,    BookingStatus.cancelled, BookingStatus.flagged_for_review],
    BookingStatus.confirmed:          [BookingStatus.assigned,     BookingStatus.cancelled, BookingStatus.flagged_for_review],
    BookingStatus.assigned:           [BookingStatus.in_progress,  BookingStatus.completed,   BookingStatus.cancelled, BookingStatus.flagged_for_review],
    BookingStatus.in_progress:        [BookingStatus.completed,    BookingStatus.cancelled,   BookingStatus.flagged_for_review],
    BookingStatus.completed:          [],
    BookingStatus.cancelled:          [],
    BookingStatus.flagged_for_review: [BookingStatus.confirmed,    BookingStatus.cancelled],
}


def validate_transition(current: BookingStatus, new: BookingStatus) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise ValueError(
            f"Cannot transition booking from '{current.value}' to '{new.value}'."
        )
