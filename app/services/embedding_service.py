# app/services/embedding_service.py
import requests
import logging
from sqlalchemy.orm import Session
from typing import List

from app.models.file import UploadedFile
from app.models.embedding import Embedding
from app.exceptions.base_exceptions import ExternalServiceError, ValidationError
from app.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EmbeddingService:
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        if not self.api_key:
            raise ExternalServiceError("MISTRAL_API_KEY not set in settings")

        # Mistral embeddings endpoint
        self.api_url = "https://api.mistral.ai/v1/embeddings"
        self.model_name = "mistral-embed"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _request_embeddings(self, inputs: List[str]) -> List[List[float]]:
        """Internal helper to call Mistral embeddings API."""
        if not inputs:
            return []

        payload = {
            "model": self.model_name,
            "input": inputs,   
        }
        try:
            logger.info(f"Requesting embeddings from Mistral for {len(inputs)} inputs")
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=60
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Mistral API request failed: {e}")
            raise ExternalServiceError(f"Mistral embeddings API request failed: {e}")

        try:
            data = response.json()
        except ValueError:
            raise ExternalServiceError("Invalid JSON response from Mistral embeddings API")

        if "data" not in data or not isinstance(data["data"], list):
            raise ExternalServiceError(
                f"Unexpected response format from Mistral: {data}"
            )

        embeddings = []
        for item in data["data"]:
            emb = item.get("embedding")
            if not isinstance(emb, list):
                raise ExternalServiceError("Invalid embedding vector in response")
            embeddings.append(emb)

        logger.info(f"Received {len(embeddings)} embeddings from Mistral")
        return embeddings

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple text chunks using Mistral."""
        return self._request_embeddings(texts)

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query string."""
        if not query.strip():
            raise ValidationError("Query text is empty")

        embeddings = self._request_embeddings([query])
        return embeddings[0] if embeddings else []

    def create_and_store_embeddings(
        self,
        db: Session,
        user_id: str,
        filename: str,
        file_path: str,
        chunks: List[str],
    ):
        """Generate embeddings via Mistral, then store file + embeddings in DB."""
        embeddings = self.create_embeddings(chunks)

        try:
            file_entry = UploadedFile(
                user_id=user_id, filename=filename, file_path=file_path
            )
            db.add(file_entry)
            db.commit()
            db.refresh(file_entry)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store uploaded file {filename}: {e}")
            raise ValidationError(f"Failed to store uploaded file: {e}")

        try:
            for chunk, vector in zip(chunks, embeddings):
                emb_obj = Embedding(
                    file_id=file_entry.id,
                    content_chunk=chunk,
                    embedding_vector=vector,
                )
                db.add(emb_obj)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store embeddings for {filename}: {e}")
            raise ValidationError(f"Failed to store embeddings: {e}")

        return file_entry, embeddings
