"""Unit tests for PaymentMethod model."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from api.models.payment.payment_method import PaymentMethod


class TestPaymentMethodModel:
    """Test suite for PaymentMethod model."""

    def test_create_payment_method_basic(self, payment_method_cash):
        """Test creating a basic payment method using fixture."""
        # Verify basic payment method
        assert payment_method_cash.id is not None
        assert payment_method_cash.name == "CASH_TEST"
        assert payment_method_cash.is_active is True
        assert payment_method_cash.min_modifier == Decimal("0.9000")
        assert payment_method_cash.max_modifier == Decimal("1.0000")
        assert payment_method_cash.points_modifier == Decimal("0.0500")
        assert payment_method_cash.additional_item_schema is None
        assert payment_method_cash.created_at is not None
        assert payment_method_cash.updated_at is not None

    def test_create_payment_method_with_schema(self, payment_method_credit_card):
        """Test creating a payment method with additional data schema."""
        # Verify payment method with schema
        assert payment_method_credit_card.id is not None
        assert payment_method_credit_card.name == "VISA_TEST"
        assert payment_method_credit_card.is_active is True
        assert payment_method_credit_card.min_modifier == Decimal("0.9500")
        assert payment_method_credit_card.max_modifier == Decimal("1.0000")
        assert payment_method_credit_card.points_modifier == Decimal("0.0300")
        assert payment_method_credit_card.additional_item_schema is not None
        assert (
            "last4" in payment_method_credit_card.additional_item_schema["properties"]
        )

    def test_create_inactive_payment_method(self, payment_method_inactive):
        """Test creating an inactive payment method."""
        assert payment_method_inactive.id is not None
        assert payment_method_inactive.is_active is False

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
            name="PAYPAL_TEST",
            min_modifier=Decimal("1.0000"),
            max_modifier=Decimal("1.0000"),
            points_modifier=Decimal("1.0000"),
        )
        db_session.add(pm)
        db_session.commit()
        db_session.refresh(pm)

        assert pm.is_active is True

    def test_update_payment_method(self, db_session, payment_method_cash):
        """Test updating payment method fields."""
        original_created_at = payment_method_cash.created_at

        # Update fields
        payment_method_cash.is_active = False
        payment_method_cash.min_modifier = Decimal("0.8500")
        payment_method_cash.max_modifier = Decimal("1.1500")
        db_session.commit()
        db_session.refresh(payment_method_cash)

        assert payment_method_cash.is_active is False
        assert payment_method_cash.min_modifier == Decimal("0.8500")
        assert payment_method_cash.max_modifier == Decimal("1.1500")
        assert payment_method_cash.created_at == original_created_at
        assert payment_method_cash.updated_at >= payment_method_cash.created_at

    def test_all_default_payment_methods_created(self, all_default_payment_methods):
        """Test that all default payment methods are created correctly."""
        assert len(all_default_payment_methods) == 12

        # Verify specific payment methods exist
        payment_method_names = [pm.name for pm in all_default_payment_methods]
        assert "CASH" in payment_method_names
        assert "VISA" in payment_method_names
        assert "MASTERCARD" in payment_method_names
        assert "BANK_TRANSFER" in payment_method_names
        assert "POINTS" in payment_method_names

        # Verify one with schema
        visa = next(pm for pm in all_default_payment_methods if pm.name == "VISA")
        assert visa.additional_item_schema is not None
        assert "last4" in visa.additional_item_schema["properties"]
