import pytest


class TestAvailablePaymentMethods:
    """Test available_payment_methods GraphQL query."""

    @pytest.mark.asyncio
    async def test_returns_all_active_methods_with_full_details(
        self, client, all_default_payment_methods
    ):
        """Test that query returns all active payment methods with complete information."""
        query = """
        query {
          availablePaymentMethods {
            id
            name
            isActive
            minModifier
            maxModifier
            pointsModifier
            additionalItemSchema
          }
        }
        """

        response = client.post("/graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None

        payment_methods = data["data"]["availablePaymentMethods"]

        # Verify response structure
        assert isinstance(payment_methods, list)
        assert len(payment_methods) > 0

        # Verify each method has required fields
        for method in payment_methods:
            assert "id" in method
            assert "name" in method
            assert "isActive" in method
            assert "minModifier" in method
            assert "maxModifier" in method
            assert "pointsModifier" in method
            assert method["isActive"] is True

        # Verify count matches active methods
        active_methods = [pm for pm in all_default_payment_methods if pm.is_active]
        assert len(payment_methods) == len(active_methods)

        # Verify expected names are present
        expected_names = {pm.name for pm in active_methods}
        actual_names = {method["name"] for method in payment_methods}
        assert actual_names == expected_names

    @pytest.mark.asyncio
    async def test_excludes_inactive_methods(
        self, client, all_default_payment_methods, payment_method_inactive
    ):
        """Test that inactive payment methods are not returned."""
        query = """
        query {
          availablePaymentMethods {
            name
            isActive
          }
        }
        """

        response = client.post("/graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        payment_methods = data["data"]["availablePaymentMethods"]

        # Verify inactive method is not in results
        method_names = [method["name"] for method in payment_methods]
        assert payment_method_inactive.name not in method_names

        # Verify all returned methods are active
        for method in payment_methods:
            assert method["isActive"] is True

    @pytest.mark.asyncio
    async def test_returns_correct_modifier_values(
        self, client, all_default_payment_methods
    ):
        """Test that modifier values are returned correctly as floats."""
        query = """
        query {
          availablePaymentMethods {
            name
            minModifier
            maxModifier
            pointsModifier
          }
        }
        """

        response = client.post("/graphql", json={"query": query})

        assert response.status_code == 200
        data = response.json()
        payment_methods = data["data"]["availablePaymentMethods"]

        # Verify modifiers are numeric and within expected ranges
        for method in payment_methods:
            assert isinstance(method["minModifier"], float)
            assert isinstance(method["maxModifier"], float)
            assert isinstance(method["pointsModifier"], float)
            assert 0 <= method["minModifier"] <= method["maxModifier"]
            assert method["pointsModifier"] >= 0
