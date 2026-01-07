from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class IdMixin:
    """Mixin for auto-incrementing integer primary key (uses BIGINT for scalability)."""

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, nullable=False
    )


class TimestampsMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )


class CreatedAtMixin:
    """Mixin for created_at only."""

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=text("now()")
    )


class UpdatedAtMixin:
    """Mixin for updated_at only."""

    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )
