"""Thin aiohttp wrapper: JSON, JSONP, error mapping."""

from __future__ import annotations

import json
import re
from typing import Any

import aiohttp

from .const import DEFAULT_TIMEOUT
from .exceptions import ApiError

_JSONP = re.compile(r"&&\s*[\w.$]+\((.*)\);?\s*$", re.DOTALL)


def parse_jsonp(text: str) -> Any:
    match = _JSONP.search(text)
    if not match:
        raise ApiError("Unexpected JSONP response")
    return json.loads(match.group(1))


class Transport:
    """Owns request mechanics so the rest of the library never touches aiohttp."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session
        self._owns_session = session is None

    async def _ensure(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            )
        return self._session

    async def close(self) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def request_json(self, method: str, url: str, *, json_body: Any = None) -> Any:
        session = await self._ensure()
        try:
            async with session.request(method, url, json=json_body) as resp:
                if resp.status >= 400:
                    raise ApiError(f"{method} {resp.url.path} -> {resp.status}", resp.status)
                text = await resp.text()
        except aiohttp.ClientError as err:
            raise ApiError(f"Network error: {err}") from err
        return json.loads(text) if text.strip() else None

    async def request_jsonp(self, url: str, params: dict[str, str]) -> Any:
        session = await self._ensure()
        try:
            async with session.get(url, params={**params, "callback": "cb"}) as resp:
                if resp.status >= 400:
                    raise ApiError(f"GET {resp.url.path} -> {resp.status}", resp.status)
                text = await resp.text()
        except aiohttp.ClientError as err:
            raise ApiError(f"Network error: {err}") from err
        return parse_jsonp(text)

    async def request_bytes(self, url: str) -> bytes:
        session = await self._ensure()
        try:
            async with session.get(url) as resp:
                if resp.status >= 400:
                    raise ApiError(f"GET {resp.url.path} -> {resp.status}", resp.status)
                return await resp.read()
        except aiohttp.ClientError as err:
            raise ApiError(f"Network error: {err}") from err
