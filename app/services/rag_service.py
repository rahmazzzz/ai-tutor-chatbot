# app/services/rag_service.py
import logging
import numpy as np
from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.file_repository import FileRepository
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.exceptions.base_exceptions import ExternalServiceError
from app.clients.mistralai_client import MistralChatClient

logger = logging.getLogger("RAGService")
logger.setLevel(logging.INFO)


class SQLAlchemyRetriever:
    """Retriever that fetches top-k similar documents from Postgres using pgvector."""

    def __init__(self, embedding_repo: EmbeddingRepository, embedding_service: EmbeddingService, top_k: int = 5):
        self.embedding_repo = embedding_repo
        self.embedding_service = embedding_service
        self.top_k = top_k

    async def get_relevant_documents(self, query: str):
        logger.info("Retrieving documents for query: %s", query)
        query_vector = np.array(await self.embedding_service.embed_query(query), dtype=np.float32)

        try:
            results = self.embedding_repo.get_top_k_similar(query_vector, self.top_k)
            return [e.content_chunk for e in results]
        except Exception as e:
            logger.exception("Failed to fetch relevant documents")
            raise ExternalServiceError(f"DB retrieval error: {e}")


class RAGService:
    """Retrieval-Augmented Generation (RAG) service with memory and context."""

    def __init__(
        self,
        db: Session,
        top_k: int = 5,
        memory_size: int = 7,
    ):
        self.db = db
        self.embedding_service = EmbeddingService(db)
        self.embedding_repo = EmbeddingRepository(db)
        self.file_repo = FileRepository(db)
        self.chat_repo = ChatHistoryRepository(db)
        self.retriever = SQLAlchemyRetriever(self.embedding_repo, self.embedding_service, top_k)
        self.memory_size = memory_size  # last N messages
        self.llm_client = MistralChatClient()

    async def _call_llm(self, prompt: str):
        """Call Mistral LLM with prompt and return plain text answer."""
        try:
            response = await self.llm_client.chat(user=prompt)
            # Mistral returns structured object with `parsed.answer`
            if hasattr(response, "parsed") and hasattr(response.parsed, "answer"):
                return response.parsed.answer
            elif hasattr(response, "answer"):
                return response.answer
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Mistral client request failed: {e}")
            raise ExternalServiceError(f"Mistral client request failed: {e}")

    async def chat(self, user_input: str, user_id: str):
        """Main method to handle chat with memory and retrieval."""
        if not user_input.strip():
            raise ValueError("Input cannot be empty")

        # 1. Fetch last N chat messages for user
        past_messages = self.chat_repo.get_last_n_messages(user_id, self.memory_size)

        # 2. Build chat memory
        chat_context = "\n".join([f"{msg.role}: {msg.message}" for msg in past_messages])

        # 3. Retrieve relevant documents
        docs = await self.retriever.get_relevant_documents(user_input)
        doc_context = "\n\n".join(docs) if docs else "No context found."

        # 4. Construct the prompt in best-practice style
        prompt = (
            "You are an AI assistant. Answer the user question using the documents and conversation history below.\n\n"
            f"--- Documents ---\n{doc_context}\n\n"
            f"--- Conversation History ---\n{chat_context}\n"
            f"user: {user_input}\n\n"
            "Provide a clear, concise answer. Include sources if possible.\nAnswer:"
        )

        # 5. Call LLM
        response_text = await self._call_llm(prompt)

        # 6. Save chat history
        self.chat_repo.save_message(user_id=user_id, role="user", message=user_input)
        self.chat_repo.save_message(user_id=user_id, role="assistant", message=response_text)

        return response_text
