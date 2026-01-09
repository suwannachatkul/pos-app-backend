import strawberry

from api.services.payment import PaymentMethodService

from .dto.outputs import PaymentMethod


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
