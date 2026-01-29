"""ChatMessage model."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.db.database import Base


class ChatMessage(Base):
    """Chat message model for conversation history."""
    
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)  # Stores tool call data
    tool_results = Column(JSON, nullable=True)  # Stores tool results
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="chat_messages")
    
    __table_args__ = (
        Index("ix_chat_messages_project_id", "project_id"),
    )
