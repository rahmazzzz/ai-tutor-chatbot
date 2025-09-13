from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Supabase user ID
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    embeddings = relationship("Embedding", back_populates="file")
