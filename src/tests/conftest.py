import contextlib
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.app import init_app
from api.models.base import Base
from config.database import get_sync_db as app_get_sync_db
from config.settings import settings


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


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
