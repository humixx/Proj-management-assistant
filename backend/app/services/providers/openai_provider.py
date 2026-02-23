"""OpenAI GPT LLM provider."""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional

from app.config import settings
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF = 2
RETRYABLE_STATUS_CODES = {429, 500, 503}


class OpenAIProvider(BaseLLMProvider):
    """LLM provider using OpenAI API."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        from openai import AsyncOpenAI
        key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=key)
        self.model = model or self.default_model

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert Anthropic-format tools to OpenAI function format."""
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
                },
            })
        return openai_tools

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert Anthropic-style messages to OpenAI format.

        Anthropic uses content blocks with type 'tool_use' and 'tool_result'.
        OpenAI uses tool_calls on assistant messages and role='tool' for results.
        """
        openai_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if isinstance(content, str):
                openai_messages.append({"role": role, "content": content})
                continue

            # content is a list of blocks
            text_parts = []
            tool_calls = []
            tool_results = []

            for block in content:
                btype = block.get("type")
                if btype == "text":
                    text_parts.append(block["text"])
                elif btype == "tool_use":
                    tool_calls.append({
                        "id": block["id"],
                        "type": "function",
                        "function": {
                            "name": block["name"],
                            "arguments": json.dumps(block.get("input", {})),
                        },
                    })
                elif btype == "tool_result":
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": block["tool_use_id"],
                        "content": block.get("content", ""),
                    })

            if tool_results:
                # Tool result messages become individual role='tool' messages
                openai_messages.extend(tool_results)
            elif tool_calls:
                text_content = " ".join(text_parts) if text_parts else None
                assistant_msg: dict = {"role": "assistant", "tool_calls": tool_calls}
                if text_content:
                    assistant_msg["content"] = text_content
                else:
                    assistant_msg["content"] = None
                openai_messages.append(assistant_msg)
            else:
                openai_messages.append({
                    "role": role,
                    "content": " ".join(text_parts),
                })

        return openai_messages

    async def _retry_delay(self, attempt: int) -> None:
        delay = INITIAL_BACKOFF * (2 ** attempt)
        logger.warning(f"OpenAI API error — retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
        await asyncio.sleep(delay)

    def _is_retryable(self, error: Exception) -> bool:
        try:
            from openai import APIStatusError, APIConnectionError
            if isinstance(error, APIConnectionError):
                return True
            if isinstance(error, APIStatusError):
                return error.status_code in RETRYABLE_STATUS_CODES
        except ImportError:
            pass
        return False

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a chat request to OpenAI."""
        from openai import APIStatusError, APIConnectionError

        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(self._convert_messages(messages))

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": openai_messages,
        }
        if tools:
            kwargs["tools"] = self._convert_tools(tools)
            kwargs["tool_choice"] = "auto"

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(**kwargs)
                choice = response.choices[0]
                message = choice.message

                result: dict = {
                    "content": message.content or "",
                    "tool_calls": [],
                    "stop_reason": choice.finish_reason,
                }

                if message.tool_calls:
                    for tc in message.tool_calls:
                        try:
                            arguments = json.loads(tc.function.arguments)
                        except (json.JSONDecodeError, AttributeError):
                            arguments = {}
                        result["tool_calls"].append({
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": arguments,
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
        """Stream a chat response from OpenAI."""
        from openai import APIStatusError, APIConnectionError

        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(self._convert_messages(messages))

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": openai_messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = self._convert_tools(tools)
            kwargs["tool_choice"] = "auto"

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                full_text = ""
                # tool_calls indexed by their position in the delta
                tool_calls_map: dict[int, dict] = {}
                finish_reason = "stop"

                async with await self.client.chat.completions.create(**kwargs) as stream:
                    async for chunk in stream:
                        if not chunk.choices:
                            continue
                        choice = chunk.choices[0]
                        delta = choice.delta

                        if choice.finish_reason:
                            finish_reason = choice.finish_reason

                        if delta.content:
                            full_text += delta.content
                            yield {"type": "text_delta", "text": delta.content}

                        if delta.tool_calls:
                            for tc_delta in delta.tool_calls:
                                idx = tc_delta.index
                                if idx not in tool_calls_map:
                                    tool_calls_map[idx] = {
                                        "id": tc_delta.id or "",
                                        "name": tc_delta.function.name if tc_delta.function else "",
                                        "arguments_str": "",
                                    }
                                if tc_delta.id:
                                    tool_calls_map[idx]["id"] = tc_delta.id
                                if tc_delta.function:
                                    if tc_delta.function.name:
                                        tool_calls_map[idx]["name"] = tc_delta.function.name
                                    if tc_delta.function.arguments:
                                        tool_calls_map[idx]["arguments_str"] += tc_delta.function.arguments

                # Build normalized tool_calls list
                tool_calls = []
                for idx in sorted(tool_calls_map.keys()):
                    tc = tool_calls_map[idx]
                    try:
                        arguments = json.loads(tc["arguments_str"]) if tc["arguments_str"] else {}
                    except json.JSONDecodeError:
                        arguments = {}
                    tool_calls.append({
                        "id": tc["id"],
                        "name": tc["name"],
                        "arguments": arguments,
                    })

                yield {
                    "type": "result",
                    "content": full_text,
                    "tool_calls": tool_calls,
                    "stop_reason": finish_reason,
                }
                return

            except (APIStatusError, APIConnectionError) as e:
                last_error = e
                if self._is_retryable(e) and attempt < MAX_RETRIES - 1:
                    await self._retry_delay(attempt)
                    continue
                raise

        raise last_error  # type: ignore[misc]
