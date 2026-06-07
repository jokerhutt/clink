
import httpx

class JinaReadError(RuntimeError):
    pass

class JinaReader:
    def __init__(self, client: httpx.AsyncClient, api_key: str | None = None) :
        self.client = client
        self.api_key = api_key

    def _build_reader_url(self, url: str) -> str:
        normalized_url = url.strip()

        if not normalized_url.startswith(("http://", "https://")):
            normalized_url = f"https://{normalized_url}"

        return f"https://r.jina.ai/{normalized_url}"

    def _is_failed_read(self, content: str) -> bool:
        failure_markers = (
            "Warning: Target URL returned error 404",
            "Title: We can't find that page",
            "\"name\":\"SecurityCompromiseError\"",
            "\"code\":451",
        )

        return any(marker in content for marker in failure_markers)

    async def read(self, url: str) -> str:

        print("READ_URL:", url)

        try :
            headers = {}

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            resp = await self.client.get(
                self._build_reader_url(url),
                headers=headers,
                timeout=30.0
            )

            resp.raise_for_status()

            if self._is_failed_read(resp.text):
                raise JinaReadError(f"Could not read URL: {url}")

            return resp.text

        except Exception as e:
            print("JINA ERROR:", repr(e))
            raise

        
