import strawberry

from api.graphql.common_types import GraphQLError
from api.services.payment.payment_service import PaymentService
from shared.logging import logger

from .dto.inputs import ProcessPaymentInput
from .dto.outputs import PaymentResult


@strawberry.type
class PaymentMutations:
    @strawberry.mutation
    async def process_payment(
        self, input: ProcessPaymentInput, info: strawberry.Info
    ) -> PaymentResult | GraphQLError:
        """Process a payment transaction."""
        try:
            db = info.context["db"]
            service = PaymentService(db)
            result = await service.process_payment(input)
            return result
        except ValueError as e:
            logger.exception("ValueError in process_payment", exc_info=e)
            # TODO: centralize error handling codes/messages
            return GraphQLError(code="INVALID_INPUT", message=str(e))
        except Exception as e:
            logger.exception("Unexpected error in process_payment", exc_info=e)
            # TODO: centralize error handling codes/messages
            return GraphQLError(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details=str(e),
            )
