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

        price = 1000.0
        price_modifier = 0.95
        payment_method_name = "CASH"

        variables = {
            "input": {
                "customerId": "1001",
                "price": price,
                "priceModifier": price_modifier,
                "paymentMethod": payment_method_name,
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

        # Calculate expected values from input
        expected_final_price = price * price_modifier
        assert result["finalPrice"] == expected_final_price

        # Get payment method to calculate expected points
        cash_method = next(
            (
                pm
                for pm in all_default_payment_methods
                if pm.name == payment_method_name
            ),
            None,
        )
        assert cash_method is not None
        expected_points = int(price * float(cash_method.points_modifier))
        assert result["points"] == expected_points

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

        price = 2000.0
        price_modifier = 1.0
        payment_method_name = "VISA"

        variables = {
            "input": {
                "customerId": "1002",
                "price": price,
                "priceModifier": price_modifier,
                "paymentMethod": payment_method_name,
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

        # Calculate expected values from input
        expected_final_price = price * price_modifier
        assert result["finalPrice"] == expected_final_price

        # Get payment method to calculate expected points
        visa_method = next(
            (
                pm
                for pm in all_default_payment_methods
                if pm.name == payment_method_name
            ),
            None,
        )
        assert visa_method is not None
        expected_points = int(price * float(visa_method.points_modifier))
        assert result["points"] == expected_points

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

        payment_method_name = "CASH"
        # Get payment method to find valid range
        cash_method = next(
            (
                pm
                for pm in all_default_payment_methods
                if pm.name == payment_method_name
            ),
            None,
        )
        assert cash_method is not None

        # Use modifier outside the valid range
        invalid_modifier = float(cash_method.max_modifier) + 0.5

        variables = {
            "input": {
                "customerId": "1003",
                "price": 1000.0,
                "priceModifier": invalid_modifier,
                "paymentMethod": payment_method_name,
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
