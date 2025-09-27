# app/graphs/langgraph_chatbot.py
from langgraph.graph import StateGraph, START, END
from app.agents.chatbot_agent import ChatbotService
from sqlalchemy.orm import Session
from app.clients.mistralai_client import MistralChatClient
from app.clients.cohere_client import CohereClient
from app.core.config import settings
from app.utils.web_search import search_web
from app.utils.youtube_search import YouTubeSearch
import asyncio
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatbotGraph:
    def __init__(self, db: Session):
        self.service = ChatbotService(db)

        # Primary LLM: Mistral
        self.primary_client = MistralChatClient(model_name=settings.MISTRAL_MODEL)
        # Fallback LLM: Cohere
        self.fallback_client = CohereClient()

        # External searchers
        self.youtube_searcher = YouTubeSearch(max_results=5)

        # Valid agents
        self.agents = [
            "video_agent",
            "lesson_agent",
            "web_agent",
            "rag_agent",
            "calendar_agent"
        ]

    async def _invoke_llm(self, message: str) -> str:
        system_prompt = """
        You are an orchestrator agent.
        Decide which specialist agent should handle the user's request.
        Respond with ONLY the agent name: video_agent, lesson_agent, web_agent, rag_agent, calendar_agent
        """
        try:
            response = await self.primary_client.chat(user=message, system=system_prompt)
            return (response.answer or "").strip().lower()
        except Exception as e:
            logger.warning(f"[ChatbotGraph] Primary LLM failed: {e}, falling back to Cohere")
            try:
                fallback_resp = await self.fallback_client.generate(f"{system_prompt}\nUser message: {message}")
                return (fallback_resp or "").strip().lower()
            except Exception as e2:
                logger.error(f"[ChatbotGraph] Fallback LLM failed: {e2}")
                return "rag_agent"

    async def orchestrator_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        message = state["message"]
        user_id = state["user_id"]
        decision = await self._invoke_llm(message)
        if decision not in self.agents:
            decision = "rag_agent"
        return {"next": decision, "message": message, "user_id": user_id}

    # --- Specialist agent handlers ---
    async def video_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": await self.service.summarize_video(state["user_id"], state["message"])}

    async def lesson_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        plan = await self.service.plan_lesson(state["user_id"], state["message"])
        return {"response": plan}

    async def web_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state["message"]
        web_links = await search_web(query, max_results=5)
        youtube_links = await self.youtube_searcher.search(query)
        return {
            "response": {
                "query": query,
                "web_links": web_links or [],
                "youtube_videos": youtube_links or []
            }
        }

    async def rag_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": await self.service.rag_response(state["user_id"], state["message"])}

    async def calendar_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Add the last generated plan to Google Calendar for the user."""
        user_id = state["user_id"]

        # Fetch last plan from ChatHistory
        last_plan = await asyncio.to_thread(self.service.chat_repo.get_last_plan, user_id)
        if not last_plan:
            return {"response": "No lesson plan found to add to your calendar."}

        # Store plan in Google Calendar via PlanCalendarAgent
        try:
            result = await self.service.plan_calendar_agent.store_plan(user_id, last_plan)
            if isinstance(result, list):
                return {"response": f"Added {len(result)} events to your Google Calendar!"}
            else:
                logger.error(f"[calendar_agent] Unexpected result format: {result}")
                return {"response": f"Failed to add events: {result}"}
        except Exception as e:
            logger.error(f"[calendar_agent] Error storing plan: {e}", exc_info=True)
            return {"response": f"Failed to add events due to an error."}

    # --- Build LangGraph workflow ---
    def build(self):
        workflow = StateGraph(dict)
        workflow.add_node("orchestrator", self.orchestrator_agent)
        workflow.add_node("video_agent", self.video_agent)
        workflow.add_node("lesson_agent", self.lesson_agent)
        workflow.add_node("web_agent", self.web_agent)
        workflow.add_node("rag_agent", self.rag_agent)
        workflow.add_node("calendar_agent", self.calendar_agent)

        workflow.add_edge(START, "orchestrator")
        workflow.add_conditional_edges(
            "orchestrator",
            lambda state: state["next"],
            {agent: agent for agent in self.agents},
        )

        workflow.add_edge("video_agent", END)
        workflow.add_edge("lesson_agent", END)
        workflow.add_edge("web_agent", END)
        workflow.add_edge("rag_agent", END)
        workflow.add_edge("calendar_agent", END)

        return workflow.compile()
