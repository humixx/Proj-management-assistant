"""Chat API routes."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
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
