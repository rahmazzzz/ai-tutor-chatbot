# app/repositories/chat_history_repository.py
from sqlalchemy.orm import Session
from typing import List

from app.repositories.base import BaseRepository
from app.models.chat_history import ChatHistory


class ChatHistoryRepository(BaseRepository[ChatHistory]):
    def __init__(self ,db: Session):
        super().__init__(ChatHistory, db)

    # Custom query: get all chat history for a user
    def get_by_user(self, db: Session, user_id: str, limit: int = 50) -> List[ChatHistory]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_last_n_messages(self, user_id: str, n: int) -> List[ChatHistory]:
        """
        Return last `n` chat messages for a user, descending by creation time.
        """
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.created_at.desc())
            .limit(n)
            .all()
        )

    def save_message(self, user_id: str, role: str, message: str) -> ChatHistory:
        """
        Save a chat message to the database.
        """
        chat_entry = ChatHistory(
            user_id=user_id,
            role=role,
            message=message
        )
        self.db.add(chat_entry)
        self.db.commit()
        self.db.refresh(chat_entry)
        return chat_entry
