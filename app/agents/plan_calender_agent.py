# app/services/plan_calendar_agent.py
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Union
from dateutil import parser as date_parser
import asyncio
from app.repositories.chat_history_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlanCalendarAgent:
    def __init__(self, llm, chat_repo: ChatHistoryRepository, google_calendar):
        self.llm = llm
        self.chat_repo = chat_repo
        self.google_calendar = google_calendar

    async def parse_plan_with_llm(self, user_text: str) -> Dict[str, Any]:
        """Convert user request into structured JSON with proper datetime."""
        system_prompt = """
        You are an AI study planner assistant.
        Convert the user request into structured JSON.

        Rules:
        - Extract:
          * title: short name of the study (string)
          * description: details of what to study (string)
          * start_time: when it begins (ISO 8601 datetime, e.g. 2025-09-29T17:00:00+03:00)
          * duration_minutes: how long (integer, default 60)
        - If user didn’t specify, set start_time = now + 1h, duration_minutes = 60.
        - Respond ONLY with valid JSON.
        """

        llm_response = await self.llm.chat(user=user_text, system=system_prompt)
        raw_answer = llm_response.answer.strip()

        try:
            plan = json.loads(raw_answer)
        except json.JSONDecodeError:
            logger.error(f"[PlanCalendarAgent] Failed to parse LLM output: {raw_answer}")
            plan = {}

        # Validate start_time
        try:
            start_time = date_parser.parse(plan.get("start_time"))
            if not start_time.tzinfo:
                start_time = start_time.replace(tzinfo=timezone.utc)
        except Exception:
            logger.warning("[PlanCalendarAgent] Invalid or missing start_time, using now()+1h")
            start_time = datetime.now(timezone.utc) + timedelta(hours=1)

        duration = int(plan.get("duration_minutes", 60))
        end_time = start_time + timedelta(minutes=duration)

        return {
            "title": plan.get("title", "Study Session"),
            "description": plan.get("description", "General study plan"),
            "start_time": start_time,
            "end_time": end_time,
        }

    async def store_plan(self, user_id: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Save a single plan and push to Google Calendar."""
        try:
            # --- Save to DB ---
            await asyncio.to_thread(
                self.chat_repo.save_message,
                user_id=user_id,
                role="plan",
                message=json.dumps({
                    "title": plan["title"],
                    "description": plan["description"],
                    "start_time": plan["start_time"].isoformat(),
                    "end_time": plan["end_time"].isoformat(),
                })
            )

            # --- Push to Google Calendar ---
            if hasattr(self.google_calendar, "create_event"):
                await asyncio.to_thread(self.google_calendar.create_event, plan)
            else:
                logger.warning("[PlanCalendarAgent] GoogleCalendarService missing create_event method.")

            logger.info(f"[PlanCalendarAgent] Stored plan for user {user_id}")
            return plan

        except Exception as e:
            logger.error(f"[PlanCalendarAgent] store_plan failed: {e}", exc_info=True)
            return {}

    async def handle_user_request(self, user_id: str, user_text: str) -> Dict[str, Any]:
        """Full pipeline: parse -> store -> return plan."""
        plan = await self.parse_plan_with_llm(user_text)
        result = await self.store_plan(user_id, plan)
        return result
