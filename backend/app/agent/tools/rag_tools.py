"""RAG tools for document search."""
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.services.embedding_service import embedding_service
from app.services.vector_store import VectorStore
from app.config import settings


class SearchDocumentsTool(BaseTool):
    """Tool for searching documents using semantic similarity."""
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
    
    @property
    def name(self) -> str:
        return "search_documents"
    
    @property
    def description(self) -> str:
        return """Search through uploaded documents using semantic similarity. 
        Use this when you need to find information from the project's documents.
        Returns relevant text chunks with source document and page number."""
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        }
    
    async def execute(self, query: str, top_k: int = 5) -> Any:
        query_embedding = await embedding_service.embed_text(query)
        
        vector_store = VectorStore(self.db)
        results = await vector_store.search_similar(
            project_id=self.project_id,
            query_embedding=query_embedding,
            top_k=top_k,
            threshold=settings.SIMILARITY_THRESHOLD,
        )
        
        if not results:
            return {
                "found": False,
                "message": "No relevant information found in the documents.",
                "results": [],
            }
        
        return {
            "found": True,
            "message": f"Found {len(results)} relevant chunks.",
            "results": [
                {
                    "text": r["chunk_text"],
                    "document": r["document_name"],
                    "page": r["page_number"],
                    "relevance": round(r["score"], 3),
                }
                for r in results
            ],
        }
