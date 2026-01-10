from datetime import datetime as dt

import strawberry
from strawberry.scalars import ID, JSON


@strawberry.type
class PaymentMethod:
    id: ID
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


@strawberry.type
class SalesReport:
    datetime: dt
    sales: float
    points: int


@strawberry.type
class PaymentMethodsResult:
    """Wrapper for list of payment methods to enable union with error type."""

    methods: list[PaymentMethod]


@strawberry.type
class SalesReportResult:
    """Wrapper for list of sales reports to enable union with error type."""

    reports: list[SalesReport]
