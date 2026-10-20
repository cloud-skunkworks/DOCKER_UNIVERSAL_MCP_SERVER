# Validation report — 2026-10-15

Environment: Windows, PowerShell 7, Python 3.12.14, MCP 2.3.0.

| Check | Result |
|---|---|
| `python -m pytest -q` | **38 passed**, 7.17 seconds |
| Real Streamable HTTP server/client | Passed; tool output, readiness and untrusted Host rejection |
| MCP tools, resources and prompts | Passed using official SDK client |
| Corpus validation/ranking/citation bounds | Passed |
| AWS, Azure, GCP adapter contracts | Passed with mocked SDK clients; no cloud credentials used |
| OTel payload filtering | Passed; only result count exported, SDK spans excluded |
| FINOS CALM 1.0 schema | Passed using vendored upstream schemas |
| Code-spec schema and CALM drift | Passed |
| `python -m pip check` | No broken requirements |
| `docker compose config --quiet` | Passed |
| Docker image build/runtime | **Not executed**: installed Docker CLI had no reachable engine |
| Live cloud IAM/network/object retrieval | **Not executed**: no target cloud environment supplied |
| GitHub Actions workflow execution | **Pending**: supplied for repository publication |
| Load, penetration, PCI and organizational TOGAF reviews | **Not performed** |

The local execution sandbox initially blocked Windows asyncio's loopback socket pair;
tests were rerun with local networking enabled. A discovered MCP output-shape issue
was fixed by declaring a Pydantic result model before the passing run.

Direct and transitive Python versions are frozen in requirements.lock; the Windows-only
pywin32 dependency has a platform marker. Docker installs runtime requirements under
these constraints. The base image and GitHub action release tags are not digest/commit
pinned; production promotion must lock those and complete security scanning.

CI is configured to build the image, wait for health, invoke the MCP client and stop
the container. Passing local Python tests does not establish that those pending checks
will pass in your environment. No infrastructure, repository or image was published.

---

# Validation report — 0.2.0rc2 — 2026-10-19

Environment: Linux x86_64, Python 3.12.3 (matches CI and the container), Docker Engine 29.8.2,
Compose v5.6.0, MCP 2.3.0. Pins are from requirements.lock after the rc2 refresh.

| Check | Result |
|---|---|
| `pip check` | No broken requirements |
| `python -m pytest -q` | **38 passed**, 2.26 seconds |
| `python scripts/export_calm.py --check` | Valid, no drift |
| `docker compose config --quiet` | Passed |
| `docker compose up --build --wait` | Healthy. Built from a scratch copy that trusts the sandbox proxy CA; shipped Dockerfile unchanged |
| `GET /healthz` | `{"status":"ready"}` |
| `python examples/agent_client.py` | Exit 0; top hit `kb://documents/idempotency` |
| Untrusted Host header on `/mcp` | HTTP 421 |
| Container user, read-only rootfs, dropped capabilities, loopback port | Confirmed with `docker inspect` |
| GitHub Actions, `scripts/verify.ps1` | Not run. PowerShell 7 is not installed; its two commands were run directly |
| Cloud retrieval (AWS, Azure, GCP) and OTLP collector | Not run. No credentials or collector supplied |

Refreshed pins: starlette 1.9.0, httpx2 2.14.0, httpcore2 2.14.0, google-cloud-storage 3.17.1,
certifi 2026.10.18. `mcp` 2.3.0 was already the latest stable release.
