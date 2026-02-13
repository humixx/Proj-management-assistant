"""Plan schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlanCreate(BaseModel):
    """Schema for creating a plan."""
    goal: str
    parent_task_id: UUID
    step_order: list[str]


class PlanResponse(BaseModel):
    """Schema for plan response."""
    id: UUID
    project_id: UUID
    parent_task_id: UUID
    goal: str
    status: str
    current_step: int
    step_order: list[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
