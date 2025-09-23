# app/routes/agent_route.py
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from app.deps import get_current_user
from app.graph.langgraph_orchestrator import TutorOrchestrator
from app.agents.advanced_lesson_planner_agent import AdvancedLessonPlannerAgent

# Router
router = APIRouter()

# Agents
orchestrator = TutorOrchestrator()
planner_agent = AdvancedLessonPlannerAgent()


# ---------- Response Models ----------

class WebLink(BaseModel):
    title: str
    link: str
    snippet: Optional[str]


class SummaryItem(BaseModel):
    type: str
    text: str


class Lesson(BaseModel):
    id: str
    title: str
    difficulty: int
    content: str
    type: str
    duration_minutes: int
    summary: List[SummaryItem]


# For Orchestrator agent (just lessons + external resources)
class OrchestratorLessonResponse(BaseModel):
    success: bool
    topic: str
    internal_lessons: str   # plain text summaries or combined content
    web_links: Optional[List[WebLink]] = None
    youtube_videos: Optional[List[dict]] = None


# For Planner agent (full structured study plan)
class LessonPlanResponse(BaseModel):
    success: bool
    topic: str
    internal_lessons: List[Lesson]   # structured lessons with summaries
    overall_summary: str
    web_links: Optional[List[WebLink]] = None
    youtube_videos: Optional[List[dict]] = None


# ---------- Routes ----------

@router.get("/plan_lesson_orchestrator", response_model=OrchestratorLessonResponse)
async def plan_lesson_orchestrator(
    topic: str = Query(..., description="Topic to study"),
    current_user=Depends(get_current_user),
):
    """
    Generate lessons + external resources using TutorOrchestrator.
    Does NOT create a structured study plan.
    """
    user_id = current_user["sub"]
    plan = await orchestrator.handle_lesson_plan(user_id, topic)

    if callable(plan) and hasattr(plan, "__await__"):
        plan = await plan

    return {"success": True, **plan}


@router.get("/plan_lesson", response_model=LessonPlanResponse)
async def plan_lesson(
    topic: str = Query(..., description="Topic to study"),
    time_per_task: int = Query(60, description="Minutes per task"),
    current_user=Depends(get_current_user),
):
    """
    Generate a structured study plan using Advanced Lesson Planner Agent.
    Each task will take 'time_per_task' minutes.
    """
    user_id = current_user["sub"]
    plan = await planner_agent.plan_lesson_for_topic(
        user_id, topic, minutes_per_task=time_per_task
    )

    if callable(plan) and hasattr(plan, "__await__"):
        plan = await plan

    return {"success": True, **plan}
