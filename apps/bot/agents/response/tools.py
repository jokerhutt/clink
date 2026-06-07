

import os
from typing import Awaitable, Callable
import httpx
from apps.bot.services.research.brave import BraveSearch
from apps.bot.services.research.jina import JinaReader
from apps.bot.services.research.service import research
from apps.shared.httpx_client import get_http_client


def create_response_tools(on_research_event:  Callable[[str, str | None], Awaitable[None]] | None = None) :
    client = get_http_client()

    brave_api_key = os.environ.get("BRAVE_SEARCH_API_KEY", "")
    if not brave_api_key:
        raise RuntimeError("BRAVE_SEARCH_API_KEY not configured")

    jina_api_key = os.environ.get("JINA_API_KEY", "")
    if not jina_api_key:
        raise RuntimeError("JINA_API_KEY not configured")

    brave = BraveSearch(
        client = client,
        api_key = brave_api_key
    )

    jina = JinaReader(
        client = client,
        api_key = jina_api_key
    )

    async def research_tool(prompt: str) -> str:
        """
        Search the web and read relevant sources to answer a question.
        Use when current, factual, or external information is needed.
        """
        return await research(
            prompt = prompt,
            brave = brave,
            jina = jina,
            on_research_event = on_research_event
        )

    return [research_tool]
    
