from domain.service_area import ServiceArea


async def get_by_postcode(pool, postcode: str) -> ServiceArea | None:
    row = await pool.fetchrow(
        "SELECT * FROM service_areas WHERE postcode = $1", postcode
    )
    if row is None:
        return None
    return ServiceArea(**dict(row))
