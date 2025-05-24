import pytest
from decimal import Decimal
from datetime import datetime, timezone
import respx
from httpx import Response

from app.services.rate_service import RateService
from app.core.config import settings
from app.core.exceptions import InvalidCurrencyException, ExternalAPIException
from app.models.models import ExchangeRate


@pytest.fixture
def rate_service():
    return RateService()


@pytest.mark.asyncio
async def test_get_exchange_rate_same_currency(rate_service, db_session):
    """Test exchange rate for same currency should be 1."""
    # For same currency, we don't need to mock the API as it won't be called
    rate = await rate_service.get_exchange_rate("EUR", "EUR", db_session)
    assert rate == Decimal("1")


@pytest.mark.asyncio
async def test_get_exchange_rate_invalid_currency(rate_service, db_session):
    """Test invalid currency raises exception."""
    with pytest.raises(InvalidCurrencyException):
        await rate_service.get_exchange_rate("INVALID", "EUR", db_session)


@pytest.mark.asyncio
async def test_get_exchange_rate_successful(
    rate_service, db_session, mock_rates_response
):
    """Test successful exchange rate retrieval."""
    with respx.mock as respx_mock:
        respx_mock.get(f"{settings.EXCHANGE_RATE_API_URL}").mock(
            return_value=Response(200, json=mock_rates_response)
        ).side_effect = lambda r: Response(200, json=mock_rates_response)

        rate = await rate_service.get_exchange_rate("USD", "EUR", db_session)
        assert isinstance(rate, Decimal)
        assert float(rate) == pytest.approx(1 / 1.18, rel=1e-6)


@pytest.mark.asyncio
async def test_get_exchange_rate_api_error(rate_service, db_session):
    """Test handling of API errors."""
    with respx.mock as respx_mock:
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )

        # First call without cached data should raise exception
        with pytest.raises(ExternalAPIException):
            await rate_service.get_exchange_rate("USD", "EUR", db_session)


@pytest.mark.asyncio
async def test_get_exchange_rate_from_cache(
    rate_service, db_session, mock_rates_response
):
    """Test exchange rate retrieval from cache."""
    with respx.mock as respx_mock:
        # First call to populate cache
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(200, json=mock_rates_response)
        )
        rate1 = await rate_service.get_exchange_rate("USD", "EUR", db_session)

        # Second call should use cache
        rate2 = await rate_service.get_exchange_rate("USD", "EUR", db_session)

        assert rate1 == rate2


@pytest.mark.asyncio
async def test_get_exchange_rate_from_db(rate_service, db_session):
    """Test exchange rate retrieval from database."""
    # Add test data to database
    db_rate = ExchangeRate(
        base_currency="EUR",
        rates={"USD": "1.18", "JPY": "129.55", "BRL": "6.35", "EUR": "1.0"},
        last_updated=datetime.now(timezone.utc),
    )
    db_session.add(db_rate)
    db_session.commit()

    with respx.mock as respx_mock:
        # Make API call fail to force DB fallback
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )

        # Clear cache to force DB lookup
        rate_service.cache = {}
        rate = await rate_service.get_exchange_rate("USD", "EUR", db_session)
        assert isinstance(rate, Decimal)
        assert float(rate) == pytest.approx(1 / 1.18, rel=1e-6)
