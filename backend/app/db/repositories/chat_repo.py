"""Chat repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage
from app.db.repositories.base import BaseRepository


class ChatRepository(BaseRepository):
    """Repository for chat message operations."""
    
    async def create(
        self,
        project_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tool_results: Optional[dict] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            project_id=project_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def list_by_project(self, project_id: UUID, limit: int = 50) -> list[ChatMessage]:
        """List chat messages for a project."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.project_id == project_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def clear_history(self, project_id: UUID) -> int:
        """Clear chat history for a project."""
        stmt = delete(ChatMessage).where(ChatMessage.project_id == project_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
