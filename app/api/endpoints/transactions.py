from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import TransactionsListResponse
from app.services.transaction_service import TransactionService

# Create service
transaction_service = TransactionService()

router = APIRouter()


@router.get("/{user_id}", response_model=TransactionsListResponse, status_code=200)
async def get_user_transactions(
    user_id: str,
    limit: Optional[int] = Query(
        None, description="Maximum number of transactions to return"
    ),
    offset: Optional[int] = Query(None, description="Offset for pagination"),
    from_date: Optional[datetime] = Query(
        None, description="Filter from date (ISO format)"
    ),
    to_date: Optional[datetime] = Query(
        None, description="Filter to date (ISO format)"
    ),
    db: Session = Depends(get_db),
):
    """
    Get transaction history for a user.

    - **user_id**: User identifier
    - **limit**: Maximum number of transactions to return
    - **offset**: Offset for pagination
    - **from_date**: Filter transactions from this date (ISO format)
    - **to_date**: Filter transactions to this date (ISO format)

    Returns the transaction history with metadata.
    """
    result = transaction_service.get_user_transactions(
        user_id=user_id,
        db=db,
        limit=limit,
        offset=offset,
        from_date=from_date,
        to_date=to_date,
    )

    return result
