from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.deps import get_current_user
from app.clients.supabase_client import get_db
from app.graph.langgraph_chatbot import ChatbotGraph
from app.services.chatbot_service import ChatbotService

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
    Sends the user message into the LangGraph workflow (Cohere orchestrator).
    """
    graph = ChatbotGraph(db).build()   # ✅ build the workflow

    result = await graph.ainvoke(
        {
            "message": request.message,
            "user_id": user["sub"],
        }
    )
    response = result.get("response", "")

    return {"response": response}


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
    return {"history": history}
