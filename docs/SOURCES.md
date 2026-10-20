# Source notes — reviewed 2026-10-15

This is an original implementation inspired by the tutorial's tool/resource/prompt
pattern. It is not a verbatim copy. Official SDK APIs and installed-package tests are
the authority for executable behavior.

- Tutorial: https://www.kdnuggets.com/build-your-first-mcp-server-in-python-stateless-spec-edition
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP v2 guide/testing: https://py.sdk.modelcontextprotocol.io/get-started/
- FINOS CALM schemas: https://github.com/finos/architecture-as-code/tree/main/calm/release/1.0/meta
- TOGAF overview: https://www.opengroup.org/togaf
- AWS credentials: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
- Azure Identity: https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme
- Google ADC: https://cloud.google.com/docs/authentication/application-default-credentials

Package versions were resolved from PyPI on the review date and frozen in requirements.lock.
CALM schemas are vendored unmodified for offline validation; see third-party notices.
