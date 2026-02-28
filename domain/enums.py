from enum import Enum


class BookingStatus(str, Enum):
    pending_payment = "pending_payment"
    confirmed = "confirmed"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    flagged_for_review = "flagged_for_review"


class ServiceType(str, Enum):
    regular = "regular"
    deep = "deep"
    end_of_lease = "end_of_lease"
