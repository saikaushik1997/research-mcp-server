import wikipediaapi


async def search_wikipedia(topic: str, language: str = "en") -> dict:
    wiki = wikipediaapi.Wikipedia(
        user_agent="research-mcp-server/0.1.0",
        language=language,
    )
    page = wiki.page(topic)
    if not page.exists():
        return {"error": f"No Wikipedia page found for '{topic}'"}
    return {
        "title": page.title,
        "summary": page.summary,
        "url": page.fullurl,
    }