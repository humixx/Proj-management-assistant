"""Chat API routes."""
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_project_id, verify_project_ownership
from app.auth.deps import get_current_user
from app.agent.core import Agent
from app.db.database import async_session_maker
from app.db.models.user import User
from app.db.repositories import ChatRepository, ProjectRepository
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
    ToolCallInfo,
)

logger = logging.getLogger(__name__)


def _friendly_api_error(e: Exception) -> str:
    """Turn LLM API errors into user-friendly messages."""
    err_str = str(e).lower()
    # Try to get status code from the exception if available
    status_code = getattr(e, "status_code", None)

    if status_code == 529 or "overloaded" in err_str:
        return "The AI provider is temporarily overloaded. Please try again in a few seconds."
    if status_code == 429 or "rate limit" in err_str or "rate_limit" in err_str:
        return "Rate limit reached. Please wait a moment and try again."
    if status_code in (500, 503) or "server error" in err_str:
        return "The AI provider API is experiencing issues. Please try again shortly."
    if "connection" in err_str or "connect" in err_str:
        return "Could not connect to the AI provider. Please check your connection."
    return f"Agent error: {str(e)}"


router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI agent.

    The agent will process the message, potentially use tools,
    and return a response.
    """
    await verify_project_ownership(project_id, current_user.id, db)

    try:
        project = await ProjectRepository(db).get_by_id(project_id)
        llm_config = (project.settings or {}) if project else {}

        agent = Agent(db, project_id, llm_config=llm_config)
        result = await agent.run(data.message)

        # Format tool calls for response
        tool_calls = None
        if result.get("tool_calls"):
            tool_calls = [
                ToolCallInfo(
                    tool_name=tc["tool_name"],
                    arguments=tc["arguments"],
                    result=tc["result"],
                )
                for tc in result["tool_calls"]
            ]

        return ChatResponse(
            message=result["message"],
            tool_calls=tool_calls,
        )

    except Exception as e:
        msg = _friendly_api_error(e)
        logger.warning(f"Chat API error: {e}")
        status = getattr(e, "status_code", 500) or 500
        raise HTTPException(status_code=status, detail=msg)


@router.post("/stream")
async def send_message_stream(
    data: ChatRequest,
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI agent with SSE streaming for live progress.

    Emits events:
      - {"type": "thinking", "stage": "analyzing"}
      - {"type": "tool_start", "tool_name": "create_task", "arguments": {...}}
      - {"type": "tool_end", "tool_name": "create_task", "result": {...}}
      - {"type": "response", "message": "...", "tool_calls": [...]}
      - {"type": "error", "message": "..."}
    """
    # Verify ownership using the request-scoped session (still valid here)
    await verify_project_ownership(project_id, current_user.id, db)

    # Load llm_config before the generator (request-scoped session is valid here)
    project = await ProjectRepository(db).get_by_id(project_id)
    llm_config = (project.settings or {}) if project else {}

    async def event_stream():
        # Create a NEW session inside the generator so it stays alive
        # for the entire stream duration (the Depends(get_db) session
        # gets closed when the endpoint function returns, before
        # streaming actually begins).
        async with async_session_maker() as stream_db:
            try:
                agent = Agent(stream_db, project_id, llm_config=llm_config)

                # Emit initial thinking stage
                yield f"data: {json.dumps({'type': 'thinking', 'stage': 'analyzing'})}\n\n"

                async for event in agent.run_streaming(data.message):
                    yield f"data: {json.dumps(event)}\n\n"

                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                msg = _friendly_api_error(e)
                logger.warning(f"Stream API error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': msg})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for a project."""
    await verify_project_ownership(project_id, current_user.id, db)

    repo = ChatRepository(db)
    messages = await repo.list_by_project(project_id, limit=limit)

    return ChatHistoryResponse(
        messages=[
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        total=len(messages),
    )


@router.delete("/history")
async def clear_chat_history(
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear chat history for a project."""
    await verify_project_ownership(project_id, current_user.id, db)

    repo = ChatRepository(db)
    count = await repo.clear_history(project_id)
    return {"deleted": count}
