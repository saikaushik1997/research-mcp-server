import json
from mcp.server.fastmcp import FastMCP
from config import settings
from tools.web_search import search_web
from tools.arxiv_search import search_arxiv
from tools.wikipedia_search import search_wikipedia
from tools.document_search import search_documents

mcp = FastMCP("research-mcp-server", log_level="ERROR")


# ─── TOOLS ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the live web for current information, news, and recent developments.
    Use for: recent events, current data, anything not likely in the document store."""
    results = await search_web(query, max_results)
    return json.dumps(results, indent=2)


@mcp.tool()
async def arxiv_search(query: str, max_results: int = 5) -> str:
    """Search Arxiv for academic papers. Returns title, authors, abstract, published date, and URL.
    Use for: technical research, finding papers, academic citations, scientific topics."""
    results = await search_arxiv(query, max_results)
    return json.dumps(results, indent=2)


@mcp.tool()
async def wikipedia_search(topic: str) -> str:
    """Search Wikipedia for background information and definitions.
    Use for: overviews, historical context, general knowledge."""
    result = await search_wikipedia(topic)
    return json.dumps(result, indent=2)


@mcp.tool()
async def document_search(query: str, namespace: str = settings.rag_namespace) -> str:
    """Search the private document knowledge base using RAG retrieval.
    Use for: questions about uploaded documents and internal knowledge."""
    result = await search_documents(query, namespace)
    return json.dumps(result, indent=2)


# ─── RESOURCES ───────────────────────────────────────────────────────────────

@mcp.resource("documents://list")
async def list_documents() -> str:
    """Lists available document namespaces in the knowledge base."""
    return json.dumps({"namespaces": [settings.rag_namespace]})


# ─── PROMPTS ─────────────────────────────────────────────────────────────────

@mcp.prompt()
def deep_research(topic: str) -> str:
    """Research a topic thoroughly across web, Arxiv, Wikipedia, and internal documents."""
    return f"""Research the following topic thoroughly: {topic}

1. Search the web for recent developments
2. Search Arxiv for relevant academic papers
3. Search Wikipedia for background context
4. Search the document knowledge base for internal knowledge
5. Synthesize into a structured report with an executive summary, key findings per source, and notable references."""


if __name__ == "__main__":
    mcp.run(transport="stdio")