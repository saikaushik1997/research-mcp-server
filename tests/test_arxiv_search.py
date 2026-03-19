import asyncio
from tools.arxiv_search import search_arxiv

async def main():
    results = await search_arxiv("retrieval augmented generation evaluation")
    for r in results:
        print(r["title"])
        print(r["published"])
        print(r["url"])
        print()

asyncio.run(main())