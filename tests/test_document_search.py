import asyncio
from tools.document_search import search_documents

async def main():
    result = await search_documents("what is gibbs sampling")
    print(result)

asyncio.run(main())