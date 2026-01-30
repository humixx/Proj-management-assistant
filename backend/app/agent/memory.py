"""Agent memory and context management."""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import ChatRepository


class AgentMemory:
    """Manages conversation history and context for the agent."""
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
        self.chat_repo = ChatRepository(db)
    
    async def get_chat_history(self, limit: int = 20) -> list[dict]:
        """
        Get recent chat history formatted for the LLM.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dicts with role and content
        """
        messages = await self.chat_repo.list_by_project(self.project_id, limit=limit)
        
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        return formatted
    
    async def save_message(
        self,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tool_results: Optional[dict] = None,
    ) -> None:
        """
        Save a message to chat history.
        
        Args:
            role: Message role (user or assistant)
            content: Message content
            tool_calls: Optional tool call data
            tool_results: Optional tool result data
        """
        await self.chat_repo.create(
            project_id=self.project_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
    
    async def clear_history(self) -> int:
        """Clear chat history. Returns number of deleted messages."""
        return await self.chat_repo.clear_history(self.project_id)
