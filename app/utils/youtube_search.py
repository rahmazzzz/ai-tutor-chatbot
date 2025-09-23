import asyncio
from youtubesearchpython import VideosSearch

class YouTubeSearch:
    def __init__(self, max_results: int = 5):
        self.max_results = max_results

    async def search(self, query: str):
        def _search():
            videos_search = VideosSearch(query, limit=self.max_results)
            results = videos_search.result().get("result", [])

            videos = []
            for item in results:
                videos.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "description": (
                        item.get("descriptionSnippet", [{}])[0].get("text", "")
                        if item.get("descriptionSnippet") else ""
                    ),
                    "thumbnail": (
                        item["thumbnails"][0]["url"]
                        if item.get("thumbnails") else None
                    )
                })
            return videos

        # Run the blocking search in a separate thread
        return await asyncio.to_thread(_search)
