# app/graphs/chatbot_graph.py
from langgraph.graph import StateGraph, START, END
from app.services.chatbot_service import ChatbotService
from sqlalchemy.orm import Session
from app.core.config import settings
from langchain_cohere import ChatCohere


class ChatbotGraph:
    def __init__(self, db: Session):
        self.service = ChatbotService(db)
        self.llm = ChatCohere(
            model="command-a-03-2025",
            cohere_api_key=settings.COHERE_API_KEY,
            temperature=0.3,
        )

    async def orchestrator_agent(self, state: dict):
        message = state["message"]
        user_id = state["user_id"]

        system_prompt = """
        You are an orchestrator agent. 
        Your job is to decide which specialist agent should handle the user's request.

        Agents:
        - human_agent
        - video_agent
        - lesson_agent
        - web_agent
        - rag_agent

        Respond with ONLY the agent name.
        """

        llm_response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ])

        decision = llm_response.content.strip().lower()
        if decision not in ["human_agent", "video_agent", "lesson_agent", "web_agent", "rag_agent"]:
            decision = "rag_agent"

        return {"next": decision, "message": message, "user_id": user_id}

    async def human_agent(self, state: dict):
        return {"response": await self.service.human_response(state["user_id"], state["message"])}

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
        workflow.add_node("human_agent", self.human_agent)
        workflow.add_node("video_agent", self.video_agent)
        workflow.add_node("lesson_agent", self.lesson_agent)
        workflow.add_node("web_agent", self.web_agent)
        workflow.add_node("rag_agent", self.rag_agent)

        workflow.add_edge(START, "orchestrator")
        workflow.add_conditional_edges(
            "orchestrator",
            lambda state: state["next"],
            {
                "human_agent": "human_agent",
                "video_agent": "video_agent",
                "lesson_agent": "lesson_agent",
                "web_agent": "web_agent",
                "rag_agent": "rag_agent",
            },
        )
        workflow.add_edge("human_agent", END)
        workflow.add_edge("video_agent", END)
        workflow.add_edge("lesson_agent", END)
        workflow.add_edge("web_agent", END)
        workflow.add_edge("rag_agent", END)

        return workflow.compile()
