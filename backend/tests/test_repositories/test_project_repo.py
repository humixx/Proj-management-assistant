"""Tests for ProjectRepository."""
import pytest
from uuid import uuid4

from app.db.repositories.project_repo import ProjectRepository
from app.schemas import ProjectCreate, ProjectUpdate, ProjectSettings


@pytest.mark.asyncio
class TestProjectRepository:
    """Test cases for ProjectRepository."""
    
    async def test_create_project(self, db_session, sample_project_data):
        """Test creating a new project."""
        repo = ProjectRepository(db_session)
        
        project_create = ProjectCreate(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
            settings=ProjectSettings(**sample_project_data["settings"]),
        )
        
        project = await repo.create(project_create)
        
        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.description == sample_project_data["description"]
        assert project.settings == sample_project_data["settings"]
        assert project.created_at is not None
        assert project.updated_at is not None
    
    async def test_create_project_without_settings(self, db_session):
        """Test creating a project without settings."""
        repo = ProjectRepository(db_session)
        
        project_create = ProjectCreate(
            name="Simple Project",
            description="No settings",
        )
        
        project = await repo.create(project_create)
        
        assert project.id is not None
        assert project.name == "Simple Project"
        assert project.settings is None
    
    async def test_get_by_id(self, db_session, sample_project_data):
        """Test getting a project by ID."""
        repo = ProjectRepository(db_session)
        
        # Create a project
        project_create = ProjectCreate(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
        )
        created_project = await repo.create(project_create)
        
        # Retrieve it
        retrieved_project = await repo.get_by_id(created_project.id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.name == created_project.name
    
    async def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent project."""
        repo = ProjectRepository(db_session)
        
        non_existent_id = uuid4()
        project = await repo.get_by_id(non_existent_id)
        
        assert project is None
    
    async def test_list_all(self, db_session):
        """Test listing all projects with pagination."""
        repo = ProjectRepository(db_session)
        
        # Create multiple projects
        for i in range(5):
            project_create = ProjectCreate(
                name=f"Project {i}",
                description=f"Description {i}",
            )
            await repo.create(project_create)
        
        # List all projects
        projects, total = await repo.list_all(skip=0, limit=10)
        
        assert len(projects) == 5
        assert total == 5
        # Should be ordered by created_at desc
        assert projects[0].name == "Project 4"
    
    async def test_list_all_pagination(self, db_session):
        """Test pagination in list_all."""
        repo = ProjectRepository(db_session)
        
        # Create multiple projects
        for i in range(10):
            project_create = ProjectCreate(
                name=f"Project {i}",
                description=f"Description {i}",
            )
            await repo.create(project_create)
        
        # Test skip and limit
        projects, total = await repo.list_all(skip=3, limit=3)
        
        assert len(projects) == 3
        assert total == 10
    
    async def test_update(self, db_session, sample_project_data):
        """Test updating a project."""
        repo = ProjectRepository(db_session)
        
        # Create a project
        project_create = ProjectCreate(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
        )
        project = await repo.create(project_create)
        
        # Update it
        project_update = ProjectUpdate(
            name="Updated Name",
            description="Updated Description",
        )
        updated_project = await repo.update(project.id, project_update)
        
        assert updated_project is not None
        assert updated_project.id == project.id
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "Updated Description"
    
    async def test_update_partial(self, db_session, sample_project_data):
        """Test partial update of a project."""
        repo = ProjectRepository(db_session)
        
        # Create a project
        project_create = ProjectCreate(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
        )
        project = await repo.create(project_create)
        
        # Update only name
        project_update = ProjectUpdate(name="New Name Only")
        updated_project = await repo.update(project.id, project_update)
        
        assert updated_project.name == "New Name Only"
        assert updated_project.description == sample_project_data["description"]
    
    async def test_update_not_found(self, db_session):
        """Test updating a non-existent project."""
        repo = ProjectRepository(db_session)
        
        non_existent_id = uuid4()
        project_update = ProjectUpdate(name="New Name")
        
        updated_project = await repo.update(non_existent_id, project_update)
        
        assert updated_project is None
    
    async def test_delete(self, db_session, sample_project_data):
        """Test deleting a project."""
        repo = ProjectRepository(db_session)
        
        # Create a project
        project_create = ProjectCreate(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
        )
        project = await repo.create(project_create)
        
        # Delete it
        result = await repo.delete(project.id)
        
        assert result is True
        
        # Verify it's gone
        deleted_project = await repo.get_by_id(project.id)
        assert deleted_project is None
    
    async def test_delete_not_found(self, db_session):
        """Test deleting a non-existent project."""
        repo = ProjectRepository(db_session)
        
        non_existent_id = uuid4()
        result = await repo.delete(non_existent_id)
        
        assert result is False
