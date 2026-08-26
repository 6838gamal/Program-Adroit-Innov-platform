import httpx

from app.core.config import settings
from app.core.exceptions import AIRuntimeError
from app.core.logging import get_logger
from app.modules.ai.providers.base import AIProvider, AIResponse

logger = get_logger(__name__)

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    async def chat_completion(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        if not self.api_key:
            raise AIRuntimeError("OpenAI API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(OPENAI_CHAT_URL, headers=headers, json=payload, timeout=60)
        except httpx.HTTPError as e:
            logger.error("openai_request_failed", error=str(e))
            raise AIRuntimeError("Failed to connect to AI provider")

        if resp.status_code != 200:
            logger.error("openai_error", status=resp.status_code, body=resp.text)
            raise AIRuntimeError(f"AI provider returned error: {resp.status_code}")

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage")
        return AIResponse(content=content, usage=usage, model=self.model, raw=data)

    async def embed_text(self, text: str) -> list[float]:
        if not self.api_key:
            raise AIRuntimeError("OpenAI API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": "text-embedding-3-small", "input": text}

        async with httpx.AsyncClient() as client:
            resp = await client.post(OPENAI_EMBEDDINGS_URL, headers=headers, json=payload, timeout=30)

        if resp.status_code != 200:
            raise AIRuntimeError("Failed to generate embeddings")

        return resp.json()["data"][0]["embedding"]
