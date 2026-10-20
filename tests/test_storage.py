import io
from unittest.mock import MagicMock, patch
import pytest
from mcp_rag import storage
from mcp_rag.corpus import MAX_BYTES

def test_local_bound(tmp_path, monkeypatch):
    p = tmp_path / "big.json"
    p.write_bytes(b"x" * (MAX_BYTES + 100))
    monkeypatch.setenv("RAG_LOCAL_PATH", str(p))
    assert len(storage.read_local()) == MAX_BYTES + 1

def test_aws_sdk(raw, monkeypatch):
    for k, v in {"AWS_REGION":"us-east-1","RAG_BUCKET":"demo","RAG_OBJECT":"corpus.json"}.items():
        monkeypatch.setenv(k, v)
    client = MagicMock()
    client.get_object.return_value = {"Body": io.BytesIO(raw)}
    with patch("boto3.client", return_value=client) as factory:
        assert storage.read_aws() == raw
        assert factory.call_args.kwargs["config"].retries["total_max_attempts"] == 3
    client.get_object.assert_called_once_with(Bucket="demo", Key="corpus.json", Range=f"bytes=0-{MAX_BYTES}")
    client.close.assert_called_once()

def test_azure_sdk(raw, monkeypatch):
    for k,v in {"AZURE_STORAGE_ACCOUNT_URL":"https://demo.blob.core.windows.net",
                "AZURE_STORAGE_CONTAINER":"kb", "RAG_OBJECT":"corpus.json"}.items():
        monkeypatch.setenv(k,v)
    with patch("azure.identity.DefaultAzureCredential") as identity, patch("azure.storage.blob.BlobClient") as factory:
        blob = factory.return_value.__enter__.return_value
        blob.download_blob.return_value.readall.return_value = raw
        assert storage.read_azure() == raw
        assert identity.call_args.kwargs["exclude_environment_credential"] is True
        assert factory.call_args.kwargs["credential"] is identity.return_value.__enter__.return_value
        assert blob.download_blob.call_args.kwargs["length"] == MAX_BYTES + 1

@pytest.mark.parametrize("url", ["http://demo", "https://demo/?sig=secret", "https://user:pass@demo"])
def test_azure_rejects_unsafe_url(url, monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_URL", url)
    with pytest.raises(ValueError):
        storage.read_azure()

def test_gcp_sdk(raw, monkeypatch):
    for k,v in {"GCP_PROJECT_ID":"demo", "RAG_BUCKET":"kb", "RAG_OBJECT":"corpus.json"}.items():
        monkeypatch.setenv(k,v)
    with patch("google.cloud.storage.Client") as factory:
        client = factory.return_value.__enter__.return_value
        blob = client.bucket.return_value.blob.return_value
        blob.download_as_bytes.return_value = raw
        assert storage.read_gcp() == raw
        factory.assert_called_once_with(project="demo")
        client.bucket.assert_called_once_with("kb")
        assert blob.download_as_bytes.call_args.kwargs["end"] == MAX_BYTES

@pytest.mark.parametrize("provider", ["local","aws","azure","gcp"])
def test_dispatch(provider, raw, monkeypatch):
    monkeypatch.setenv("RAG_PROVIDER",provider)
    with patch.object(storage,"read_"+provider,return_value=raw):
        assert len(storage.load_corpus()) == 3

def test_fail_closed(monkeypatch):
    monkeypatch.setenv("RAG_PROVIDER","aws")
    with patch.object(storage,"read_aws",side_effect=RuntimeError("denied")), patch.object(storage,"read_local") as local:
        with pytest.raises(RuntimeError):
            storage.load_corpus()
        local.assert_not_called()

def test_bad_provider(monkeypatch):
    monkeypatch.setenv("RAG_PROVIDER","other")
    with pytest.raises(ValueError):
        storage.load_corpus()
