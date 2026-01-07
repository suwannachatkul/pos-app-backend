"""Unit tests for PaymentMethod model."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from api.models.payment.payment_method import PaymentMethod


class TestPaymentMethodModel:
    """Test suite for PaymentMethod model."""

    def test_create_payment_methods(self, db_session):
        """Test creating payment methods with various configurations."""
        # Create payment method without additional schema
        pm1 = PaymentMethod(
            name="Cash",
            is_active=True,
            min_modifier=Decimal("0.9500"),
            max_modifier=Decimal("1.0500"),
            points_modifier=Decimal("1.0000"),
        )
        db_session.add(pm1)
        db_session.commit()
        db_session.refresh(pm1)

        # Verify basic payment method
        assert pm1.id is not None
        assert pm1.name == "Cash"
        assert pm1.is_active is True
        assert pm1.min_modifier == Decimal("0.9500")
        assert pm1.max_modifier == Decimal("1.0500")
        assert pm1.points_modifier == Decimal("1.0000")
        assert pm1.additional_data_schema is None
        assert pm1.created_at is not None
        assert pm1.updated_at is not None

        # Create payment method with additional data schema
        schema = {
            "type": "object",
            "properties": {
                "card_number": {"type": "string"},
                "cvv": {"type": "string"},
            },
            "required": ["card_number"],
        }
        pm2 = PaymentMethod(
            name="Credit Card",
            is_active=False,
            min_modifier=Decimal("0.1234"),
            max_modifier=Decimal("9.9876"),
            points_modifier=Decimal("1.2345"),
            additional_data_schema=schema,
        )
        db_session.add(pm2)
        db_session.commit()
        db_session.refresh(pm2)

        # Verify payment method with schema and decimal precision
        assert pm2.id is not None
        assert pm2.id != pm1.id
        assert pm2.name == "Credit Card"
        assert pm2.is_active is False
        assert pm2.min_modifier == Decimal("0.1234")
        assert pm2.max_modifier == Decimal("9.9876")
        assert pm2.points_modifier == Decimal("1.2345")
        assert pm2.additional_data_schema == schema
        assert "card_number" in pm2.additional_data_schema["properties"]

    def test_unique_name_constraint(self, db_session):
        """Test that payment method name must be unique."""
        pm1 = PaymentMethod(
            name="VISA",
            min_modifier=Decimal("1.0000"),
            max_modifier=Decimal("1.0000"),
            points_modifier=Decimal("1.0000"),
        )
        db_session.add(pm1)
        db_session.commit()

        # Try to create another payment method with the same name
        pm2 = PaymentMethod(
            name="VISA",
            min_modifier=Decimal("1.0000"),
            max_modifier=Decimal("1.0000"),
            points_modifier=Decimal("1.0000"),
        )
        db_session.add(pm2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        # Rollback to clean up the failed transaction
        db_session.rollback()

    def test_default_is_active_value(self, db_session):
        """Test that is_active defaults to True when not specified."""
        pm = PaymentMethod(
            name="PAYPAL",
            min_modifier=Decimal("1.0000"),
            max_modifier=Decimal("1.0000"),
            points_modifier=Decimal("1.0000"),
        )
        db_session.add(pm)
        db_session.commit()
        db_session.refresh(pm)

        assert pm.is_active is True

    def test_update_payment_method(self, db_session):
        """Test updating payment method fields."""
        pm = PaymentMethod(
            name="POINTS",
            is_active=True,
            min_modifier=Decimal("1.0000"),
            max_modifier=Decimal("1.0000"),
            points_modifier=Decimal("1.0000"),
        )
        db_session.add(pm)
        db_session.commit()
        original_created_at = pm.created_at

        # Update fields
        pm.is_active = False
        pm.min_modifier = Decimal("0.8500")
        pm.max_modifier = Decimal("1.1500")
        db_session.commit()
        db_session.refresh(pm)

        assert pm.is_active is False
        assert pm.min_modifier == Decimal("0.8500")
        assert pm.max_modifier == Decimal("1.1500")
        assert pm.created_at == original_created_at
        assert pm.updated_at >= pm.created_at
