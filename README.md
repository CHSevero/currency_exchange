# Currency Exchange API

A FastAPI-based REST API for currency conversion with transaction tracking.

[![CI/CD](https://github.com/CHSevero/currency_exchange/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/CHSevero/currency_exchange/actions/workflows/ci-cd.yml)

🚀 **Live Demo:** [https://currency-exchange-nhm9.onrender.com/docs](https://currency-exchange-nhm9.onrender.com/docs)  
⏳ *Note: Initial load may take up to 2 minutes if the application is in sleep mode.*

## Features

- Convert between BRL, USD, EUR, and JPY currencies
- Real-time exchange rates from exchangeratesapi.io
- Transaction history tracking per user
- Pagination and date filtering for transactions
- SQLite database for transaction storage
- Exchange rate caching
- Comprehensive test suite
- API documentation via Swagger UI

## Quick Start

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment:
```bash
uv venv
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Set up your environment:
```bash
cp .env.example .env
# Edit .env and add your exchangeratesapi.io API key
```

5. Run the application:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for the interactive API documentation.

## Development

### Install development dependencies:
```bash
uv pip install -e .[test]
```

### Run tests:
```bash
uv run pytest
```

### Code formatting and linting:
```bash
uvx ruff format .
uvx ruff check .
```

## API Documentation

For detailed API documentation, see [docs/api_documentation.md](docs/api_documentation.md).

For product requirements and specifications, see [docs/prd.md](docs/prd.md).

## Environment Variables

- `EXCHANGE_RATE_API_KEY` - Your exchangeratesapi.io API key
- `EXCHANGE_RATE_API_URL` - API endpoint (default: http://api.exchangeratesapi.io/latest)
- `EXCHANGE_RATE_BASE_CURRENCY` - Base currency for rates (default: EUR)
- `EXCHANGE_RATE_CACHE_TTL` - Cache duration in seconds (default: 3600)

## Limitations

- Currently supports only EUR as base currency (exchangeratesapi.io free tier limitation)
- Supports BRL, USD, EUR, and JPY currencies
- Uses SQLite database (suitable for development/demo)
- No built-in authentication

## License

MIT License
