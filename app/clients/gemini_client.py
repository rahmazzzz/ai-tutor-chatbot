import logging
from typing import Optional, List
from pydantic import BaseModel
import google.generativeai as genai
from app.clients.base_client import LLMClient
from app.core.config import settings  # <-- import config

logger = logging.getLogger(__name__)

# --- Response schema using Pydantic ---
class GeminiGenerateResponse(BaseModel):
    text: str
    model: Optional[str] = None


class GeminiEmbedResponse(BaseModel):
    embedding: List[float]
    model: Optional[str] = None


# --- Client implementation ---
class GeminiClient(LLMClient):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key is required (set GEMINI_API_KEY or GOOGLE_API_KEY).")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)

    async def generate(self, prompt: str, **kwargs) -> GeminiGenerateResponse:
        try:
            logger.info(f"Generating content with Gemini model {self.model_name}")

            generation_config = kwargs.get("generation_config")
            if generation_config is None:
                generation_config = genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=GeminiGenerateResponse,
                )

            resp = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                **{k: v for k, v in kwargs.items() if k != "generation_config"},
            )

            return GeminiGenerateResponse.model_validate({
                "text": resp.text,
                "model": getattr(resp, "model", None),
            })

        except Exception as e:
            logger.exception("Gemini generate_content failed")
            raise

    async def embed(self, text: str, **kwargs) -> GeminiEmbedResponse:
        try:
            logger.info("Generating embedding via Gemini")
            embed_model = kwargs.get("model", "models/embedding-001")

            resp = genai.embed_content(model=embed_model, content=text)

            return GeminiEmbedResponse.model_validate({
                "embedding": resp["embedding"],
                "model": embed_model,
            })

        except Exception as e:
            logger.exception("Gemini embed failed")
            raise
