# app/services/langchain_service.py
import aiohttp
import cohere
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings


class LangChainLLMService:
    """
    Unified LLM service with primary Mistral support and Cohere fallback.
    """

    def __init__(self):
        # --- Mistral setup ---
        self.mistral_api_url = "https://api.mistral.ai/v1/chat/completions"
        self.mistral_model = settings.MISTRAL_MODEL
        self.mistral_api_key = settings.MISTRAL_API_KEY
        self.mistral_temperature = settings.MISTRAL_TEMPERATURE

        # --- Cohere setup ---
        self.cohere_client = cohere.ClientV2(api_key=settings.COHERE_API_KEY)
        self.cohere_model = "command-a-03-2025"

    async def summarize_lessons(self, lessons: list[str]) -> str:
        """
        Summarize a list of lessons using Mistral first,
        fallback to Cohere on failure (e.g., 429 rate limit).
        """
        summary_prompt = (
            "Summarize the following lessons concisely and clearly:\n"
            + "\n".join(lessons)
        )

        # ---------- Try Mistral ----------
        mistral_payload = {
            "model": self.mistral_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that summarizes lessons.",
                },
                {"role": "user", "content": summary_prompt},
            ],
            "temperature": self.mistral_temperature,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.mistral_api_url,
                    json=mistral_payload,
                    headers={"Authorization": f"Bearer {self.mistral_api_key}"},
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        # Trigger fallback on rate limit
                        if response.status == 429:
                            raise RuntimeError(f"Mistral rate limit: {text}")
                        raise Exception(f"Mistral API error {response.status}: {text}")

                    data = await response.json()
                    return data["choices"][0]["message"]["content"]

        except Exception as e:
            # ---------- Fallback to Cohere ----------
            print(f"[LangChainLLMService] Falling back to Cohere due to: {e}")
            cohere_response = self.cohere_client.chat(
                model=self.cohere_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that summarizes lessons.",
                    },
                    {"role": "user", "content": summary_prompt},
                ],
            )
            return cohere_response.message.content[0].text
