import asyncio
from tools.wikipedia_search import search_wikipedia

async def main():
    result = await search_wikipedia("Retrieval-augmented generation")
    print(result["title"])
    print(result["url"])
    print(result["summary"][:300])

asyncio.run(main())