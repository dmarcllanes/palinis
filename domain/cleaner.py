from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Cleaner(BaseModel):
    id: UUID
    name: str
    email: str
    is_active: bool
    username: str | None = None
    password_hash: str | None = None
    phone: str | None = None
    created_at: datetime | None = None
