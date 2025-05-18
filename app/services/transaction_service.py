import logging
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Transaction
from app.core.exceptions import UserNotFoundException

logger = logging.getLogger(__name__)


class TransactionService:
    """Service to handle transaction operations"""

    def get_user_transactions(
        self,
        user_id: str,
        db: Session,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Get transaction history for a user.

        Args:
            user_id: User identifier
            db: Database session
            limit: Maximum number of transactions to return
            offset: Offset for pagination
            from_date: Filter transactions from this date
            to_date: Filter transactions to this date

        Returns:
            Dict: Transaction history with metadata

        Raises:
            UserNotFoundException: If no transactions found for user
        """
        # Build query
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        # Apply date filters if provided
        if from_date:
            query = query.filter(Transaction.timestamp >= from_date)
        if to_date:
            query = query.filter(Transaction.timestamp <= to_date)

        # Get total count
        total = query.count()
        if total == 0:
            raise UserNotFoundException(user_id)

        # Order by timestamp (newest first) and apply pagination
        query = query.order_by(desc(Transaction.timestamp))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        # Execute query
        transactions = query.all()

        # Format response
        formatted_transactions = [self._format_transaction(tx) for tx in transactions]

        return {
            "user_id": user_id,
            "transactions": formatted_transactions,
            "count": len(formatted_transactions),
            "total": total,
        }

    def _format_transaction(self, transaction: Transaction) -> Dict:
        """
        Format transaction model to response dictionary.

        Args:
            transaction: Transaction model

        Returns:
            Dict: Formatted transaction
        """
        return {
            "transaction_id": transaction.id,
            "from": {
                "currency": transaction.source_currency,
                "amount": transaction.source_amount,
            },
            "to": {
                "currency": transaction.target_currency,
                "amount": transaction.target_amount,
            },
            "rate": transaction.exchange_rate,
            "timestamp": transaction.timestamp,
        }
