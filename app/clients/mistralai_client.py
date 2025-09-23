# app/clients/mistralai_client.py
from typing import List, Optional
from pydantic import BaseModel
import logging
from mistralai import Mistral
from app.clients.base_client import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class MistralChatResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = []
    language: str = "english"

class MistralChatClient(LLMClient):
    def __init__(self, model_name: str = "ministral-8b-latest"):
        self.api_key = settings.MISTRAL_API_KEY
        if not self.api_key:
            raise ValueError("Mistral API key is required.")
        self.model_name = model_name
        self.client = Mistral(api_key=self.api_key)

    async def chat(self, user: str, system: Optional[str] = None) -> MistralChatResponse:
        """Send chat request to Mistral"""
        try:
            logger.info("Sending chat request to Mistral...")

            sdk_response = self.client.chat.complete(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system or "You are a helpful AI assistant."},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                max_tokens=512,
            )

            # Take the first completion
            answer = sdk_response.choices[0].message.content

            return MistralChatResponse(
                answer=answer,
                sources=[],
                language="english",
            )
        except Exception as e:
            logger.exception("Mistral API request failed")
            raise

    # Implement abstract methods
    async def generate(self, prompt: str, **kwargs) -> str:
        resp = await self.chat(user=prompt, system=kwargs.get("system"))
        return resp.answer

    async def embed(self, text: str, **kwargs) -> List[float]:
        if not hasattr(self.client, "embeddings"):
            raise NotImplementedError("Mistral embeddings not implemented")
        return self.client.embeddings.create(model="mistral-embed", input=text).data[0].embedding
