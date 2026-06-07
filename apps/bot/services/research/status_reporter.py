
from typing import Protocol
import hikari
import lightbulb

class ResearchEventHandler(Protocol):
    async def search_started(self, query: str) -> None:
        ...

    async def reading(self, url: str) -> None:
        ...

class ResearchStatusReporter:

    def __init__(self, bot: lightbulb.BotApp, channel_id: hikari.Snowflake):
        self.bot = bot
        self.channel_id = channel_id

        self.status_messsage: hikari.Message | None = None
        self.query: str | None = None
        self.read_count: int = 0

    async def search_started(self, query: str) -> None:
        self.query = query
        await self._update()

    async def reading(self, url: str) -> None:
        self.read_count += 1
        await self._update()

    async def _update(self) -> None:
        content = self._build_content()

        if self.status_messsage is None:
            self.status_messsage = await self.bot.rest.create_message(
                channel = self.channel_id,
                content = content,
                flags = hikari.MessageFlag.SUPPRESS_EMBEDS
            )
        else :
            await self.bot.rest.edit_message(
                self.channel_id,
                self.status_messsage.id,
                content,
                flags = hikari.MessageFlag.SUPPRESS_EMBEDS
            )

    def _build_content(self) -> str:
        lines: list[str] = []

        if self.query:
            lines.append(f"> -# Searching the web: {self.query}")
        if self.read_count:
            lines.append(f"> -# Reading {self.read_count} source(s)") 
        
        return "\n".join(lines)



