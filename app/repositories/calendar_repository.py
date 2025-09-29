from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.calendar_event import CalendarEvent


class CalendarRepository(BaseRepository[CalendarEvent]):
    def __init__(self, db: Session):
        super().__init__(CalendarEvent, db)

    def get_by_google_event_id(self, db: Session, google_event_id: str):
        return db.query(CalendarEvent).filter(CalendarEvent.google_event_id == google_event_id).first()
