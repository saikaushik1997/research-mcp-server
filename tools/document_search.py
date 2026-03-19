import httpx
from config import settings

# RAG tool
async def search_documents(query: str, namespace: str = settings.rag_namespace) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.rag_api_url}/api/v1/query",
            json={"question": query, "namespace": namespace, "streaming": False},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()