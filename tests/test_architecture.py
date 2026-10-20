import copy
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location("calm_export", ROOT/"scripts/export_calm.py")
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

def test_calm_schema_and_drift():
    spec = json.loads((ROOT/"architecture/code-spec.json").read_text())
    model = module.compile_spec(spec)
    module.validate_calm(model)
    assert model == json.loads((ROOT/"architecture/architecture.calm.json").read_text())

def test_dangling_relationship():
    spec = json.loads((ROOT/"architecture/code-spec.json").read_text())
    spec["connections"][0]["target"] = "missing"
    with pytest.raises(ValueError, match="Dangling"):
        module.compile_spec(spec)

def test_schema_rejects_bad_node():
    model = json.loads((ROOT/"architecture/architecture.calm.json").read_text())
    del model["nodes"][0]["unique-id"]
    with pytest.raises(Exception):
        module.validate_calm(model)
