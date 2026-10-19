"""Optional, authenticated HTTP adapter for local service experiments."""
from __future__ import annotations

import hmac
import json
import os
from time import monotonic
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from starlette.concurrency import run_in_threadpool

from .runner import run

MAX_BODY_BYTES = 2_000_000


def create_app(api_key=None):
    key = api_key if api_key is not None else os.getenv("OR_API_KEY", "")
    if not isinstance(key, str) or len(key) < 16:
        raise RuntimeError("OR_API_KEY must contain at least 16 characters")
    app = FastAPI(title=__package__, version="0.3.0")
    header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def authorize(supplied=Depends(header)):
        if not supplied or not hmac.compare_digest(supplied.encode(), key.encode()):
            raise HTTPException(401, "invalid credentials")

    @app.middleware("http")
    async def observe(request, call_next):
        correlation = str(uuid4())
        started = monotonic()
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation
        response.headers["Server-Timing"] = f"processing;dur={(monotonic() - started) * 1000:.2f}"
        return response

    @app.get("/health/live")
    def health():
        return {"status": "ok", "storage": "none"}

    @app.post("/v1/analyze", dependencies=[Depends(authorize)], openapi_extra={
        "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}}
    })
    async def analyze(request: Request):
        chunks, size = [], 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_BODY_BYTES:
                raise HTTPException(413, "request body exceeds limit")
            chunks.append(chunk)
        try:
            payload = json.loads(b"".join(chunks))
            result = await run_in_threadpool(run, payload)
        except (ValueError, TypeError, KeyError, RecursionError):
            return JSONResponse(status_code=422, content={"detail": "invalid request; check the input contract"})
        return {"module": __package__, "schema_version": "2.0", "result": result}

    return app
