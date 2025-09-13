from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.utils.hashing import Hasher

class UserRepository:
    def create_user(self, db: Session, user: UserCreate):
        hashed_password = Hasher.get_password_hash(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()
