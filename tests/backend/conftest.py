import asyncio
import os
import sys
from pathlib import Path

# create an isolated sqlite db for each test run
TEST_DB_URL_TEMPLATE = "sqlite+aiosqlite:///{db_file}"

os.environ["TESTING"] = "1"
os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test"
os.environ["OPENAI_API_KEY"] = "test-openai-key"

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Make sure the backend package (which contains the `app` module) is importable.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.append(str(BACKEND_PATH))

import types, openai, azure.storage.blob, faiss, pickle

openai.OpenAI = lambda *a, **k: types.SimpleNamespace()
azure.storage.blob.BlobServiceClient = types.SimpleNamespace(from_connection_string=lambda *a, **k: types.SimpleNamespace(get_container_client=lambda *a, **k: types.SimpleNamespace(get_blob_client=lambda *a, **k: types.SimpleNamespace(download_blob=lambda *a, **k: types.SimpleNamespace(readall=lambda: b"")), list_blobs=lambda *a, **k: [])))
faiss.read_index = lambda *a, **k: faiss.IndexFlatL2(1536)
pickle.load = lambda *a, **k: []

# Mock cohere module
sys.modules['cohere'] = types.SimpleNamespace(
    Client=lambda *a, **k: types.SimpleNamespace(
        classify=lambda *a, **k: types.SimpleNamespace(
            classifications=[
                types.SimpleNamespace(
                    prediction="general_query",
                    confidence=0.8
                )
            ]
        )
    )
)

from app.db.sqlite import get_db
from app.models.base import Base
from app.routers.auth import router as auth_router
from app.routers.chatbot import router as chat_router


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session (pytest-asyncio requirement)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
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


@pytest_asyncio.fixture()
async def _session(_engine):
    """Provide a fresh SQLAlchemy AsyncSession to every test function."""
    async_session = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # In tests we usually want changes rolled back at the end of the test to
        # guarantee isolation. Sub-transactions with SAVEPOINTs are not yet
        # supported for SQLite+aiosqlite, so we simply use a new database file
        # per test session and a new session per test function.
        yield session


@pytest_asyncio.fixture()
async def app(_session):
    """Create a FastAPI app instance with dependency overrides for testing."""

    async def override_get_db():
        """Yield the test database session instead of the production one."""
        yield _session

    application = FastAPI()
    application.include_router(auth_router, prefix="/auth", tags=["auth"])
    application.include_router(chat_router, prefix="/chat", tags=["chat"])
    application.dependency_overrides[get_db] = override_get_db
    yield application


@pytest_asyncio.fixture()
async def client(app):
    """Return an httpx.AsyncClient that targets the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
def test_user():
    """Default user payload used across auth endpoint tests."""
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password123",
        "organization_id": None,
    } 