"""Chat API routes."""
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_project_id
from app.agent.core import Agent
from app.db.repositories import ChatRepository
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
    ToolCallInfo,
)

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    project_id: UUID = Depends(get_current_project_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI agent.
    
    The agent will process the message, potentially use tools,
    and return a response.
    """
    try:
        agent = Agent(db, project_id)
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
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/stream")
async def send_message_stream(
    data: ChatRequest,
    project_id: UUID = Depends(get_current_project_id),
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
    async def event_stream():
        try:
            agent = Agent(db, project_id)
            
            # Emit initial thinking stage
            yield f"data: {json.dumps({'type': 'thinking', 'stage': 'analyzing'})}\n\n"
            
            async for event in agent.run_streaming(data.message):
                yield f"data: {json.dumps(event)}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
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
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for a project."""
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
    db: AsyncSession = Depends(get_db),
):
    """Clear chat history for a project."""
    repo = ChatRepository(db)
    count = await repo.clear_history(project_id)
    return {"deleted": count}
