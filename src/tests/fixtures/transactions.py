"""Transaction fixtures for testing."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from api.models.payment.transaction import Transaction


@pytest.fixture
def transaction_basic_cash(db_session, payment_method_cash):
    """Create a basic cash transaction."""
    transaction = Transaction(
        customer_id=1001,
        price=Decimal("100.00"),
        price_modifier=Decimal("0.9500"),
        final_price=Decimal("95.00"),
        points=5,
        payment_method=payment_method_cash.name,
        transaction_datetime=datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC),
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


@pytest.fixture
def transaction_credit_card(db_session, payment_method_credit_card):
    """Create a credit card transaction with additional data."""
    transaction = Transaction(
        customer_id=1002,
        price=Decimal("250.50"),
        price_modifier=Decimal("0.9800"),
        final_price=Decimal("245.49"),
        points=7,
        payment_method=payment_method_credit_card.name,
        additional_data={"last4": "1234", "card_type": "VISA"},
        transaction_datetime=datetime(2025, 1, 16, 14, 30, 0, tzinfo=UTC),
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


@pytest.fixture
def transaction_bank_transfer(db_session, payment_method_bank_transfer):
    """Create a bank transfer transaction with zero points."""
    transaction = Transaction(
        customer_id=1003,
        price=Decimal("1000.00"),
        price_modifier=Decimal("1.0000"),
        final_price=Decimal("1000.00"),
        points=0,
        payment_method=payment_method_bank_transfer.name,
        additional_data={"bank": "Test Bank", "account_number": "123456789"},
        transaction_datetime=datetime(2025, 1, 17, 9, 15, 0, tzinfo=UTC),
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


@pytest.fixture
def transaction_no_payment_method(db_session):
    """Create a transaction without payment method (orphaned transaction)."""
    transaction = Transaction(
        customer_id=1004,
        price=Decimal("50.00"),
        price_modifier=Decimal("1.0000"),
        final_price=Decimal("50.00"),
        points=1,
        payment_method=None,
        transaction_datetime=datetime(2025, 1, 18, 16, 45, 0, tzinfo=UTC),
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


@pytest.fixture
def multiple_transactions_same_customer(
    db_session, payment_method_cash, payment_method_credit_card
):
    """Create multiple transactions for the same customer."""
    customer_id = 1005
    base_time = datetime(2025, 1, 19, 12, 0, 0, tzinfo=UTC)

    transactions = [
        Transaction(
            customer_id=customer_id,
            price=Decimal("100.00"),
            price_modifier=Decimal("0.9500"),
            final_price=Decimal("95.00"),
            points=5,
            payment_method=payment_method_cash.name,
            transaction_datetime=base_time,
        ),
        Transaction(
            customer_id=customer_id,
            price=Decimal("200.00"),
            price_modifier=Decimal("0.9800"),
            final_price=Decimal("196.00"),
            points=6,
            payment_method=payment_method_credit_card.name,
            transaction_datetime=base_time,
        ),
    ]
    db_session.add_all(transactions)
    db_session.commit()

    for t in transactions:
        db_session.refresh(t)
    return transactions
