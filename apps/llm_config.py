"""Centralized LLM configuration for the project."""

from typing import Any

import dspy
from google import genai

from apps.shared.config import get_settings


_PROVIDER_ALIASES = {
    "google": "google",
    "gemini": "google",
    "openai": "openai",
    "anthropic": "anthropic",
}

_DSPY_PROVIDER_PREFIXES = {
    "google": "gemini",
    "openai": "openai",
    "anthropic": "anthropic",
}


def get_llm_model(*, cache: bool = False) -> dspy.LM:
    provider = get_provider_name()
    return dspy.LM(
        model=get_dspy_model_name(),
        api_key=get_api_key(provider),
        cache=cache,
    )


def get_model_info() -> dict[str, Any]:
    provider = get_provider_name()
    return {
        "model_name": get_model_name(),
        "provider": provider,
        "has_api_key": bool(get_api_key(provider)),
        "env_vars": ["LLM_PROVIDER", "LLM_MODEL"],
    }


def get_model_name() -> str:
    return get_settings().llm_model.strip()


def get_provider_name() -> str:
    raw_provider = get_settings().llm_provider.strip().lower()
    try:
        return _PROVIDER_ALIASES[raw_provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported LLM_PROVIDER: {get_settings().llm_provider}") from exc


def get_dspy_model_name() -> str:
    provider = get_provider_name()
    return f"{_DSPY_PROVIDER_PREFIXES[provider]}/{get_model_name()}"


def get_pydantic_ai_model_name() -> str:
    return f"{get_provider_name()}:{get_model_name()}"


def get_gemini_client_for_tts(model_name: str | None = None):
    """Return Gemini client for TTS (not handled by DSPy)."""
    if model_name is None:
        settings = get_settings()
        model_name = settings.voice_tts_model or settings.llm_model

    api_key = get_settings().google_api_key or get_settings().gemini_api_key
    if model_name.startswith("gemini/"):
        model_name = model_name.removeprefix("gemini/")
    return genai.Client(api_key=api_key), model_name


def get_api_key(provider: str | None = None) -> str | None:
    settings = get_settings()
    provider = provider or get_provider_name()
    if provider == "openai":
        return settings.openai_api_key
    if provider == "google":
        return settings.google_api_key or settings.gemini_api_key
    if provider == "anthropic":
        return settings.anthropic_api_key
    raise ValueError(f"Unsupported LLM provider: {provider}")


def validate_model_config() -> tuple[bool, str]:
    """Validate that model configuration is complete."""
    try:
        info = get_model_info()
        if not info["has_api_key"]:
            provider_key = (
                "GOOGLE_API_KEY or GEMINI_API_KEY"
                if info["provider"] == "google"
                else f"{info['provider'].upper()}_API_KEY"
            )
            return False, f"Missing {provider_key} in .env for model {info['model_name']}"
        return True, ""
    except Exception as e:
        return False, f"Configuration error: {e}"
