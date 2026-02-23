"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Optional


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers.

    All messages are passed in Anthropic-style format (the canonical internal
    format). Each provider adapter is responsible for converting to its own
    API format and returning normalized responses.

    Normalized response format:
        {
            "content": str,
            "tool_calls": [{"id": str, "name": str, "arguments": dict}],
            "stop_reason": str,
        }

    Streaming yields:
        {"type": "text_delta", "text": str}
        {"type": "result", "content": str, "tool_calls": [...], "stop_reason": str}

    Tool definitions are received in Anthropic format:
        {"name": str, "description": str, "input_schema": dict}
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. 'anthropic', 'openai', 'gemini')."""

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model ID for this provider."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a chat request and return a normalized response dict."""

    @abstractmethod
    async def chat_streaming(
        self,
        messages: list[dict],
        system_prompt: str,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[dict, None]:
        """Stream a chat response, yielding normalized events."""
