"""Opt-in OTel export. Never record queries, document text, credentials or exceptions."""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

class RetrievalOnlyExporter(SpanExporter):
    """Do not forward SDK spans, which may include argument or exception data."""
    def __init__(self, delegate):
        self.delegate = delegate

    def export(self, spans):
        safe = [s for s in spans if s.instrumentation_scope.name == "mcp_rag.retrieval"
                and s.name == "rag.search" and not s.events
                and set(s.attributes).issubset({"rag.result_count"})]
        return self.delegate.export(safe) if safe else SpanExportResult.SUCCESS

    def shutdown(self):
        self.delegate.shutdown()

    def force_flush(self, timeout_millis=30000):
        return self.delegate.force_flush(timeout_millis)

def configure():
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    if not endpoint:
        return None
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    provider = TracerProvider(resource=Resource.create({"service.name": "mcp-rag-demo"}))
    provider.add_span_processor(BatchSpanProcessor(RetrievalOnlyExporter(
        OTLPSpanExporter(endpoint=endpoint, timeout=5))))
    trace.set_tracer_provider(provider)
    return provider
