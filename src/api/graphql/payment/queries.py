from datetime import datetime

import strawberry

from api.graphql.common_types import GraphQLError
from api.services.payment import PaymentMethodService, ReportingService, ReportPeriod
from shared.logging import logger

from .dto.outputs import (
    PaymentMethod,
    PaymentMethodsResult,
    SalesReportResult,
)


ReportPeriodEnum = strawberry.enum(ReportPeriod)


@strawberry.type
class PaymentQueries:
    @strawberry.field
    async def available_payment_methods(
        self, info: strawberry.Info
    ) -> PaymentMethodsResult | GraphQLError:
        """List all active payment methods from database with full details."""
        try:
            db = info.context["db"]
            service = PaymentMethodService(db)
            methods = await service.get_all_active_methods()
            return PaymentMethodsResult(
                methods=[
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
            )
        except Exception as e:
            logger.exception(
                "Unexpected error in available_payment_methods", exc_info=e
            )
            # TODO: centralize error handling codes/messages
            return GraphQLError(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred while fetching payment methods",
                details=str(e),
            )

    @strawberry.field
    async def sales_report(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        info: strawberry.Info,
        period: ReportPeriod = ReportPeriod.HOUR,
    ) -> SalesReportResult | GraphQLError:
        """Get sales report broken down by hour."""
        try:
            db = info.context["db"]
            service = ReportingService(db)
            reports = await service.get_sales_report(
                start_datetime, end_datetime, period
            )
            return SalesReportResult(reports=reports)
        except ValueError as e:
            logger.exception("ValueError in sales_report", exc_info=e)
            return GraphQLError(code="INVALID_INPUT", message=str(e))
        except Exception as e:
            logger.exception("Unexpected error in sales_report", exc_info=e)
            # TODO: centralize error handling codes/messages
            return GraphQLError(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred while generating sales report",
                details=str(e),
            )
