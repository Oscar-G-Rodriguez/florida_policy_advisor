from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.citations import validate_response_citations
from app.data.refresh import refresh_all
from app.data.registry import list_datasets
from app.models import AdviceRequest, AdviceResponse, MemoRequest, MemoResponse
from app.services.advisor import generate_advice
from app.services.memo import save_memo
from app.web import get_static_dir

app = FastAPI(title="Florida Policy Advisor", version="0.1.0")

allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/datasets")
async def datasets() -> dict:
    return {"datasets": list_datasets()}


@app.post("/api/refresh")
async def refresh() -> dict:
    results = refresh_all(allow_network=True)
    return {"status": "completed", "results": results}


@app.post("/api/advice", response_model=AdviceResponse)
async def advice(request: AdviceRequest) -> AdviceResponse:
    response = generate_advice(request)
    try:
        validate_response_citations(response)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return response


@app.post("/api/memo", response_model=MemoResponse)
async def memo(request: MemoRequest) -> MemoResponse:
    advice = request.advice or generate_advice(request.inputs)
    try:
        validate_response_citations(advice)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    memo_path, memo_markdown = save_memo(request.inputs, advice)
    return MemoResponse(memo_path=memo_path, memo_markdown=memo_markdown)


static_dir = get_static_dir()
if static_dir.exists():
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/{path:path}")
    async def serve_spa(path: str) -> FileResponse:
        if path.startswith("api") or path in {"health", "docs", "openapi.json"}:
            raise HTTPException(status_code=404, detail="Not found.")
        candidate = static_dir / path
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
