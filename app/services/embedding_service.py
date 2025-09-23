# app/services/embedding_service.py
import logging
from sqlalchemy.orm import Session
from typing import List, Tuple

from app.models.file import UploadedFile
from app.repositories.embedding_repository import EmbeddingRepository
from app.exceptions.base_exceptions import ExternalServiceError, ValidationError
from app.clients.cohere_client import CohereClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EXPECTED_DIM = 1024  # Must match your Postgres VECTOR column

class EmbeddingService:
    def __init__(self, db: Session):
        self.embedding_repo = EmbeddingRepository(db)

        # Use only Cohere
        try:
            self.client = CohereClient()
            logger.info("Using CohereClient for embeddings")
        except ValueError as e:
            raise ExternalServiceError(f"Cohere embedding client not available: {e}")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        embeddings = []
        for text in texts:
            emb = await self.client.embed(text)

            # Dimension check
            if len(emb) != EXPECTED_DIM:
                raise ValidationError(
                    f"Embedding dimension mismatch: got {len(emb)}, expected {EXPECTED_DIM}"
                )

            embeddings.append(emb)

        logger.info(f"Generated {len(embeddings)} embeddings via CohereClient")
        return embeddings

    async def embed_query(self, query: str) -> List[float]:
        if not query.strip():
            raise ValidationError("Query text is empty")

        emb = await self.client.embed(query)
        if len(emb) != EXPECTED_DIM:
            raise ValidationError(
                f"Query embedding dimension mismatch: got {len(emb)}, expected {EXPECTED_DIM}"
            )
        return emb

    async def create_and_store_embeddings(
        self,
        user_id: str,
        filename: str,
        file_path: str,
        chunks: List[str],
    ) -> Tuple[UploadedFile, List[List[float]]]:
        embeddings = await self.create_embeddings(chunks)
        return self.embedding_repo.store_file_and_embeddings(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            chunks=chunks,
            embeddings=embeddings,
        )
