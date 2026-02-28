from pydantic import BaseModel, EmailStr, field_validator
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID
from domain.enums import BookingStatus, ServiceType


class CreateBookingRequest(BaseModel):
    customer_name: str
    email: EmailStr
    phone: str
    address: str
    postcode: str
    service_date: date
    service_type: ServiceType
    bedrooms: int
    bathrooms: int

    @field_validator("bedrooms")
    @classmethod
    def validate_bedrooms(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Bedrooms must be between 1 and 5")
        return v

    @field_validator("bathrooms")
    @classmethod
    def validate_bathrooms(cls, v):
        if not 1 <= v <= 4:
            raise ValueError("Bathrooms must be between 1 and 4")
        return v


class Booking(BaseModel):
    id: UUID
    customer_name: str
    email: str
    phone: str
    address: str
    postcode: str
    service_date: date
    service_type: ServiceType
    bedrooms: int
    bathrooms: int
    total_price: Decimal
    status: BookingStatus
    created_at: datetime
