"""Plan model."""
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.db.database import Base


class Plan(Base):
    """Lightweight plan metadata that tracks a parent task + ordered subtasks."""

    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, unique=True)
    goal = Column(Text, nullable=False)
    status = Column(String(50), server_default="active", nullable=False)  # active, completed, cancelled
    current_step = Column(Integer, server_default="0", nullable=False)
    step_order = Column(JSONB, nullable=False, server_default="[]")  # Ordered list of subtask UUIDs
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    parent_task = relationship("Task", foreign_keys=[parent_task_id])
