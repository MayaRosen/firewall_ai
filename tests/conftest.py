"""
Pytest configuration and fixtures for all tests
"""
import pytest
from app.database.connection import db_manager


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database connection pool for all tests"""
    db_manager.initialize()
    yield
    db_manager.close()


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test"""
    # This runs before each test
    with db_manager.get_cursor() as cur:
        cur.execute("DELETE FROM connections")
        cur.execute("DELETE FROM policies")
    
    yield
    
    # This runs after each test (cleanup)
    with db_manager.get_cursor() as cur:
        cur.execute("DELETE FROM connections")
        cur.execute("DELETE FROM policies")
