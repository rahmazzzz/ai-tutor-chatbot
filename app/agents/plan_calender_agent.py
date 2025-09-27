# app/services/plan_calendar_agent.py
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union
from dateutil import parser as date_parser
import asyncio
from app.repositories.chat_history_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlanCalendarAgent:
    def __init__(self, llm, chat_repo: ChatHistoryRepository, google_calendar):
        """
        Args:
            llm: LLM client (e.g., Mistral, OpenAI wrapper)
            chat_repo: ChatHistoryRepository for saving plans
            google_calendar: GoogleCalendarService for pushing events
        """
        self.llm = llm
        self.chat_repo = chat_repo  # Use repository directly
        self.google_calendar = google_calendar

    async def parse_plan_with_llm(self, user_text: str) -> Dict[str, Any]:
        """Convert user request into structured plan JSON using LLM."""
        system_prompt = """
        You are an AI study planner.
        Convert the user request into structured JSON plan metadata.

        Rules:
        - Extract:
          * title: short name of the study (string)
          * content: description of what to study (string)
          * start_date: date only, format YYYY-MM-DD
          * time: start time only, format HH:MM (24h)
          * days: number of study days (integer)
        - Do not expand into multiple lessons (the system will do that).
        - Respond ONLY with valid JSON.
        """
        llm_response = await self.llm.chat(user=user_text, system=system_prompt)
        raw_answer = llm_response.answer.strip()

        try:
            plan = json.loads(raw_answer)
        except json.JSONDecodeError:
            logger.error(f"[PlanCalendarAgent] Failed to parse LLM output as JSON: {raw_answer}")
            plan = {}

        return {
            "title": plan.get("title", "Study Session"),
            "content": plan.get("content", "General study plan"),
            "start_date": plan.get("start_date", datetime.utcnow().strftime("%Y-%m-%d")),
            "time": plan.get("time", "10:00"),
            "days": int(plan.get("days", 1)),
        }

    async def expand_plan(self, plan: Union[Dict[str, Any], str]) -> List[Dict[str, Any]]:
        """Expand a plan into individual lessons with datetime."""
        if isinstance(plan, str):
            plan = {
                "title": "Lesson Plan",
                "content": plan,
                "start_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "time": "10:00",
                "days": 1,
            }

        lessons = []
        try:
            base_date = date_parser.parse(f"{plan['start_date']} {plan['time']}")
        except Exception:
            logger.warning("[PlanCalendarAgent] Invalid start date/time, using now()")
            base_date = datetime.utcnow()

        for i in range(plan.get("days", 1)):
            start_time = base_date + timedelta(days=i)
            lessons.append(
                {
                    "title": plan.get("title", "Lesson Plan"),
                    "content": f"{plan.get('content', '')} (Day {i+1})",
                    "date": start_time,
                }
            )

        return lessons

    async def store_plan(self, user_id: str, plan: Union[Dict[str, Any], str]) -> List[Dict[str, Any]]:
        """Save lessons to DB and push to Google Calendar."""
        try:
            lessons = await self.expand_plan(plan)

            for lesson in lessons:
                # --- Save to DB ---
                await asyncio.to_thread(
                    self.chat_repo.save_message,  # call repository method directly
                    user_id=user_id,
                    role="plan",
                    message=json.dumps({
                        "title": lesson["title"],
                        "content": lesson["content"],
                        "date": lesson["date"].isoformat(),
                    })
                )

                # --- Push to Google Calendar ---
                if hasattr(self.google_calendar, "create_event"):
                    event_data = {
                        "title": lesson["title"],
                        "description": lesson["content"],
                        "start_time": lesson["date"],
                        "end_time": lesson["date"] + timedelta(hours=1),
                        "plan_text": plan.get("content") if isinstance(plan, dict) else str(plan)
                    }
                    await asyncio.to_thread(self.google_calendar.create_event, event_data)
                else:
                    logger.warning("[PlanCalendarAgent] GoogleCalendarService missing create_event method.")

            logger.info(f"[PlanCalendarAgent] Stored {len(lessons)} lessons for user {user_id}")
            return lessons

        except Exception as e:
            logger.error(f"[PlanCalendarAgent] store_plan failed: {e}", exc_info=True)
            return []

    async def handle_user_request(self, user_id: str, user_text: str) -> List[Dict[str, Any]]:
        """Full pipeline: parse -> expand -> store."""
        plan = await self.parse_plan_with_llm(user_text)
        lessons = await self.store_plan(user_id, plan)
        return lessons
