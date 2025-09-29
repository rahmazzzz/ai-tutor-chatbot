from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime


class CalendarEventCreate(CalendarEventBase):
    user_id: UUID


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class CalendarEventOut(CalendarEventBase):
    id: UUID
    user_id: UUID
    status: str
    google_event_id: Optional[str] = None

    class Config:
        orm_mode = True
