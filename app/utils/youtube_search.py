from youtubesearchpython import VideosSearch

class YouTubeSearch:
    def __init__(self, max_results: int = 5):
        self.max_results = max_results

    def search(self, query: str):
        videos_search = VideosSearch(query, limit=self.max_results)
        results = videos_search.result().get("result", [])

        videos = []
        for item in results:
            videos.append({
                "title": item["title"],
                "url": item["link"],
                "description": item.get("descriptionSnippet", [{}])[0].get("text", ""),
                "thumbnail": item["thumbnails"][0]["url"] if item.get("thumbnails") else None
            })
        return videos
