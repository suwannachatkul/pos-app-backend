"""Unit tests for Transaction model."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select

from api.models.payment.transaction import Transaction


class TestTransactionModel:
    """Test suite for Transaction model."""

    def test_create_basic_transaction(self, transaction_basic_cash):
        """Test creating a basic transaction with required fields."""
        # Verify basic transaction using fixture
        assert transaction_basic_cash.id is not None
        assert transaction_basic_cash.customer_id == 1001
        assert transaction_basic_cash.price == Decimal("100.00")
        assert transaction_basic_cash.price_modifier == Decimal("0.9500")
        assert transaction_basic_cash.final_price == Decimal("95.00")
        assert transaction_basic_cash.points == 5
        assert transaction_basic_cash.additional_item is None
        assert transaction_basic_cash.created_at is not None
        assert transaction_basic_cash.updated_at is not None

    def test_create_transaction_with_additional_item(self, transaction_credit_card):
        """Test creating a transaction with additional payment data."""
        # Verify transaction with additional data using fixture
        assert transaction_credit_card.additional_item is not None
        assert transaction_credit_card.additional_item["last4"] == "1234"
        assert transaction_credit_card.additional_item["card_type"] == "VISA"
        assert transaction_credit_card.customer_id == 1002
        assert transaction_credit_card.price == Decimal("250.50")

    def test_transaction_payment_method_relationship(
        self, transaction_bank_transfer, payment_method_bank_transfer
    ):
        """Test the relationship between Transaction and PaymentMethod."""
        # Access relationship
        assert transaction_bank_transfer.payment_method_detail is not None
        assert (
            transaction_bank_transfer.payment_method_detail.name
            == payment_method_bank_transfer.name
        )
        assert (
            transaction_bank_transfer.payment_method_detail.id
            == payment_method_bank_transfer.id
        )

    def test_transaction_with_null_payment_method(self, transaction_no_payment_method):
        """Test transaction with null payment method (deleted payment method scenario)."""
        assert transaction_no_payment_method.payment_method is None
        assert transaction_no_payment_method.payment_method_detail is None
        assert transaction_no_payment_method.customer_id == 1004

    def test_multiple_transactions_same_customer(
        self, multiple_transactions_same_customer
    ):
        """Test multiple transactions for the same customer."""
        # Verify both transactions exist with same customer_id
        assert len(multiple_transactions_same_customer) == 2
        for t in multiple_transactions_same_customer:
            assert t.customer_id == 1005
            assert t.id is not None

    def test_transaction_price_precision(self, transaction_basic_cash):
        """Test that price fields maintain decimal precision."""
        # Verify precision is maintained
        assert transaction_basic_cash.price == Decimal("100.00")
        assert transaction_basic_cash.price_modifier == Decimal("0.9500")
        assert transaction_basic_cash.final_price == Decimal("95.00")

    def test_transaction_customer_id_index(
        self, db_session, all_default_payment_methods
    ):
        """Test that customer_id index allows efficient querying."""
        customer_id = 9999
        payment_method = next(
            pm for pm in all_default_payment_methods if pm.name == "CASH"
        )

        # Create multiple transactions with same customer_id
        for i in range(5):
            transaction = Transaction(
                customer_id=customer_id,
                price=Decimal("100.00"),
                price_modifier=Decimal("1.0000"),
                final_price=Decimal("100.00"),
                points=5,
                payment_method=payment_method.name,
                datetime=datetime.now(UTC),
            )
            db_session.add(transaction)

        db_session.commit()

        # Query by customer_id (indexed field)
        stmt = select(Transaction).where(Transaction.customer_id == customer_id)
        results = db_session.execute(stmt).scalars().all()

        assert len(results) == 5
        for result in results:
            assert result.customer_id == customer_id

    def test_transaction_with_zero_points(self, transaction_bank_transfer):
        """Test transaction with zero points (e.g., bank transfer)."""
        assert transaction_bank_transfer.points == 0
        assert transaction_bank_transfer.price == Decimal("1000.00")
        assert transaction_bank_transfer.final_price == Decimal("1000.00")

    def test_transaction_datetime_index(self, db_session, payment_method_cash):
        """Test that transaction_datetime is indexed for time-based queries."""
        # Create transactions with different timestamps
        for i in range(3):
            transaction = Transaction(
                customer_id=2000 + i,
                price=Decimal("100.00"),
                price_modifier=Decimal("1.0000"),
                final_price=Decimal("100.00"),
                points=5,
                payment_method=payment_method_cash.name,
                datetime=datetime(2025, 1, i + 1, 12, 0, 0, tzinfo=UTC),
            )
            db_session.add(transaction)

        db_session.commit()

        # Query by datetime range
        stmt = select(Transaction).where(
            Transaction.datetime >= datetime(2025, 1, 2, 0, 0, 0, tzinfo=UTC)
        )
        results = db_session.execute(stmt).scalars().all()

        assert len(results) >= 2

    def test_update_transaction(self, db_session, transaction_basic_cash):
        """Test updating transaction fields."""
        original_created_at = transaction_basic_cash.created_at

        # Update transaction
        transaction_basic_cash.points = 10
        transaction_basic_cash.additional_item = {"note": "Updated transaction"}
        db_session.commit()
        db_session.refresh(transaction_basic_cash)

        assert transaction_basic_cash.points == 10
        assert transaction_basic_cash.additional_item["note"] == "Updated transaction"
        assert transaction_basic_cash.created_at == original_created_at
        assert transaction_basic_cash.updated_at >= transaction_basic_cash.created_at

    def test_transaction_cascade_on_payment_method_deletion(
        self, db_session, payment_method_cash
    ):
        """Test that transaction payment_method is set to NULL when payment method is deleted (SET NULL)."""
        transaction = Transaction(
            customer_id=1009,
            price=Decimal("100.00"),
            price_modifier=Decimal("1.0000"),
            final_price=Decimal("100.00"),
            points=5,
            payment_method=payment_method_cash.name,
            datetime=datetime.now(UTC),
        )
        db_session.add(transaction)
        db_session.commit()
        transaction_id = transaction.id

        # Delete payment method
        db_session.delete(payment_method_cash)
        db_session.commit()

        # Verify transaction still exists but payment_method is NULL
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = db_session.execute(stmt).scalar_one()

        assert result.payment_method is None
        assert result.customer_id == 1009
