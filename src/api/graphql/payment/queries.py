from datetime import datetime

import strawberry

from api.services.payment import PaymentMethodService, ReportingService

from .dto.outputs import PaymentMethod, SalesReport


@strawberry.type
class PaymentQueries:
    @strawberry.field
    async def available_payment_methods(
        self, info: strawberry.Info
    ) -> list[PaymentMethod]:
        """List all active payment methods from database with full details."""
        db = info.context["db"]
        service = PaymentMethodService(db)
        methods = await service.get_all_active_methods()
        return [
            PaymentMethod(
                id=method.id,
                name=method.name,
                is_active=method.is_active,
                min_modifier=float(method.min_modifier),
                max_modifier=float(method.max_modifier),
                points_modifier=float(method.points_modifier),
                additional_item_schema=method.additional_item_schema,
            )
            for method in methods
        ]

    @strawberry.field
    async def sales_report(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        info: strawberry.Info,
        period: str = "hour",
    ) -> list[SalesReport]:
        """Get sales report broken down by hour."""
        db = info.context["db"]
        service = ReportingService(db)
        return await service.get_sales_report(start_datetime, end_datetime, period)
