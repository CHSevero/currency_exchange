import logging
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.models import Transaction
from app.services.rate_service import RateService
from app.core.exceptions import InvalidAmountException

logger = logging.getLogger(__name__)

class ConversionService:
    """Service to handle currency conversion operations"""

    def __init__(self, rate_service: RateService):
        self.rate_service = rate_service

    async def convert_currency(
        self,
        user_id: str,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        db: Session
    ) -> dict:
        """
        Convert currency and save transaction.

        Args:
            user_id: User identifier
            from_currency: Source currency code
            to_currency: Target currency code
            amount: Amount to convert
            db: Database session

        Returns:
            dict: Conversion result with transaction details

        Raises:
            InvalidAmountException: If amount is not positive
            InvalidCurrencyException: If currency is not supported
            ExternalAPIException: If exchange rate API call fails
        """
        # Validate amount
        if amount <= Decimal('0'):
            raise InvalidAmountException(amount)

        # Get exchange rate
        exchange_rate = await self.rate_service.get_exchange_rate(
            from_currency=from_currency,
            to_currency=to_currency,
            db=db
        )
        
        # Ensure exchange_rate is also a Decimal
        if not isinstance(exchange_rate, Decimal):
            exchange_rate = Decimal(str(exchange_rate))

        # Calculate converted amount
        converted_amount = amount * exchange_rate

        # Save transaction
        transaction = Transaction(
            user_id=user_id,
            source_currency=from_currency,
            target_currency=to_currency,
            source_amount=amount,
            target_amount=converted_amount,
            exchange_rate=exchange_rate,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Return conversion result
        return {
            "transaction_id": transaction.id,
            "user_id": user_id,
            "from": {
                "currency": from_currency,
                "amount": amount
            },
            "to": {
                "currency": to_currency,
                "amount": converted_amount
            },
            "rate": exchange_rate,
            "timestamp": transaction.timestamp
        }