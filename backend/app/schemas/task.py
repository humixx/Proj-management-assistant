"""Task schemas."""
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None
    parent_task_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    project_id: UUID
    parent_task_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Schema for list of tasks."""
    tasks: list[TaskResponse]
    total: int


class BulkTaskCreate(BaseModel):
    """Schema for bulk creating tasks."""
    tasks: list[TaskCreate]


class BulkTaskResponse(BaseModel):
    """Schema for bulk task creation response."""
    created: list[TaskResponse]
    count: int
