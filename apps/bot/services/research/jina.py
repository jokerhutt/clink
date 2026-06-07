

import httpx

class JinaReader:
    def __init__(self, client: httpx.AsyncClient, api_key: str | None = None) :
        self.client = client
        self.api_key = api_key

    async def read(self, url: str) -> str:

        print("READ_URL:", url)

        try :
            headers = {}

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            resp = await self.client.get(
                f"https://r.jina.ai/http://{url.removeprefix('https://').removeprefix('http://')}",
                headers=headers,
                timeout=30.0
            )

            resp.raise_for_status()

            print(resp.text[:1000])

            return resp.text

        except Exception as e:
            print("JINA ERROR:", repr(e))
            raise

        
