from datetime import datetime, timezone
from typing import Optional
from fastapi.exceptions import HTTPException
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
        None, gt=0, description="Maximum number of transactions to return"
    ),
    offset: Optional[int] = Query(
        None, ge=0, description="Offset for pagination"
    ),
    from_date: Optional[str] = Query(
        None, description="Filter from date (ISO format)"
    ),
    to_date: Optional[str] = Query(
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
    try:
        # Parse the date strings and ensure UTC timezone
        from_date_obj = None
        to_date_obj = None
        
        if from_date:
            try:
                # Handle both ISO formats (with Z or +00:00)
                parsed_date = from_date.replace('Z', '+00:00')
                from_date_obj = datetime.fromisoformat(parsed_date)
                # Convert to UTC if not already
                if from_date_obj.tzinfo is None:
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
                else:
                    from_date_obj = from_date_obj.astimezone(timezone.utc)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid date format for from_date",
                        "detail": f"Please provide date in ISO format (e.g., 2025-05-18T00:00:00+00:00 or 2025-05-18T00:00:00Z). Error: {str(e)}"
                    }
                )

        if to_date:
            try:
                # Handle both ISO formats (with Z or +00:00)
                parsed_date = to_date.replace('Z', '+00:00')
                to_date_obj = datetime.fromisoformat(parsed_date)
                # Convert to UTC if not already
                if to_date_obj.tzinfo is None:
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
                else:
                    to_date_obj = to_date_obj.astimezone(timezone.utc)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid date format for to_date",
                        "detail": f"Please provide date in ISO format (e.g., 2025-05-18T00:00:00+00:00 or 2025-05-18T00:00:00Z). Error: {str(e)}"
                    }
                )

        result = transaction_service.get_user_transactions(
            user_id=user_id,
            db=db,
            limit=limit,
            offset=offset,
            from_date=from_date_obj,
            to_date=to_date_obj,
        )

        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Date parsing error",
                "detail": str(e)
            }
        )
