

import os
from typing import Awaitable, Callable
import httpx
from apps.bot.services.research.brave import BraveSearch
from apps.bot.services.research.jina import JinaReadError, JinaReader
from apps.bot.services.research.service import research
from apps.bot.services.research.status_reporter import ResearchEventHandler
from apps.shared.httpx_client import get_http_client


def create_response_tools(research_handler: ResearchEventHandler | None = None) :
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
        Search the web only when external information is genuinely needed.

        Before using this tool ask:

        1. Can I answer this from my existing knowledge?
        2. Is the answer likely to still be correct today?
        3. Would searching materially improve the answer?

        Use this tool only if the answer depends on:
        - recent information
        - changing information
        - information not already known
        - verification from external sources

        Do not use this tool when you can already answer confidently.

        A factual question alone is NOT sufficient reason to research.

        Default to answering directly.
        Research should be the exception, not the default.
        """
        return await research(
            prompt = prompt,
            brave = brave,
            jina = jina,
            research_handler = research_handler
        )

    async def url_tool(url: str) -> str:
        """
        Read and summarize the contents of a URL.
        Use when the user provides a specific URL.
        """
        
        if research_handler:
            await research_handler.reading(url)

        try:
            return await jina.read(url)

        except JinaReadError:
            return await research(
                prompt = (
                    "Read and summarize the content from this URL. "
                    "If the page is unavailable, search for the same article or topic using the URL as the starting point: "
                    f"{url}"
                ),
                brave = brave,
                jina = jina,
                research_handler = research_handler
            )

    return [url_tool, research_tool]
    
