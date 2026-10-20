import pytest
from mcp import Client
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from mcp_rag.telemetry import RetrievalOnlyExporter
from mcp_rag.server import create_server

@pytest.mark.anyio
async def test_payload_not_exported(docs, monkeypatch):
    sink = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(RetrievalOnlyExporter(sink)))
    monkeypatch.setattr("mcp_rag.server.trace.get_tracer", provider.get_tracer)
    async with Client(create_server(docs)) as client:
        await client.call_tool("search_kb", {"query":"idempotency confidential-marker"})
    with provider.get_tracer("third.party").start_as_current_span("unsafe") as span:
        span.set_attribute("query", "confidential-marker")
    spans = sink.get_finished_spans()
    assert len(spans) == 1
    assert dict(spans[0].attributes) == {"rag.result_count":1}
    assert not spans[0].events
    assert "confidential-marker" not in spans[0].to_json()
    provider.shutdown()
