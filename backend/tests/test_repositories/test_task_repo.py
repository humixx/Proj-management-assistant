"""Tests for TaskRepository."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.db.repositories.task_repo import TaskRepository
from app.db.repositories.project_repo import ProjectRepository
from app.schemas import TaskCreate, TaskUpdate, ProjectCreate


@pytest.mark.asyncio
class TestTaskRepository:
    """Test cases for TaskRepository."""
    
    async def create_test_project(self, db_session):
        """Helper to create a test project."""
        repo = ProjectRepository(db_session)
        project_create = ProjectCreate(
            name="Test Project",
            description="For testing tasks",
        )
        return await repo.create(project_create)
    
    async def test_create_task(self, db_session, sample_task_data):
        """Test creating a new task."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        task_create = TaskCreate(
            title=sample_task_data["title"],
            description=sample_task_data["description"],
            priority=sample_task_data["priority"],
            assignee=sample_task_data["assignee"],
            tags=sample_task_data["tags"],
        )
        
        task = await repo.create(project.id, task_create)
        
        assert task.id is not None
        assert task.project_id == project.id
        assert task.title == sample_task_data["title"]
        assert task.description == sample_task_data["description"]
        assert task.priority == sample_task_data["priority"]
        assert task.assignee == sample_task_data["assignee"]
        assert task.tags == sample_task_data["tags"]
        assert task.status == "pending"  # Default status
        assert task.created_at is not None
    
    async def test_create_task_with_defaults(self, db_session):
        """Test creating a task with default values."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        task_create = TaskCreate(
            title="Simple Task",
            description="No priority specified",
        )
        
        task = await repo.create(project.id, task_create)
        
        assert task.priority == "medium"  # Default
        assert task.status == "pending"
    
    async def test_bulk_create(self, db_session):
        """Test creating multiple tasks at once."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        tasks_data = [
            TaskCreate(title=f"Task {i}", description=f"Description {i}")
            for i in range(3)
        ]
        
        created_tasks = await repo.bulk_create(project.id, tasks_data)
        
        assert len(created_tasks) == 3
        assert all(task.id is not None for task in created_tasks)
        assert all(task.project_id == project.id for task in created_tasks)
    
    async def test_get_by_id(self, db_session, sample_task_data):
        """Test getting a task by ID."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create a task
        task_create = TaskCreate(
            title=sample_task_data["title"],
            description=sample_task_data["description"],
        )
        created_task = await repo.create(project.id, task_create)
        
        # Retrieve it
        retrieved_task = await repo.get_by_id(created_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title
    
    async def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent task."""
        repo = TaskRepository(db_session)
        
        non_existent_id = uuid4()
        task = await repo.get_by_id(non_existent_id)
        
        assert task is None
    
    async def test_list_by_project(self, db_session):
        """Test listing tasks by project."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create multiple tasks
        for i in range(3):
            task_create = TaskCreate(
                title=f"Task {i}",
                description=f"Description {i}",
            )
            await repo.create(project.id, task_create)
        
        # List all tasks for project
        tasks = await repo.list_by_project(project.id)
        
        assert len(tasks) == 3
        # Should be ordered by created_at desc
        assert tasks[0].title == "Task 2"
    
    async def test_list_by_project_filter_status(self, db_session):
        """Test filtering tasks by status."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create tasks with different statuses
        task1 = await repo.create(project.id, TaskCreate(title="Task 1"))
        task2 = await repo.create(project.id, TaskCreate(title="Task 2"))
        
        # Update one to in_progress
        await repo.update(task2.id, TaskUpdate(status="in_progress"))
        
        # Filter by status
        pending_tasks = await repo.list_by_project(project.id, status="pending")
        in_progress_tasks = await repo.list_by_project(project.id, status="in_progress")
        
        assert len(pending_tasks) == 1
        assert len(in_progress_tasks) == 1
        assert pending_tasks[0].id == task1.id
    
    async def test_list_by_project_filter_priority(self, db_session):
        """Test filtering tasks by priority."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create tasks with different priorities
        await repo.create(project.id, TaskCreate(title="High", priority="high"))
        await repo.create(project.id, TaskCreate(title="Low", priority="low"))
        
        # Filter by priority
        high_tasks = await repo.list_by_project(project.id, priority="high")
        
        assert len(high_tasks) == 1
        assert high_tasks[0].title == "High"
    
    async def test_list_by_project_filter_assignee(self, db_session):
        """Test filtering tasks by assignee."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create tasks with different assignees
        await repo.create(project.id, TaskCreate(title="Task 1", assignee="user1@test.com"))
        await repo.create(project.id, TaskCreate(title="Task 2", assignee="user2@test.com"))
        
        # Filter by assignee
        user1_tasks = await repo.list_by_project(project.id, assignee="user1@test.com")
        
        assert len(user1_tasks) == 1
        assert user1_tasks[0].title == "Task 1"
    
    async def test_update(self, db_session, sample_task_data):
        """Test updating a task."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create a task
        task_create = TaskCreate(
            title=sample_task_data["title"],
            description=sample_task_data["description"],
        )
        task = await repo.create(project.id, task_create)
        
        # Update it
        task_update = TaskUpdate(
            title="Updated Title",
            status="in_progress",
            priority="critical",
        )
        updated_task = await repo.update(task.id, task_update)
        
        assert updated_task is not None
        assert updated_task.id == task.id
        assert updated_task.title == "Updated Title"
        assert updated_task.status == "in_progress"
        assert updated_task.priority == "critical"
    
    async def test_update_partial(self, db_session):
        """Test partial update of a task."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create a task
        task_create = TaskCreate(
            title="Original Title",
            description="Original Description",
            priority="high",
        )
        task = await repo.create(project.id, task_create)
        
        # Update only status
        task_update = TaskUpdate(status="completed")
        updated_task = await repo.update(task.id, task_update)
        
        assert updated_task.status == "completed"
        assert updated_task.title == "Original Title"
        assert updated_task.priority == "high"
    
    async def test_update_not_found(self, db_session):
        """Test updating a non-existent task."""
        repo = TaskRepository(db_session)
        
        non_existent_id = uuid4()
        task_update = TaskUpdate(title="New Title")
        
        updated_task = await repo.update(non_existent_id, task_update)
        
        assert updated_task is None
    
    async def test_delete(self, db_session, sample_task_data):
        """Test deleting a task."""
        project = await self.create_test_project(db_session)
        repo = TaskRepository(db_session)
        
        # Create a task
        task_create = TaskCreate(
            title=sample_task_data["title"],
            description=sample_task_data["description"],
        )
        task = await repo.create(project.id, task_create)
        
        # Delete it
        result = await repo.delete(task.id)
        
        assert result is True
        
        # Verify it's gone
        deleted_task = await repo.get_by_id(task.id)
        assert deleted_task is None
    
    async def test_delete_not_found(self, db_session):
        """Test deleting a non-existent task."""
        repo = TaskRepository(db_session)
        
        non_existent_id = uuid4()
        result = await repo.delete(non_existent_id)
        
        assert result is False
