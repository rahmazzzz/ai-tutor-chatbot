from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base
from pgvector.sqlalchemy import VECTOR

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    content_chunk = Column(String, nullable=False)
    embedding_vector = Column(VECTOR(1024))  # pgvector-compatible

    file = relationship("UploadedFile", back_populates="embeddings")
