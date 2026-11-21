# Dependency and smoke checks

The `verify-demo` workflow tests the existing Python 3.12/3.15 matrix. Each job
checks installed direct dependencies against requirements.lock, runs pip check,
the regression suite and CALM drift check, then builds the Python 3.15 container.
The matrix varies the client/test Python; both jobs use the same container Python.

Two explicit container smoke checks must pass:

1. `python scripts/ci_checks.py health`: GET /healthz returns HTTP 200 and ready.
2. `python scripts/ci_checks.py retrieval`: a real MCP call returns the synthetic
   idempotency document, its citation, and the untrusted-content label.

Both smoke checks run after a successful build even if the first fails. Cleanup
runs regardless of prior failures. A text report records each step outcome and is
uploaded as `validation-python-3.12` or `validation-python-3.15`, retained 14 days.
Download it from the workflow run's Artifacts section. Failed, skipped or absent
checks cannot produce an overall PASS. A runner cancellation or setup failure may
prevent report creation; missing reports are not evidence of success.

This workflow does not merge or deploy. All checks must be green for the exact PR
commit before a merge decision. Dependency consistency is not a vulnerability
audit. Live cloud retrieval, real OTLP receipt, security/compliance/load reviews,
and immutable image/action pinning remain separate production gates.
