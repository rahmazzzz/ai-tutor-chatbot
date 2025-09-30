# app/agents/chatbot_agent.py
import re
from typing import Any, Dict
from sqlalchemy.orm import Session
import asyncio
import logging

from app.clients.mistralai_client import MistralChatClient
from app.services.summarize_video import summarize_video_service
from app.services.rag_service import RAGService
from app.services.sql_rag_service import SQLRAGService
from app.agents.advanced_search_agent import LessonPlannerAgent
from app.agents.advanced_lesson_planner_agent import AdvancedLessonPlannerAgent
from app.utils.web_search import search_web
from app.utils.youtube_search import YouTubeSearch
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.file_repository import FileRepository

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

        # --- Core dependencies ---
        self.llm_client = MistralChatClient()

        # --- RAG services ---
        self.rag_service = RAGService(db=db)
        embedding_repo = EmbeddingRepository(db)
        file_repo = FileRepository(db)
        self.sql_rag_service = SQLRAGService(
            embedding_repo=embedding_repo,
            file_repo=file_repo,
        )

    # --- Specialist Tools ---

    async def summarize_video(self, user_id: str, url: str) -> str:
        self.chat_repo.save_message(user_id, "user", url)
        summary = await asyncio.to_thread(summarize_video_service, url)
        self.chat_repo.save_message(user_id, "assistant", summary)
        return summary

    async def plan_lesson(self, user_id: str, message: str) -> Dict[str, Any]:
        topic = (
            message.replace("plan lesson", "")
            .replace("lesson plan", "")
            .strip()
            or "general"
        )
        self.chat_repo.save_message(user_id, "user", message)

        try:
            plan = await self.advanced_planner.plan_lesson_for_topic(user_id, topic)
            self.chat_repo.save_message(user_id, "assistant", str(plan))
            self.chat_repo.save_last_plan(user_id, plan)
            return {"plan_text": str(plan)}
        except Exception as e:
            logger.error(f"[ChatbotService] plan_lesson failed: {e}")
            return {"error": str(e)}

    async def web_search(self, user_id: str, message: str) -> Dict[str, Any]:
        query = message.replace("search web", "").strip()
        self.chat_repo.save_message(user_id, "user", message)

        try:
            results = await search_web(query)
            self.chat_repo.save_message(user_id, "assistant", str(results))
            return results
        except Exception as e:
            logger.error(f"[ChatbotService] web_search failed: {e}")
            return {"success": False, "error": str(e)}

    async def rag_response(self, user_id: str, message: str) -> str:
        self.chat_repo.save_message(user_id, "user", message)

        try:
            response = await self.rag_service.chat(user_input=message, user_id=user_id)
            if asyncio.iscoroutine(response):
                response = await response
            if isinstance(response, list):
                response = " ".join(str(r) for r in response)
            response = str(response)
        except Exception as e:
            logger.error(f"[ChatbotService] RAG failed: {e}")
            response = f"I'm sorry, I encountered an error while processing your request: {str(e)}"

        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    async def sql_rag_response(self, user_id: str, query_embedding: list[float], k: int = 5) -> str:
        self.chat_repo.save_message(user_id, "user", f"[SQL RAG QUERY] {query_embedding}")

        try:
            docs = self.sql_rag_service.get_similar_documents(query_embedding=query_embedding, k=k)
            if asyncio.iscoroutine(docs):
                docs = await docs
            response = " ".join(str(d) for d in docs) if isinstance(docs, list) else str(docs)
        except Exception as e:
            logger.error(f"[ChatbotService] SQL RAG failed: {e}")
            response = "[SQL RAG ERROR] Unable to fetch documents."

        self.chat_repo.save_message(user_id, "assistant", response)
        return response

    async def get_history(self, user_id: str, limit: int = 50):
        try:
            return self.chat_repo.get_by_user(self.db, user_id=user_id, limit=limit)
        except Exception as e:
            logger.error(f"[ChatbotService] get_history failed: {e}")
            return []

    async def handle_user_message(self, user_id: str, message: str) -> Dict[str, Any]:
        if "plan lesson" in message.lower() or "lesson plan" in message.lower():
            return await self.plan_lesson(user_id, message)
        else:
            return {"success": False, "info": "Message received, but no action matched."}
