"""Websocket API used by the Garfinho sidebar panel."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .coordinator import GarfinhoCoordinator
from .garfinho_client import GarfinhoError, Query, Recipe, Sort

TOP_TAGS = 40


def serialize(recipe: Recipe, favorites: set[str]) -> dict[str, Any]:
    return {
        "id": recipe.id,
        "title": recipe.title,
        "image": recipe.image_url,
        "tags": [t.name for t in recipe.tags],
        "ingredients": [i.name for i in recipe.ingredients],
        "favorite": recipe.id in favorites,
    }


def _coordinator(hass: HomeAssistant) -> GarfinhoCoordinator | None:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return entries[0].runtime_data if entries else None


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_state)
    websocket_api.async_register_command(hass, ws_search)
    websocket_api.async_register_command(hass, ws_set_favorite)
    websocket_api.async_register_command(hass, ws_recipe)


def _not_setup(connection: websocket_api.ActiveConnection, msg_id: int) -> None:
    connection.send_error(msg_id, "not_setup", "Garfinho is not set up")


@websocket_api.websocket_command({vol.Required("type"): "garfinho/state"})
@websocket_api.async_response
async def ws_state(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    coordinator = _coordinator(hass)
    if coordinator is None:
        _not_setup(connection, msg["id"])
        return
    try:
        data = await coordinator.client.favorites.snapshot()
        catalog = await coordinator.client.catalog()
    except GarfinhoError as err:
        connection.send_error(msg["id"], "garfinho_error", str(err))
        return
    favorites = set(data.bookmarks)
    by_id = {rid: catalog.get(rid) for rid in data.bookmarks}
    connection.send_result(
        msg["id"],
        {
            "total": len(catalog),
            "favorites": [serialize(r, favorites) for r in by_id.values() if r],
            "folders": [{"title": f.title, "recipes": f.recipes} for f in data.folders],
            "tags": [{"name": t.name, "count": c} for t, c in catalog.tags()[:TOP_TAGS]],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "garfinho/search",
        vol.Optional("text", default=""): str,
        vol.Optional("tags", default=[]): [str],
        vol.Optional("sort", default=Sort.RELEVANCE.value): vol.In([s.value for s in Sort]),
        vol.Optional("limit", default=24): vol.All(int, vol.Range(min=1, max=100)),
        vol.Optional("offset", default=0): vol.All(int, vol.Range(min=0)),
    }
)
@websocket_api.async_response
async def ws_search(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    coordinator = _coordinator(hass)
    if coordinator is None:
        _not_setup(connection, msg["id"])
        return
    try:
        favorites = set(await coordinator.client.favorites.ids())
        recipes = await coordinator.client.search(
            Query(
                text=msg["text"],
                tags=msg["tags"],
                sort=Sort(msg["sort"]),
                limit=msg["limit"] + 1,
                offset=msg["offset"],
            )
        )
    except GarfinhoError as err:
        connection.send_error(msg["id"], "garfinho_error", str(err))
        return
    connection.send_result(
        msg["id"],
        {
            "recipes": [serialize(r, favorites) for r in recipes[: msg["limit"]]],
            "has_more": len(recipes) > msg["limit"],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "garfinho/set_favorite",
        vol.Required("recipe_id"): str,
        vol.Required("favorite"): bool,
    }
)
@websocket_api.async_response
async def ws_set_favorite(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    coordinator = _coordinator(hass)
    if coordinator is None:
        _not_setup(connection, msg["id"])
        return
    favorites = coordinator.client.favorites
    try:
        if msg["favorite"]:
            await favorites.add(msg["recipe_id"])
        else:
            await favorites.remove(msg["recipe_id"])
    except GarfinhoError as err:
        connection.send_error(msg["id"], "garfinho_error", str(err))
        return
    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"favorite": msg["favorite"]})


@websocket_api.websocket_command(
    {vol.Required("type"): "garfinho/recipe", vol.Required("recipe_id"): str}
)
@websocket_api.async_response
async def ws_recipe(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    coordinator = _coordinator(hass)
    if coordinator is None:
        _not_setup(connection, msg["id"])
        return
    try:
        content = await coordinator.client.recipe_content(msg["recipe_id"])
    except GarfinhoError as err:
        connection.send_error(msg["id"], "garfinho_error", str(err))
        return
    connection.send_result(
        msg["id"],
        {"html": content.html, "video_id": content.video_id}
        if content
        else {"html": "", "video_id": None},
    )
