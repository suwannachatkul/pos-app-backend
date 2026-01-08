from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..common_fields import IdMixin, TimestampsMixin


class Transaction(Base, IdMixin, TimestampsMixin):
    """Transaction record for payment processing."""

    __tablename__: str = "transactions"

    customer_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_modifier: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    final_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("payment_methods.name", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    additional_item: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    transaction_datetime: Mapped[datetime] = mapped_column(
        name="datetime", nullable=False, index=True
    )

    # back populates from PaymentMethod
    payment_method_detail: Mapped["PaymentMethod"] = relationship(
        "PaymentMethod",
        back_populates="transactions",
        lazy="selectin",
    )
