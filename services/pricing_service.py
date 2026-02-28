from decimal import Decimal, ROUND_HALF_UP
from domain.enums import ServiceType

BASE_PRICES: dict[ServiceType, dict[int, int]] = {
    ServiceType.regular:      {1: 89,  2: 135, 3: 165, 4: 195, 5: 225},
    ServiceType.deep:         {1: 149, 2: 189, 3: 245, 4: 299, 5: 349},
    ServiceType.end_of_lease: {1: 199, 2: 299, 3: 399, 4: 499, 5: 599},
}

BATHROOM_MULTIPLIERS: dict[int, float] = {
    1: 1.0, 2: 1.15, 3: 1.3, 4: 1.45,
}


def calculate_price(
    service_type: ServiceType,
    bedrooms: int,
    bathrooms: int,
) -> Decimal:
    base = BASE_PRICES[service_type][bedrooms]
    multiplier = BATHROOM_MULTIPLIERS[bathrooms]
    price = Decimal(str(base * multiplier)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return price
