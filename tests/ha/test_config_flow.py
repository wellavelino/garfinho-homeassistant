from unittest.mock import patch

from custom_components.garfinho.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .fakes import SESSION, fake_client


async def test_login_flow_waits_then_creates_entry(hass: HomeAssistant):
    client = fake_client()
    with patch("custom_components.garfinho.config_flow.GarfinhoClient", return_value=client):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        assert result["type"] is FlowResultType.FORM
        assert result["description_placeholders"]["url"].endswith("code-1")

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        assert result["errors"] == {"base": "login_not_completed"}

        client.auth.poll.return_value = SESSION
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Ana"
    assert result["data"]["user_id"] == "user-1"


async def test_same_account_is_not_added_twice(hass: HomeAssistant):
    client = fake_client()
    client.auth.poll.return_value = SESSION
    with patch("custom_components.garfinho.config_flow.GarfinhoClient", return_value=client):
        for expected in (FlowResultType.CREATE_ENTRY, FlowResultType.ABORT):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
            assert result["type"] is expected
