"""Unofficial Garfinho recipe integration."""

from __future__ import annotations

import contextlib
import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    RECIPE_REFRESH_INTERVAL,
    SERVICE_ADD_FAVORITE,
    SERVICE_REFRESH,
    SERVICE_REMOVE_FAVORITE,
    SERVICE_SEARCH,
)
from .coordinator import GarfinhoCoordinator
from .garfinho_client import GarfinhoClient, GarfinhoError, Query, Session, Sort
from .websocket import async_register as async_register_websocket

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]
PANEL_URL = "garfinho"
STATIC_URL = "/garfinho_static"

type GarfinhoConfigEntry = ConfigEntry[GarfinhoCoordinator]

SEARCH_SCHEMA = vol.Schema(
    {
        vol.Optional("text", default=""): cv.string,
        vol.Optional("tags", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("exclude_tags", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("ingredients", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("exclude_ingredients", default=[]): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("sort", default=Sort.RELEVANCE.value): vol.In([s.value for s in Sort]),
        vol.Optional("limit", default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
    }
)
RECIPE_SCHEMA = vol.Schema({vol.Required("recipe_id"): cv.string})


async def async_setup_entry(hass: HomeAssistant, entry: GarfinhoConfigEntry) -> bool:
    client = GarfinhoClient(
        Session.from_dict(entry.data), http_session=async_get_clientsession(hass)
    )
    coordinator = GarfinhoCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass)
    await _register_panel(hass)

    async def refresh_recipes(_now: object = None) -> None:
        try:
            await client.refresh()
        except GarfinhoError as err:
            _LOGGER.warning("Could not refresh Garfinho recipes: %s", err)

    # Warm the caches in the background, then refresh the recipes once a day.
    entry.async_create_background_task(hass, refresh_recipes(), "garfinho_warmup")
    entry.async_on_unload(async_track_time_interval(hass, refresh_recipes, RECIPE_REFRESH_INTERVAL))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GarfinhoConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and not hass.config_entries.async_loaded_entries(DOMAIN):
        for service in (
            SERVICE_SEARCH,
            SERVICE_ADD_FAVORITE,
            SERVICE_REMOVE_FAVORITE,
            SERVICE_REFRESH,
        ):
            hass.services.async_remove(DOMAIN, service)
        frontend.async_remove_panel(hass, PANEL_URL)
        hass.data.pop(f"{DOMAIN}_panel", None)
    return unloaded


async def _register_panel(hass: HomeAssistant) -> None:
    if hass.data.get(f"{DOMAIN}_panel"):
        return
    hass.data[f"{DOMAIN}_panel"] = True
    async_register_websocket(hass)
    with contextlib.suppress(RuntimeError):  # already registered before a reload
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "www"), False)]
        )
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="garfinho-panel",
        frontend_url_path=PANEL_URL,
        module_url=f"{STATIC_URL}/garfinho-panel.js",
        sidebar_title="Garfinho",
        sidebar_icon="mdi:chef-hat",
        require_admin=False,
    )


def _coordinator(hass: HomeAssistant) -> GarfinhoCoordinator:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError("Garfinho is not set up")
    coordinator: GarfinhoCoordinator = entries[0].runtime_data
    return coordinator


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SEARCH):
        return

    async def search(call: ServiceCall) -> dict[str, object]:
        client = _coordinator(hass).client
        query = Query(
            text=call.data["text"],
            tags=call.data["tags"],
            exclude_tags=call.data["exclude_tags"],
            ingredients=call.data["ingredients"],
            exclude_ingredients=call.data["exclude_ingredients"],
            sort=Sort(call.data["sort"]),
            limit=call.data["limit"],
        )
        try:
            recipes = await client.search(query)
        except GarfinhoError as err:
            raise HomeAssistantError(str(err)) from err
        return {
            "recipes": [
                {
                    "id": r.id,
                    "title": r.title,
                    "image": r.image_url,
                    "tags": [t.name for t in r.tags],
                    "ingredients": [i.name for i in r.ingredients],
                }
                for r in recipes
            ]
        }

    async def _favorite(call: ServiceCall, *, add: bool) -> None:
        coordinator = _coordinator(hass)
        favorites = coordinator.client.favorites
        try:
            if add:
                await favorites.add(call.data["recipe_id"])
            else:
                await favorites.remove(call.data["recipe_id"])
        except GarfinhoError as err:
            raise HomeAssistantError(str(err)) from err
        await coordinator.async_request_refresh()

    async def add_favorite(call: ServiceCall) -> None:
        await _favorite(call, add=True)

    async def remove_favorite(call: ServiceCall) -> None:
        await _favorite(call, add=False)

    async def refresh(call: ServiceCall) -> None:
        try:
            await _coordinator(hass).client.refresh()
        except GarfinhoError as err:
            raise HomeAssistantError(str(err)) from err

    hass.services.async_register(DOMAIN, SERVICE_REFRESH, refresh)
    hass.services.async_register(
        DOMAIN, SERVICE_SEARCH, search, SEARCH_SCHEMA, supports_response=SupportsResponse.ONLY
    )
    hass.services.async_register(DOMAIN, SERVICE_ADD_FAVORITE, add_favorite, RECIPE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_FAVORITE, remove_favorite, RECIPE_SCHEMA)
