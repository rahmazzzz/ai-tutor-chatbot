# app/utils/web_search.py
from langchain_tavily import TavilySearch
async def search_web(query: str, max_results: int = 5):
    """
    Perform a web search using Tavily's Search API.
    Returns a list of dict: {"title": ..., "link": ..., "snippet": ...}
    """
    tavily_search = TavilySearch(
        max_results=max_results,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )

    results = await tavily_search.arun(query)
    return [
        {
            "title": result["title"],
            "link": result["url"],
            "snippet": result["content"][:200],
        }
        for result in results
    ]
