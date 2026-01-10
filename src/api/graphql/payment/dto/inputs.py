from datetime import datetime

import strawberry
from strawberry.scalars import ID


@strawberry.input
class AdditionalItemInput:
    """
    Flexible input for payment-specific additional data.
    Can add more fields as needed for different payment methods in future.
    """

    last4: str | None = None  # For credit cards
    courier: str | None = None  # For cash on delivery
    bank: str | None = None  # For bank transfer
    account_number: str | None = None  # For bank transfer
    cheque_number: str | None = None  # For cheque

    def to_dict(self) -> dict:
        """Return a dict with only non-None fields."""
        return {k: v for k, v in strawberry.asdict(self).items() if v is not None}


@strawberry.input
class ProcessPaymentInput:
    customer_id: ID
    price: float
    price_modifier: float
    payment_method: str
    datetime: datetime
    additional_item: AdditionalItemInput | None = None
