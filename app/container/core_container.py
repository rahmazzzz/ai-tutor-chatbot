# app/container/core_container.py
from sqlalchemy.orm import Session
from app.clients.supabase_client import get_db  # SQLAlchemy session dependency
from app.core.config import settings

# --- Repositories ---
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.file_repository import FileRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.user_repository import UserRepository

# --- Services ---
from app.services.auth_service import AuthService
from app.services.embedding_service import EmbeddingService
from app.services.file_processing import FileProcessingService
from app.services.langchain_service import LangChainLLMService
from app.services.rag_service import RAGService
from app.services.sql_rag_service import SQLRAGService
from app.services.storage_service import StorageService
from app.services.summarize_video import summarize_video_service
from app.services.user_progress_service import UserProgressService


# === Initialize DB session once ===
db_session: Session = next(get_db())


# === Repositories ===
chat_history_repo = ChatHistoryRepository(db_session)
embedding_repo = EmbeddingRepository(db_session)
file_repo = FileRepository(db_session)
progress_repo = ProgressRepository(db_session)
user_repo = UserRepository(db_session)


# === Services ===
auth_service = AuthService()
embedding_service = EmbeddingService(db_session)
file_processing_service = FileProcessingService()
mistral_service = LangChainLLMService()
rag_service = RAGService(db=db_session , top_k=5, memory_size=7)
sql_rag_service = SQLRAGService(
    embedding_repo=embedding_repo,
    file_repo=file_repo
)
storage_service = StorageService()
summarize_video_service = summarize_video_service
user_progress_service = UserProgressService()


# === Container Class ===
class CoreContainer:
    """
    Global singleton container exposing clients, repositories, and services.
    Designed for direct import in routes without Depends.
    """

    def __init__(self):
        # Repositories
        self.chat_history_repo = chat_history_repo
        self.embedding_repo = embedding_repo
        self.file_repo = file_repo
        self.progress_repo = progress_repo
        self.user_repo = user_repo

        # Services
        self.auth_service = auth_service
        self.embedding_service = embedding_service
        self.file_processing_service = file_processing_service
        self.mistral_service = mistral_service
        self.rag_service = rag_service
        self.sql_rag_service = sql_rag_service
        self.storage_service = storage_service
        self.summarize_video_service = summarize_video_service
        self.user_progress_service = user_progress_service


# === Global singleton instance ===
container = CoreContainer()
