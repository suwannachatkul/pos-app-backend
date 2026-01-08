"""Payment method fixtures for testing."""

from decimal import Decimal

import pytest

from api.models.payment.payment_method import PaymentMethod
from config.initializers.default_payment_method import DEFAULT_PAYMENT_METHODS


@pytest.fixture
def payment_method_cash(db_session):
    """Create a basic cash payment method."""
    pm = PaymentMethod(
        name="CASH_TEST",
        is_active=True,
        min_modifier=Decimal("0.9000"),
        max_modifier=Decimal("1.0000"),
        points_modifier=Decimal("0.0500"),
    )
    db_session.add(pm)
    db_session.commit()
    db_session.refresh(pm)
    return pm


@pytest.fixture
def payment_method_credit_card(db_session):
    """Create a credit card payment method with additional data schema."""
    schema = {
        "type": "object",
        "properties": {
            "last4": {
                "type": "string",
                "pattern": "^[0-9]{4}$",
                "description": "Last 4 digits of card",
            }
        },
        "required": ["last4"],
    }
    pm = PaymentMethod(
        name="VISA_TEST",
        is_active=True,
        min_modifier=Decimal("0.9500"),
        max_modifier=Decimal("1.0000"),
        points_modifier=Decimal("0.0300"),
        additional_item_schema=schema,
    )
    db_session.add(pm)
    db_session.commit()
    db_session.refresh(pm)
    return pm


@pytest.fixture
def payment_method_inactive(db_session):
    """Create an inactive payment method."""
    pm = PaymentMethod(
        name="INACTIVE_TEST",
        is_active=False,
        min_modifier=Decimal("1.0000"),
        max_modifier=Decimal("1.0000"),
        points_modifier=Decimal("0.0000"),
    )
    db_session.add(pm)
    db_session.commit()
    db_session.refresh(pm)
    return pm


@pytest.fixture
def payment_method_bank_transfer(db_session):
    """Create a bank transfer payment method with complex schema."""
    schema = {
        "type": "object",
        "properties": {
            "bank": {"type": "string", "description": "Bank name"},
            "account_number": {
                "type": "string",
                "description": "Account number",
            },
        },
        "required": ["bank", "account_number"],
    }
    pm = PaymentMethod(
        name="BANK_TRANSFER_TEST",
        is_active=True,
        min_modifier=Decimal("1.0000"),
        max_modifier=Decimal("1.0000"),
        points_modifier=Decimal("0.0000"),
        additional_item_schema=schema,
    )
    db_session.add(pm)
    db_session.commit()
    db_session.refresh(pm)
    return pm


@pytest.fixture
def all_default_payment_methods(db_session):
    """Create all default payment methods as defined in initializer."""
    payment_methods = []
    # TODO: refactor this if DEFAULT_PAYMENT_METHODS move out of initializer
    for pm_data in DEFAULT_PAYMENT_METHODS:
        # Convert float modifiers to Decimal for precision
        pm = PaymentMethod(
            name=pm_data["name"],
            is_active=pm_data.get("is_active", True),
            min_modifier=Decimal(str(pm_data["min_modifier"])),
            max_modifier=Decimal(str(pm_data["max_modifier"])),
            points_modifier=Decimal(str(pm_data["points_modifier"])),
            additional_item_schema=pm_data.get("additional_item_schema"),
        )
        db_session.add(pm)
        payment_methods.append(pm)

    db_session.commit()
    for pm in payment_methods:
        db_session.refresh(pm)
    return payment_methods
