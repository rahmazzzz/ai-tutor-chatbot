# app/graph/langgraph_orchestrator.py
from app.agents.advanced_search_agent import LessonPlannerAgent

class TutorOrchestrator:
    def __init__(self):
        self.lesson_planner = LessonPlannerAgent()

    async def handle_lesson_plan(self, user_id: str, topic: str):
        return await self.lesson_planner.plan_lesson_for_topic(user_id, topic)
