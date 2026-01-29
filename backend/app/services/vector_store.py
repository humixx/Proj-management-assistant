"""Vector store service for similarity search using pgvector."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk


class VectorStore:
    """Service for vector storage and similarity search."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize vector store.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def search_similar(
        self,
        project_id: UUID,
        query_embedding: list[float],
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict]:
        """
        Search for similar document chunks using cosine similarity.
        
        Args:
            project_id: Project ID to search within
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of results with chunk_text, document_id, document_name, page_number, score
        """
        # Convert embedding to string format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Build query using pgvector cosine distance
        # Note: cosine distance = 1 - cosine similarity, so lower is better
        # We compute score as 1 - distance
        # Using CAST instead of :: to avoid parameter binding issues
        query = text("""
            SELECT 
                dc.id,
                dc.chunk_text,
                dc.chunk_index,
                dc.page_number,
                d.id as document_id,
                d.filename as document_name,
                1 - (dc.embedding <=> CAST(:embedding AS vector)) as score
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.project_id = CAST(:project_id AS uuid)
              AND dc.embedding IS NOT NULL
              AND 1 - (dc.embedding <=> CAST(:embedding AS vector)) >= :threshold
            ORDER BY dc.embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """)
        
        result = await self.db.execute(
            query,
            {
                "embedding": embedding_str,
                "project_id": str(project_id),
                "threshold": threshold,
                "top_k": top_k,
            },
        )
        
        rows = result.fetchall()
        
        return [
            {
                "chunk_text": row.chunk_text,
                "document_id": row.document_id,
                "document_name": row.document_name,
                "page_number": row.page_number,
                "score": float(row.score),
            }
            for row in rows
        ]
    
    async def delete_by_document(self, document_id: UUID) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Number of deleted chunks
        """
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def get_document_chunks(self, document_id: UUID) -> list[DocumentChunk]:
        """
        Get all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
        """
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
