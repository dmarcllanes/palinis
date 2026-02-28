from pydantic import BaseModel


class ServiceArea(BaseModel):
    id: int
    postcode: str
    suburb: str
    is_active: bool
