"""LLM service factory — returns the appropriate provider based on configuration."""
from typing import Optional

from app.services.providers.base import BaseLLMProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.gemini_provider import GeminiProvider


def get_llm_provider(
    provider: str = "anthropic",
    model: Optional[str] = None,
) -> BaseLLMProvider:
    """Return an LLM provider instance for the given provider name.

    Args:
        provider: One of "anthropic", "openai", or "gemini".
        model: Optional model override. If None, the provider's default is used.

    Returns:
        A configured BaseLLMProvider instance.
    """
    if provider == "openai":
        return OpenAIProvider(model=model)
    elif provider == "gemini":
        return GeminiProvider(model=model)
    else:
        return AnthropicProvider(model=model)


# Default singleton for backward compatibility (Anthropic)
llm_service = get_llm_provider("anthropic")
