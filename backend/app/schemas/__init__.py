"""Schemas package."""
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectSettings,
)
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    BulkTaskCreate,
    BulkTaskResponse,
)
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentChunkResponse,
    SearchResult,
    SearchResponse,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ChatHistoryResponse,
    ToolCallInfo,
    PlanInfo,
    PlanStep,
)
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
)
from app.schemas.integration import (
    SlackConnectRequest,
    SlackChannel,
    SlackChannelList,
    SlackIntegrationResponse,
    SlackMessageRequest,
    SlackMessageResponse,
)

__all__ = [
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectSettings",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "BulkTaskCreate",
    "BulkTaskResponse",
    # Document
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentChunkResponse",
    "SearchResult",
    "SearchResponse",
    # Chat
    "ChatRequest",
    "ChatResponse",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ToolCallInfo",
    "PlanInfo",
    "PlanStep",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "AuthResponse",
    "UserResponse",
    # Integration
    "SlackConnectRequest",
    "SlackChannel",
    "SlackChannelList",
    "SlackIntegrationResponse",
    "SlackMessageRequest",
    "SlackMessageResponse",
]