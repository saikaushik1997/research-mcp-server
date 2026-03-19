import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    async with stdio_client(
        StdioServerParameters(command="python", args=["server.py"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print("Tools:")
            for t in tools.tools:
                print(f"  - {t.name}")

            # List resources
            resources = await session.list_resources()
            print("\nResources:")
            for r in resources.resources:
                print(f"  - {r.uri}")

            # List prompts
            prompts = await session.list_prompts()
            print("\nPrompts:")
            for p in prompts.prompts:
                print(f"  - {p.name}")

            # Call a tool
            print("\nTesting web_search tool:")
            result = await session.call_tool("web_search", {"query": "RAG evaluation 2025"})
            print(result.content[0].text[:300])


asyncio.run(main())