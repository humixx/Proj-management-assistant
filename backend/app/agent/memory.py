"""Agent memory and context management."""
import json
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

        Reconstructs tool_use / tool_result pairs from stored tool_calls
        so the LLM can see the full context of previous tool interactions
        (e.g. propose_tasks results that haven't been confirmed yet).

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dicts with role and content
        """
        messages = await self.chat_repo.list_by_project(self.project_id, limit=limit)

        formatted = []
        for msg in messages:
            if msg.role == "assistant" and msg.tool_calls:
                # Reconstruct the tool_use + tool_result turns so the LLM
                # sees what tools were called and what they returned.
                calls = msg.tool_calls.get("calls", []) if isinstance(msg.tool_calls, dict) else []

                if calls:
                    # 1) Assistant message: text + tool_use blocks
                    assistant_content = []
                    if msg.content:
                        assistant_content.append({"type": "text", "text": msg.content})

                    for i, tc in enumerate(calls):
                        assistant_content.append({
                            "type": "tool_use",
                            "id": f"hist_{id(msg)}_{i}",
                            "name": tc.get("tool_name", "unknown"),
                            "input": tc.get("arguments", {}),
                        })

                    formatted.append({"role": "assistant", "content": assistant_content})

                    # 2) Tool results as a user message
                    tool_result_content = []
                    for i, tc in enumerate(calls):
                        tool_result_content.append({
                            "type": "tool_result",
                            "tool_use_id": f"hist_{id(msg)}_{i}",
                            "content": json.dumps(tc.get("result", {})),
                        })

                    formatted.append({"role": "user", "content": tool_result_content})
                else:
                    # Has tool_calls key but no calls — just use plain text
                    formatted.append({"role": msg.role, "content": msg.content})
            else:
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
