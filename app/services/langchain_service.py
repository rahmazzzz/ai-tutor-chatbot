import logging
from typing import List, Optional

from app.clients.base_client import LLMClient
from app.clients.mistralai_client import MistralChatClient
from app.clients.cohere_client import CohereClient

logger = logging.getLogger(__name__)


class LangChainLLMService:
    """
    Unified LLM service with dependency-injected primary and fallback clients.
    Default: Mistral (primary), Cohere (fallback).
    """

    def __init__(
        self,
        primary_client: Optional[LLMClient] = None,
        fallback_client: Optional[LLMClient] = None,
    ):
        # Inject clients or use defaults
        self.primary_client = primary_client or MistralChatClient()
        self.fallback_client = fallback_client or CohereClient()

    async def summarize_lessons(self, lessons: List[str]) -> str:
        """
        Summarize a list of lessons using the primary client,
        fallback to secondary on failure (e.g., rate limit).
        Always returns a string.
        """
        if not lessons:
            return "No lessons provided to summarize."

        summary_prompt = (
            "Summarize the following lessons concisely and clearly:\n"
            + "\n".join(lessons)
        )

        # --- Try primary client (Mistral) ---
        try:
            logger.info("[LangChainLLMService] Using primary client")
            response = await self.primary_client.generate(prompt=summary_prompt)

            # Normalize response into string
            if isinstance(response, str):
                return response
            if hasattr(response, "answer"):
                return str(response.answer)
            if hasattr(response, "content"):
                return str(response.content)
            return str(response)

        except Exception as e:
            logger.warning(f"[LangChainLLMService] Primary client failed: {e}")

        # --- Fallback to secondary client (Cohere) ---
        try:
            logger.info("[LangChainLLMService] Falling back to secondary client")
            result = await self.fallback_client.generate(prompt=summary_prompt)
            return str(result)
        except Exception as e:
            logger.error(f"[LangChainLLMService] Both clients failed: {e}")
            raise RuntimeError(f"LLM summarization failed: {e}")
