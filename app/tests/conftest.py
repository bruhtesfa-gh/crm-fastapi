import asyncio
from typing import AsyncGenerator, Dict

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import Base
from app.tests.test_seed import create_defaults, create_tables
from app.tests.utils.db import get_test_db
from app.util.setting import get_settings

settings = get_settings()


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create an event_loop fixture at session scope so everything runs on the same loop.
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Create a test engine and session maker for the in-memory SQLite database.
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# Override the original get_db dependency so that your app uses the test database.
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = get_test_db


# Fixture to set up the database tables for the tests.
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Create an AsyncClient fixture that uses ASGITransport with your FastAPI app.
@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
async def seed_database():
    # Create tables and seed data before tests run.
    await create_tables()
    await create_defaults()


@pytest.fixture
def admin_token_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDU5NTk4NDQuMDI4NywibmJmIjoxNzQzMzY3ODQ0LCJzdWIiOiIxIiwidXNlciI6eyJjcmVhdGVkX2F0IjoiMjAyNS0wMy0zMFQxODo0OTo1NS43OTA1NzUiLCJ1cGRhdGVkX2F0IjoiMjAyNS0wMy0zMFQxODo0OTo1NS43OTA1NzUiLCJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbkBnbWFpbC5jb20iLCJyb2xlX2lkIjoxLCJyb2xlIjp7ImlkIjoxLCJuYW1lIjoiQWRtaW4iLCJkZXNjcmlwdGlvbiI6IkFkbWluIHdpdGggcGVybWlzc2lvbiB0byBtYW5hZ2UgdXNlcnMsIHJvbGVzLCBhbmQgYXVkaXQgbG9ncy4iLCJwZXJtaXNzaW9ucyI6W3siaWQiOjIsIm5hbWUiOiJHRVQ6L3VzZXJzL21lLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBHRVQ6L3VzZXJzL21lLyJ9LHsiaWQiOjMsIm5hbWUiOiJHRVQ6L3VzZXJzLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBHRVQ6L3VzZXJzLyJ9LHsiaWQiOjQsIm5hbWUiOiJHRVQ6L3VzZXJzLyovIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIEdFVDovdXNlcnMvKi8ifSx7ImlkIjo1LCJuYW1lIjoiUFVUOi91c2Vycy8qLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBQVVQ6L3VzZXJzLyovIn0seyJpZCI6NiwibmFtZSI6IkRFTEVURTovdXNlcnMvKi8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gREVMRVRFOi91c2Vycy8qLyJ9LHsiaWQiOjcsIm5hbWUiOiJQVVQ6L3VzZXJzLyovcm9sZS8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gUFVUOi91c2Vycy8qL3JvbGUvIn0seyJpZCI6OCwibmFtZSI6IkdFVDovcm9sZXMvIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIEdFVDovcm9sZXMvIn0seyJpZCI6OSwibmFtZSI6IlBPU1Q6L3JvbGVzLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBQT1NUOi9yb2xlcy8ifSx7ImlkIjoxMCwibmFtZSI6IkdFVDovcm9sZXMvKi8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gR0VUOi9yb2xlcy8qLyJ9LHsiaWQiOjExLCJuYW1lIjoiUFVUOi9yb2xlcy8qLyIsImRlc2NyaXB0aW9uIjoiUGVybWlzc2lvbiB0byBQVVQ6L3JvbGVzLyovIn0seyJpZCI6MTIsIm5hbWUiOiJERUxFVEU6L3JvbGVzLyovIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIERFTEVURTovcm9sZXMvKi8ifSx7ImlkIjoxMywibmFtZSI6IlBPU1Q6L3JvbGVzLyovcGVybWlzc2lvbnMvKi8iLCJkZXNjcmlwdGlvbiI6IlBlcm1pc3Npb24gdG8gUE9TVDovcm9sZXMvKi9wZXJtaXNzaW9ucy8qLyJ9LHsiaWQiOjE0LCJuYW1lIjoiREVMRVRFOi9yb2xlcy8qL3Blcm1pc3Npb25zLyovIiwiZGVzY3JpcHRpb24iOiJQZXJtaXNzaW9uIHRvIERFTEVURTovcm9sZXMvKi9wZXJtaXNzaW9ucy8qLyJ9XX19LCJ0eXBlIjoiYXBpIiwiYWN0aW9uIjoiYWNjZXNzIn0.Un09M0Z2FBks7U6dSjpMCSH4JmfXosiMDL9slzfKER4"
    }
