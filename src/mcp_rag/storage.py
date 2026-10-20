"""Only deployment configuration selects the corpus; MCP callers cannot select URLs."""
import os
from pathlib import Path
from urllib.parse import urlsplit
from .corpus import MAX_BYTES, parse_corpus

def required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError("Missing configuration: " + name)
    return value

def read_local():
    with Path(os.getenv("RAG_LOCAL_PATH", "data/corpus.json")).open("rb") as stream:
        return stream.read(MAX_BYTES + 1)

def read_aws():
    import boto3
    from botocore.config import Config
    client = boto3.client("s3", region_name=required("AWS_REGION"), config=Config(
        connect_timeout=5, read_timeout=15, retries={"mode": "standard", "total_max_attempts": 3}))
    try:
        result = client.get_object(Bucket=required("RAG_BUCKET"), Key=required("RAG_OBJECT"),
                                   Range=f"bytes=0-{MAX_BYTES}")
        with result["Body"] as body:
            return body.read(MAX_BYTES + 1)
    finally:
        client.close()

def read_azure():
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobClient
    url = required("AZURE_STORAGE_ACCOUNT_URL")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.query or parsed.fragment:
        raise ValueError("Azure account URL must be HTTPS without credentials or query")
    with DefaultAzureCredential(exclude_environment_credential=True,
                                exclude_interactive_browser_credential=True) as credential:
        with BlobClient(account_url=url, container_name=required("AZURE_STORAGE_CONTAINER"),
                        blob_name=required("RAG_OBJECT"), credential=credential,
                        retry_total=2, connection_timeout=5, read_timeout=15) as blob:
            return blob.download_blob(offset=0, length=MAX_BYTES + 1, max_concurrency=1,
                                      timeout=15).readall()

def read_gcp():
    from google.cloud import storage
    from google.api_core.retry import Retry
    with storage.Client(project=required("GCP_PROJECT_ID")) as client:
        blob = client.bucket(required("RAG_BUCKET")).blob(required("RAG_OBJECT"))
        return blob.download_as_bytes(start=0, end=MAX_BYTES, timeout=15,
                                      retry=Retry(initial=1, maximum=4, deadline=30))

def load_corpus():
    provider = os.getenv("RAG_PROVIDER", "local")
    readers = {"local": read_local, "aws": read_aws, "azure": read_azure, "gcp": read_gcp}
    if provider not in readers:
        raise ValueError("Unsupported RAG_PROVIDER")
    # Fail closed: provider failures never silently switch to demo data.
    return parse_corpus(readers[provider]())
