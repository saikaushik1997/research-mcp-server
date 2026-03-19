# research-mcp-server

![Python](https://img.shields.io/badge/Python-3.11-blue)
![MCP](https://img.shields.io/badge/MCP-1.26.0-green)
![FastMCP](https://img.shields.io/badge/FastMCP-Latest-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

An MCP (Model Context Protocol) server that exposes multi-source research tools to any MCP-compatible host. Connects Claude Desktop to live web search, Arxiv, Wikipedia, and a private RAG knowledge base — enabling intelligent, orchestrated research workflows without a single hardcoded step.

**Built as a capstone project after completing both Anthropic MCP courses.**

---

## Demo

> TODO: Add Loom demo here — show Connectors menu, toggle on research server, run "search arxiv for RAG evaluation papers", show tool call blocks firing in sequence.

---

## Architecture

```
Claude Desktop (MCP Client)
        │
        │  stdio transport
        ▼
research-mcp-server (FastMCP)
        │
        ├── web_search       → Tavily Search API
        ├── arxiv_search     → Arxiv API (public)
        ├── wikipedia_search → Wikipedia API (public)
        ├── document_search  → RAG microservice (Project 1)
        │                      POST /api/v1/query
        │
        ├── resource: documents://list
        └── prompt:   deep_research(topic)
```

Claude Desktop sends tool call requests over stdio. The server executes the appropriate API call and returns results. Claude decides which tools to invoke and in what order — no orchestration logic lives in this server.

---

## Tools

| Tool | Description | When Claude Uses It |
|---|---|---|
| `web_search` | Live web search via Tavily | Recent events, current data, anything time-sensitive |
| `arxiv_search` | Academic paper search via Arxiv API | Technical research, finding papers, citations |
| `wikipedia_search` | Wikipedia summaries | Background context, definitions, general knowledge |
| `document_search` | RAG retrieval against uploaded documents | Questions about private/internal knowledge base |

**On tool selection:** Claude reads each tool's name and docstring at initialization and decides which to call based on the user's query. Well-written docstrings are the mechanism — a vague docstring leads to wrong tool selection. This is why each tool has an explicit "Use for:" line in its description.

---

## Resources & Prompts

**Resource — `documents://list`**
Returns the list of available Pinecone namespaces from the connected RAG service. Tells Claude which document collections it can search.

**Prompt — `deep_research(topic)`**
A structured research prompt that instructs Claude to use all four tools in sequence: web → Arxiv → Wikipedia → document store. Produces a comprehensive synthesis across all sources.

---

## Key Engineering Decisions

**document_search calls Project 1 over HTTP, not locally**
The RAG pipeline (Pinecone + Cohere reranking) is a production service deployed on Render. Rather than duplicating retrieval logic in this server, `document_search` calls the `/api/v1/query` endpoint over HTTP. This demonstrates service composition — each system has a clear boundary and owns its responsibility. The tradeoff is a cold start latency on Render's free tier (~30s if the service has spun down).

**stdio transport over HTTP**
Claude Desktop uses stdio (stdin/stdout) to communicate with local MCP servers. HTTP+SSE would require a running server process with a port — stdio is simpler, zero-config, and appropriate for a local development server. The server process is spawned and managed by Claude Desktop directly.

**FastMCP over raw MCP SDK**
FastMCP provides the `@mcp.tool()` decorator pattern that keeps tool definitions clean and co-located with their implementation. The docstring becomes the tool description the LLM reads — this is the critical interface. FastMCP handles the MCP protocol plumbing so tool logic stays readable.

**venv isolation**
The server runs in a dedicated Python 3.11 venv rather than the system Python. This avoids dependency conflicts with other projects on the same machine. Claude Desktop's config points directly to the venv Python executable.

---

## Running Locally

**Prerequisites:** Python 3.11, a Claude Desktop Pro account, a Tavily API key

```bash
# 1. Clone the repo
git clone https://github.com/saikaushik1997/research-mcp-server
cd research-mcp-server

# 2. Create and activate venv
python -m venv venv311
venv311\Scripts\activate          # Windows
# source venv311/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Fill in TAVILY_API_KEY in .env

# 5. Add to Claude Desktop config
# C:\Users\<user>\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "research": {
      "command": "C:\\path\\to\\venv311\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\research-mcp-server\\server.py"],
      "env": {
        "TAVILY_API_KEY": "your-tavily-key",
        "RAG_API_URL": "https://document-qna-rag.onrender.com",
        "RAG_NAMESPACE": "your-namespace"
      }
    }
  }
}
```

Restart Claude Desktop. Go to **+ → Connectors → research** and toggle it on.

---

## What I Would Do Next

**1. Add a citation aggregator tool**
Currently each tool returns raw results and Claude synthesizes them. A `synthesize_sources` tool that accepts results from multiple tools and deduplicates + ranks them by relevance would improve output quality on complex research queries. The interesting engineering challenge: what's the right deduplication signal — URL, semantic similarity, or both?

**2. Semantic caching for repeated queries**
Arxiv and Wikipedia results for the same query don't change hour-to-hour. Adding a Redis-backed cache keyed by query embedding (not exact string) would cut latency and API costs on repeated or semantically similar queries. Would also make the demo more reliable since Tavily's free tier has rate limits.

**3. Streaming tool results back to the client**
Currently `document_search` waits for the full RAG response before returning. FastMCP supports streaming — implementing it would allow Claude to start processing retrieved chunks before the full response arrives, which matters most for long documents. Requires the RAG microservice to also expose SSE streaming (it does — just not wired through here yet).

**4. Package as a DXT extension**
Claude Desktop now supports `.dxt` extension packages — a bundled format that includes the server, dependencies, and manifest in a single installable file. Packaging this as a DXT would let anyone install it from the Extensions marketplace with one click, no manual config file editing. The manifest would expose `TAVILY_API_KEY` and `RAG_API_URL` as user-configurable fields surfaced in the UI.

**5. Add PubMed as a fifth tool**
`arxiv_search` covers CS and ML well but misses biomedical research entirely. Adding a `pubmed_search` tool using the NCBI E-utilities API (free, no key required) would make the server genuinely useful for cross-domain research — especially relevant for AI in healthcare queries where both the ML methodology (Arxiv) and the medical application (PubMed) matter.

---

## Stack

| Component | Tool |
|---|---|
| MCP framework | FastMCP |
| Web search | Tavily Search API |
| Academic search | Arxiv API |
| General knowledge | Wikipedia API |
| Document retrieval | Project 1 RAG microservice |
| Transport | stdio |
| Python | 3.11 (venv) |
| Config | pydantic-settings + .env |

---

## Related Projects

- **[document-qna-rag](https://github.com/saikaushik1997/document-qna-rag)** — The RAG microservice that `document_search` calls. FastAPI + Pinecone + Cohere reranking, deployed on Render.
- **[autonomous-research-agent](https://github.com/saikaushik1997/autonomous-research-agent)** — LangGraph ReAct agent using similar tools directly via LangChain. Compare: MCP exposes tools to any host; LangGraph hardwires the orchestration loop.
