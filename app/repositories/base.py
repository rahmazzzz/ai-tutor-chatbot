# app/repositories/base.py
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeMeta

# T is any SQLAlchemy model inheriting from DeclarativeMeta
T = TypeVar("T", bound=DeclarativeMeta)


class BaseRepository(Generic[T]):
    """
    Generic repository for basic CRUD.
    - Services control commit/rollback.
    """

    def __init__(self, model: Type[T] ,db: Session):
        self.model = model
        self.db = db
    def get(self, db: Session, id: Any) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: Union[Dict[str, Any], Any]) -> T:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        return db_obj  # commit in service layer

    def update(self, db: Session, db_obj: T, obj_in: Union[Dict[str, Any], Any]) -> T:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> Optional[T]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
        return obj
