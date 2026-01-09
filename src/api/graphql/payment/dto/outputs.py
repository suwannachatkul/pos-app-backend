import strawberry
from strawberry.scalars import JSON


@strawberry.type
class PaymentMethod:
    id: str
    name: str
    is_active: bool
    min_modifier: float
    max_modifier: float
    points_modifier: float
    additional_item_schema: JSON | None


@strawberry.type
class PaymentResult:
    final_price: float
    points: int
