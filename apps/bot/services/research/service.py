from pydantic_ai import Agent, RunContext

from apps.bot.services.research.brave import BraveSearch
from apps.bot.services.research.jina import JinaReader
from apps.llm_config import get_pydantic_ai_model_name

from .models import ResearchDeps, SearchResult

RESEARCH_MODEL = get_pydantic_ai_model_name()

_research_agent = Agent(
    RESEARCH_MODEL,
    deps_type=ResearchDeps,
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
) -> str:
    deps = ResearchDeps(
        brave=brave,
        jina=jina,
    )

    result = await _research_agent.run(
        prompt,
        deps=deps,
    )

    return result.output
