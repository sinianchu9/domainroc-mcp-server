"""End-to-end MCP stdio protocol smoke test (never calls the live domain API)."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_stdio_tool_discovery_and_rejected_url():
    async def run():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "domainroc_mcp.server"],
        )
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listed = await session.list_tools()
                assert any(tool.name == "check_domain" for tool in listed.tools)
                response = await session.call_tool(
                    "check_domain", arguments={"domain": "https://127.0.0.1"}
                )
                assert not response.isError
                assert "invalid_domain" in str(response.content)

    asyncio.run(asyncio.wait_for(run(), timeout=15))
