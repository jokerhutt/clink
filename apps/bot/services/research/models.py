

from dataclasses import dataclass
import httpx
from pydantic import BaseModel

from apps.bot.services.research.brave import BraveSearch
from apps.bot.services.research.jina import JinaReader

@dataclass
class ResearchDeps:
    brave: BraveSearch
    jina: JinaReader
    search_count: int = 0

class PageContent(BaseModel):
    url: str
    title: str
    content: str
    description: str | None = None

class SearchResult(BaseModel):
    title: str
    url: str
    description: str
    content: str | None = None
