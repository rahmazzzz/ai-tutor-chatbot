# app/services/langchain_service.py
import aiohttp
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from app.core.config import settings

class MistralService:
    """
    Service to interact with Mistral LLM using async HTTP requests.
    Uses LangChain's ChatPromptTemplate for structured prompts.
    """
    def __init__(self):
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = settings.MISTRAL_MODEL
        self.api_key = settings.MISTRAL_API_KEY
        self.temperature = settings.MISTRAL_TEMPERATURE

    async def summarize_lessons(self, lessons: list[str]) -> str:
        """
        Summarize a list of lessons using Mistral LLM.
        """
        # Build prompt using LangChain
        prompt_template = ChatPromptTemplate.from_template(
            "Summarize the following lessons concisely and clearly:\n{lessons}"
        )
        prompt_text = prompt_template.format(lessons="\n".join(lessons))

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant that summarizes lessons."},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": self.temperature
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Mistral API error {response.status}: {text}")
                data = await response.json()
        
        # Extract content from Mistral response
        return data["choices"][0]["message"]["content"]
