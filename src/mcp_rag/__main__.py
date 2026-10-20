"""Run behind loopback locally or a controlled container network."""
import logging
import os
import uvicorn
from starlette.responses import JSONResponse
from starlette.routing import Route
from .server import create_server
from .telemetry import configure

async def health(request):
    return JSONResponse({"status": "ready"})

def main():
    # SDK errors can carry user input: suppress library logs in this demo.
    logging.disable(logging.CRITICAL)
    provider = configure()
    try:
        server = create_server()
        app = server.streamable_http_app(stateless_http=True, json_response=True,
                                         max_request_body_size=16384)
        app.routes.append(Route("/healthz", health))
        uvicorn.run(app, host=os.getenv("MCP_HOST", "127.0.0.1"), port=int(os.getenv("MCP_PORT", "8000")),
                    access_log=False, log_level="critical")
    except Exception:
        raise SystemExit("Server failed; check configuration, corpus and workload identity.") from None
    finally:
        if provider:
            provider.shutdown()

if __name__ == "__main__":
    main()
