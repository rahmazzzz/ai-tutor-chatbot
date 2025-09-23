# app/clients/mistralai_embed_client.py
import os
import logging
import httpx
from typing import List

logger = logging.getLogger(__name__)


class MistralEmbedClient:
    """
    Standalone client for generating embeddings via Mistral API.
    Uses the new endpoint and enforces expected vector dimension.
    """

    def __init__(self, api_key: str = None, model_name: str = "mistral-embed", expected_dim: int = 1536):
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required for embeddings.")

        self.api_url = "https://api.mistral.ai/v1/embeddings"
        self.model_name = model_name
        self.expected_dim = expected_dim
        logger.info(f"Initialized MistralEmbedClient with model {self.model_name}")

    async def embed(self, text: str, model: str = None) -> List[float]:
        model_to_use = model or self.model_name
        logger.info(f"Requesting embedding from Mistral model={model_to_use}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_to_use,
            "input": text
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # The actual embedding depends on Mistral API response structure
                embedding = data["data"][0]["embedding"]
                logger.info(f"Received embedding of length {len(embedding)}")

                if len(embedding) != self.expected_dim:
                    raise ValueError(f"Embedding dimension mismatch: got {len(embedding)}, expected {self.expected_dim}")

                return embedding

            except Exception as e:
                logger.exception("Mistral embedding request failed")
                raise
