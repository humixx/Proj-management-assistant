"""Project schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.auth.encryption import encrypt_api_key, decrypt_api_key


class ProjectSettings(BaseModel):
    """Project settings including LLM provider and RAG configuration."""
    # RAG settings
    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 50
    top_k: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7
    # LLM provider settings
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None

    @field_validator('llm_api_key', mode='before')
    @classmethod
    def encrypt_api_key_on_store(cls, v):
        """Encrypt API key when storing to database."""
        if v:
            return encrypt_api_key(v)
        return v

    def get_decrypted_api_key(self) -> Optional[str]:
        """Get the decrypted API key for use with LLM providers."""
        if self.llm_api_key:
            return decrypt_api_key(self.llm_api_key)
        return None


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
