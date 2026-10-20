"""Exercise actual Streamable HTTP, startup readiness and DNS rebinding protection."""
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from mcp import Client

ROOT = Path(__file__).resolve().parents[1]

def test_real_http():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port = sock.getsockname()[1]
    env = dict(os.environ, PYTHONPATH=str(ROOT/"src"), MCP_HOST="127.0.0.1", MCP_PORT=str(port),
               RAG_PROVIDER="local", RAG_LOCAL_PATH=str(ROOT/"data/corpus.json"))
    env.pop("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",None)
    process = subprocess.Popen([sys.executable,"-m","mcp_rag"],cwd=ROOT,env=env,
                               stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    try:
        ready = False
        for _ in range(100):
            assert process.poll() is None, "Server exited before readiness"
            try:
                with urllib.request.urlopen(url+"/healthz",timeout=1) as response:
                    ready = json.load(response)["status"] == "ready"
                if ready:
                    break
            except OSError:
                time.sleep(0.1)
        assert ready
        async def call():
            async with Client(url+"/mcp") as client:
                result = await client.call_tool("search_kb",{"query":"idempotency"})
                assert not result.is_error
                assert result.structured_content["matches"][0]["id"] == "idempotency"
        asyncio.run(call())
        request = urllib.request.Request(url+"/mcp",data=b'{}',headers={"Content-Type":"application/json", "Host":"attacker.invalid"})
        try:
            urllib.request.urlopen(request,timeout=3)
            raise AssertionError("Untrusted host accepted")
        except urllib.error.HTTPError as error:
            assert error.code == 421
    finally:
        process.terminate()
        process.wait(timeout=10)
