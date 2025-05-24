from sqlalchemy import Column, Integer, String, DateTime, JSON, Numeric
from datetime import datetime, timezone
from app.core.database import (
    Base,
)  # Import Base from database.py instead of creating new one


class Transaction(Base):
    """SQLAlchemy model for currency conversion transactions."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    source_currency = Column(String(3))  # ISO 4217 currency code (e.g., USD)
    target_currency = Column(String(3))  # ISO 4217 currency code (e.g., EUR)
    source_amount = Column(Numeric(precision=18, scale=2))
    target_amount = Column(Numeric(precision=18, scale=2))
    exchange_rate = Column(Numeric(precision=8, scale=2))
    timestamp = Column(
        DateTime(timezone=True),  # Store timezone info
        default=lambda: datetime.now(timezone.utc),
    )


class ExchangeRate(Base):
    """SQLAlchemy model for storing exchange rates as backup."""

    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3))
    rates = Column(JSON)  # JSON field to store all rates
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
