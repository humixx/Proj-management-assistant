"""Google Gemini LLM provider."""
import asyncio
import logging
from typing import AsyncGenerator, Optional

from app.config import settings
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF = 2


class GeminiProvider(BaseLLMProvider):
    """LLM provider using Google Gemini API."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        import google.generativeai as genai
        key = api_key or settings.GEMINI_API_KEY
        genai.configure(api_key=key)
        self._genai = genai
        self.model = model or self.default_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    # JSON Schema keywords that Gemini does not support.
    # NOTE: Do NOT add "title" here — it collides with legitimate property names
    # like `properties.title` inside tool schemas.
    _UNSUPPORTED_SCHEMA_KEYS = {"default", "examples", "$schema", "additionalProperties"}

    def _sanitize_schema(self, obj: dict) -> dict:
        """Recursively strip keys that Gemini does not accept in JSON Schema."""
        cleaned: dict = {}
        for key, value in obj.items():
            if key in self._UNSUPPORTED_SCHEMA_KEYS:
                continue
            if isinstance(value, dict):
                cleaned[key] = self._sanitize_schema(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._sanitize_schema(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value
        return cleaned

    def _convert_tools(self, tools: list[dict]) -> list:
        """Convert Anthropic-format tools to Gemini FunctionDeclarations."""
        from google.generativeai.types import FunctionDeclaration, Tool

        declarations = []
        for tool in tools:
            schema = tool.get("input_schema", {})
            # Sanitize properties to remove unsupported fields like "default"
            properties = self._sanitize_schema(schema.get("properties", {}))
            parameters = {
                "type": schema.get("type", "object"),
                "properties": properties,
            }
            if "required" in schema:
                parameters["required"] = schema["required"]

            declarations.append(
                FunctionDeclaration(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    parameters=parameters,
                )
            )
        return [Tool(function_declarations=declarations)]

    def _convert_messages(self, messages: list[dict], system_prompt: str) -> tuple[str, list]:
        """Convert Anthropic-style messages to Gemini contents format.

        Returns (system_instruction, contents_list).
        """
        contents = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            # Map Anthropic roles to Gemini roles
            gemini_role = "model" if role == "assistant" else "user"

            if isinstance(content, str):
                contents.append({"role": gemini_role, "parts": [{"text": content}]})
                continue

            parts = []
            pending_tool_responses = []

            for block in content:
                btype = block.get("type")
                if btype == "text":
                    parts.append({"text": block["text"]})
                elif btype == "tool_use":
                    parts.append({
                        "function_call": {
                            "name": block["name"],
                            "args": block.get("input", {}),
                        }
                    })
                elif btype == "tool_result":
                    # Tool results become function_response parts in a user message
                    pending_tool_responses.append({
                        "function_response": {
                            "name": block.get("tool_name", "tool"),
                            "response": {"result": block.get("content", "")},
                        }
                    })

            if pending_tool_responses:
                contents.append({"role": "user", "parts": pending_tool_responses})
            elif parts:
                contents.append({"role": gemini_role, "parts": parts})

        return system_prompt, contents

    async def _retry_delay(self, attempt: int) -> None:
        delay = INITIAL_BACKOFF * (2 ** attempt)
        logger.warning(f"Gemini API error — retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
        await asyncio.sleep(delay)

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a chat request to Gemini."""
        system_instruction, contents = self._convert_messages(messages, system_prompt)

        model_kwargs: dict = {
            "model_name": self.model,
            "system_instruction": system_instruction,
            "generation_config": {"max_output_tokens": max_tokens},
        }
        if tools:
            model_kwargs["tools"] = self._convert_tools(tools)

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                model = self._genai.GenerativeModel(**model_kwargs)
                response = await model.generate_content_async(contents)

                result: dict = {
                    "content": "",
                    "tool_calls": [],
                    "stop_reason": "stop",
                }

                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            result["content"] += part.text
                        elif hasattr(part, "function_call") and part.function_call:
                            fc = part.function_call
                            result["tool_calls"].append({
                                "id": fc.name,  # Gemini doesn't have IDs; use name
                                "name": fc.name,
                                "arguments": dict(fc.args),
                            })
                    if candidate.finish_reason:
                        result["stop_reason"] = str(candidate.finish_reason)

                return result
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
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
        """Stream a chat response from Gemini."""
        system_instruction, contents = self._convert_messages(messages, system_prompt)

        model_kwargs: dict = {
            "model_name": self.model,
            "system_instruction": system_instruction,
            "generation_config": {"max_output_tokens": max_tokens},
        }
        if tools:
            model_kwargs["tools"] = self._convert_tools(tools)

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                model = self._genai.GenerativeModel(**model_kwargs)
                full_text = ""
                tool_calls: list[dict] = []
                finish_reason = "stop"

                async for chunk in await model.generate_content_async(contents, stream=True):
                    for candidate in chunk.candidates:
                        if candidate.finish_reason:
                            finish_reason = str(candidate.finish_reason)
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                full_text += part.text
                                yield {"type": "text_delta", "text": part.text}
                            elif hasattr(part, "function_call") and part.function_call:
                                fc = part.function_call
                                tool_calls.append({
                                    "id": fc.name,
                                    "name": fc.name,
                                    "arguments": dict(fc.args),
                                })

                yield {
                    "type": "result",
                    "content": full_text,
                    "tool_calls": tool_calls,
                    "stop_reason": finish_reason,
                }
                return

            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    await self._retry_delay(attempt)
                    continue
                raise

        raise last_error  # type: ignore[misc]
