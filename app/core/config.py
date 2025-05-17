import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Currency Converter API"
    DESCRIPTION: str = "Currency Converter API with transaction tracking"
    VERSION: str = "1.0.0"

    # Exchange Rate API settings
    EXCHANGE_RATE_API_URL: str = "http://api.exchangeratesapi.io/latest"
    EXCHANGE_RATE_API_KEY: str = os.getenv("EXCHANGE_RATE_API_KEY", "")
    EXCHANGE_RATE_BASE_CURRENCY: str = "EUR"

    # Caching settings
    EXCHANGE_RATE_CACHE_TTL: int = 3600  # 1 hour in seconds

    # Supported currencies
    SUPPORTED_CURRENCIES: List[str] = ["USD", "EUR", "JPY", "BRL"]

    # Database settings
    DATABASE_NAME: str = "currency_converter.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
