"""Integration tests for GraphQL payment mutations."""

from datetime import UTC, datetime

import pytest


class TestProcessPayment:
    """Test process_payment GraphQL mutation."""

    @pytest.mark.asyncio
    async def test_process_payment_success_cash(
        self, client, all_default_payment_methods
    ):
        """Test successful payment processing with CASH payment method."""
        mutation = """
        mutation ProcessPayment($input: ProcessPaymentInput!) {
          processPayment(input: $input) {
            ... on PaymentResult {
              finalPrice
              points
            }
            ... on GraphQLError {
              code
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "customerId": "1001",
                "price": 1000.0,
                "priceModifier": 0.95,
                "paymentMethod": "CASH",
                "datetime": datetime.now(UTC).isoformat(),
                "additionalItem": {},
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["processPayment"]
        assert "finalPrice" in result
        assert "points" in result
        assert result["finalPrice"] == 950.0  # 1000 * 0.95
        assert result["points"] == 50  # 1000 * 0.05

    @pytest.mark.asyncio
    async def test_process_payment_success_with_additional_data(
        self, client, all_default_payment_methods
    ):
        """Test payment processing with additional item data (credit card)."""
        mutation = """
        mutation ProcessPayment($input: ProcessPaymentInput!) {
          processPayment(input: $input) {
            ... on PaymentResult {
              finalPrice
              points
            }
            ... on GraphQLError {
              code
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "customerId": "1002",
                "price": 2000.0,
                "priceModifier": 1.0,
                "paymentMethod": "VISA",
                "datetime": datetime.now(UTC).isoformat(),
                "additionalItem": {"last4": "1234"},
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["processPayment"]
        assert result["finalPrice"] == 2000.0  # 2000 * 1.0
        assert result["points"] == 60  # 2000 * 0.03

    @pytest.mark.asyncio
    async def test_process_payment_invalid_modifier(
        self, client, all_default_payment_methods
    ):
        """Test payment fails with price modifier out of valid range."""
        mutation = """
        mutation ProcessPayment($input: ProcessPaymentInput!) {
          processPayment(input: $input) {
            ... on PaymentResult {
              finalPrice
              points
            }
            ... on GraphQLError {
              code
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "customerId": "1003",
                "price": 1000.0,
                "priceModifier": 1.5,  # Out of range (0.9-1.0)
                "paymentMethod": "CASH",
                "datetime": datetime.now(UTC).isoformat(),
                "additionalItem": {},
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()

        result = data["data"]["processPayment"]
        assert "code" in result
        assert "message" in result
        assert result["code"] == "INVALID_INPUT"
        assert "out of range" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_process_payment_unknown_payment_method(self, client):
        """Test payment fails with unknown payment method."""
        mutation = """
        mutation ProcessPayment($input: ProcessPaymentInput!) {
          processPayment(input: $input) {
            ... on PaymentResult {
              finalPrice
              points
            }
            ... on GraphQLError {
              code
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "customerId": "1004",
                "price": 1000.0,
                "priceModifier": 1.0,
                "paymentMethod": "UNKNOWN_METHOD",
                "datetime": datetime.now(UTC).isoformat(),
                "additionalItem": {},
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()

        result = data["data"]["processPayment"]
        assert "code" in result
        assert "message" in result
        assert result["code"] == "INVALID_INPUT"
        assert (
            "unknown" in result["message"].lower()
            or "inactive" in result["message"].lower()
        )

    @pytest.mark.asyncio
    async def test_process_payment_inactive_payment_method(
        self, client, payment_method_inactive
    ):
        """Test payment fails with inactive payment method."""
        mutation = """
        mutation ProcessPayment($input: ProcessPaymentInput!) {
          processPayment(input: $input) {
            ... on PaymentResult {
              finalPrice
              points
            }
            ... on GraphQLError {
              code
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "customerId": "1005",
                "price": 1000.0,
                "priceModifier": 1.0,
                "paymentMethod": payment_method_inactive.name,
                "datetime": datetime.now(UTC).isoformat(),
                "additionalItem": {},
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()

        result = data["data"]["processPayment"]
        assert "code" in result
        assert "message" in result
        assert result["code"] == "INVALID_INPUT"
        assert "inactive" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_process_payment_missing_required_additional_data(
        self, client, payment_method_credit_card
    ):
        """Test payment fails when required additional data is missing."""
        mutation = """
        mutation ProcessPayment($input: ProcessPaymentInput!) {
          processPayment(input: $input) {
            ... on PaymentResult {
              finalPrice
              points
            }
            ... on GraphQLError {
              code
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "customerId": "1006",
                "price": 1000.0,
                "priceModifier": 1.0,
                "paymentMethod": payment_method_credit_card.name,
                "datetime": datetime.now(UTC).isoformat(),
                # Missing additionalItem with last4
            }
        }

        response = client.post(
            "/graphql", json={"query": mutation, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()

        result = data["data"]["processPayment"]
        assert "code" in result
        assert "message" in result
        assert result["code"] == "INVALID_INPUT"
