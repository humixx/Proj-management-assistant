"""Simple test runner for repositories."""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.db.database import Base
from app.db.repositories.project_repo import ProjectRepository
from app.db.repositories.task_repo import TaskRepository
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.chat_repo import ChatRepository
from app.schemas import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


async def setup_db():
    """Setup test database."""
    import os
    from sqlalchemy import text
    
    # Get database credentials from environment
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    
    # Test database URL (use test database on PostgreSQL)
    TEST_DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/project_assistant_test"
    
    # Connect to default database to create test database
    default_engine = create_async_engine(
        f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/postgres",
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    
    async with default_engine.connect() as conn:
        # Drop test database if exists
        await conn.execute(text("DROP DATABASE IF EXISTS project_assistant_test"))
        # Create test database
        await conn.execute(text("CREATE DATABASE project_assistant_test"))
    
    await default_engine.dispose()
    
    # Create tables in test database
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    
    return engine


async def test_project_repository(session):
    """Test ProjectRepository."""
    print("\n=== Testing ProjectRepository ===")
    repo = ProjectRepository(session)
    
    # Test create
    project = await repo.create(ProjectCreate(
        name="Test Project",
        description="Testing project repo",
    ))
    print(f"  > Created project: {project.id} - {project.name}")
    
    # Test get_by_id
    retrieved = await repo.get_by_id(project.id)
    assert retrieved is not None, "Failed to retrieve project"
    print(f"  > Retrieved project: {retrieved.name}")
    
    # Test list_all
    projects, total = await repo.list_all()
    assert len(projects) == 1, "Should have 1 project"
    assert total == 1, "Total should be 1"
    print(f"  > Listed {total} project(s)")
    
    # Test update
    updated = await repo.update(project.id, ProjectUpdate(name="Updated Project"))
    assert updated.name == "Updated Project", "Failed to update project"
    print(f"  > Updated project name to: {updated.name}")
    
    # Test delete
    result = await repo.delete(project.id)
    assert result is True, "Failed to delete project"
    print(f"  > Deleted project")
    
    print("[PASS] ProjectRepository tests passed!\n")
    return True


async def test_task_repository(session):
    """Test TaskRepository."""
    print("\n=== Testing TaskRepository ===")
    
    # First create a project
    project_repo = ProjectRepository(session)
    project = await project_repo.create(ProjectCreate(
        name="Test Project",
        description="For testing tasks",
    ))
    
    repo = TaskRepository(session)
    
    # Test create
    task = await repo.create(project.id, TaskCreate(
        title="Test Task",
        description="Testing task repo",
        priority="high",
    ))
    print(f"  > Created task: {task.id} - {task.title}")
    
    # Test bulk_create
    tasks = await repo.bulk_create(project.id, [
        TaskCreate(title="Task 1", description="Desc 1"),
        TaskCreate(title="Task 2", description="Desc 2"),
    ])
    assert len(tasks) == 2, "Should have created 2 tasks"
    print(f"  > Bulk created {len(tasks)} tasks")
    
    # Test get_by_id
    retrieved = await repo.get_by_id(task.id)
    assert retrieved is not None, "Failed to retrieve task"
    print(f"  > Retrieved task: {retrieved.title}")
    
    # Test list_by_project
    all_tasks = await repo.list_by_project(project.id)
    assert len(all_tasks) == 3, "Should have 3 tasks"
    print(f"  > Listed {len(all_tasks)} task(s)")
    
    # Test filtering by priority
    high_tasks = await repo.list_by_project(project.id, priority="high")
    assert len(high_tasks) == 1, "Should have 1 high priority task"
    print(f"  > Filtered by priority: {len(high_tasks)} high priority task(s)")
    
    # Test update
    updated = await repo.update(task.id, TaskUpdate(status="completed"))
    assert updated.status == "completed", "Failed to update task"
    print(f"  > Updated task status to: {updated.status}")
    
    # Test delete
    result = await repo.delete(task.id)
    assert result is True, "Failed to delete task"
    print(f"  > Deleted task")
    
    print("[PASS] TaskRepository tests passed!\n")
    return True


async def test_document_repository(session):
    """Test DocumentRepository."""
    print("\n=== Testing DocumentRepository ===")
    
    # First create a project
    project_repo = ProjectRepository(session)
    project = await project_repo.create(ProjectCreate(
        name="Test Project",
        description="For testing documents",
    ))
    
    repo = DocumentRepository(session)
    
    # Test create
    document = await repo.create(
        project_id=project.id,
        filename="test.pdf",
        file_type="application/pdf",
        storage_path="/uploads/test.pdf",
        file_size=1024,
    )
    print(f"  > Created document: {document.id} - {document.filename}")
    
    # Test get_by_id
    retrieved = await repo.get_by_id(document.id)
    assert retrieved is not None, "Failed to retrieve document"
    print(f"  > Retrieved document: {retrieved.filename}")
    
    # Test list_by_project
    documents = await repo.list_by_project(project.id)
    assert len(documents) == 1, "Should have 1 document"
    print(f"  > Listed {len(documents)} document(s)")
    
    # Test add_chunks
    chunks = [
        {"chunk_text": "Chunk 1", "chunk_index": 0, "page_number": 1},
        {"chunk_text": "Chunk 2", "chunk_index": 1, "page_number": 1},
    ]
    chunk_count = await repo.add_chunks(document.id, chunks)
    assert chunk_count == 2, "Should have added 2 chunks"
    print(f"  > Added {chunk_count} chunk(s)")
    
    # Test update_processed
    updated = await repo.update_processed(document.id, chunk_count=2)
    assert updated.processed is True, "Failed to mark as processed"
    assert updated.chunk_count == 2, "Chunk count should be 2"
    print(f"  > Marked document as processed with {updated.chunk_count} chunks")
    
    # Test delete
    result = await repo.delete(document.id)
    assert result is True, "Failed to delete document"
    print(f"  > Deleted document")
    
    print("[PASS] DocumentRepository tests passed!\n")
    return True


async def test_chat_repository(session):
    """Test ChatRepository."""
    print("\n=== Testing ChatRepository ===")
    
    # First create a project
    project_repo = ProjectRepository(session)
    project = await project_repo.create(ProjectCreate(
        name="Test Project",
        description="For testing chat",
    ))
    
    repo = ChatRepository(session)
    
    # Test create
    message = await repo.create(
        project_id=project.id,
        role="user",
        content="Hello, this is a test message",
    )
    print(f"  > Created message: {message.id} - {message.role}")
    
    # Test create with tool calls
    message_with_tools = await repo.create(
        project_id=project.id,
        role="assistant",
        content="Creating a task",
        tool_calls={"tool": "create_task", "params": {}},
    )
    print(f"  > Created message with tool calls")
    
    # Test list_by_project
    messages = await repo.list_by_project(project.id)
    assert len(messages) == 2, "Should have 2 messages"
    print(f"  > Listed {len(messages)} message(s)")
    
    # Test clear_history
    deleted_count = await repo.clear_history(project.id)
    assert deleted_count == 2, "Should have deleted 2 messages"
    print(f"  > Cleared {deleted_count} message(s)")
    
    # Verify cleared
    messages_after = await repo.list_by_project(project.id)
    assert len(messages_after) == 0, "Should have 0 messages after clearing"
    print(f"  > Verified history cleared")
    
    print("[PASS] ChatRepository tests passed!\n")
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("REPOSITORY TESTS")
    print("=" * 60)
    
    try:
        engine = await setup_db()
        print("  > Database setup complete")
        
        # Create a session factory
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # Run tests
        async with async_session() as session:
            await test_project_repository(session)
        
        async with async_session() as session:
            await test_task_repository(session)
        
        async with async_session() as session:
            await test_document_repository(session)
        
        async with async_session() as session:
            await test_chat_repository(session)
        
        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
        # Cleanup: drop test database
        await engine.dispose()
        
    except Exception as e:
        print(f"\n[X] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
