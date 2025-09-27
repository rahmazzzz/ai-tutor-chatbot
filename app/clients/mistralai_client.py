# app/clients/mistralai_client.py
from typing import List, Optional
from pydantic import BaseModel
import logging
import asyncio
import os
import httpx
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

        # ✅ Optional proxy setup with httpx.Client
        proxies = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
        if proxies:
            logger.info(f"Using proxy for Mistral client: {proxies}")
            http_client = httpx.Client(proxies=proxies, timeout=30.0)
            self.client = Mistral(api_key=self.api_key, http_client=http_client)
        else:
            self.client = Mistral(api_key=self.api_key)

    async def chat(self, user: str, system: Optional[str] = None) -> MistralChatResponse:
        """Send chat request to Mistral asynchronously"""
        try:
            logger.info("Sending chat request to Mistral...")

            loop = asyncio.get_event_loop()
            sdk_response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.complete(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system or "You are a helpful AI assistant."},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.2,
                    max_tokens=512,
                ),
            )

            # --- Normalize response ---
            content = sdk_response.choices[0].message.content
            if isinstance(content, list):
                answer = " ".join(
                    chunk.text for chunk in content if getattr(chunk, "type", None) == "text"
                )
            else:
                answer = str(content)

            return MistralChatResponse(
                answer=answer.strip(),
                sources=[],
                language="english",
            )
        except Exception as e:
            logger.exception("Mistral API request failed")
            raise

    async def generate(self, prompt: str, **kwargs) -> str:
        resp = await self.chat(user=prompt, system=kwargs.get("system"))
        return resp.answer

    async def embed(self, text: str, **kwargs) -> List[float]:
        """Generate embeddings with Mistral"""
        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    model="mistral-embed",
                    input=text
                ),
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.exception("Mistral embeddings request failed")
            raise
