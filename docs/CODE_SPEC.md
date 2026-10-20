# Executable code specification

Authoritative input: `architecture/code-spec.json`. It defines stable requirement IDs,
component IDs, connections, typed MCP contracts, bounds, decisions and TOGAF views.
The Python implementation realizes this specification; the generator does not infer
architecture from arbitrary Python. Changes to behavior require spec and test review.

| Specification field | CALM 1.0 output |
|---|---|
| components.id/type/name/description | nodes.unique-id/node-type/name/description |
| connections.id/source/target/protocol | relationships with connects endpoints |
| container + mcp | deployed-in relationship |
| requirements, interfaces, data_contract, decisions, scope, togaf | metadata preserving traceability |

Run `python scripts/export_calm.py` to generate; use `--check` as a pipeline gate.
The converter validates the input schema, unique IDs, connection references, the
vendored FINOS CALM schema and byte-for-byte generated-output drift. It is intentionally
a small, explicit compiler that can be extended to your enterprise CALM patterns.
No custom enterprise pipeline schema was supplied; this package targets FINOS CALM 1.0.

## Behavior contract

Startup MUST read exactly one configured corpus. Cloud failures MUST fail startup.
Documents MUST have unique safe IDs, bounded strings and no extra fields. The corpus
MUST be sanitized before ingestion; this demo does not perform DLP or prove content safe.
Search MUST return token-overlap matches ordered by score then ID, up to the limit.
Empty matches MUST be returned as an empty list, never invented evidence. Scores are
lexical coverage, not probabilities. Unicode word tokenization does not perform stemming.
Resource access MUST use known IDs; caller input MUST NOT select a path or cloud URL.
Every match MUST include a stable citation URI and content digest. Restart refreshes
the snapshot; content hashes distinguish revisions at the same URI.

## Acceptance and boundaries

See requirement verification pointers in the JSON and tests. SDKs supply retry behavior
with configured bounds; startup cloud availability is outside offline test coverage.
The service has no inference calls, session memory, ingestion write API, transaction
tool or vector index. An agent uses the client example to pass retrieved evidence to
its separately approved LLM. This is a retrieval component of RAG, not a complete agent.
