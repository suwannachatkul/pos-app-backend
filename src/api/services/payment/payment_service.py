from sqlalchemy.ext.asyncio import AsyncSession

from api.graphql.payment.dto.inputs import ProcessPaymentInput
from api.graphql.payment.dto.outputs import PaymentResult
from api.models.payment.transaction import Transaction

from .payment_method_service import PaymentMethodService


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_method_service = PaymentMethodService(db)

    async def process_payment(self, input: ProcessPaymentInput) -> PaymentResult:
        # Get payment method configuration from database
        method = await self.payment_method_service.get_method(input.payment_method)

        # Validate price modifier
        self.payment_method_service.validate_price_modifier(
            method, input.price_modifier
        )

        # Validate additional data
        additional_item = self.payment_method_service.validate_additional_data(
            method, input.additional_item.to_dict()
        )

        # Calculate final price and points
        final_price = self.payment_method_service.calculate_final_price(
            input.price, input.price_modifier
        )
        points = self.payment_method_service.calculate_points(method, input.price)

        # Create transaction record
        transaction = Transaction(
            customer_id=input.customer_id,
            price=input.price,
            price_modifier=input.price_modifier,
            final_price=final_price,
            points=points,
            payment_method=input.payment_method,
            additional_item=additional_item,
            datetime=input.datetime,
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        return PaymentResult(final_price=final_price, points=points)
