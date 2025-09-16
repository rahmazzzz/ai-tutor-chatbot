# app/services/sql_rag_service.py
import numpy as np
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.file_repository import FileRepository


class SQLRAGService:
    """
    Service for SQL-based RAG operations using repositories and pgvector.
    """

    def __init__(self, embedding_repo: EmbeddingRepository, file_repo: FileRepository):
        self.embedding_repo = embedding_repo
        self.file_repo = file_repo

    def get_similar_documents(self, query_embedding: list[float], k: int = 5):
        """
        Retrieve top-k similar documents using pgvector cosine similarity.
        """
        query_embedding_np = np.array(query_embedding)
        return self.embedding_repo.find_similar(query_embedding_np, k)
