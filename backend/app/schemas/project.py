"""Project schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectSettings(BaseModel):
    """Project settings including LLM provider and RAG configuration."""
    # LLM provider settings
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    # RAG settings
    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 50
    top_k: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7


class ProjectCreate(BaseModel):
    """Schema for creating a project."""
    name: str
    description: Optional[str] = None
    settings: Optional[ProjectSettings] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[ProjectSettings] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    name: str
    description: Optional[str] = None
    settings: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for list of projects."""
    projects: list[ProjectResponse]
    total: int