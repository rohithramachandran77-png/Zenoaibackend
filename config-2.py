from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Zeno AI Backend"

    # Any OpenAI-compatible server works: Ollama, vLLM, llama.cpp server, etc.
    model_url: str = "http://localhost:11434/v1"
    model_name: str = "llama3.2"
    model_api_key: str | None = None  # only if the model server needs one

    # Optional key that clients must send to use this backend (Bearer token)
    zeno_api_key: str | None = None

    temperature: float = 0.7
    max_tokens: int = 512
    request_timeout: float = 120.0

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
