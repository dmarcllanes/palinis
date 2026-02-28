from repositories import service_area_repo
from domain.service_area import ServiceArea


async def validate_postcode(pool, postcode: str) -> ServiceArea:
    area = await service_area_repo.get_by_postcode(pool, postcode)
    if area is None:
        raise ValueError(f"Postcode {postcode} is not in our service area.")
    if not area.is_active:
        raise ValueError(f"We are not currently servicing postcode {postcode}.")
    return area
