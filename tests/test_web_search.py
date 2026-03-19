import asyncio
from tools.web_search import search_web

async def main():
    results = await search_web("RAG evaluation frameworks 2025")
    for r in results:
        print(r.get("title"))
        print(r.get("url"))
        print()

asyncio.run(main())