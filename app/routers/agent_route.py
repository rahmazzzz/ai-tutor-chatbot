# app/routes/agent_route.py
from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.graph.langgraph_orchestrator import TutorOrchestrator

router = APIRouter()
orchestrator = TutorOrchestrator()

@router.get("/plan_lesson")
async def plan_lesson(topic: str, current_user=Depends(get_current_user)):
    user_id = current_user['sub']  # <- use 'sub' here
    plan = await orchestrator.handle_lesson_plan(user_id, topic)
    return plan