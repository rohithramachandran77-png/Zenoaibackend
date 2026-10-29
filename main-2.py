import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.llm_client import chat_completion
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_key(authorization: str | None = Header(default=None)) -> None:
    """If ZENO_API_KEY is set, require 'Authorization: Bearer <key>'."""
    if not settings.zeno_api_key:
        return
    if authorization != f"Bearer {settings.zeno_api_key}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
async def health() -> dict:
    model_status = "unreachable"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(settings.model_url.rstrip("/") + "/models")
            model_status = "ok" if r.status_code == 200 else f"http {r.status_code}"
    except httpx.HTTPError:
        pass
    return {"status": "ok", "model": settings.model_name, "model_server": model_status}


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_key)])
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        reply = await chat_completion(req.messages, req.temperature, req.max_tokens)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Model server error: {e.response.status_code}")
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Model server unreachable")
    except (KeyError, IndexError, ValueError):
        raise HTTPException(status_code=502, detail="Unexpected response from model server")
    return ChatResponse(reply=reply, model=settings.model_name)
