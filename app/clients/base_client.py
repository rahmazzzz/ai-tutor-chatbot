from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMClient(ABC):
    """Interface for all LLM clients."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from the LLM provider."""
        pass

    @abstractmethod
    async def embed(self, text: str, **kwargs) -> Any:
        """Generate embeddings from the LLM provider."""
        pass
