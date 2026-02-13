"""Task model."""
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from app.db.database import Base


class Task(Base):
    """Task model for project work items."""
    
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), server_default="todo", nullable=False)  # todo, in_progress, review, done
    priority = Column(String(50), server_default="medium", nullable=False)  # low, medium, high, critical
    assignee = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    order = Column(Integer, nullable=True)  # Position within plan (0-indexed), null for non-plan tasks
    external_id = Column(String(255), nullable=True)  # For Slack thread ID
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    
    __table_args__ = (
        Index("ix_tasks_project_id", "project_id"),
    )
