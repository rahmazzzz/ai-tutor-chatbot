# app/agents/lesson_planner.py
from app.services.user_progress_service import UserProgressService
from app.utils.web_search import search_web
from app.utils.youtube_search import YouTubeSearch
from app.services.langchain_service import summarize_lessons

class LessonPlannerAgent:
    def __init__(self, max_results: int = 5):
        self.progress = UserProgressService()
        self.max_results = max_results
        self.youtube_searcher = YouTubeSearch(max_results=max_results)

    async def plan_lesson_for_topic(self, user_id: str, topic: str):
        """
        Generate a learning plan for a given topic including:
        - Internal lessons
        - Web links (Tavily)
        - YouTube videos (youtube-search-python class)
        """
        # 1️⃣ User profile and progress
        profile = self.progress.get_user_profile(user_id)
        completed = self.progress.get_completed_lessons(user_id)

        # 2️⃣ Internal lessons (mock example; replace with embeddings search)
        lessons = [
            {
                "id": f"{topic}_{i}",
                "title": f"{topic} Lesson {i+1}",
                "difficulty": i+1,
                "content": f"Content for {topic} lesson {i+1}",
                "type": "pdf"
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
        youtube_videos = self.youtube_searcher.search(topic)  # class-based search

        # 4️⃣ Summarize internal lessons
        summarized_lessons = await summarize_lessons(ranked_internal)

        # 5️⃣ Compile final lesson plan
        plan = {
            "topic": topic,
            "internal_lessons": summarized_lessons,
            "web_links": web_links,
            "youtube_videos": youtube_videos
        }
        return plan
