import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.core.database import Base, set_engine
from app.models.models import Transaction
from app.main import app

@pytest.fixture(scope="function")
def test_app():
    """Create a fresh app instance for each test."""
    from app.main import app  # local import for test isolation
    return app

@pytest.fixture(scope="function")
def engine():
    """Create a new test database engine for each test."""
    # Create a new in-memory database for each test
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Import all models to ensure they're registered with Base
    from app.core.database import Base
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Set as current engine
    set_engine(test_engine)
    
    yield test_engine
    
    # Drop all tables
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    """Create a test database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Start with clean tables
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    yield session
    
    # Clean up
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def client(engine):
    """Create a test client with the test database."""
    # Make sure all models are imported and tables exist
    
    yield TestClient(app)

@pytest.fixture(scope="function")
def sample_transactions(db_session):
    """Create sample transactions for testing."""
    # Clean up any existing data
    db_session.query(Transaction).delete()
    db_session.commit()
    
    # Create new test transactions with fixed timestamps
    base_time = datetime(2025, 5, 19, 12, 0, 0, tzinfo=timezone.utc)
    transactions = []
    
    for i in range(5):
        tx = Transaction(
            user_id="test_user",
            source_currency="USD",
            target_currency="EUR",
            source_amount=100.00,
            target_amount=85.00,
            exchange_rate=0.85,
            timestamp=base_time - timedelta(days=i)
        )
        transactions.append(tx)
    
    db_session.add_all(transactions)
    db_session.commit()
    
    yield transactions
    
    # Clean up
    db_session.query(Transaction).delete()
    db_session.commit()

@pytest.fixture
def mock_rates_response():
    """Mock response from exchange rates API."""
    return {
        "base": "EUR",
        "rates": {
            "USD": 1.18,
            "JPY": 129.55,
            "BRL": 6.35,
            "EUR": 1.0
        },
        "success": True,
        "timestamp": 1620000000
    }

@pytest.fixture
def test_data():
    """Common test data."""
    return {
        "user_id": "test_user",
        "from_currency": "USD",
        "to_currency": "EUR",
        "amount": "100.00",
        "exchange_rate": "0.85",
        "base_currency": "EUR",
        "rates": {
            "USD": "1.18",
            "JPY": "129.55",
            "BRL": "6.35"
        }
    }
