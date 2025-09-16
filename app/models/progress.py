# app/models/progress.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class Progress(Base):
    __tablename__ = "progress"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # references users.id
    lesson_id = Column(String, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
