# app/services/sql_rag_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.embedding import Embedding
from app.models.file import UploadedFile
import numpy as np

def get_similar_documents(session: Session, query_embedding: list[float], k: int = 5):
    """
    Simple cosine similarity search using SQLAlchemy
    """
    query_embedding_np = np.array(query_embedding)

    results = (
        session.query(UploadedFile, Embedding)
        .join(Embedding, UploadedFile.id == Embedding.file_id)
        .order_by(
            func.cosine_distance(Embedding.vector, query_embedding_np)  # Requires pgvector
        )
        .limit(k)
        .all()
    )
    return results
