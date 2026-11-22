"""Regression checks for failure reporting and mismatched dependency pins."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("ci_checks", Path(__file__).resolve().parents[1] / "scripts/ci_checks.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def test_direct_pin_drift_is_rejected(tmp_path):
    (tmp_path / "requirements.txt").write_text("boto3==1.44.3\n")
    (tmp_path / "requirements-dev.txt").write_text("-r requirements.txt\n")
    (tmp_path / "requirements.lock").write_text("boto3==1.43.123\n")
    with pytest.raises(ValueError, match="lock=1.43.123"):
        checks.check_pins(tmp_path)


@pytest.mark.parametrize("outcome", ["failure", "skipped", "cancelled", None])
def test_incomplete_smoke_never_reports_pass(tmp_path, outcome):
    steps = {name: {"outcome": "success"} for name in checks.CHECKS}
    steps["retrieval"] = {} if outcome is None else {"outcome": outcome}
    output = tmp_path / "report.txt"
    assert not checks.report(steps, output)
    assert "Overall: NOT PASSED" in output.read_text()


def test_success_report(tmp_path):
    assert checks.report({name: {"outcome": "success"} for name in checks.CHECKS}, tmp_path / "report.txt")
