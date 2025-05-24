import pytest
import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.services.transaction_service import TransactionService
from app.core.exceptions import UserNotFoundException
from app.models.models import Transaction

logger = logging.getLogger(__name__)


@pytest.fixture
def transaction_service():
    return TransactionService()


@pytest.fixture
def sample_transactions(db_session):
    """Create sample transactions for testing."""
    # Clean up existing transactions
    db_session.query(Transaction).delete()
    db_session.commit()

    # Create new transactions with specific timestamps
    base_time = datetime.now(timezone.utc).replace(
        microsecond=0
    )  # Remove microseconds for consistent comparison
    transactions = []

    # Create 5 transactions with different dates
    for i in range(5):
        tx_time = base_time - timedelta(days=i)
        transaction = Transaction(
            user_id="test_user",
            source_currency="USD",
            target_currency="EUR",
            source_amount=Decimal("100.00"),
            target_amount=Decimal("85.00"),
            exchange_rate=Decimal("0.85"),
            timestamp=tx_time,
        )
        transactions.append(transaction)

    db_session.add_all(transactions)
    db_session.commit()

    for tx in transactions:
        db_session.refresh(tx)  # Refresh to ensure timestamps are loaded from DB

    return transactions


def test_get_user_transactions(transaction_service, db_session, sample_transactions):
    """Test retrieving user transactions."""
    result = transaction_service.get_user_transactions(
        user_id="test_user", db=db_session
    )

    assert result["user_id"] == "test_user"
    assert result["count"] == 5
    assert result["total"] == 5
    assert len(result["transactions"]) == 5

    # Check transactions are ordered by timestamp (newest first)
    timestamps = [tx["timestamp"] for tx in result["transactions"]]
    assert timestamps == sorted(timestamps, reverse=True)


def test_get_user_transactions_with_pagination(
    transaction_service, db_session, sample_transactions
):
    """Test transaction retrieval with pagination."""
    result = transaction_service.get_user_transactions(
        user_id="test_user", db=db_session, limit=2, offset=1
    )

    assert result["count"] == 2
    assert result["total"] == 5
    assert len(result["transactions"]) == 2


def test_get_user_transactions_with_date_filter(transaction_service, db_session):
    """Test transaction retrieval with date filtering."""
    # Clean up existing transactions
    db_session.query(Transaction).delete()
    db_session.commit()

    # Create transactions with precise timestamps
    base_time = datetime(2025, 5, 19, 12, 0, 0, tzinfo=timezone.utc)
    transactions = []

    # Create transactions for last 5 days
    for i in range(5):
        tx_time = base_time - timedelta(days=i)
        logger.info(f"Creating transaction with timestamp: {tx_time}")
        transaction = Transaction(
            user_id="test_user",
            source_currency="USD",
            target_currency="EUR",
            source_amount=Decimal("100.00"),
            target_amount=Decimal("85.00"),
            exchange_rate=Decimal("0.85"),
            timestamp=tx_time,
        )
        transactions.append(transaction)

    db_session.add_all(transactions)
    db_session.commit()

    # Set from_date to 2 days before base_time
    from_date = base_time - timedelta(days=2)
    logger.info("\nTest parameters:")
    logger.info(f"Base time: {base_time}")
    logger.info(f"From date: {from_date}")

    # Log all transaction timestamps in database
    all_txns = (
        db_session.query(Transaction).order_by(Transaction.timestamp.desc()).all()
    )
    logger.info("\nAll transactions in database:")
    for tx in all_txns:
        logger.info(f"Transaction ID: {tx.id}, Timestamp: {tx.timestamp}")

    result = transaction_service.get_user_transactions(
        user_id="test_user", db=db_session, from_date=from_date
    )

    logger.info("\nFiltered transactions:")
    for tx in result["transactions"]:
        logger.info(f"Transaction timestamp: {tx['timestamp']}")

    # Should return transactions from last 3 days (including base_time, -1 day, and -2 days)
    assert result["count"] == 3, f"Expected 3 transactions, got {result['count']}"
    assert result["total"] == 3, (
        f"Expected total of 3 transactions, got {result['total']}"
    )

    # Verify timestamps are correct
    for tx in result["transactions"]:
        tx_time = tx["timestamp"]  # Already a datetime object
        logger.info(
            f"Verifying transaction timestamp {tx_time} is >= from_date {from_date}"
        )
        assert tx_time >= from_date, (
            f"Transaction timestamp {tx_time} is before from_date {from_date}"
        )
        assert (tx_time - from_date) <= timedelta(days=2), (
            f"Transaction timestamp {tx_time} is more than 2 days after from_date"
        )


def test_get_user_transactions_unknown_user(transaction_service, db_session):
    """Test retrieving transactions for unknown user raises exception."""
    with pytest.raises(UserNotFoundException):
        transaction_service.get_user_transactions(user_id="unknown_user", db=db_session)


def test_transaction_format(transaction_service, db_session, sample_transactions):
    """Test transaction formatting."""
    result = transaction_service.get_user_transactions(
        user_id="test_user", db=db_session, limit=1
    )

    transaction = result["transactions"][0]
    assert all(
        key in transaction
        for key in ["transaction_id", "from", "to", "rate", "timestamp"]
    )
    assert all(key in transaction["from"] for key in ["currency", "amount"])
    assert all(key in transaction["to"] for key in ["currency", "amount"])
    assert isinstance(transaction["rate"], Decimal)
    assert isinstance(transaction["timestamp"], datetime)
