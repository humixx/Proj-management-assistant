"""Anthropic Claude LLM provider."""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional

from anthropic import AsyncAnthropic, APIStatusError, APIConnectionError

from app.config import settings
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF = 2
RETRYABLE_STATUS_CODES = {429, 529, 503, 500}


class AnthropicProvider(BaseLLMProvider):
    """LLM provider using Anthropic Claude API."""

    def __init__(self, model: Optional[str] = None):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = model or self.default_model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    async def _retry_delay(self, attempt: int) -> None:
        delay = INITIAL_BACKOFF * (2 ** attempt)
        logger.warning(f"Anthropic API error — retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
        await asyncio.sleep(delay)

    def _is_retryable(self, error: Exception) -> bool:
        if isinstance(error, APIConnectionError):
            return True
        if isinstance(error, APIStatusError):
            return error.status_code in RETRYABLE_STATUS_CODES
        return False

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

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
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
            except (APIStatusError, APIConnectionError) as e:
                last_error = e
                if self._is_retryable(e) and attempt < MAX_RETRIES - 1:
                    await self._retry_delay(attempt)
                    continue
                raise

        raise last_error  # type: ignore[misc]

    async def chat_streaming(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[dict, None]:
        """Stream a chat response from Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                full_text = ""
                tool_calls: list[dict] = []
                current_tool: dict | None = None
                current_tool_json = ""

                async with self.client.messages.stream(**kwargs) as stream:
                    async for event in stream:
                        if event.type == "content_block_start":
                            block = event.content_block
                            if block.type == "tool_use":
                                current_tool = {"id": block.id, "name": block.name, "arguments": {}}
                                current_tool_json = ""

                        elif event.type == "content_block_delta":
                            delta = event.delta
                            if delta.type == "text_delta":
                                full_text += delta.text
                                yield {"type": "text_delta", "text": delta.text}
                            elif delta.type == "input_json_delta":
                                if current_tool is not None:
                                    current_tool_json += delta.partial_json

                        elif event.type == "content_block_stop":
                            if current_tool is not None:
                                try:
                                    current_tool["arguments"] = json.loads(current_tool_json) if current_tool_json else {}
                                except json.JSONDecodeError:
                                    current_tool["arguments"] = {}
                                tool_calls.append(current_tool)
                                current_tool = None
                                current_tool_json = ""

                    final = await stream.get_final_message()

                yield {
                    "type": "result",
                    "content": full_text,
                    "tool_calls": tool_calls,
                    "stop_reason": final.stop_reason,
                }
                return

            except (APIStatusError, APIConnectionError) as e:
                last_error = e
                if self._is_retryable(e) and attempt < MAX_RETRIES - 1:
                    await self._retry_delay(attempt)
                    continue
                raise

        raise last_error  # type: ignore[misc]
