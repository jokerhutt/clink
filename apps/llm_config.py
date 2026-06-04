"""Centralized LLM configuration for the project.

This module provides a consistent way to configure LLM models across the entire
project using environment variables.
"""

import os
import dotenv
import dspy
from google import genai
from typing import Any, Optional


def get_llm_model(model_type: str = "fast") -> dspy.LM:
    model_name, _ = get_model_name(model_type)
    api_key = _get_api_key_for_model(model_name)
    cache = False if model_type in ("fast", "default") else True
    return dspy.LM(model=model_name, api_key=api_key, cache=cache)


def get_model_info(model_type: str = "fast") -> dict[str, Any]:
    model_name, env_var = get_model_name(model_type)
    provider = _get_provider_from_model(model_name)
    api_key = _get_api_key_for_model(model_name)

    return {
        "model_name": model_name,
        "provider": provider,
        "has_api_key": bool(api_key),
        "env_var": env_var,
    }

def get_model_name(model_type: str = "fast") -> tuple[str, str]:
    if model_type == "judge":
        return (
            os.getenv(
                "LLM_JUDGE_MODEL", 
                "gemini/gemini-3.1-flash-lite-preview"
            ),
            "LLM_JUDGE_MODEL"
        )
    else :
        return (
            os.getenv(
                "LLM_FAST_MODEL",
                "gemini/gemini-3.1-flash-lite-preview"
            ),
            "LLM_FAST_MODEL"
        )

def get_gemini_client_for_tts(model_name: str | None = None):
    """Return Gemini client for TTS (not handled by DSPy)."""
    if model_name is None:
        from apps.shared.config import get_settings

        model_name = get_settings().voice_tts_model
    api_key = os.getenv("GEMINI_API_KEY") or dotenv.get_key(".env", "GEMINI_API_KEY")
    if model_name.startswith("gemini/"):
        model_name = model_name.removeprefix("gemini/")
    return genai.Client(api_key=api_key), model_name


def _get_provider_from_model(model_name: str) -> str:
    """Determine provider from model name."""
    if model_name.startswith("gpt-") or model_name.startswith("openai/"):
        return "openai"
    elif model_name.startswith("gemini/"):
        return "gemini"
    elif model_name.startswith("claude-"):
        return "anthropic"
    else:
        return "unknown"


def _get_api_key_for_model(model_name: str) -> Optional[str]:

    provider = _get_provider_from_model(model_name)

    if provider == "openai":
        return os.getenv("OPENAI_API_KEY") or dotenv.get_key(".env", "OPENAI_API_KEY")
    elif provider == "gemini":
        return os.getenv("GEMINI_API_KEY") or dotenv.get_key(".env", "GEMINI_API_KEY")
    elif provider == "anthropic":
        return os.getenv("ANTHROPIC_API_KEY") or dotenv.get_key(".env", "ANTHROPIC_API_KEY")
    else:
        return (os.getenv("OPENAI_API_KEY") or
                os.getenv("GEMINI_API_KEY") or
                os.getenv("ANTHROPIC_API_KEY") or
                dotenv.get_key(".env", "OPENAI_API_KEY") or
                dotenv.get_key(".env", "GEMINI_API_KEY") or
                dotenv.get_key(".env", "ANTHROPIC_API_KEY"))


def validate_model_config(model_type: str = "fast") -> tuple[bool, str]:
    """Validate that model configuration is complete.
    
    Args:
        model_type: Type of model to validate
        
    Returns:
        (is_valid, error_message) tuple
    """
    try:
        info = get_model_info(model_type)
        
        if not info["has_api_key"]:
            provider_key = f"{info['provider'].upper()}_API_KEY"
            return False, f"Missing {provider_key} in .env for model {info['model_name']}"
        
        return True, ""
    except Exception as e:
        return False, f"Configuration error: {e}"

