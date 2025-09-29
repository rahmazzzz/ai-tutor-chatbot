from app.services.user_progress_service import UserProgressService
from app.utils.web_search import search_web
from app.utils.youtube_search import YouTubeSearch
from app.services.langchain_service import LangChainLLMService


class LessonPlannerAgent:
    """
    Agent to plan lessons for a user, integrating:
    - Internal lessons first
    - Always include external web links + YouTube
    - Summarization via Mistral LLM
    """
    def __init__(self, max_results: int = 5):
        self.progress = UserProgressService()
        self.max_results = max_results
        self.youtube_searcher = YouTubeSearch(max_results=max_results)
        self.mistral = LangChainLLMService()

    async def plan_lesson_for_topic(self, user_id: str, topic: str):
        # 1️⃣ User profile and progress
        profile = self.progress.get_user_profile(user_id)
        completed = self.progress.get_completed_lessons(user_id)

        # 2️⃣ Internal lessons (mock example)
        lessons = [
            {
                "id": f"{topic}_{i}",
                "title": f"{topic} Lesson {i+1}",
                "difficulty": i + 1,
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

        # 3️⃣ Summarize internal lessons if available
        if ranked_internal:
            lesson_texts = [l["content"] for l in ranked_internal]
            summarized_lessons = await self.mistral.summarize_lessons(lesson_texts)
        else:
            summarized_lessons = []

        # 4️⃣ Always fetch external resources (web + YouTube)
        web_links = await search_web(topic, max_results=self.max_results)
        youtube_videos = await self.youtube_searcher.search(topic)

        # 5️⃣ Return unified response
        return {
            "topic": topic,
            "internal_lessons": summarized_lessons,
            "web_links": web_links or [],
            "youtube_videos": youtube_videos or []
        }
