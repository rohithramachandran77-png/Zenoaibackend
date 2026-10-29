import httpx

from app.config import settings
from app.schemas import Message


async def chat_completion(
    messages: list[Message],
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Send a chat to the OpenAI-compatible model server and return the reply text."""
    headers = {"Content-Type": "application/json"}
    if settings.model_api_key:
        headers["Authorization"] = f"Bearer {settings.model_api_key}"

    payload = {
        "model": settings.model_name,
        "messages": [m.model_dump() for m in messages],
        "temperature": temperature if temperature is not None else settings.temperature,
        "max_tokens": max_tokens or settings.max_tokens,
    }

    url = settings.model_url.rstrip("/") + "/chat/completions"
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]
