import json
from pathlib import Path
import pytest
from mcp_rag.corpus import parse_corpus

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
def raw():
    return (Path(__file__).resolve().parents[1] / "data/corpus.json").read_bytes()

@pytest.fixture
def docs(raw):
    return parse_corpus(raw)
