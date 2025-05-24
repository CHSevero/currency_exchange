import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.models.models import Transaction


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_transactions(db_session):
    """Create sample transactions for testing."""
    # Drop and recreate tables to ensure clean state
    engine = db_session.get_bind()
    Transaction.__table__.drop(engine, checkfirst=True)
    Transaction.__table__.create(engine)

    # Create new test transactions with fixed timestamps
    base_time = datetime(
        2025, 5, 19, 12, 0, 0, tzinfo=timezone.utc
    )  # Fixed date for testing
    transactions = []

    for i in range(5):
        tx = Transaction(
            user_id="test_user",
            source_currency="USD",
            target_currency="EUR",
            source_amount=100.00,
            target_amount=85.00,
            exchange_rate=0.85,
            timestamp=base_time - timedelta(days=i),
        )
        transactions.append(tx)

    db_session.add_all(transactions)
    db_session.commit()

    # Refresh to get the actual timestamps
    for tx in transactions:
        db_session.refresh(tx)

    yield transactions

    # Cleanup after test
    db_session.query(Transaction).delete()
    db_session.commit()


def test_get_user_transactions(client, sample_transactions):
    """Test getting user transactions."""
    response = client.get("/api/v1/transactions/test_user")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"
    assert data["count"] == 5
    assert data["total"] == 5
    assert len(data["transactions"]) == 5


def test_get_user_transactions_with_pagination(client, sample_transactions):
    """Test getting user transactions with pagination."""
    response = client.get("/api/v1/transactions/test_user?limit=2&offset=1")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["total"] == 5
    assert len(data["transactions"]) == 2


def test_get_user_transactions_with_date_filter(client, sample_transactions):
    """Test getting user transactions with date filter."""
    # Use a fixed date that matches our sample data
    base_time = datetime(2025, 5, 19, 12, 0, 0, tzinfo=timezone.utc)
    from_date = (base_time - timedelta(days=2)).isoformat().replace("+00:00", "Z")

    response = client.get(f"/api/v1/transactions/test_user?from_date={from_date}")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3  # Should return only transactions from last 2 days
    # Verify timestamps are after from_date
    for tx in data["transactions"]:
        tx_time = datetime.fromisoformat(tx["timestamp"].replace("Z", "+00:00"))
        assert tx_time >= datetime.fromisoformat(from_date.replace("Z", "+00:00"))


def test_get_user_transactions_unknown_user(client, db_session):
    """Test getting transactions for unknown user."""
    response = client.get("/api/v1/transactions/unknown_user")

    assert response.status_code == 404
    assert "error" in response.json()


def test_get_user_transactions_invalid_date_format(client, sample_transactions):
    """Test getting transactions with invalid date format."""
    response = client.get("/api/v1/transactions/test_user?from_date=invalid-date")

    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert "detail" in data["detail"]


def test_get_user_transactions_invalid_limit(client, sample_transactions):
    """Test getting transactions with invalid limit."""
    response = client.get("/api/v1/transactions/test_user?limit=-1")

    assert response.status_code == 400
    assert "error" in response.json()
