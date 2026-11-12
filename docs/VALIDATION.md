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


# Stability refresh — 2026-11-12

Scope: integrate PRs #1, #6, #7, #8, #9 and #10 with synchronized constraints.
The boto3 update requires a matching botocore update. The OTLP HTTP exporter
update requires the compatible OTel 1.45.2 / 0.66b2 dependency family.
CI now tests Python 3.12 and 3.15 and runs pip check. The telemetry payload test
uses an explicit always-on sampler so host sampling configuration cannot suppress
its assertion. Runtime sampling behavior is unchanged.

Historical evidence: main commit fff430bde58430ddfcc551a7eadcdf1f3a831a76 passed
[GitHub Actions run 40716883771](https://github.com/cloud-skunkworks/DOCKER_UNIVERSAL_MCP_SERVER/actions/runs/40716883771)
on October 28: 38 tests in 2.73 seconds on Python 3.12.15; verify.ps1 and CALM
checks passed; the Python 3.15 container built, became healthy and returned the
idempotency result through the MCP client. The earlier “Actions not run” and
“Python 3.12 matches the container” statements are historical, not current status.

Local integrated validation passed on November 12: 38 tests on Python 3.12.14
(4.27 s) and 38 tests on Python 3.15.2 (3.91 s); CALM checks passed on both;
pip check (3.12) and uv pip check (3.15) found no dependency conflicts.
Workspace proxy variables were removed for localhost tests.

The integrated changes must pass both CI matrix jobs before merge. Consult the
PR checks for the exact tested SHA and container build evidence. Local Docker
validation is unavailable in the editing environment.

Still pending: live AWS/Azure/GCP identity and object retrieval, real OTLP collector
receipt, load/penetration/compliance reviews, image/action pinning and security
scanning. Mocked cloud tests and in-memory telemetry tests do not close those gates.
Version remains 0.2.0rc2 until release scope and outstanding promotion gates are
satisfied; merging dependency updates does not itself certify production readiness.
