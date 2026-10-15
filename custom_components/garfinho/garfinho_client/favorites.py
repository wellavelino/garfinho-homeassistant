"""Favorites (bookmarks) for the logged-in user."""

from __future__ import annotations

import asyncio

from .datastore import Datastore
from .models import Folder, Session, UserData


class Favorites:
    """Read-modify-write over the user document; unknown fields are preserved."""

    def __init__(self, datastore: Datastore, session: Session) -> None:
        self._ds = datastore
        self._session = session
        self._lock = asyncio.Lock()

    async def snapshot(self) -> UserData:
        """The whole user document in one request."""
        return await self._ds.load_user_data(self._session)

    async def ids(self) -> list[str]:
        return (await self._ds.load_user_data(self._session)).bookmarks

    async def folders(self) -> list[Folder]:
        return (await self._ds.load_user_data(self._session)).folders

    async def contains(self, recipe_id: str) -> bool:
        return recipe_id in await self.ids()

    async def add(self, recipe_id: str) -> bool:
        """Returns True if the recipe was newly favorited."""
        async with self._lock:
            data = await self._ds.load_user_data(self._session)
            if recipe_id in data.bookmarks:
                return False
            data.bookmarks.append(recipe_id)
            await self._ds.save_user_data(self._session, data)
            return True

    async def remove(self, recipe_id: str) -> bool:
        """Unfavorite, also dropping it from every folder (same as the app)."""
        async with self._lock:
            data = await self._ds.load_user_data(self._session)
            changed = _strip(data, recipe_id)
            if changed:
                await self._ds.save_user_data(self._session, data)
            return changed


def _strip(data: UserData, recipe_id: str) -> bool:
    changed = recipe_id in data.bookmarks
    data.bookmarks = [b for b in data.bookmarks if b != recipe_id]
    for folder in data.folders:
        if recipe_id in folder.recipes:
            folder.recipes = [r for r in folder.recipes if r != recipe_id]
            changed = True
    return changed
