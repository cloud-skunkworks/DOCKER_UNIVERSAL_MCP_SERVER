import pytest
from mcp import Client
from mcp_rag.server import create_server

@pytest.mark.anyio
async def test_protocol(docs):
    async with Client(create_server(docs)) as client:
        tools = await client.list_tools()
        assert any(t.name == "search_kb" for t in tools.tools)
        result = await client.call_tool("search_kb", {"query":"idempotency","limit":1})
        assert not result.is_error
        assert result.structured_content["matches"][0]["id"] == "idempotency"
        resources = await client.read_resource("kb://articles")
        assert "idempotency" in resources.contents[0].text
        doc = await client.read_resource("kb://documents/idempotency")
        assert "Synthetic" in doc.contents[0].text
        prompt = await client.get_prompt("grounded_answer", {"question":"How to retry?"})
        assert "untrusted" in prompt.messages[0].content.text

@pytest.mark.anyio
async def test_tool_error(docs):
    async with Client(create_server(docs)) as client:
        result = await client.call_tool("search_kb", {"query":" ","limit":3})
        assert result.is_error
        result = await client.call_tool("search_kb", {"query":"x","limit":11})
        assert result.is_error

@pytest.mark.anyio
async def test_resource_unknown(docs):
    async with Client(create_server(docs)) as client:
        with pytest.raises(Exception):
            await client.read_resource("kb://documents/not-found")
