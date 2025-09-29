from yt_dlp import YoutubeDL
import asyncio

class YouTubeSearch:
    def __init__(self, max_results: int = 5):
        self.max_results = max_results

    async def search(self, query: str):
        def _search():
            ydl_opts = {"quiet": True, "noplaylist": True, "extract_flat": "in_playlist"}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{self.max_results}:{query}", download=False)
                videos = []
                for entry in info["entries"]:
                    videos.append({
                        "title": entry.get("title"),
                        "url": entry.get("webpage_url"),
                        "description": entry.get("description"),
                        "thumbnail": entry.get("thumbnail")
                    })
            return videos

        return await asyncio.to_thread(_search)
