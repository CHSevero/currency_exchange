from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import (
    ConversionRequest,
    ConversionResponse,
    ExchangeRatesResponse,
)
from app.services.conversion_service import ConversionService
from app.services.rate_service import RateService
from app.core.config import settings

# Create services
rate_service = RateService()
conversion_service = ConversionService(rate_service)

router = APIRouter()


@router.post("/convert", response_model=ConversionResponse, status_code=200)
async def convert_currency(request: ConversionRequest, db: Session = Depends(get_db)):
    """
    Convert an amount from one currency to another.

    - **user_id**: User identifier
    - **from_currency**: Source currency code (ISO 4217)
    - **to_currency**: Target currency code (ISO 4217)
    - **amount**: Amount to convert (must be positive)

    Returns the conversion result with transaction details.
    """
    result = await conversion_service.convert_currency(
        user_id=request.user_id,
        from_currency=request.from_currency,
        to_currency=request.to_currency,
        amount=request.amount,
        db=db,
    )

    return result


@router.get("/rates", response_model=ExchangeRatesResponse, status_code=200)
async def get_exchange_rates(
    base: Optional[str] = Query(
        settings.EXCHANGE_RATE_BASE_CURRENCY,
        description="Base currency (only EUR supported for now)",
    ),
    db: Session = Depends(get_db),
):
    """
    Get current exchange rates.

    - **base**: Base currency (default: EUR, only EUR supported for now)

    Returns the exchange rates with the base currency and timestamp.
    """
    # Currently, we only support EUR as base currency due to API limitations
    if base != settings.EXCHANGE_RATE_BASE_CURRENCY:
        base = settings.EXCHANGE_RATE_BASE_CURRENCY

    rates = await rate_service._get_rates(db)

    return {"base": base, "rates": rates, "timestamp": datetime.utcnow()}
