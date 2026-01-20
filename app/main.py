from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.citations import validate_response_citations
from app.data.refresh import refresh_all
from app.data.registry import list_datasets
from app.models import AdviceRequest, AdviceResponse, MemoRequest, MemoResponse
from app.services.advisor import generate_advice
from app.services.memo import save_memo

app = FastAPI(title="Florida Policy Advisor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"] ,
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
