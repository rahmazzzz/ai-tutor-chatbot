import re
from typing import Any, Dict
from app.services.summarize_video import summarize_video_service
from app.services.rag_service import RAGService
from app.services.sql_rag_service import SQLRAGService
from app.agents.lesson_planner import LessonPlannerAgent
from app.agents.advanced_lesson_planner_agent import AdvancedLessonPlannerAgent
from app.utils.web_search import search_web
from app.utils.youtube_search import YouTubeSearch
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.file_repository import FileRepository
from sqlalchemy.orm import Session
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIDEO_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"


class ChatbotService:
    """
    A toolbox of specialist skills that the orchestrator agent (Gemini) can call.
    """

    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatHistoryRepository(db)
        self.youtube_searcher = YouTubeSearch()
        self.lesson_planner = LessonPlannerAgent()
        self.advanced_planner = AdvancedLessonPlannerAgent()

        self.rag_service = RAGService(db=db)

        embedding_repo = EmbeddingRepository(db)
        file_repo = FileRepository(db)
        self.sql_rag_service = SQLRAGService(
            embedding_repo=embedding_repo,
            file_repo=file_repo
        )

    # --- Specialist Tools ---

    async def human_response(self, user_id: str, message: str) -> str:
        self.chat_repo.save_message(user_id, "user", message)
        response = "[HUMAN OVERRIDE] A human will respond shortly."
        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    async def summarize_video(self, user_id: str, url: str) -> str:
        self.chat_repo.save_message(user_id, "user", url)
        summary = await asyncio.to_thread(summarize_video_service, url)
        self.chat_repo.save_message(user_id, "assistant", summary)
        return summary

    async def plan_lesson(self, user_id: str, message: str) -> Dict[str, Any]:
        topic = message.replace("plan lesson", "").replace("lesson plan", "").strip() or "general"
        self.chat_repo.save_message(user_id, "user", message)
        plan = await self.advanced_planner.plan_lesson_for_topic(user_id, topic)
        self.chat_repo.save_message(user_id, "assistant", str(plan))
        return plan

    async def web_search(self, user_id: str, message: str) -> Dict[str, Any]:
        query = message.replace("search web", "").strip()
        self.chat_repo.save_message(user_id, "user", message)
        results = await search_web(query)
        self.chat_repo.save_message(user_id, "assistant", str(results))
        return results

    async def rag_response(self, user_id: str, message: str) -> str:
        """Answer using RAG (documents + LLM), safely handling coroutines and list responses."""
        self.chat_repo.save_message(user_id, "user", message)

        try:
            response = await self.rag_service.chat(user_input=message, user_id=user_id)

            # If a coroutine is returned unexpectedly, await it
            if asyncio.iscoroutine(response):
                response = await response

            # If it's a list of objects, try to extract text
            if isinstance(response, list):
                def extract_text(r):
                    if hasattr(r, "text"):
                        return str(r.text)
                    elif hasattr(r, "thinking"):
                        return " ".join(str(t) for t in r.thinking)
                    return str(r)
                response = " ".join(extract_text(r) for r in response)

            # Ensure final response is a string
            response = str(response)

        except Exception as e:
            logger.error(f"[ChatbotService] RAG failed: {e}")
            response = "[RAG ERROR] Unable to fetch response."

        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    async def sql_rag_response(self, user_id: str, query_embedding: list[float], k: int = 5) -> str:
        """Retrieve documents from SQLRAGService and return combined text."""
        self.chat_repo.save_message(user_id, "user", f"[SQL RAG QUERY] {query_embedding}")

        try:
            docs = self.sql_rag_service.get_similar_documents(query_embedding=query_embedding, k=k)
            if asyncio.iscoroutine(docs):
                docs = await docs
            if isinstance(docs, list):
                response = " ".join(str(d) for d in docs)
            else:
                response = str(docs)
        except Exception as e:
            logger.error(f"[ChatbotService] SQL RAG failed: {e}")
            response = "[SQL RAG ERROR] Unable to fetch documents."

        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    # --- History ---

    async def get_history(self, user_id: str, limit: int = 50):
        return self.chat_repo.get_by_user(self.db, user_id=user_id, limit=limit)
