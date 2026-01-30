"""Document schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: UUID
    project_id: UUID
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    processed: bool
    chunk_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""
    documents: list[DocumentResponse]
    total: int


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk."""
    id: UUID
    chunk_text: str
    chunk_index: int
    page_number: Optional[int] = None
    document_name: str


class SearchResult(BaseModel):
    """Schema for a single search result."""
    chunk_text: str
    document_id: UUID
    document_name: str
    page_number: Optional[int] = None
    score: float


class SearchResponse(BaseModel):
    """Schema for search results."""
    results: list[SearchResult]
    query: str
    total: int