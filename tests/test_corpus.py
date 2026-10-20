import json
import pytest
from mcp_rag.corpus import MAX_BYTES, parse_corpus, search

def test_rank_and_citations(docs):
    result = search(docs, "payment idempotency", 1)
    item = result["matches"][0]
    assert item["id"] == "idempotency"
    assert item["citation"] == "kb://documents/idempotency"
    assert len(item["sha256"]) == 64
    assert result["untrusted_content"] is True

def test_no_match(docs):
    assert search(docs, "unfindableword")["matches"] == []

@pytest.mark.parametrize("query,limit", [("",3),("  ",3),("x"*501,3),("...",3),("a",0),("a",11),("a",True)])
def test_invalid_search(docs, query, limit):
    with pytest.raises(ValueError):
        search(docs, query, limit)

@pytest.mark.parametrize("data", [[], {}, [{"id":"../bad","title":"x","text":"x"}],
    [{"id":"x","title":"x","text":1}], [{"id":"x","title":"x","text":"x","secret":"no"}],
    [{"id":"x","title":"x","text":"x"}]*2])
def test_invalid_corpus(data):
    with pytest.raises(ValueError):
        parse_corpus(json.dumps(data).encode())

def test_byte_bound():
    with pytest.raises(ValueError, match="byte limit"):
        parse_corpus(b" " * (MAX_BYTES + 1))

def test_tie_break():
    docs = parse_corpus(b'[{"id":"z","title":"test","text":"word"},{"id":"a","title":"test","text":"word"}]')
    assert [x["id"] for x in search(docs, "word")["matches"]] == ["a","z"]
