# app/utils/web_search.py
from langchain_tavily import TavilySearch
from app.core.config import settings

async def search_web(query: str, max_results: int = 5):
    """
    Perform a web search using Tavily's Search API.
    Returns a list of dict: {"title": ..., "link": ..., "snippet": ...}
    """
    tavily_search = TavilySearch(
        tavily_api_key=settings.TAVILY_API_KEY,
        max_results=max_results,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )

    results = await tavily_search.arun(query)

    # Print/log the raw results to see what we actually got
    print("Raw TavilySearch results:", results)

    # If it's a dict with 'results' key, use that
    if isinstance(results, dict) and "results" in results:
        results_list = results["results"]
    elif isinstance(results, list):
        results_list = results
    else:
        # Fallback: wrap single string or unknown type into a list
        results_list = [str(results)]

    # Map results safely
    mapped_results = []
    for r in results_list:
        if isinstance(r, dict):
            mapped_results.append({
                "title": r.get("title", ""),
                "link": r.get("url", ""),
                "snippet": r.get("content", "")[:200],
            })
        else:  # if it's a string
            mapped_results.append({
                "title": "",
                "link": "",
                "snippet": str(r)[:200],
            })

    return mapped_results
