# app/services/rag_service.py

import logging
import numpy as np
from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.models.embedding import Embedding
from app.models.file import UploadedFile
from app.exceptions.base_exceptions import ExternalServiceError
from app.core.config import settings
import requests

logger = logging.getLogger("RAGService")
logger.setLevel(logging.INFO)


class SQLAlchemyRetriever:
    """Retriever that fetches top-k similar documents from Postgres using pgvector."""

    def __init__(self, db: Session, embedding_service: EmbeddingService, top_k: int = 5):
        self.db = db
        self.embedding_service = embedding_service
        self.top_k = top_k

    def get_relevant_documents(self, query: str):
        logger.info("Retrieving documents for query: %s", query)
        query_vector = np.array(self.embedding_service.embed_query(query), dtype=np.float32)

        try:
            results = (
                self.db.query(Embedding)
                .join(UploadedFile)
                .order_by(Embedding.embedding_vector.cosine_distance(query_vector))
                .limit(self.top_k)
                .all()
            )
            return [e.content_chunk for e in results]
        except Exception as e:
            logger.exception("Failed to fetch relevant documents")
            raise ExternalServiceError(f"DB retrieval error: {e}")


class RAGService:
    def __init__(self, db: Session, top_k: int = 5):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.retriever = SQLAlchemyRetriever(db, self.embedding_service, top_k)
        self.api_key = settings.MISTRAL_API_KEY
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        if not self.api_key:
            raise ExternalServiceError("MISTRAL_API_KEY not set")

    def _call_llm(self, prompt: str) -> str:
        """Call Mistral LLM with retrieved context."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "mistral-medium",  # pick a chat model
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Mistral API request failed: {e}")
            raise ExternalServiceError(f"Mistral API request failed: {e}")

        return data["choices"][0]["message"]["content"].strip()

    def ask_question(self, question: str) -> str:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        docs = self.retriever.get_relevant_documents(question)
        context = "\n\n".join(docs) if docs else "No context found."
        prompt = f"Answer the question based on the context below:\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
        return self._call_llm(prompt)
