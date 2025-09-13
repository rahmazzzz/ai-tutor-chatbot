# app/services/sql_rag_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.embedding import Embedding
from app.models.file import UploadedFile
import numpy as np


class SQLRAGService:
    """
    Service for SQL-based RAG operations using SQLAlchemy and pgvector.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_similar_documents(self, query_embedding: list[float], k: int = 5):
        """
        Simple cosine similarity search using SQLAlchemy and pgvector.
        Returns top-k similar documents.
        """
        query_embedding_np = np.array(query_embedding)

        results = (
            self.db.query(UploadedFile, Embedding)
            .join(Embedding, UploadedFile.id == Embedding.file_id)
            .order_by(
                func.cosine_distance(Embedding.vector, query_embedding_np)  # Requires pgvector
            )
            .limit(k)
            .all()
        )
        return results
