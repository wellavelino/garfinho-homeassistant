"""Public facade tying the modules together."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from types import TracebackType

import aiohttp

from .auth import AuthClient
from .catalog import Catalog, Query
from .const import BUNDLE_TTL, BUNDLE_URL
from .content import RecipeContent, parse_bundle
from .datastore import Datastore
from .exceptions import NotAuthenticatedError
from .favorites import Favorites
from .http import Transport
from .models import Recipe, Session

CATALOG_TTL = 3600.0


class GarfinhoClient:
    """Async client. Pass an existing ``aiohttp.ClientSession`` (e.g. Home Assistant's)."""

    def __init__(
        self,
        session: Session | None = None,
        *,
        http_session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._transport = Transport(http_session)
        self._datastore = Datastore(self._transport)
        self.auth = AuthClient(self._transport)
        self.session = session
        self._catalog: Catalog | None = None
        self._catalog_at = 0.0
        self._content: dict[str, RecipeContent] | None = None
        self._content_at = 0.0
        self._content_lock = asyncio.Lock()

    async def __aenter__(self) -> GarfinhoClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self._transport.close()

    async def login(self, on_url: Callable[[str], None], *, timeout: float = 300.0) -> Session:
        """Run the browser login. ``on_url`` receives the URL the user must open."""
        code = await self.auth.request_code()
        on_url(self.auth.login_url(code))
        self.session = await self.auth.wait_for_login(code, timeout=timeout)
        return self.session

    async def catalog(self, *, refresh: bool = False) -> Catalog:
        stale = time.monotonic() - self._catalog_at > CATALOG_TTL
        if self._catalog is None or refresh or stale:
            self._catalog = Catalog(await self._datastore.fetch_recipes())
            self._catalog_at = time.monotonic()
        return self._catalog

    async def _load_content(self, *, force: bool = False) -> dict[str, RecipeContent]:
        async with self._content_lock:
            stale = time.monotonic() - self._content_at > BUNDLE_TTL
            if self._content is None or force or stale:
                archive = await self._transport.request_bytes(BUNDLE_URL)
                self._content = await asyncio.to_thread(parse_bundle, archive)
                self._content_at = time.monotonic()
            return self._content

    async def recipe_content(self, recipe_id: str) -> RecipeContent | None:
        """Ingredients with quantities and the steps, or None if the app has no text for it."""
        return (await self._load_content()).get(recipe_id)

    async def refresh(self) -> None:
        """Re-download the recipe index and the recipe texts."""
        await self.catalog(refresh=True)
        await self._load_content(force=True)

    async def search(self, query: Query = Query()) -> list[Recipe]:  # noqa: B008
        return (await self.catalog()).search(query)

    @property
    def favorites(self) -> Favorites:
        if self.session is None:
            raise NotAuthenticatedError("Log in first")
        return Favorites(self._datastore, self.session)
