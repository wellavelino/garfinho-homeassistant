from unittest.mock import patch

from custom_components.garfinho.const import DOMAIN
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .fakes import SESSION, fake_client


async def setup_entry(hass: HomeAssistant, client):
    entry = MockConfigEntry(domain=DOMAIN, unique_id="user-1", data=SESSION.to_dict())
    entry.add_to_hass(hass)
    with patch("custom_components.garfinho.GarfinhoClient", return_value=client):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_sensor_reports_favorites(hass: HomeAssistant):
    await setup_entry(hass, fake_client())
    state = hass.states.get("sensor.garfinho_favorite_recipes")
    assert state is not None and state.state == "1"
    assert state.attributes["recipes"] == ["Bolo de cenoura"]


async def test_search_service_returns_filtered_recipes(hass: HomeAssistant):
    await setup_entry(hass, fake_client())
    result = await hass.services.async_call(
        DOMAIN,
        "search",
        {"text": "ovo", "tags": ["jantar"]},
        blocking=True,
        return_response=True,
    )
    assert [r["id"] for r in result["recipes"]] == ["r2"]


async def test_favorite_services_call_the_client(hass: HomeAssistant):
    client = fake_client()
    await setup_entry(hass, client)
    await hass.services.async_call(DOMAIN, "add_favorite", {"recipe_id": "r2"}, blocking=True)
    await hass.services.async_call(DOMAIN, "remove_favorite", {"recipe_id": "r1"}, blocking=True)
    client.favorites.add.assert_awaited_once_with("r2")
    client.favorites.remove.assert_awaited_once_with("r1")


async def test_unload_removes_services(hass: HomeAssistant):
    entry = await setup_entry(hass, fake_client())
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert not hass.services.has_service(DOMAIN, "search")


async def test_refresh_service_and_startup_warmup(hass: HomeAssistant):
    client = fake_client()
    await setup_entry(hass, client)
    assert client.refresh.await_count == 1  # warm-up on setup
    await hass.services.async_call(DOMAIN, "refresh", {}, blocking=True)
    assert client.refresh.await_count == 2


async def test_recipes_refresh_daily(hass: HomeAssistant):
    from datetime import timedelta

    from homeassistant.util import dt as dt_util
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    client = fake_client()
    await setup_entry(hass, client)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(hours=24, minutes=1))
    await hass.async_block_till_done()
    assert client.refresh.await_count == 2
