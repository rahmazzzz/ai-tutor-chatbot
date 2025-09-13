# app/container/core_container.py
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.services.embedding_service import EmbeddingService
from app.services.file_processing import FileProcessingService
from app.services.rag_service import RAGService
from app.services.sql_rag_service import SQLRAGService
from app.services.storage_service import StorageService

# Core container exposes service instances only
class AuthContainer:
    def __init__(self):
        self.service = AuthService()  # Expose the service directly

class EmbeddingContainer:
    def __init__(self):
        self.service = EmbeddingService()

class FileProcessingContainer:
    def __init__(self):
        self.service = FileProcessingService()

class RAGContainer:
    def __init__(self, db: Session):
        self.service = RAGService(db=db)

class SQLRAGContainer:
    def __init__(self, db: Session):
        self.service = SQLRAGService(db=db)

class StorageContainer:
    def __init__(self):
        self.service = StorageService()
