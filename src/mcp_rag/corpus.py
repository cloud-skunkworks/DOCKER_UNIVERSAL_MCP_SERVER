"""Bounded, immutable corpus snapshots and deterministic lexical retrieval."""
from dataclasses import dataclass
from hashlib import sha256
import json
import re

MAX_BYTES = 1_048_576

@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str

def parse_corpus(raw: bytes) -> tuple[Document, ...]:
    if len(raw) > MAX_BYTES:
        raise ValueError("Corpus exceeds byte limit")
    records = json.loads(raw)
    if not isinstance(records, list) or not 1 <= len(records) <= 200:
        raise ValueError("Corpus requires 1..200 documents")
    docs, ids = [], set()
    for row in records:
        if not isinstance(row, dict) or set(row) != {"id", "title", "text"}:
            raise ValueError("Document requires id, title and text only")
        if not all(isinstance(v, str) for v in row.values()):
            raise ValueError("Document fields must be strings")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", row["id"]):
            raise ValueError("Invalid document id")
        if row["id"] in ids or not 1 <= len(row["title"]) <= 160 or not 1 <= len(row["text"]) <= 12000:
            raise ValueError("Duplicate id or invalid field length")
        ids.add(row["id"])
        docs.append(Document(**row))
    return tuple(docs)

def tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.casefold()))

def search(docs: tuple[Document, ...], query: str, limit: int = 3) -> dict:
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 500:
        raise ValueError("Query must contain 1..500 characters")
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ValueError("Limit must be 1..10")
    terms = tokens(query)
    if not terms:
        raise ValueError("Query requires searchable words")
    ranked = []
    for doc in docs:
        matched = terms & tokens(doc.title + " " + doc.text)
        if matched:
            score = len(matched) / len(terms)
            ranked.append((score, doc))
    ranked.sort(key=lambda item: (-item[0], item[1].id))
    return {"matches": [
        {"id": d.id, "title": d.title, "text": d.text,
         "citation": "kb://documents/" + d.id,
         "sha256": sha256(d.text.encode()).hexdigest(), "score": round(s, 4)}
        for s, d in ranked[:limit]
    ], "retrieval": "lexical-token-overlap", "untrusted_content": True}
