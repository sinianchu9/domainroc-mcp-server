"""Run a real local stdio MCP session against DomainRoc's public, read-only search.

After `python -m pip install -e .`:
    python examples/demo_stdio.py --domain example.com

This process launches the local server, discovers tools, queries one domain,
and exits. No registrar credentials or DomainRoc account are needed.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(domain: str) -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "domainroc_mcp.server"],
    )
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            print("Discovered MCP tools:", ", ".join(names))
            if "check_domain" not in names:
                raise RuntimeError("The server did not advertise check_domain")
            response = await session.call_tool("check_domain", arguments={"domain": domain})
            if response.isError:
                raise RuntimeError("check_domain returned an MCP tool error")
            # MCP SDKs can expose the returned dict as structuredContent
            # or as a TextContent item; support either without changing it.
            payload = response.structuredContent
            if payload is None:
                for item in response.content:
                    if item.type == "text":
                        payload = json.loads(item.text)
                        break
            if not isinstance(payload, dict):
                raise RuntimeError("check_domain returned no JSON result")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            if payload.get("status") == "unknown":
                print("Result not confirmed. Do not infer availability or price.")


def main() -> int:
    parser = argparse.ArgumentParser(description="DomainRoc MCP stdio demo (read-only)")
    parser.add_argument("--domain", default="example.com", help="A single domain name")
    args = parser.parse_args()
    try:
        asyncio.run(asyncio.wait_for(run(args.domain), timeout=25))
    except (OSError, RuntimeError, ValueError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Demo failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
