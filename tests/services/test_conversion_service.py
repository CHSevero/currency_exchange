import pytest
from decimal import Decimal
from datetime import datetime
import respx
from httpx import Response

from app.services.conversion_service import ConversionService
from app.services.rate_service import RateService
from app.core.exceptions import InvalidAmountException
from app.models.models import Transaction
from app.core.config import settings

@pytest.fixture
def conversion_service():
    rate_service = RateService()
    return ConversionService(rate_service)

@pytest.mark.asyncio
async def test_convert_currency_success(conversion_service, db_session, mock_rates_response, test_data):
    """Test successful currency conversion."""
    with respx.mock as respx_mock:
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(200, json=mock_rates_response)
        )
        
        result = await conversion_service.convert_currency(
            user_id=test_data["user_id"],
            from_currency=test_data["from_currency"],
            to_currency=test_data["to_currency"],
            amount=Decimal(test_data["amount"]),
            db=db_session
        )
        
        assert result["user_id"] == test_data["user_id"]
        assert result["from"]["currency"] == test_data["from_currency"]
        assert result["from"]["amount"] == Decimal(test_data["amount"])
        assert result["to"]["currency"] == test_data["to_currency"]
        assert isinstance(result["rate"], Decimal)
        assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_convert_currency_negative_amount(conversion_service, db_session):
    """Test conversion with negative amount raises exception."""
    with pytest.raises(InvalidAmountException):
        await conversion_service.convert_currency(
            user_id="test_user",
            from_currency="USD",
            to_currency="EUR",
            amount=Decimal("-100.00"),
            db=db_session
        )

@pytest.mark.asyncio
async def test_convert_currency_saves_transaction(conversion_service, db_session, mock_rates_response, test_data):
    """Test that conversion creates a transaction record."""
    with respx.mock as respx_mock:
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(200, json=mock_rates_response)
        )
        
        result = await conversion_service.convert_currency(
            user_id=test_data["user_id"],
            from_currency=test_data["from_currency"],
            to_currency=test_data["to_currency"],
            amount=Decimal(test_data["amount"]),
            db=db_session
        )
        
        # Verify transaction was saved
        transaction = db_session.query(Transaction).filter_by(id=result["transaction_id"]).first()
        assert transaction is not None
        assert transaction.user_id == test_data["user_id"]
        assert transaction.source_currency == test_data["from_currency"]
        assert transaction.target_currency == test_data["to_currency"]
        assert transaction.source_amount == Decimal(test_data["amount"])

@pytest.mark.asyncio
async def test_convert_currency_same_currency(conversion_service, db_session):
    """Test conversion between same currencies."""
    result = await conversion_service.convert_currency(
        user_id="test_user",
        from_currency="EUR",
        to_currency="EUR",
        amount=Decimal("100.00"),
        db=db_session
    )
    
    assert result["from"]["amount"] == result["to"]["amount"]
    assert result["rate"] == Decimal("1")
