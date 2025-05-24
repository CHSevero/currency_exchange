# Currency Exchange API Documentation

## Overview

The Currency Exchange API is a RESTful service that enables currency conversion between multiple supported currencies (USD, EUR, JPY, BRL) using live exchange rates. The service tracks and persists all conversion transactions per user and provides comprehensive transaction history management.

## Features

- Currency conversion between BRL, USD, EUR, and JPY
- Live exchange rates from exchangeratesapi.io
- Transaction history tracking per user
- Pagination and date filtering for transaction queries
- Robust error handling and input validation
- Caching mechanism for exchange rates

## Technical Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (embedded)
- **Exchange Rates**: exchangeratesapi.io
- **Documentation**: OpenAPI (Swagger)

## Check a demo running version:
https://currency-exchange-nhm9.onrender.com/docs
## Installation

1. Clone the repository

2. Install and set up uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
```

Note: `uv` automatically handles virtual environment activation when running commands with `uv pip` or `uv run`.

3. Install dependencies:
```bash
uv pip install -e .
```

4. Set up environment variables:
Create a `.env` file with:
```
EXCHANGE_RATE_API_KEY=your_api_key_here
```

5. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Currency Conversion

#### Convert Currency
```
POST /api/v1/convert/convert
```

Converts an amount from one currency to another.

**Request Body**:
```json
{
    "user_id": "string",
    "from_currency": "USD",
    "to_currency": "EUR",
    "amount": "100.00"
}
```

**Response**:
```json
{
    "transaction_id": 1,
    "user_id": "string",
    "from": {
        "currency": "USD",
        "amount": "100.00"
    },
    "to": {
        "currency": "EUR",
        "amount": "85.00"
    },
    "rate": "0.85",
    "timestamp": "2025-05-24T14:00:00Z"
}
```

#### Get Exchange Rates
```
GET /api/v1/convert/rates?base=EUR
```

Returns current exchange rates.

**Query Parameters**:
- `base`: Base currency (default: EUR, currently only EUR supported)

**Response**:
```json
{
    "base": "EUR",
    "rates": {
        "USD": "1.18",
        "JPY": "129.55",
        "BRL": "6.35"
    },
    "timestamp": "2025-05-24T14:00:00Z"
}
```

### Transaction History

#### Get User Transactions
```
GET /api/v1/transactions/{user_id}
```

Retrieves transaction history for a user.

**Query Parameters**:
- `limit`: Maximum number of transactions to return
- `offset`: Offset for pagination
- `from_date`: Filter transactions from this date (ISO format)
- `to_date`: Filter transactions to this date (ISO format)

**Response**:
```json
{
    "user_id": "string",
    "transactions": [
        {
            "transaction_id": 1,
            "from": {
                "currency": "USD",
                "amount": "100.00"
            },
            "to": {
                "currency": "EUR",
                "amount": "85.00"
            },
            "rate": "0.85",
            "timestamp": "2025-05-24T14:00:00Z"
        }
    ],
    "count": 1,
    "total": 1
}
```

### Health Check

#### Check API Health
```
GET /health
```

Returns the health status of the API.

**Response**:
```json
{
    "status": "healthy"
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages in a consistent format:

```json
{
    "error": "string",
    "status_code": int,
    "detail": "string"
}
```

Common error codes:
- `400`: Bad Request (invalid input)
- `404`: Not Found (user or resource not found)
- `500`: Internal Server Error
- `503`: Service Unavailable (external API issues)

## Data Models

### Transaction
- `id`: Integer (primary key)
- `user_id`: String
- `source_currency`: String (3-letter ISO code)
- `target_currency`: String (3-letter ISO code)
- `source_amount`: Decimal
- `target_amount`: Decimal
- `exchange_rate`: Decimal
- `timestamp`: DateTime (UTC)

### Exchange Rate
- `id`: Integer (primary key)
- `base_currency`: String
- `rates`: JSON (currency rates)
- `last_updated`: DateTime

## Development

### Running Tests

First, install test dependencies:
```bash
uv pip install -e .[test]
```

Run all tests:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=app --cov-report=term-missing
```

Run specific test files:
```bash
uv run pytest tests/services/test_rate_service.py
```

Run tests in parallel:
```bash
uv run pytest -n auto
```

### Code Style
The project uses Ruff for linting and formatting:
```bash
uv run ruff check .
uv run ruff format .
```

### CI/CD
The project includes GitHub Actions workflows for:
- Running tests
- Code linting
- Automatic deployment to Render.com

## Environment Variables

- `EXCHANGE_RATE_API_KEY`: API key for exchangeratesapi.io
- `EXCHANGE_RATE_API_URL`: Base URL for exchange rate API (default: http://api.exchangeratesapi.io/latest)
- `EXCHANGE_RATE_BASE_CURRENCY`: Base currency for rates (default: EUR)
- `EXCHANGE_RATE_CACHE_TTL`: Cache time-to-live in seconds (default: 3600)

## Limitations and Considerations

1. The free tier of exchangeratesapi.io only supports EUR as the base currency
2. Exchange rates are cached for 1 hour to avoid API rate limits
3. SQLite database is used for simplicity; may need to switch to a more robust solution for production
4. User authentication is not implemented; user_id is passed as a parameter
5. Only supports BRL, USD, EUR, and JPY currencies currently
