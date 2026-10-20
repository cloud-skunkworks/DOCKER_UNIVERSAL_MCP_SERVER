# Cloud SDK configuration

All modes consume the same JSON array as `data/corpus.json`. Set `RAG_PROVIDER` to
exactly one of `local`, `aws`, `azure`, `gcp`. SDK imports are lazy; only the selected
adapter contacts a provider. Authentication and object loading occur at startup.
The MCP tool cannot choose another provider, object, endpoint or identity.

| Provider | Configuration | Identity | Least privilege |
|---|---|---|---|
| local | RAG_LOCAL_PATH | filesystem | read only approved file |
| aws | AWS_REGION, RAG_BUCKET, RAG_OBJECT | workload role through Boto3 credential chain | s3:GetObject on exact object; kms:Decrypt only if needed |
| azure | AZURE_STORAGE_ACCOUNT_URL, AZURE_STORAGE_CONTAINER, RAG_OBJECT | DefaultAzureCredential with secret-based EnvironmentCredential excluded; managed/workload identity in hosting | Storage Blob Data Reader on approved container |
| gcp | GCP_PROJECT_ID, RAG_BUCKET, RAG_OBJECT | ADC with attached service account or workload federation | storage.objects.get, scoped by bucket/condition |

Production configuration MUST use identity federation/attached roles. Boto3 and Google
ADC also support credential forms that are prohibited by this project's deployment
policy: do not inject static keys or service-account private-key JSON. Local Azure CLI
identity is for local testing only. Identity configuration is not automatically created
by Compose. Do not copy workstation credential directories into images. For cloud-mode
containers, provide the platform's short-lived federation token mount and non-secret
identity configuration using your deployment system. The supplied Compose file runs
local mode out of the box; cloud modes require this platform integration.

S3 uses standard retries (3 total attempts), 5s connect and 15s read timeouts. Azure
uses two retries, 5s connect and 15s read/service timeouts. GCS uses a 30s retry deadline
and 15s request timeout. These are SDK controls, not a strict total startup SLA.
Each adapter requests at most 1 MiB + 1 byte; parsing rejects oversized content.
Use uncompressed UTF-8 JSON objects; do not use content-encoding transforms.

Provision private storage endpoints/restricted access, encryption, retention and
metadata-only audit logging via your approved Terraform modules. No Terraform apply
or deployment is included. Pipeline authentication must use OIDC trust restricted to
the repository and approved branch/environment, with an explicit audience.

Cloud support here means **retrieval from object storage**, not Bedrock, Vertex AI or
Azure OpenAI inference. Model choice and model credentials remain with the agent host.
Cloud integration tests use mocked SDK clients; validate actual IAM/network access in
your sandbox before deployment.
