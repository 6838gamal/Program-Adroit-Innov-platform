from app.core.config import settings
from app.modules.ai.providers.base import AIProvider, AIResponse
from app.modules.ai.providers.openai_provider import OpenAIProvider


def get_provider(provider_name: str | None = None) -> AIProvider:
    name = provider_name or settings.AI_PROVIDER
    if name == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unknown AI provider: {name}")


__all__ = ["AIProvider", "AIResponse", "get_provider", "OpenAIProvider"]
