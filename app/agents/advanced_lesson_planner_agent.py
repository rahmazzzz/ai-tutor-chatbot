# app/agents/advanced_lesson_planner_agent.py
from app.services.user_progress_service import UserProgressService
from app.utils.web_search import search_web
from app.utils.youtube_search import YouTubeSearch
from app.services.langchain_service import MistralService  # Keep your existing service

class AdvancedLessonPlannerAgent:
    """
    Advanced lesson planner agent that:
    - Fetches user progress
    - Ranks internal lessons
    - Uses web and YouTube searches
    - Summarizes lessons using MistralService
    - Allows user to set time per task
    """
    def __init__(self, max_results: int = 5):
        self.progress = UserProgressService()
        self.max_results = max_results
        self.youtube_searcher = YouTubeSearch(max_results=max_results)
        self.llm = MistralService()  # Use your existing langchain_service

    async def plan_lesson_for_topic(self, user_id: str, topic: str, minutes_per_task: int = 60):
        """
        Plan lessons for a given topic.
        `minutes_per_task` defines the duration for each lesson/task.
        """
        # 1️⃣ Get user profile and completed lessons
        profile = self.progress.get_user_profile(user_id)
        completed = self.progress.get_completed_lessons(user_id)

        # 2️⃣ Internal lessons (mock example, replace with embeddings search later)
        lessons = [
            {
                "id": f"{topic}_{i}",
                "title": f"{topic} Lesson {i+1}",
                "difficulty": i+1,
                "content": f"Content for {topic} lesson {i+1}",
                "type": "pdf",
                "duration_minutes": minutes_per_task  # <-- user-defined duration
            }
            for i in range(10)
        ]
        remaining_lessons = [l for l in lessons if l["id"] not in completed]
        ranked_internal = sorted(
            remaining_lessons,
            key=lambda x: abs(x['difficulty'] - profile['skill_level'])
        )[:self.max_results]

        # 3️⃣ External searches
        web_links = await search_web(topic, max_results=self.max_results)
        youtube_videos = self.youtube_searcher.search(topic)

        # 4️⃣ Summarize internal lessons using MistralService
        lesson_texts = [l["content"] for l in ranked_internal]
        summarized_lessons = await self.llm.summarize_lessons(lesson_texts)
        
        for lesson in ranked_internal:
            lesson_summary = await self.llm.summarize_lessons([lesson["content"]])
            lesson["summary"] = [{"type": "text", "text": lesson_summary}]

        # 5️⃣ Compile final lesson plan
        plan = {
            "topic": topic,
            "internal_lessons": [
                {**lesson, "summary": summarized_lessons} for lesson in ranked_internal
            ],
            "web_links": web_links,
            "youtube_videos": youtube_videos
        }
        return plan
