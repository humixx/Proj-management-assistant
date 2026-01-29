"""Tests for ChatRepository."""
import pytest
from uuid import uuid4

from app.db.repositories.chat_repo import ChatRepository
from app.db.repositories.project_repo import ProjectRepository
from app.schemas import ProjectCreate


@pytest.mark.asyncio
class TestChatRepository:
    """Test cases for ChatRepository."""
    
    async def create_test_project(self, db_session):
        """Helper to create a test project."""
        repo = ProjectRepository(db_session)
        project_create = ProjectCreate(
            name="Test Project",
            description="For testing chat",
        )
        return await repo.create(project_create)
    
    async def test_create_message(self, db_session, sample_chat_data):
        """Test creating a new chat message."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        message = await repo.create(
            project_id=project.id,
            role=sample_chat_data["role"],
            content=sample_chat_data["content"],
        )
        
        assert message.id is not None
        assert message.project_id == project.id
        assert message.role == sample_chat_data["role"]
        assert message.content == sample_chat_data["content"]
        assert message.tool_calls is None
        assert message.tool_results is None
        assert message.created_at is not None
    
    async def test_create_message_with_tool_calls(self, db_session):
        """Test creating a message with tool calls."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        tool_calls = {
            "tool": "create_task",
            "parameters": {"title": "Test Task"},
        }
        
        message = await repo.create(
            project_id=project.id,
            role="assistant",
            content="Creating a task",
            tool_calls=tool_calls,
        )
        
        assert message.tool_calls == tool_calls
    
    async def test_create_message_with_tool_results(self, db_session):
        """Test creating a message with tool results."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        tool_results = {
            "success": True,
            "task_id": "12345",
        }
        
        message = await repo.create(
            project_id=project.id,
            role="tool",
            content="Task created successfully",
            tool_results=tool_results,
        )
        
        assert message.tool_results == tool_results
    
    async def test_list_by_project(self, db_session):
        """Test listing chat messages by project."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        # Create multiple messages
        for i in range(3):
            await repo.create(
                project_id=project.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
            )
        
        # List all messages
        messages = await repo.list_by_project(project.id)
        
        assert len(messages) == 3
        # Should be ordered by created_at asc (oldest first)
        assert messages[0].content == "Message 0"
        assert messages[1].content == "Message 1"
        assert messages[2].content == "Message 2"
    
    async def test_list_by_project_with_limit(self, db_session):
        """Test listing messages with limit."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        # Create many messages
        for i in range(60):
            await repo.create(
                project_id=project.id,
                role="user",
                content=f"Message {i}",
            )
        
        # List with default limit (50)
        messages = await repo.list_by_project(project.id)
        
        assert len(messages) == 50
        
        # List with custom limit
        messages = await repo.list_by_project(project.id, limit=10)
        
        assert len(messages) == 10
    
    async def test_list_by_project_empty(self, db_session):
        """Test listing messages for a project with no messages."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        messages = await repo.list_by_project(project.id)
        
        assert len(messages) == 0
    
    async def test_clear_history(self, db_session):
        """Test clearing chat history for a project."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        # Create multiple messages
        for i in range(5):
            await repo.create(
                project_id=project.id,
                role="user",
                content=f"Message {i}",
            )
        
        # Verify messages exist
        messages = await repo.list_by_project(project.id)
        assert len(messages) == 5
        
        # Clear history
        deleted_count = await repo.clear_history(project.id)
        
        assert deleted_count == 5
        
        # Verify messages are gone
        messages = await repo.list_by_project(project.id)
        assert len(messages) == 0
    
    async def test_clear_history_empty(self, db_session):
        """Test clearing history for a project with no messages."""
        project = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        deleted_count = await repo.clear_history(project.id)
        
        assert deleted_count == 0
    
    async def test_messages_isolated_by_project(self, db_session):
        """Test that messages are isolated between projects."""
        # Create two projects
        project1 = await self.create_test_project(db_session)
        repo = ChatRepository(db_session)
        
        project_repo = ProjectRepository(db_session)
        project2 = await project_repo.create(
            ProjectCreate(name="Project 2", description="Second project")
        )
        
        # Add messages to both projects
        await repo.create(project_id=project1.id, role="user", content="Project 1 message")
        await repo.create(project_id=project2.id, role="user", content="Project 2 message")
        
        # List messages for each project
        project1_messages = await repo.list_by_project(project1.id)
        project2_messages = await repo.list_by_project(project2.id)
        
        assert len(project1_messages) == 1
        assert len(project2_messages) == 1
        assert project1_messages[0].content == "Project 1 message"
        assert project2_messages[0].content == "Project 2 message"
        
        # Clear project 1 history
        await repo.clear_history(project1.id)
        
        # Project 2 messages should still exist
        project2_messages = await repo.list_by_project(project2.id)
        assert len(project2_messages) == 1
