from datetime import datetime, timedelta
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.payment.transaction import Transaction

from ...graphql.payment.dto.outputs import SalesReport


class ReportPeriod(StrEnum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class ReportingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_period_range(
        self, start: datetime, end: datetime, period: ReportPeriod
    ) -> list[datetime]:
        """Generate all periods between start and end."""
        start = start.replace(tzinfo=None) if start.tzinfo else start
        end = end.replace(tzinfo=None) if end.tzinfo else end
        periods = []
        current = start

        # Truncate start to match database truncation
        if period == ReportPeriod.HOUR:
            current = current.replace(minute=0, second=0, microsecond=0)
            delta = timedelta(hours=1)
        elif period == ReportPeriod.DAY:
            current = current.replace(hour=0, minute=0, second=0, microsecond=0)
            delta = timedelta(days=1)
        elif period == ReportPeriod.WEEK:
            # Truncate to start of week (Monday)
            current = current.replace(hour=0, minute=0, second=0, microsecond=0)
            current = current - timedelta(days=current.weekday())
            delta = timedelta(weeks=1)
        elif period == ReportPeriod.MONTH:
            current = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            delta = timedelta(days=30)

        while current <= end:
            periods.append(current)
            if period == ReportPeriod.MONTH:
                # More accurate month increment
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            else:
                current += delta

        return periods

    async def get_sales_report(
        self,
        start: datetime,
        end: datetime,
        period: ReportPeriod = ReportPeriod.HOUR,
        include_empty_periods: bool = True,
    ) -> list[SalesReport]:
        """Get sales broken down by the given `period` using PostgreSQL aggregation."""
        truncated = func.date_trunc(period, Transaction.datetime).label("period")

        query = (
            select(
                truncated,
                func.sum(Transaction.final_price).label("total_sales"),
                func.sum(Transaction.points).label("total_points"),
            )
            .where(Transaction.datetime.between(start, end))
            .group_by(truncated)
            .order_by(truncated)
        )

        result = await self.db.execute(query)
        rows = result.fetchall()

        reports = [
            SalesReport(
                datetime=row.period,
                sales=float(row.total_sales or 0),
                points=int(row.total_points or 0),
            )
            for row in rows
        ]

        if include_empty_periods:
            # Create a map of existing periods
            existing_periods = {report.datetime: report for report in reports}

            # Generate all periods and fill gaps
            all_periods = self._generate_period_range(start, end, period)
            reports = [
                existing_periods.get(
                    period,
                    SalesReport(datetime=period, sales=0.0, points=0),
                )
                for period in all_periods
            ]

        return reports
