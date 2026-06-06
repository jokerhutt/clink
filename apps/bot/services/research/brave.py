


from dataclasses import dataclass

import httpx
from apps.bot.services.research.models import SearchResult

class BraveSearch:
    def __init__(self, client: httpx.AsyncClient, api_key: str):
        self.client = client
        self.api_key = api_key

    async def search(self, query: str) -> list[SearchResult]:
        resp = await self.client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query},
                headers={
                    "X-Subscription-Token": self.api_key,
                },
        )

        resp.raise_for_status()

        data = resp.json()
        items = data["web"]["results"]

        results = []

        for item in items:
            results.append(
                SearchResult(
                    title = item["title"],
                    url = item["url"],
                    description = item["description"]
                )
            )

        return results



