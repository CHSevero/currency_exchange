import httpx
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from decimal import Decimal, getcontext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ExternalAPIException, InvalidCurrencyException
from app.models.models import ExchangeRate

# Set decimal precision for monetary calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


class RateService:
    """Service to handle exchange rate operations"""

    def __init__(self):
        self.base_url = settings.EXCHANGE_RATE_API_URL
        self.api_key = settings.EXCHANGE_RATE_API_KEY
        self.base_currency = settings.EXCHANGE_RATE_BASE_CURRENCY
        self.ttl = settings.EXCHANGE_RATE_CACHE_TTL

        # In-memory cache
        self.cache = {}

    async def get_exchange_rate(
        self, from_currency: str, to_currency: str, db: Session
    ) -> Decimal:
        """
        Get exchange rate between two currencies.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            db: Database session for fallback storage

        Returns:
            Decimal: Exchange rate (from_currency to to_currency)

        Raises:
            InvalidCurrencyException: If currency is not supported
            ExternalAPIException: If external API call fails
        """
        # Validate currencies
        for currency in [from_currency, to_currency]:
            if currency not in settings.SUPPORTED_CURRENCIES:
                raise InvalidCurrencyException(currency)

        # Get rates with EUR as base
        rates = await self._get_rates(db)

        # Calculate exchange rate
        if from_currency == self.base_currency:
            return rates[to_currency]
        elif to_currency == self.base_currency:
            return Decimal("1") / rates[from_currency]
        else:
            # Cross rate calculation
            return rates[to_currency] / rates[from_currency]

    async def _get_rates(self, db: Session) -> Dict[str, Decimal]:
        """
        Get all exchange rates with caching.

        Returns:
            Dict[str, Decimal]: Dictionary with currency codes as keys and rates as values
        """
        # Check if rates are in cache and not expired
        if self.base_currency in self.cache:
            cached_data = self.cache[self.base_currency]
            if datetime.now(timezone.utc) < cached_data["expires_at"]:
                logger.debug("Using cached exchange rates")
                return cached_data["rates"]

        try:
            # Fetch from external API
            logger.info("Fetching exchange rates from external API")
            rates = await self._fetch_from_external_api()

            # Cache the rates
            self.cache[self.base_currency] = {
                "rates": rates,
                "expires_at": datetime.now(timezone.utc) + timedelta(seconds=self.ttl),
            }

            # Save to database as backup
            self._save_rates_to_db(db, rates)

            return rates

        except Exception as e:
            logger.error(f"Error fetching exchange rates: {str(e)}")

            # Try to use cached rates even if expired
            if self.base_currency in self.cache:
                logger.warning("Using expired cached exchange rates")
                return self.cache[self.base_currency]["rates"]

            # Try to use rates from database
            db_rates = self._get_rates_from_db(db)
            if db_rates:
                logger.warning("Using exchange rates from database")
                return db_rates

            # If all else fails, raise exception
            raise ExternalAPIException(f"Failed to get exchange rates: {str(e)}")

    async def _fetch_from_external_api(self) -> Dict[str, Decimal]:
        """
        Fetch exchange rates from external API.

        Returns:
            Dict[str, Decimal]: Dictionary with currency codes as keys and rates as values
        """
        params = {"base": self.base_currency}
        if self.api_key:
            params["access_key"] = self.api_key

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)

            if response.status_code != 200:
                raise ExternalAPIException(
                    f"API returned status code {response.status_code}"
                )

            data = response.json()

            if "rates" not in data:
                raise ExternalAPIException("Invalid response from exchange rate API")

            # Convert float rates to Decimal
            decimal_rates = {
                currency: Decimal(str(rate)) for currency, rate in data["rates"].items()
            }

            return decimal_rates

    def _save_rates_to_db(self, db: Session, rates: Dict[str, Decimal]) -> None:
        """
        Save exchange rates to database as backup.

        Args:
            db: Database session
            rates: Dictionary with currency codes as keys and rates as values
        """
        try:
            # Convert Decimal to string to ensure proper serialization
            str_rates = {currency: str(rate) for currency, rate in rates.items()}

            exchange_rate = ExchangeRate(
                base_currency=self.base_currency,
                rates=str_rates,
                last_updated=datetime.now(timezone.utc),
            )

            db.add(exchange_rate)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving exchange rates to database: {str(e)}")
            db.rollback()

    def _get_rates_from_db(self, db: Session) -> Optional[Dict[str, Decimal]]:
        """
        Get exchange rates from database.

        Args:
            db: Database session

        Returns:
            Optional[Dict[str, Decimal]]: Dictionary with currency codes as keys and rates as values
        """
        try:
            # Get the most recent rates
            exchange_rate = (
                db.query(ExchangeRate)
                .filter(ExchangeRate.base_currency == self.base_currency)
                .order_by(ExchangeRate.last_updated.desc())
                .first()
            )

            if exchange_rate:
                # Convert string rates back to Decimal
                return {
                    currency: Decimal(rate)
                    for currency, rate in exchange_rate.rates.items()
                }

            return None
        except Exception as e:
            logger.error(f"Error retrieving exchange rates from database: {str(e)}")
            return None
