from mcp.server.fastmcp import FastMCP 
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.services.google_calendar_service import GoogleCalendarService
from app.repositories.calendar_repository import CalendarRepository
from app.schemas.calendar import CalendarEventCreate
from app.models.calendar_event import EventStatus
from app.clients.supabase_client import get_db

# New imports for notes
from app.services.voice_service import VoiceService
from app.services.notes_service import NotesService

app = FastAPI()
mcp_server = FastMCP(app)

calendar_service = GoogleCalendarService()
voice_service = VoiceService()
notes_service = NotesService()

# --------------------
# Calendar Tools
# --------------------
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


# --------------------
# Notes Tool
# --------------------
@mcp_server.tool()
async def save_voice_notes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Transcribe audio -> organize notes -> save in Google Keep.
    """
    audio_bytes = await file.read()
    transcript = await voice_service.transcribe(audio_bytes)
    notes = notes_service.make_notes(transcript)

    # Save into Google Keep
    result = notes_service.save_to_keep("Lecture Notes", notes)

    return {
        "transcript": transcript,
        "notes": notes,
        "google_keep": result,
    }
