"""Integration tests for GraphQL sales report query."""

from datetime import UTC, datetime

import pytest


class TestSalesReport:
    """Test sales_report GraphQL query."""

    @pytest.mark.asyncio
    async def test_sales_report_basic_functionality(self, client):
        """Test sales report query works and returns correct structure."""
        query = """
        query SalesReport($startDatetime: DateTime!, $endDatetime: DateTime!, $period: String!) {
          salesReport(startDatetime: $startDatetime, endDatetime: $endDatetime, period: $period) {
            datetime
            sales
            points
          }
        }
        """

        start_dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
        end_dt = datetime(2025, 1, 2, 23, 59, 59, tzinfo=UTC)
        period = "day"

        variables = {
            "startDatetime": start_dt.isoformat(),
            "endDatetime": end_dt.isoformat(),
            "period": period,
        }

        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None

        reports = data["data"]["salesReport"]

        # Should return a list with proper structure
        assert isinstance(reports, list)

        # Calculate expected number of days (inclusive)
        expected_days = (end_dt.date() - start_dt.date()).days + 1
        assert len(reports) >= expected_days

        # Verify each report has required fields
        for report in reports:
            assert "datetime" in report
            assert "sales" in report
            assert "points" in report
            assert isinstance(report["sales"], int | float)
            assert isinstance(report["points"], int)
            assert report["sales"] >= 0
            assert report["points"] >= 0

    @pytest.mark.asyncio
    async def test_sales_report_empty_period(self, client):
        """Test sales report returns empty results for period with no transactions."""
        query = """
        query SalesReport($startDatetime: DateTime!, $endDatetime: DateTime!, $period: String!) {
          salesReport(startDatetime: $startDatetime, endDatetime: $endDatetime, period: $period) {
            datetime
            sales
            points
          }
        }
        """

        # Query for a future date range with no transactions
        start_dt = datetime(2030, 1, 1, 0, 0, 0, tzinfo=UTC)
        end_dt = datetime(2030, 1, 1, 23, 59, 59, tzinfo=UTC)
        period = "day"

        variables = {
            "startDatetime": start_dt.isoformat(),
            "endDatetime": end_dt.isoformat(),
            "period": period,
        }

        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None

        reports = data["data"]["salesReport"]

        # Should have reports with zero values (empty periods included)
        assert isinstance(reports, list)

        # Calculate expected number of days
        expected_days = (end_dt.date() - start_dt.date()).days + 1
        assert len(reports) == expected_days

        for report in reports:
            assert report["sales"] == 0.0
            assert report["points"] == 0

    @pytest.mark.asyncio
    async def test_sales_report_hourly_period(self, client):
        """Test sales report with hourly period parameter."""
        query = """
        query SalesReport($startDatetime: DateTime!, $endDatetime: DateTime!, $period: String!) {
          salesReport(startDatetime: $startDatetime, endDatetime: $endDatetime, period: $period) {
            datetime
            sales
            points
          }
        }
        """

        # Query for hourly breakdown
        start_dt = datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC)
        end_dt = datetime(2025, 1, 15, 13, 59, 59, tzinfo=UTC)
        period = "hour"

        variables = {
            "startDatetime": start_dt.isoformat(),
            "endDatetime": end_dt.isoformat(),
            "period": period,
        }

        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None

        reports = data["data"]["salesReport"]
        assert isinstance(reports, list)

        # Calculate expected number of hours (inclusive)
        time_diff = end_dt - start_dt
        expected_hours = int(time_diff.total_seconds() // 3600) + 1
        assert len(reports) >= expected_hours

        # Verify structure and values
        for report in reports:
            assert "datetime" in report
            assert "sales" in report
            assert "points" in report
            assert report["sales"] >= 0
            assert report["points"] >= 0

    @pytest.mark.asyncio
    async def test_sales_report_response_structure(self, client):
        """Test that sales report response has correct structure."""
        query = """
        query SalesReport($startDatetime: DateTime!, $endDatetime: DateTime!) {
          salesReport(startDatetime: $startDatetime, endDatetime: $endDatetime) {
            datetime
            sales
            points
          }
        }
        """

        start_dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
        end_dt = datetime(2025, 1, 2, 0, 0, 0, tzinfo=UTC)

        variables = {
            "startDatetime": start_dt.isoformat(),
            "endDatetime": end_dt.isoformat(),
        }

        response = client.post(
            "/graphql", json={"query": query, "variables": variables}
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert "data" in data
        assert "salesReport" in data["data"]

        reports = data["data"]["salesReport"]
        assert isinstance(reports, list)
        assert len(reports) > 0

        # Verify structure of each report
        for report in reports:
            assert "datetime" in report
            assert "sales" in report
            assert "points" in report
            assert isinstance(report["sales"], int | float)
            assert isinstance(report["points"], int)
