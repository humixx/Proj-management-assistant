"""Pytest fixtures for testing."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.db.database import Base
from app.db.models import Project, Task, Document, DocumentChunk, ChatMessage


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project",
        "settings": {
            "default_priority": "medium",
            "auto_assign": False,
        }
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task",
        "priority": "high",
        "assignee": "test@example.com",
        "tags": ["backend", "testing"],
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "filename": "test.pdf",
        "file_type": "application/pdf",
        "storage_path": "/uploads/test.pdf",
        "file_size": 1024,
    }


@pytest.fixture
def sample_chat_data():
    """Sample chat message data for testing."""
    return {
        "role": "user",
        "content": "Hello, this is a test message",
    }
