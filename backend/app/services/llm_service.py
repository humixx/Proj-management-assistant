"""LLM service using Anthropic Claude API."""
import json
from typing import Any, Optional

from anthropic import AsyncAnthropic

from app.config import settings


class LLMService:
    """Service for interacting with Claude API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncAnthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def chat(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a chat request to Claude with optional tools."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }
        
        if tools:
            kwargs["tools"] = tools
        
        response = await self.client.messages.create(**kwargs)
        
        result = {
            "content": "",
            "tool_calls": [],
            "stop_reason": response.stop_reason,
        }
        
        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input,
                })
        
        return result
    
    async def chat_with_tool_results(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: list[dict],
        tool_results: list[dict],
        max_tokens: int = 4096,
    ) -> dict:
        """Continue conversation with tool results."""
        tool_result_content = []
        for result in tool_results:
            tool_result_content.append({
                "type": "tool_result",
                "tool_use_id": result["tool_use_id"],
                "content": json.dumps(result["result"]) if not isinstance(result["result"], str) else result["result"],
            })
        
        messages = messages + [{"role": "user", "content": tool_result_content}]
        
        return await self.chat(
            messages=messages,
            system_prompt=system_prompt,
            tools=tools,
            max_tokens=max_tokens,
        )


llm_service = LLMService()
