# app/repositories/embedding_repository.py
import logging
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.file import UploadedFile
from app.models.embedding import Embedding
from app.repositories.base import BaseRepository
from app.exceptions.base_exceptions import ValidationError
from sqlalchemy import text

logger = logging.getLogger(__name__)


class EmbeddingRepository(BaseRepository[Embedding]):
    def __init__(self, db: Session):
        super().__init__(Embedding, db)

    def store_file_and_embeddings(
        self,
        user_id: str,
        filename: str,
        file_path: str,
        chunks: list[str],
        embeddings: list[list[float]]
    ):
        """
        Persist uploaded file entry along with its embeddings.
        """
        try:
            file_entry = UploadedFile(
                user_id=user_id, filename=filename, file_path=file_path
            )
            self.db.add(file_entry)
            self.db.commit()
            self.db.refresh(file_entry)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store uploaded file {filename}: {e}")
            raise ValidationError(f"Failed to store uploaded file: {e}")

        try:
            for chunk, vector in zip(chunks, embeddings):
                # Ensure each embedding vector is a Python list
                if isinstance(vector, np.ndarray):
                    vector = vector.tolist()

                emb_obj = Embedding(
                    file_id=file_entry.id,
                    content_chunk=chunk,
                    embedding_vector=vector,
                )
                self.db.add(emb_obj)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store embeddings for {filename}: {e}")
            raise ValidationError(f"Failed to store embeddings: {e}")

        return file_entry, embeddings

    def get_top_k_similar(self, query_vector: np.ndarray, top_k: int = 5):
        """
        Retrieve the top-k most similar embeddings using pgvector cosine distance.
        """
        try:
            # Ensure query_vector is a Python list for SQL query
            if isinstance(query_vector, np.ndarray):
                query_vector = query_vector.tolist()

            results = (
            self.db.query(Embedding)
            .order_by(text(f"embedding_vector <=> ARRAY{query_vector}::vector"))
            .limit(top_k)
            .all()
          )
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve top-{top_k} embeddings: {e}")
            raise ValidationError(f"Failed to retrieve embeddings: {e}")
