# app/models/chat_history.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.models.user import User
from app.models.base import Base  # make sure Base is your declarative_base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)  # assuming users table
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
