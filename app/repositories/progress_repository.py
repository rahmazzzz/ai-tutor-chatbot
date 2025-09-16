# app/repositories/progress_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.repositories.base import BaseRepository
from app.models.progress import Progress


class ProgressRepository(BaseRepository[Progress]):
    def __init__(self,db: Session):
        super().__init__(Progress,db)

    # Get all progress records for a specific user
    def get_by_user(self, db: Session, user_id: str) -> List[Progress]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    # Get progress for a specific user + lesson
    def get_by_user_and_lesson(self, db: Session, user_id: str, lesson_id: str) -> Optional[Progress]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.lesson_id == lesson_id)
            .first()
        )
