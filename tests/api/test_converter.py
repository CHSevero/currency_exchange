import pytest
from fastapi.testclient import TestClient
import respx
from httpx import Response

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    return TestClient(app)


def test_convert_currency_success(client, mock_rates_response, test_data):
    """Test successful currency conversion endpoint."""
    with respx.mock() as respx_mock:
        # Mock the exchange rate API with the correct params
        respx_mock.get(
            settings.EXCHANGE_RATE_API_URL,
            params={
                "base": settings.EXCHANGE_RATE_BASE_CURRENCY,
                "access_key": settings.EXCHANGE_RATE_API_KEY,
            },
        ).mock(return_value=Response(200, json=mock_rates_response))

        response = client.post(
            "/api/v1/convert/convert",
            json={
                "user_id": test_data["user_id"],
                "from_currency": test_data["from_currency"],
                "to_currency": test_data["to_currency"],
                "amount": test_data["amount"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_data["user_id"]
        assert data["from"]["currency"] == test_data["from_currency"]
        assert data["to"]["currency"] == test_data["to_currency"]
        assert "transaction_id" in data


def test_convert_currency_invalid_amount(client):
    """Test conversion with invalid amount."""
    response = client.post(
        "/api/v1/convert/convert",
        json={
            "user_id": "test_user",
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": "-100.00",
        },
    )

    assert response.status_code == 400
    assert "error" in response.json()


def test_convert_currency_invalid_currency(client):
    """Test conversion with invalid currency."""
    response = client.post(
        "/api/v1/convert/convert",
        json={
            "user_id": "test_user",
            "from_currency": "INVALID",
            "to_currency": "EUR",
            "amount": "100.00",
        },
    )

    assert response.status_code == 400
    assert "error" in response.json()


def test_get_exchange_rates(client, mock_rates_response):
    """Test getting exchange rates."""
    route = respx.mock.get(settings.EXCHANGE_RATE_API_URL)
    route.mock(side_effect=lambda r: Response(200, json=mock_rates_response))

    response = client.get("/api/v1/convert/rates")

    assert response.status_code == 200
    data = response.json()
    assert data["base"] == settings.EXCHANGE_RATE_BASE_CURRENCY
    assert "rates" in data
    assert "timestamp" in data


def test_get_exchange_rates_unsupported_base(client, mock_rates_response):
    """Test getting exchange rates with unsupported base currency."""
    route = respx.mock.get(settings.EXCHANGE_RATE_API_URL)
    route.mock(return_value=Response(200, json=mock_rates_response))

    response = client.get("/api/v1/convert/rates?base=USD")

    assert response.status_code == 200
    data = response.json()
    # Should default to EUR
    assert data["base"] == settings.EXCHANGE_RATE_BASE_CURRENCY
