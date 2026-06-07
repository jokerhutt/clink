from typing import Awaitable, Callable
from pydantic_ai import Agent, AgentRunResultEvent, RunContext

from apps.bot.services.research.brave import BraveSearch
from apps.bot.services.research.jina import JinaReader

from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)

from apps.llm_config import get_pydantic_ai_model_name

from .models import ResearchDeps, SearchResult

RESEARCH_MODEL = get_pydantic_ai_model_name()

_research_agent = Agent(
    RESEARCH_MODEL,
    deps_type=ResearchDeps,
    system_prompt="""
    You are a web research agent.
    For current information:

    1. Search first.
    2. Read at least one relevant result.
    3. Read multiple sources when possible.
    4. Never answer based only on search snippets.
    5. If search results exist, call read() before producing a final answer.
    """
)

@_research_agent.tool
async def search(
    ctx: RunContext[ResearchDeps],
    query: str,
) -> list[SearchResult]:
    ctx.deps.search_count += 1
    return await ctx.deps.brave.search(query)

@_research_agent.tool
async def read(
    ctx: RunContext[ResearchDeps],
    url: str,
) -> str:
    return await ctx.deps.jina.read(url)

async def research(
    prompt: str,
    brave: BraveSearch,
    jina: JinaReader,
    on_research_event: Callable[[str, str | None], Awaitable[None]] | None = None,
) -> str:
    deps = ResearchDeps(
        brave=brave,
        jina=jina,
        on_event = on_research_event
    )

    final_output: str | None = None

    async with _research_agent.run_stream_events(
        prompt,
        deps=deps,
    ) as stream:
        async for event in stream:
            if isinstance(event, FunctionToolCallEvent):
                if deps.on_event is None:
                    continue
                tool_name = event.part.tool_name
                if tool_name == "search":
                    query = prompt
                    await deps.on_event("search_started", query)
                elif tool_name == "read":
                    await deps.on_event("read_finished", None)

            elif isinstance(event, FunctionToolResultEvent):
                if deps.on_event is None:
                    continue
                tool_name = event.part.tool_name
                if tool_name == "search":
                    await deps.on_event("Search complete.")
                elif tool_name == "read":
                    await deps.on_event("Source read.")
            elif isinstance(event, AgentRunResultEvent):
                final_output = event.result.output

    if final_output is None:
        raise RuntimeError("Agent produced no result")

    return final_output
