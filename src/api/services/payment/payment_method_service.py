from typing import Any

from jsonschema import (
    ValidationError as JsonSchemaValidationError,
)
from jsonschema import (
    validate as json_schema_validate,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import PaymentMethod


class PaymentMethodService:
    """Service for managing payment methods."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_method(self, name: str) -> PaymentMethod:
        """Get active payment method configuration from database."""
        # TODO: cache results
        result = await self.db.execute(
            select(PaymentMethod).where(
                PaymentMethod.name == name, PaymentMethod.is_active == True
            )
        )
        method = result.scalar_one_or_none()

        if not method:
            raise ValueError(f"Unknown or inactive payment method: {name}")

        return method

    async def get_all_active_methods(self) -> list[PaymentMethod]:
        """Get all active payment methods."""
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.is_active == True)
        )
        return result.scalars().all()

    def validate_price_modifier(self, method: PaymentMethod, modifier: float) -> None:
        """Validate price modifier is within allowed range."""
        min_mod = float(method.min_modifier)
        max_mod = float(method.max_modifier)

        if not (min_mod <= modifier <= max_mod):
            raise ValueError(
                f"Price modifier {modifier} is out of range "
                f"[{min_mod}, {max_mod}] for {method.name}"
            )

    def validate_additional_data(
        self, method: PaymentMethod, data: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Validate additional data using JSON Schema."""
        if method.additional_item_schema is None:
            return None

        if data is None:
            raise ValueError(f"Payment method {method.name} requires additional data")

        # Validate using JSON Schema
        try:
            json_schema_validate(instance=data, schema=method.additional_item_schema)
        except JsonSchemaValidationError as e:
            raise ValueError(f"Invalid additional data for {method.name}: {e.message}")

        return data

    def calculate_final_price(self, price: float, modifier: float) -> float:
        """Calculate final price."""
        return round(price * modifier, 2)

    def calculate_points(self, method: PaymentMethod, price: float) -> int:
        """Calculate loyalty points based on payment method."""
        return round(price * float(method.points_modifier))
