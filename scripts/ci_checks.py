"""Dependency and container smoke checks with a CI text report; no cloud access."""
import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ("install", "dependencies", "tests", "build", "health", "retrieval", "cleanup")


def pins(path):
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-r ")):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^;\s]+)(?:\s*;.*)?", line)
        if not match:
            raise ValueError(f"Expected exact pin in {path.name}: {line}")
        name = re.sub(r"[-_.]+", "-", match[1]).lower()
        if name in result:
            raise ValueError(f"Duplicate pin: {name}")
        result[name] = match[2]
    return result


def check_pins(root):
    locked = pins(root / "requirements.lock")
    for filename in ("requirements.txt", "requirements-dev.txt"):
        for name, expected in pins(root / filename).items():
            if locked.get(name) != expected:
                raise ValueError(f"{name}: {filename}={expected}, lock={locked.get(name)}")
            if version(name) != expected:
                raise ValueError(f"{name}: installed={version(name)}, expected={expected}")


def dependencies():
    check_pins(ROOT)
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    print("PASS: direct pins match constraints and installed packages; pip check passed")


def health(base_url):
    # Do not send loopback smoke traffic through environment-configured proxies.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(base_url + "/healthz", timeout=10) as response:
        if response.status != 200 or json.load(response).get("status") != "ready":
            raise ValueError("Health endpoint is not ready")
    print("PASS smoke 1: GET /healthz returned ready")


async def retrieval(base_url):
    from mcp import Client
    async with Client(base_url + "/mcp") as client:
        result = await client.call_tool("search_kb", {"query": "idempotency", "limit": 1})
        if result.is_error:
            raise ValueError("MCP tool returned an error")
        data = result.structured_content
        matches = data.get("matches", []) if isinstance(data, dict) else []
        if not matches or matches[0].get("id") != "idempotency":
            raise ValueError("Expected synthetic idempotency document")
        if matches[0].get("citation") != "kb://documents/idempotency":
            raise ValueError("Missing expected citation")
        if data.get("untrusted_content") is not True:
            raise ValueError("Retrieved content must be labelled untrusted")
    print("PASS smoke 2: MCP retrieval returned expected document, citation and trust label")


def report(steps, destination):
    results = {name: steps.get(name, {}).get("outcome", "not_run") for name in CHECKS}
    passed = all(value == "success" for value in results.values())
    lines = ["MCP dependency and smoke validation report",
             f"UTC: {datetime.now(timezone.utc).isoformat()}",
             f"Commit: {os.getenv('GITHUB_SHA', 'local working tree')}",
             f"Python: {sys.version.split()[0]}",
             f"Run: {os.getenv('GITHUB_SERVER_URL', '')}/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}",
             f"Requirements lock SHA256: {sha256((ROOT / 'requirements.lock').read_bytes()).hexdigest()}",
             "", *[f"{name}: {status}" for name, status in results.items()],
             "", f"Overall: {'PASS' if passed else 'NOT PASSED'}",
             "Scope: pinned dependency consistency, tests/CALM, Docker build, health and MCP retrieval.",
             "Not a vulnerability audit or production approval. Live cloud retrieval, OTLP receipt,",
             "security/compliance/load reviews and image/action pinning remain separate gates."]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=("dependencies", "health", "retrieval", "report"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/validation.txt")
    args = parser.parse_args()
    if args.check == "dependencies":
        dependencies()
    elif args.check == "health":
        health(args.base_url)
    elif args.check == "retrieval":
        asyncio.run(asyncio.wait_for(retrieval(args.base_url), timeout=30))
    elif not report(json.loads(os.environ.get("CHECK_STEPS_JSON", "{}")), args.output):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
