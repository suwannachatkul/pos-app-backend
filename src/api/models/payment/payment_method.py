from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..common_fields import IdMixin, TimestampsMixin


class PaymentMethod(Base, IdMixin, TimestampsMixin):
    """Payment method configuration stored in database."""

    __tablename__: str = "payment_methods"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Pricing configuration
    min_modifier: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    max_modifier: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    points_modifier: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)

    # Validation schema (None = no additional data required)
    additional_item_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # back-reference
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="payment_method_detail",
        lazy="noload",  # Avoid loading unless explicitly queried
    )
