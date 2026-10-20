# Security scope

This is a local synthetic-data demo. The MCP endpoint has no OAuth authorization layer.
Compose binds the host port to 127.0.0.1. Do not expose it publicly or load sensitive
data. Container-network peers may reach the service; use an isolated demo network.

Before shared hosting: require explicit approval for any public exposure, private
networking, TLS, MCP-compatible OAuth validation (issuer, audience and scopes),
authorized data access, request limits, identity-based storage access, egress control,
image vulnerability review, metadata-only audits and architecture/change approvals.
The demo's prompt-injection guidance is not a security enforcement mechanism.

No secrets belong in source, logs, GitHub variables or architecture JSON. Local-only
secrets, if absolutely required by other tooling, belong in ignored .env/.env.local;
this demo does not need them. Never submit payment/PII data to the sample corpus.
Library logging is disabled in the entry point to avoid accidental payload exposure.
If embedding create_server in another app, the host must review SDK logs and tracing.
Do not enable debug logs or broad automatic span instrumentation without redaction.

Use your organization's private security-reporting channel; do not paste credentials
or customer data into a public GitHub issue. Dependencies are version-pinned, not
claimed vulnerability-free. Review licenses, scan the image and lock file, and pin the
base-image digest and CI action commit hashes before governed production use.
