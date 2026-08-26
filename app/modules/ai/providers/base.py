from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AIResponse:
    content: str
    usage: dict | None = None
    model: str | None = None
    raw: dict | None = None


class AIProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> AIResponse:
        ...

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        ...
