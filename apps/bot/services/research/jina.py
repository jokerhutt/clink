

import httpx

class JinaReader:
    def __init__(self, client: httpx.AsyncClient, api_key: str | None = None) :
        self.client = client
        self.api_key = api_key

    async def read(self, url: str) -> str:

        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = await self.client.get(
            f"https://r.jina.ai/http://{url.removeprefix('https://').removeprefix('http://')}"
        )

        resp.raise_for_status()

        return resp.text

        
