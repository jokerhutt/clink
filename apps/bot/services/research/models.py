from __future__ import annotations

from dataclasses import dataclass
import httpx
from pydantic import BaseModel

from typing import TYPE_CHECKING, Awaitable, Callable

if TYPE_CHECKING:
    from apps.bot.services.research.brave import BraveSearch
    from apps.bot.services.research.jina import JinaReader

@dataclass
class ResearchDeps:
    brave: BraveSearch
    jina: JinaReader
    search_count: int = 0
    on_event: Callable[[str], Awaitable[None]] | None = None

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
