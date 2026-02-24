"""Integration schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SlackSetupRequest(BaseModel):
    """Schema for saving Slack app credentials."""
    client_id: str
    client_secret: str


class SlackConnectRequest(BaseModel):
    """Schema for Slack OAuth callback."""
    code: str
    redirect_uri: str


class SlackOAuthURLResponse(BaseModel):
    """Schema for OAuth URL response."""
    oauth_url: str
    message: str


class SlackSetDefaultChannelRequest(BaseModel):
    """Schema for setting default channel."""
    channel_id: str
    channel_name: str


class SlackChannel(BaseModel):
    """Schema for Slack channel."""
    id: str
    name: str


class SlackChannelList(BaseModel):
    """Schema for list of Slack channels."""
    channels: list[SlackChannel]


class SlackIntegrationResponse(BaseModel):
    """Schema for Slack integration status."""
    id: UUID
    has_credentials: bool = False
    connected: bool = False
    team_name: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
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
