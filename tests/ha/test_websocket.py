from homeassistant.core import HomeAssistant

from .fakes import fake_client
from .test_integration import setup_entry


async def test_state_lists_favorites_and_tags(hass: HomeAssistant, hass_ws_client):
    await setup_entry(hass, fake_client())
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "garfinho/state"})
    result = (await ws.receive_json())["result"]
    assert [r["id"] for r in result["favorites"]] == ["r1"]
    assert result["total"] == 2
    assert {t["name"] for t in result["tags"]} == {"Fácil", "Jantar"}


async def test_search_marks_favorites(hass: HomeAssistant, hass_ws_client):
    await setup_entry(hass, fake_client())
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "garfinho/search", "text": "", "sort": "title"})
    result = (await ws.receive_json())["result"]
    assert [(r["id"], r["favorite"]) for r in result["recipes"]] == [("r1", True), ("r2", False)]
    assert result["has_more"] is False


async def test_set_favorite_calls_client(hass: HomeAssistant, hass_ws_client):
    client = fake_client()
    await setup_entry(hass, client)
    ws = await hass_ws_client(hass)
    await ws.send_json(
        {"id": 1, "type": "garfinho/set_favorite", "recipe_id": "r2", "favorite": True}
    )
    assert (await ws.receive_json())["success"]
    client.favorites.add.assert_awaited_once_with("r2")
    await ws.send_json(
        {"id": 2, "type": "garfinho/set_favorite", "recipe_id": "r1", "favorite": False}
    )
    assert (await ws.receive_json())["success"]
    client.favorites.remove.assert_awaited_once_with("r1")


async def test_recipe_returns_text_or_empty(hass: HomeAssistant, hass_ws_client):
    await setup_entry(hass, fake_client())
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "garfinho/recipe", "recipe_id": "r1"})
    assert (await ws.receive_json())["result"] == {
        "html": "<h4>Como preparar:</h4>",
        "video_id": "vid123",
    }
    await ws.send_json({"id": 2, "type": "garfinho/recipe", "recipe_id": "zzz"})
    assert (await ws.receive_json())["result"] == {"html": "", "video_id": None}
