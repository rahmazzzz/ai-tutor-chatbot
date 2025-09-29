# app/services/google_calendar_service.py
from googleapiclient.discovery import build
from typing import Dict, Any
from app.utils.google_auth import get_google_credentials
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GoogleCalendarService:
    def __init__(self):
        creds = get_google_credentials()
        self.service = build("calendar", "v3", credentials=creds)

    def create_event(self, event_data: Dict[str, Any]) -> str:
        """
        Create a Google Calendar event with study plan details.
        event_data should include:
        - title (str)
        - description (str) -> Lesson content for that day
        - start_time (datetime)
        - end_time (datetime)
        - plan_text (optional) -> Full plan content from LLM
        """
        description = event_data.get("description", "").strip()

        # Append the full plan if available
        if event_data.get("plan_text"):
            description += f"\n\n--- Full Plan ---\n{event_data['plan_text'].strip()}"

        event_body = {
            "summary": event_data["title"],
            "description": description or "No description provided",
            "start": {
                "dateTime": event_data["start_time"].isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": event_data["end_time"].isoformat(),
                "timeZone": "UTC",
            },
        }

        try:
            created_event = (
                self.service.events()
                .insert(calendarId="primary", body=event_body)
                .execute()
            )
            logger.info(f"[GoogleCalendarService] Event created: {created_event['id']}")
            return created_event["id"]
        except Exception as e:
            logger.error(f"[GoogleCalendarService] Failed to create event: {e}")
            raise

    def update_event(self, google_event_id: str, updates: Dict[str, Any]):
        return self.service.events().patch(
            calendarId="primary",
            eventId=google_event_id,
            body=updates,
        ).execute()

    def mark_event_done(self, google_event_id: str):
        """Mark an event as completed by updating both title and description."""
        event = self.service.events().get(
            calendarId="primary", eventId=google_event_id
        ).execute()

        updated_summary = f"✅ {event.get('summary', '')}".strip()
        updated_description = (
            (event.get("description") or "").strip() + "\n\nStatus: ✅ Completed"
        )

        return self.update_event(
            google_event_id,
            {
                "summary": updated_summary,
                "description": updated_description,
                "colorId": "11",  # green color
            },
        )

    def delete_event(self, google_event_id: str):
        self.service.events().delete(
            calendarId="primary", eventId=google_event_id
        ).execute()
