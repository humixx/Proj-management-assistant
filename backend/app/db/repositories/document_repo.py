"""Document repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk
from app.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    """Repository for document operations."""
    
    async def create(
        self,
        project_id: UUID,
        filename: str,
        file_type: str,
        storage_path: str,
        file_size: int,
    ) -> Document:
        """Create a new document record."""
        document = Document(
            project_id=project_id,
            filename=filename,
            file_type=file_type,
            storage_path=storage_path,
            file_size=file_size,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID."""
        stmt = select(Document).where(Document.id == document_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_project(self, project_id: UUID) -> list[Document]:
        """List all documents for a project."""
        stmt = select(Document).where(Document.project_id == project_id).order_by(Document.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update_processed(self, document_id: UUID, chunk_count: int) -> Optional[Document]:
        """Mark document as processed with chunk count."""
        document = await self.get_by_id(document_id)
        if not document:
            return None
        
        document.processed = True
        document.chunk_count = chunk_count
        
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def add_chunks(self, document_id: UUID, chunks: list[dict]) -> int:
        """Add chunks to a document."""
        for chunk_data in chunks:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_text=chunk_data["chunk_text"],
                chunk_index=chunk_data["chunk_index"],
                page_number=chunk_data.get("page_number"),
                embedding=chunk_data.get("embedding"),
            )
            self.db.add(chunk)
        
        await self.db.commit()
        return len(chunks)
    
    async def delete(self, document_id: UUID) -> bool:
        """Delete a document and its chunks."""
        document = await self.get_by_id(document_id)
        if not document:
            return False
        
        await self.db.delete(document)
        await self.db.commit()
        return True
