"""Pydantic schemas for cache validation and serialization."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class PaymentMethodCache(BaseModel):
    """Schema for cached PaymentMethod data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
    min_modifier: float
    max_modifier: float
    points_modifier: float
    additional_item_schema: dict[str, Any] | None = None
