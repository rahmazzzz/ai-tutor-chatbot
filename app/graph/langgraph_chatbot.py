# app/graphs/chatbot_graph.py
from langgraph.graph import StateGraph, START, END
from app.agents.chatbot_agent import ChatbotService
from sqlalchemy.orm import Session
from app.clients.mistralai_client import MistralChatClient
from app.clients.cohere_client import CohereClient
from app.core.config import settings


class ChatbotGraph:
    def __init__(self, db: Session):
        self.service = ChatbotService(db)
        # Primary LLM: Mistral
        self.mistral_client = MistralChatClient(model_name=settings.MISTRAL_MODEL)
        # Fallback LLM: Cohere
        self.cohere_client = CohereClient()

    async def _invoke_llm(self, message: str) -> str:
        system_prompt = """
        You are an orchestrator agent. 
        Your job is to decide which specialist agent should handle the user's request.

        Agents:
        
        - video_agent
        - lesson_agent
        - web_agent
        - rag_agent

        Respond with ONLY the agent name.
        """
        # Try Mistral first
        try:
            response = await self.mistral_client.chat(
                user=message,
                system=system_prompt
            )
            return response.answer.strip().lower()
        except Exception as e:
            # Fallback to Cohere
            print(f"[ChatbotGraph] Mistral failed, falling back to Cohere: {e}")
            response_text = await self.cohere_client.generate(
                prompt=f"{system_prompt}\nUser message: {message}",
                max_tokens=50
            )
            return response_text.strip().lower()

    async def orchestrator_agent(self, state: dict):
        message = state["message"]
        user_id = state["user_id"]

        decision = await self._invoke_llm(message)
        if decision not in [ "video_agent", "lesson_agent", "web_agent", "rag_agent"]:
            decision = "rag_agent"

        return {"next": decision, "message": message, "user_id": user_id}



    async def video_agent(self, state: dict):
        return {"response": await self.service.summarize_video(state["user_id"], state["message"])}

    async def lesson_agent(self, state: dict):
        return {"response": await self.service.plan_lesson(state["user_id"], state["message"])}

    async def web_agent(self, state: dict):
        return {"response": await self.service.web_search(state["user_id"], state["message"])}

    async def rag_agent(self, state: dict):
        return {"response": self.service.rag_response(state["user_id"], state["message"])}

    def build(self):
        workflow = StateGraph(dict)

        workflow.add_node("orchestrator", self.orchestrator_agent)
        workflow.add_node("video_agent", self.video_agent)
        workflow.add_node("lesson_agent", self.lesson_agent)
        workflow.add_node("web_agent", self.web_agent)
        workflow.add_node("rag_agent", self.rag_agent)

        workflow.add_edge(START, "orchestrator")
        workflow.add_conditional_edges(
            "orchestrator",
            lambda state: state["next"],
            {
                
                "video_agent": "video_agent",
                "lesson_agent": "lesson_agent",
                "web_agent": "web_agent",
                "rag_agent": "rag_agent",
            },
        )
        
        workflow.add_edge("video_agent", END)
        workflow.add_edge("lesson_agent", END)
        workflow.add_edge("web_agent", END)
        workflow.add_edge("rag_agent", END)

        return workflow.compile()
