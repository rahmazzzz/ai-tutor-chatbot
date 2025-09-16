# app/repositories/file_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.repositories.base import BaseRepository
from app.models.file import UploadedFile


class FileRepository(BaseRepository[UploadedFile]):
    def __init__(self,db: Session):
        super().__init__(UploadedFile,db)

    # Get files uploaded by a specific user
    def get_by_user(self, db: Session, user_id: str) -> List[UploadedFile]:
        return db.query(self.model).filter(self.model.user_id == user_id).all()

    # Get a file by its filename (useful for avoiding duplicates)
    def get_by_filename(self, db: Session, user_id: str, filename: str) -> Optional[UploadedFile]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.filename == filename)
            .first()
        )
