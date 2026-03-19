import httpx
from config import settings


async def search_web(query: str, max_results: int = 5) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.tavily_api_key,
                "query": query,
                "max_results": max_results,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json().get("results", [])