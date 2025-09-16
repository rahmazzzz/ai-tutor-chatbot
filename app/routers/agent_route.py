# app/routes/agent_route.py
from fastapi import APIRouter, Depends, Query
from app.deps import get_current_user
from app.graph.langgraph_orchestrator import TutorOrchestrator
from app.agents.advanced_lesson_planner_agent import AdvancedLessonPlannerAgent

router = APIRouter()

# Existing orchestrator-based route
orchestrator = TutorOrchestrator()

@router.get("/plan_lesson_orchestrator")
async def plan_lesson_orchestrator(
    topic: str = Query(..., description="Topic to study"),
    current_user=Depends(get_current_user)
):
    """
    Generate lesson plan via TutorOrchestrator.
    """
    user_id = current_user['sub']  # use 'sub' from JWT payload
    plan = await orchestrator.handle_lesson_plan(user_id, topic)
    return {"success": True, "plan": plan}

# New route using AdvancedLessonPlannerAgent
planner_agent = AdvancedLessonPlannerAgent()

@router.get("/plan_lesson")
async def plan_lesson(
    topic: str = Query(..., description="Topic to study"),
    time_per_task: int = Query(60, description="Minutes per task"),
    current_user=Depends(get_current_user)
):
    """
    Generate a structured study plan for the given topic using the Advanced Lesson Planner Agent.
    Each task will take 'time_per_task' minutes.
    """
    user_id = current_user['sub']
    plan = await planner_agent.plan_lesson_for_topic(user_id, topic, minutes_per_task=time_per_task)
    return {"success": True, "plan": plan}
