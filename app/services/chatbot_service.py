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
from sqlalchemy.orm import Session
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIDEO_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"


class ChatbotService:
    """
    A toolbox of specialist skills that the orchestrator agent (Gemini) can call.
    This class no longer does keyword-based routing.
    """

    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatHistoryRepository(db)
        self.youtube_searcher = YouTubeSearch()
        self.lesson_planner = LessonPlannerAgent()
        self.advanced_planner = AdvancedLessonPlannerAgent()
        self.rag_service = RAGService(
            db,
            embedding_service=None,
            embedding_repo=None,
            file_repo=None,
            chat_repo=self.chat_repo,
        )
        self.sql_rag_service = SQLRAGService(
            embedding_repo=None,
            file_repo=None,
        )

    # --- Specialist Tools ---

    async def human_response(self, user_id: str, message: str) -> str:
        """Escalate to human support."""
        self.chat_repo.save_message(user_id, "user", message)
        response = "[HUMAN OVERRIDE] A human will respond shortly."
        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    async def summarize_video(self, user_id: str, url: str) -> str:
        """Summarize YouTube video."""
        self.chat_repo.save_message(user_id, "user", url)
        summary = await asyncio.to_thread(summarize_video_service, url)
        self.chat_repo.save_message(user_id, "assistant", summary)
        return summary

    async def plan_lesson(self, user_id: str, message: str) -> Dict[str, Any]:
        """Generate lesson plan for a topic."""
        topic = message.replace("plan lesson", "").replace("lesson plan", "").strip() or "general"
        self.chat_repo.save_message(user_id, "user", message)
        plan = await self.advanced_planner.plan_lesson_for_topic(user_id, topic)
        self.chat_repo.save_message(user_id, "assistant", str(plan))
        return plan

    async def web_search(self, user_id: str, message: str) -> Dict[str, Any]:
        """Perform web search."""
        query = message.replace("search web", "").strip()
        self.chat_repo.save_message(user_id, "user", message)
        results = await search_web(query)
        self.chat_repo.save_message(user_id, "assistant", str(results))
        return results

    def rag_response(self, user_id: str, message: str) -> str:
        """Answer using RAG (documents + LLM)."""
        self.chat_repo.save_message(user_id, "user", message)
        response = self.rag_service.chat(message, user_id)
        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    # --- History ---

    async def get_history(self, user_id: str, limit: int = 50):
        return self.chat_repo.get_by_user(self.db, user_id=user_id, limit=limit)
