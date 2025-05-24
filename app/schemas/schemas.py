from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
from datetime import datetime
from decimal import Decimal
from app.core.config import settings


class BaseSchema(BaseModel):
    """Base model with common configuration for all schema models."""

    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),  # Ensure Decimal is properly serialized
        }
        populate_by_name = True  # Allow both alias and field name for data population


# Request Models
class ConversionRequest(BaseModel):
    """Model for currency conversion requests."""

    user_id: str = Field(..., description="User identifier")
    from_currency: str = Field(..., description="Source currency code (ISO 4217)")
    to_currency: str = Field(..., description="Target currency code (ISO 4217)")
    amount: Decimal = Field(
        ..., gt=0, description="Amount to convert (must be positive)"
    )

    @field_validator("from_currency", "to_currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate that currency codes are supported."""
        if v not in settings.SUPPORTED_CURRENCIES:
            supported = ", ".join(settings.SUPPORTED_CURRENCIES)
            raise ValueError(
                f"Currency code '{v}' is not supported. Must be one of: {supported}"
            )
        return v.upper()  # Ensure consistent formatting

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate and normalize the decimal amount."""
        # Format decimal amount to 2 decimal places
        return v.quantize(Decimal("0.01"))


# Response Models
class CurrencyAmount(BaseSchema):
    """Model representing an amount in a specific currency."""

    currency: str
    amount: Decimal


class ConversionResponse(BaseSchema):
    """Model for currency conversion responses."""

    transaction_id: int
    user_id: str
    from_: CurrencyAmount = Field(..., alias="from")
    to: CurrencyAmount
    rate: Decimal
    timestamp: datetime


class TransactionResponse(BaseSchema):
    """Model for retrieving individual transaction details."""

    transaction_id: int
    from_: CurrencyAmount = Field(..., alias="from")
    to: CurrencyAmount
    rate: Decimal
    timestamp: datetime


class TransactionsListResponse(BaseSchema):
    """Model for listing multiple transactions with pagination support."""

    user_id: str
    transactions: List[TransactionResponse]
    count: int  # Number of transactions in the current response
    total: int  # Total number of transactions available


class ExchangeRatesResponse(BaseSchema):
    """Model for currency exchange rates responses."""

    base: str  # Base currency
    rates: Dict[str, Decimal]  # Dictionary of currency code -> rate
    timestamp: datetime


# Error Response Models
class ErrorResponse(BaseSchema):
    """Model for API error responses."""

    error: str  # Error type/title
    status_code: int  # HTTP status code
    detail: str  # Detailed error message

    @classmethod
    def create(cls, error: str, status_code: int, detail: str) -> "ErrorResponse":
        """Factory method to create error responses more easily."""
        return cls(error=error, status_code=status_code, detail=detail)
