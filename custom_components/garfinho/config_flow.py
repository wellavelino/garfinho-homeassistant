"""Config flow: sign in through the browser, then confirm here."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .garfinho_client import GarfinhoClient, GarfinhoError


class GarfinhoConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._client: GarfinhoClient | None = None
        self._code: str | None = None
        self._url = ""

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if self._client is None:
            self._client = GarfinhoClient(http_session=async_get_clientsession(self.hass))
        if self._code is None:
            try:
                self._code = await self._client.auth.request_code()
            except GarfinhoError:
                return self.async_abort(reason="cannot_connect")
            self._url = self._client.auth.login_url(self._code)

        if user_input is not None:
            try:
                session = await self._client.auth.poll(self._code)
            except GarfinhoError:
                errors["base"] = "cannot_connect"
            else:
                if session is None:
                    errors["base"] = "login_not_completed"
                else:
                    await self.async_set_unique_id(session.user_id)
                    self._abort_if_unique_id_configured()
                    title = session.display_name or session.email or "Garfinho"
                    return self.async_create_entry(title=title, data=session.to_dict())

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={"url": self._url},
            errors=errors,
        )
