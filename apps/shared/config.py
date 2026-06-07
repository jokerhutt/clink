from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    llm_model: str = "gemini-2.5-flash-lite"
    llm_provider: str = "GOOGLE"
    discord_bot_token: str | None = None
    discord_application_id: int | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    google_api_key: str | None = None
    anthropic_api_key: str | None = None
    bot_personality: str = ""
    voice_tts_model: str | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()
