import httpx

_http_client: httpx.AsyncClient | None = None


def init_http_client() -> httpx.AsyncClient:
    global _http_client

    if _http_client is None:
        _http_client = httpx.AsyncClient()

    return _http_client


def get_http_client() -> httpx.AsyncClient:
    if _http_client is None:
        raise RuntimeError("Global httpx client has not been initialized")

    return _http_client


async def close_http_client() -> None:
    global _http_client

    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None
