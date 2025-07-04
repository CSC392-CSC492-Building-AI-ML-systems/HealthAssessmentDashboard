import asyncio
import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Make sure the backend package (which contains the `app` module) is importable.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.append(str(BACKEND_PATH))

from app.db.sqlite import get_db
from app.models.base import Base
from app.routers.auth import router as auth_router
from app.core.config import settings

# GLOBAL SETTINGS FOR TESTING
settings.jwt_secret_key = "TEST_SECRET_KEY"

# create an isolated sqlite db for each test run
TEST_DB_URL_TEMPLATE = "sqlite+aiosqlite:///{db_file}"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session (pytest-asyncio requirement)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def _engine(tmp_path_factory):
    """Create the test database engine and initialise the schema once."""
    db_dir = tmp_path_factory.mktemp("db")
    db_file = db_dir / "test.db"
    db_url = TEST_DB_URL_TEMPLATE.format(db_file=db_file.as_posix())

    engine = create_async_engine(db_url, future=True, echo=False)

    # Create database schema.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Dispose engine after tests complete.
    await engine.dispose()


@pytest.fixture()
async def _session(_engine):
    """Provide a fresh SQLAlchemy AsyncSession to every test function."""
    async_session = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # In tests we usually want changes rolled back at the end of the test to
        # guarantee isolation. Sub-transactions with SAVEPOINTs are not yet
        # supported for SQLite+aiosqlite, so we simply use a new database file
        # per test session and a new session per test function.
        yield session


@pytest.fixture()
async def app(_session):
    """Create a FastAPI app instance with dependency overrides for testing."""

    async def override_get_db():
        """Yield the test database session instead of the production one."""
        yield _session

    application = FastAPI()
    application.include_router(auth_router, prefix="/auth", tags=["auth"])
    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture()
async def client(app):
    """Return an httpx.AsyncClient that targets the test app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
def test_user():
    """Default user payload used across auth endpoint tests."""
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password123",
        "organization_id": None,
    } 