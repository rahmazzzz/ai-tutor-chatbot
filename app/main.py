# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.routers import auth_routes, tutor_routes
from app.routers.agent_route import router as agent_router

# --------------------------
# Database setup (SQLAlchemy)
# --------------------------
DATABASE_URL = f"postgresql://postgres:{settings.SUPABASE_KEY}@{settings.SUPABASE_URL.split('//')[1]}/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables. Call only when running the server, not during tests."""
    Base.metadata.create_all(bind=engine)


# --------------------------
# FastAPI initialization
# --------------------------
app = FastAPI(
    title="AI Tutor with RAG",
    description="AI Tutor using Supabase, SQLAlchemy, LangChain, Mistral LLM, and JWT Auth",
    version="1.0.0"
)

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Include routers safely
# --------------------------
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(tutor_routes.router)  # /tutor prefix already defined in router
app.include_router(agent_router, prefix="/agent", tags=["Agent"])
app.include_router(agent_router, prefix="/agent", tags=["Lesson Planner"])
app.include_router(tutor_routes.router)
# --------------------------
# Entry point for running with `python -m app.main`
# --------------------------
if __name__ == "__main__":
    # Initialize database tables only when starting the server
    init_db()

    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
