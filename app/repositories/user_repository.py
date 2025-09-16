# app/repositories/user_repository.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> User | None:
        """Fetch a user by their username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their email."""
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, username: str, email: str, hashed_password: str) -> User:
        """Create and persist a new user."""
        user = User(username=username, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
