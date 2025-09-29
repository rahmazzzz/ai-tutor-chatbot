# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.base import Base
from app.routers import auth_routes, tutor_routes, chatbot_routes
from app.routers.agent_route import router as agent_router
from app.routers.voice_routes import router as voice_router
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.routers import voice_routes
from app.routers import notes_routes
# --------------------------
# Database setup
# --------------------------
DATABASE_URL = f"postgresql://postgres:{settings.SUPABASE_KEY}@{settings.SUPABASE_URL.split('//')[1]}/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

# --------------------------
# FastAPI app
# --------------------------
app = FastAPI(
    title="AI Tutor with RAG",
    description="AI Tutor using Supabase, SQLAlchemy, LangChain, Mistral LLM, and JWT Auth",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(notes_routes.router)
app.include_router(auth_routes.router)
app.include_router(tutor_routes.router, prefix="/tutor", tags=["Tutor"])
app.include_router(chatbot_routes.router)
app.include_router(agent_router, prefix="/agent", tags=["Agent"])

app.include_router(voice_routes.router)
# --------------------------
# Print routes on startup
# --------------------------
@app.on_event("startup")
async def print_routes():
    print("\n📌 Registered Routes:")
    for route in app.router.routes:
        if hasattr(route, "methods"):
            print(f"  {route.path} → {route.methods}")
        else:  # WebSockets don't have .methods
            print(f"  {route.path} → WebSocket")

# --------------------------
# Entry point
# --------------------------
if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
