import logging
from typing import Protocol

logger = logging.getLogger(__name__)

class HasLMUsage(Protocol):
    def get_lm_usage(self) -> dict[str, int]: ...

class BaseAgent:

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def truncate_response(
        self,
        text:str,
        max_length: int = 2000
        ) -> str:

        if len(text) <= max_length:
            return text

        logger.warning("Response Truncated")
        return text[:max_length - 3] + "..."

    def extract_token_usage(self, result: HasLMUsage) -> int:
        try:
            usage_data = result.get_lm_usage()
            if usage_data:
                total_tokens = usage_data.get("total_tokens", 0)
                completion_tokens = usage_data.get("completion_tokens", 0)
                prompt_tokens = usage_data.get("prompt_tokens", 0)

                tokens_used = total_tokens if total_tokens else (prompt_tokens + completion_tokens)
                logger.debug(f"DSPy usage data: {usage_data}, extracted tokens: {tokens_used}")
                return tokens_used
        except (AttributeError, TypeError) as e:
            logger.debug(f"DSPy get_lm_usage() not available or empty: {e}")

        return 0

    def estimate_tokens(self, text: str) -> int :
        return len(text) // 4

