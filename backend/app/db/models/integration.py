"""Integration models (Slack, etc.)."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.db.database import Base


class SlackIntegration(Base):
    """Slack integration settings for a project."""
    
    __tablename__ = "slack_integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    client_id = Column(String(255), nullable=True)
    client_secret = Column(String(500), nullable=True)
    access_token = Column(String(500), nullable=True)
    bot_token = Column(String(500), nullable=True)
    team_id = Column(String(100), nullable=True)
    team_name = Column(String(255), nullable=True)
    channel_id = Column(String(100), nullable=True)
    channel_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="slack_integration")
