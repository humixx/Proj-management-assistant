"""Integration schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SlackConnectRequest(BaseModel):
    """Schema for Slack OAuth connect."""
    code: str
    redirect_uri: str


class SlackChannel(BaseModel):
    """Schema for Slack channel."""
    id: str
    name: str


class SlackChannelList(BaseModel):
    """Schema for list of Slack channels."""
    channels: list[SlackChannel]


class SlackIntegrationResponse(BaseModel):
    """Schema for Slack integration."""
    id: UUID
    team_name: Optional[str] = None
    channel_name: Optional[str] = None
    connected: bool = True
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SlackMessageRequest(BaseModel):
    """Schema for sending Slack message."""
    channel: str
    message: str


class SlackMessageResponse(BaseModel):
    """Schema for Slack message response."""
    success: bool
    ts: Optional[str] = None
    channel: str