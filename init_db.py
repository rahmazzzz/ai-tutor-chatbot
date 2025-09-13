# init_db.py
import logging
from sqlalchemy import create_engine
from app.models.base import Base
from app.models.embedding import Embedding  # 👈 ensures table gets registered
from app.models.file import UploadedFile  
from app.models.chat_history import ChatHistory# 👈 ensures table gets registered
from app.models.user import User
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

def init_db():
    logging.info("Creating tables...")

    # Use transaction pooler URL from .env
    engine = create_engine(settings.SUPABASE_DB_URL)

    # Create all tables from models
    Base.metadata.create_all(bind=engine)

    logging.info("✅ Tables created successfully in Supabase!")

if __name__ == "__main__":
    init_db()
