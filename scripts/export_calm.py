"""Compile code-spec JSON to CALM 1.0; validate offline and detect drift."""
import argparse
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]

def compile_spec(spec):
    Draft202012Validator(json.loads((ROOT / "architecture/code-spec.schema.json").read_text())).validate(spec)
    ids = [c["id"] for c in spec["components"]]
    relation_ids = [r["id"] for r in spec["connections"]]
    req_ids = [r["id"] for r in spec["requirements"]]
    if len(set(ids)) != len(ids) or len(set(relation_ids)) != len(relation_ids) or len(set(req_ids)) != len(req_ids):
        raise ValueError("Duplicate architecture identifiers")
    for relation in spec["connections"]:
        if relation["source"] not in ids or relation["target"] not in ids:
            raise ValueError("Dangling relationship")
    if not {"container", "mcp"}.issubset(ids) or "mcp-deployment" in relation_ids:
        raise ValueError("Required deployment nodes missing or reserved relationship ID used")
    return {
        "$schema": "https://calm.finos.org/release/1.0/meta/calm.json",
        "nodes": [{"unique-id": c["id"], "node-type": c["type"], "name": c["name"],
                   "description": c["description"]} for c in spec["components"]],
        "relationships": [{"unique-id": r["id"], "description": r["description"],
            "protocol": r["protocol"], "relationship-type": {"connects": {
                "source": {"node": r["source"]}, "destination": {"node": r["target"]}}}}
            for r in spec["connections"]] + [{"unique-id":"mcp-deployment", "relationship-type": {
                "deployed-in": {"container":"container", "nodes":["mcp"]}}}],
        "metadata": {"code-spec-version": spec["spec_version"], "status": spec["architecture_status"],
                     "requirements": spec["requirements"], "togaf": spec["togaf"],
                     "interfaces": spec["interfaces"], "data-contract": spec["data_contract"],
                     "decisions": spec["decisions"], "scope": spec["scope"]}
    }

def validate_calm(model):
    schemas = [json.loads(p.read_text()) for p in (ROOT / "architecture/schemas/calm-1.0").glob("*.json")]
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas)
    schema = next(s for s in schemas if s["$id"].endswith("/calm.json"))
    Draft202012Validator(schema, registry=registry).validate(model)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    spec = json.loads((ROOT / "architecture/code-spec.json").read_text())
    model = compile_spec(spec)
    validate_calm(model)
    output = json.dumps(model, indent=2) + "\n"
    path = ROOT / "architecture/architecture.calm.json"
    if args.check:
        if not path.exists() or path.read_text() != output:
            raise SystemExit("CALM drift: run python scripts/export_calm.py and commit the result")
    else:
        path.write_text(output, encoding="utf-8")
    print("Code spec and CALM 1.0 valid; no drift" if args.check else "Generated validated CALM 1.0")

if __name__ == "__main__":
    main()
