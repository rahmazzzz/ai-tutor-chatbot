# app/services/user_progress_service.py
from supabase import create_client
from app.core.config import settings

class UserProgressService:
    def __init__(self):
        # Initialize Supabase client
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def get_user_profile(self, user_id: str):
        """
        Return basic user profile: skill level, language preference, etc.
        """
        response = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            user = response.data[0]
            return {
                "skill_level": user.get("skill_level", 1),
                "language": user.get("language", "en")
            }
        return {"skill_level": 1, "language": "en"}

    def get_completed_lessons(self, user_id: str):
        """
        Return list of completed lesson IDs for the user.
        """
        response = self.supabase.table("progress").select("lesson_id").eq("user_id", user_id).execute()
        if response.data:
            return [p["lesson_id"] for p in response.data]
        return []

    def mark_lesson_completed(self, user_id: str, lesson_id: str):
        """
        Mark a lesson as completed for the user.
        """
        self.supabase.table("progress").insert({"user_id": user_id, "lesson_id": lesson_id}).execute()
