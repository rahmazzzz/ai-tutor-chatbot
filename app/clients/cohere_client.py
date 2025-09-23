# app/clients/cohere_client.py
import cohere
import logging
import asyncio
from app.clients.base_client import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class CohereClient(LLMClient):
    def __init__(self):
        self.api_key = settings.COHERE_API_KEY
        if not self.api_key:
            raise ValueError("Cohere API key is required. Please set it in config.py/.env")

        self.client = cohere.Client(self.api_key)
        self.embedding_model = "embed-english-light-v2.0"  # 1536-dim
        logger.info(f"CohereClient initialized with embedding model {self.embedding_model}")

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Use Cohere Chat API (replacement for deprecated Generate API).
        """
        try:
            # Run in threadpool to avoid blocking
            response = await asyncio.to_thread(
                self.client.chat,
                model=kwargs.get("model", "command-r7b-12-2024"),  # latest recommended chat model
                message=prompt,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 200),
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Cohere chat failed: {e}")
            raise

    async def embed(self, text: str, **kwargs):
        """
        Generate embeddings using Cohere Embed API.
        """
        try:
            model_to_use = kwargs.get("model", self.embedding_model)
            response = await asyncio.to_thread(
                self.client.embed,
                texts=[text],
                model=model_to_use
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Cohere embed failed: {e}")
            raise
