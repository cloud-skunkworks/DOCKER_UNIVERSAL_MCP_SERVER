"""Retrieval handoff for an agent. Generation remains in the host application."""
import asyncio
import json
import os
from mcp import Client

async def retrieve(question):
    async with Client(os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")) as client:
        result = await client.call_tool("search_kb", {"query": question, "limit": 3})
        if result.is_error:
            raise RuntimeError("Retrieval failed")
        return result.structured_content

if __name__ == "__main__":
    # Synthetic data only. A real agent passes evidence to its approved model,
    # enforces citation checking, and gates any financial action separately.
    print(json.dumps(asyncio.run(retrieve("payment retry idempotency")), indent=2))
