"""Tests for DocumentRepository."""
import pytest
from uuid import uuid4

from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.project_repo import ProjectRepository
from app.schemas import ProjectCreate


@pytest.mark.asyncio
class TestDocumentRepository:
    """Test cases for DocumentRepository."""
    
    async def create_test_project(self, db_session):
        """Helper to create a test project."""
        repo = ProjectRepository(db_session)
        project_create = ProjectCreate(
            name="Test Project",
            description="For testing documents",
        )
        return await repo.create(project_create)
    
    async def test_create_document(self, db_session, sample_document_data):
        """Test creating a new document."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        document = await repo.create(
            project_id=project.id,
            filename=sample_document_data["filename"],
            file_type=sample_document_data["file_type"],
            storage_path=sample_document_data["storage_path"],
            file_size=sample_document_data["file_size"],
        )
        
        assert document.id is not None
        assert document.project_id == project.id
        assert document.filename == sample_document_data["filename"]
        assert document.file_type == sample_document_data["file_type"]
        assert document.storage_path == sample_document_data["storage_path"]
        assert document.file_size == sample_document_data["file_size"]
        assert document.processed is False
        assert document.chunk_count == 0
        assert document.created_at is not None
    
    async def test_get_by_id(self, db_session, sample_document_data):
        """Test getting a document by ID."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        # Create a document
        created_doc = await repo.create(
            project_id=project.id,
            filename=sample_document_data["filename"],
            file_type=sample_document_data["file_type"],
            storage_path=sample_document_data["storage_path"],
            file_size=sample_document_data["file_size"],
        )
        
        # Retrieve it
        retrieved_doc = await repo.get_by_id(created_doc.id)
        
        assert retrieved_doc is not None
        assert retrieved_doc.id == created_doc.id
        assert retrieved_doc.filename == created_doc.filename
    
    async def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent document."""
        repo = DocumentRepository(db_session)
        
        non_existent_id = uuid4()
        document = await repo.get_by_id(non_existent_id)
        
        assert document is None
    
    async def test_list_by_project(self, db_session, sample_document_data):
        """Test listing documents by project."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        # Create multiple documents
        for i in range(3):
            await repo.create(
                project_id=project.id,
                filename=f"doc{i}.pdf",
                file_type="application/pdf",
                storage_path=f"/uploads/doc{i}.pdf",
                file_size=1024 * (i + 1),
            )
        
        # List all documents for project
        documents = await repo.list_by_project(project.id)
        
        assert len(documents) == 3
        # Should be ordered by created_at desc
        assert documents[0].filename == "doc2.pdf"
    
    async def test_update_processed(self, db_session, sample_document_data):
        """Test marking a document as processed."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        # Create a document
        document = await repo.create(
            project_id=project.id,
            filename=sample_document_data["filename"],
            file_type=sample_document_data["file_type"],
            storage_path=sample_document_data["storage_path"],
            file_size=sample_document_data["file_size"],
        )
        
        assert document.processed is False
        assert document.chunk_count == 0
        
        # Mark as processed
        updated_doc = await repo.update_processed(document.id, chunk_count=5)
        
        assert updated_doc is not None
        assert updated_doc.processed is True
        assert updated_doc.chunk_count == 5
    
    async def test_update_processed_not_found(self, db_session):
        """Test updating a non-existent document."""
        repo = DocumentRepository(db_session)
        
        non_existent_id = uuid4()
        updated_doc = await repo.update_processed(non_existent_id, chunk_count=5)
        
        assert updated_doc is None
    
    async def test_add_chunks(self, db_session, sample_document_data):
        """Test adding chunks to a document."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        # Create a document
        document = await repo.create(
            project_id=project.id,
            filename=sample_document_data["filename"],
            file_type=sample_document_data["file_type"],
            storage_path=sample_document_data["storage_path"],
            file_size=sample_document_data["file_size"],
        )
        
        # Add chunks
        chunks = [
            {
                "chunk_text": "This is chunk 1",
                "chunk_index": 0,
                "page_number": 1,
            },
            {
                "chunk_text": "This is chunk 2",
                "chunk_index": 1,
                "page_number": 1,
            },
            {
                "chunk_text": "This is chunk 3",
                "chunk_index": 2,
                "page_number": 2,
            },
        ]
        
        chunk_count = await repo.add_chunks(document.id, chunks)
        
        assert chunk_count == 3
    
    async def test_add_chunks_with_embeddings(self, db_session, sample_document_data):
        """Test adding chunks with embeddings."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        # Create a document
        document = await repo.create(
            project_id=project.id,
            filename=sample_document_data["filename"],
            file_type=sample_document_data["file_type"],
            storage_path=sample_document_data["storage_path"],
            file_size=sample_document_data["file_size"],
        )
        
        # Add chunks with embeddings
        chunks = [
            {
                "chunk_text": "This is chunk 1",
                "chunk_index": 0,
                "page_number": 1,
                "embedding": [0.1, 0.2, 0.3],
            },
        ]
        
        chunk_count = await repo.add_chunks(document.id, chunks)
        
        assert chunk_count == 1
    
    async def test_delete(self, db_session, sample_document_data):
        """Test deleting a document."""
        project = await self.create_test_project(db_session)
        repo = DocumentRepository(db_session)
        
        # Create a document
        document = await repo.create(
            project_id=project.id,
            filename=sample_document_data["filename"],
            file_type=sample_document_data["file_type"],
            storage_path=sample_document_data["storage_path"],
            file_size=sample_document_data["file_size"],
        )
        
        # Add some chunks
        chunks = [
            {
                "chunk_text": "Chunk 1",
                "chunk_index": 0,
            },
        ]
        await repo.add_chunks(document.id, chunks)
        
        # Delete document (should cascade delete chunks)
        result = await repo.delete(document.id)
        
        assert result is True
        
        # Verify it's gone
        deleted_doc = await repo.get_by_id(document.id)
        assert deleted_doc is None
    
    async def test_delete_not_found(self, db_session):
        """Test deleting a non-existent document."""
        repo = DocumentRepository(db_session)
        
        non_existent_id = uuid4()
        result = await repo.delete(non_existent_id)
        
        assert result is False
