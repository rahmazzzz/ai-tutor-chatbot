from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.deps import get_current_user
from app.clients.supabase_client import get_db
from app.graph.langgraph_chatbot import ChatbotGraph
from app.agents.chatbot_agent import ChatbotService
import asyncio

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def chat_endpoint(
    request: ChatRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Main chatbot endpoint.
    Runs the LangGraph workflow, which orchestrates agents
    (lesson, video, web, rag, calendar, etc.).
    """
    graph = ChatbotGraph(db).build()

    # Run the graph with user message
    state = await graph.ainvoke(
        {
            "message": request.message,
            "user_id": user["sub"],
        }
    )

    # Extract response (may be str, list, or coroutine)
    response = state.get("response", "")
    if asyncio.iscoroutine(response):
        response = await response
    if isinstance(response, list):
        response = " ".join(str(r) for r in response)

    # Optional: expose the orchestrator's decision
    decision = state.get("next", None)

    return {
        "response": response,
        "decision": decision,  # useful for debugging
        "raw_state": state,    # optional, remove in production if too verbose
    }


@router.get("/history")
async def chat_history(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve past chat history directly from ChatbotService.
    """
    service = ChatbotService(db)
    history = await service.get_history(user_id=user["sub"])
    return {"history": history or []}
