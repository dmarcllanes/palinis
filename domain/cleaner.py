from pydantic import BaseModel
from uuid import UUID


class Cleaner(BaseModel):
    id: UUID
    name: str
    email: str
    is_active: bool
