import asyncio
import time
import httpx
from dataclasses import dataclass


BASE_URL = "https://api.scryfall.com"

REQUIRED_HEADERS = {"Accept": "application/json", "User-Agent": "mtg-navi-jp"}

# Scryfall's API guidelines ask clients to wait 50-100ms between requests.
MIN_REQUEST_INTERVAL = 0.1

_rate_limit_lock = asyncio.Lock()
_last_request_time = 0.0


class ScryfallError(Exception):
    """Raised when a Scryfall API request fails."""


class CardNotFoundError(ScryfallError):
    """Raised when no card matches the search query."""


@dataclass
class FuzzySearchResult:
    name: str
    colors: list[str]
    color_identity: list[str]


async def _throttled_get(
    client: httpx.AsyncClient, path: str, params: dict
) -> httpx.Response:
    global _last_request_time

    async with _rate_limit_lock:
        wait = _last_request_time + MIN_REQUEST_INTERVAL - time.monotonic()
        if wait > 0:
            await asyncio.sleep(wait)
        response = await client.get(
            f"{BASE_URL}{path}", params=params, headers=REQUIRED_HEADERS
        )
        _last_request_time = time.monotonic()

    if response.status_code == 429:
        retry_after = float(response.headers.get("Retry-After", 1))
        await asyncio.sleep(retry_after)
        return await _throttled_get(client, path, params)

    return response


async def fuzzy_search(query: str) -> FuzzySearchResult:
    async with httpx.AsyncClient() as client:
        response = await _throttled_get(client, "/cards/named", {"fuzzy": query})

    if response.status_code == 404:
        raise CardNotFoundError(f"No card found matching '{query}'")
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ScryfallError(f"Scryfall request failed: {exc}") from exc

    pruned_response = {
        k: v
        for k, v in response.json().items()
        if k in FuzzySearchResult.__annotations__
    }
    return FuzzySearchResult(**pruned_response)
