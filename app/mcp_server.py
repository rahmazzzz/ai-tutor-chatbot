from mcp.server.fastmcp import FastMCP 
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.services.google_calendar_service import GoogleCalendarService
from app.repositories.calendar_repository import CalendarRepository
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate
from app.models.calendar_event import CalendarEvent, EventStatus
from app.models.base import Base
from app.repositories.base import BaseRepository
from app.clients.supabase_client import get_db

app = FastAPI()
mcp_server = FastMCP(app)

calendar_service = GoogleCalendarService()


@mcp_server.tool()
async def create_event(event: CalendarEventCreate, db: Session = Depends(get_db)):
    repo = CalendarRepository(db)
    google_event_id = calendar_service.create_event(event.dict())
    db_event = repo.create(db, {**event.dict(), "google_event_id": google_event_id})
    db.commit()
    return {"db_event": str(db_event.id), "google_event_id": google_event_id}


@mcp_server.tool()
async def mark_event_done(event_id: str, db: Session = Depends(get_db)):
    repo = CalendarRepository(db)
    db_event = repo.get(db, event_id)
    if not db_event:
        return {"error": "Event not found"}

    calendar_service.mark_event_done(db_event.google_event_id)
    db_event.status = EventStatus.completed
    db.commit()
    return {"message": "Event marked as done"}
