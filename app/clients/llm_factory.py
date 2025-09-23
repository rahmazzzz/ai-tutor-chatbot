import os
from app.clients.cohere_client import CohereClient
from app.clients.mistralai_client import MistralAIClient
from app.clients.gemini_client import GeminiClient
from app.clients.base_client import LLMClient

class LLMFactory:
    @staticmethod
    def create(provider: str) -> LLMClient:
        provider = provider.lower()

        if provider == "cohere":
            return CohereClient(api_key=os.getenv("COHERE_API_KEY"))
        elif provider == "mistral":
            return MistralAIClient(api_key=os.getenv("MISTRAL_API_KEY"))
        elif provider == "gemini":
            return GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider}")
