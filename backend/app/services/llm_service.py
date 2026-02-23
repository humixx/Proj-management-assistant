"""LLM service factory — returns the appropriate provider based on configuration."""
from typing import Optional

from app.services.providers.base import BaseLLMProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.openai_provider import OpenAIProvider


def get_llm_provider(
    provider: str = "anthropic",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseLLMProvider:
    """Return an LLM provider instance for the given provider name.

    Args:
        provider: One of "anthropic" or "openai".
        model: Optional model override. If None, the provider's default is used.
        api_key: Optional per-project API key. Falls back to env var if not set.

    Returns:
        A configured BaseLLMProvider instance.
    """
    if provider == "openai":
        return OpenAIProvider(model=model, api_key=api_key)
    else:
        return AnthropicProvider(model=model, api_key=api_key)


# Default singleton for backward compatibility (Anthropic)
llm_service = get_llm_provider("anthropic")
