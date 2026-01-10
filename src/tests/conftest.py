import contextlib
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.app import init_app
from api.models.base import Base
from config.database import get_sync_db as app_get_sync_db
from config.initializers.initialize import InitializeTask
from config.settings import settings


# Disable cache via the cache_manager singleton for the whole test session.
@pytest.fixture(scope="session", autouse=True)
def disable_cache_manager():
    from api.helpers.cache_manager import cache_manager

    prev = cache_manager.is_enabled
    cache_manager.is_enabled = False
    try:
        yield
    finally:
        cache_manager.is_enabled = prev


# Import shared fixtures
pytest_plugins = ["tests.fixtures.payment_methods", "tests.fixtures.transactions"]


@pytest.fixture(scope="session")
def test_engine():
    # Build test engine using settings from src/config
    engine = create_engine(settings.test_database_url, future=True)
    # Create tables if models exist
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        with contextlib.suppress(Exception):
            Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def initialize_test_data(test_engine):
    """Initialize default data for tests using the existing initializer."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = SessionLocal()
    try:
        initializer = InitializeTask()
        initializer.create_default_payment_methods(db)
    finally:
        db.close()


@pytest.fixture()
def db_session(test_engine, initialize_test_data) -> Generator[Session]:
    # Create a connection and begin a transaction
    connection = test_engine.connect()
    transaction = connection.begin()

    # Create session bound to this connection
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()  # Rollback the transaction to reset database state
        connection.close()


@pytest.fixture()
def app(db_session):
    app = init_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[app_get_sync_db] = override_get_db
    return app


@pytest.fixture()
def client(app) -> TestClient:
    return TestClient(app)
