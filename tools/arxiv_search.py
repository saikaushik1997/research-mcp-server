import arxiv

# web search catered towards research papers
async def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)
    return [
        {
            "title": p.title,
            "authors": [a.name for a in p.authors],
            "abstract": p.summary,
            "published": p.published.strftime("%Y-%m-%d"),
            "url": p.entry_id,
        }
        for p in client.results(search)
    ]