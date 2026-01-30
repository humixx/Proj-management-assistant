"""Chat schemas."""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    include_context: bool = True


class ToolCallInfo(BaseModel):
    """Schema for tool call information."""
    tool_name: str
    arguments: dict
    result: Any


class PlanStep(BaseModel):
    """Schema for a plan step."""
    step_id: int
    action: str
    description: str
    status: str


class PlanInfo(BaseModel):
    """Schema for plan information."""
    plan_id: str
    goal: str
    steps: list[PlanStep]
    current_step: int
    status: str


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    tool_calls: Optional[list[ToolCallInfo]] = None
    plan: Optional[PlanInfo] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message."""
    id: UUID
    role: str
    content: str
    tool_calls: Optional[dict] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    """Schema for chat history."""
    messages: list[ChatMessageResponse]
    total: int