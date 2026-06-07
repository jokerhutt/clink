
from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
