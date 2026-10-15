"""Polls the user's favorites."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MAX_TITLES_ATTRIBUTE, UPDATE_INTERVAL
from .garfinho_client import GarfinhoClient, GarfinhoError

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class FavoritesData:
    count: int
    titles: list[str]
    folders: dict[str, int]


class GarfinhoCoordinator(DataUpdateCoordinator[FavoritesData]):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: GarfinhoClient) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=UPDATE_INTERVAL
        )
        self.client = client

    async def _async_update_data(self) -> FavoritesData:
        try:
            data = await self.client.favorites.snapshot()
            catalog = await self.client.catalog()
        except GarfinhoError as err:
            raise UpdateFailed(str(err)) from err
        titles = []
        for recipe_id in data.bookmarks[:MAX_TITLES_ATTRIBUTE]:
            recipe = catalog.get(recipe_id)
            titles.append(recipe.title if recipe else recipe_id)
        return FavoritesData(
            count=len(data.bookmarks),
            titles=titles,
            folders={f.title: len(f.recipes) for f in data.folders},
        )
