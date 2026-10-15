"""Access to the BuildFire datastore documents used by the app."""

from __future__ import annotations

from typing import Any

from .const import APP_ID, DATASTORE_URL, INSTANCE_ID, PLUGIN_ID
from .exceptions import ApiError
from .http import Transport
from .models import Recipe, Session, UserData

_BASE = f"{DATASTORE_URL}/user"
_SCOPE = f"{APP_ID}/{PLUGIN_ID}/{INSTANCE_ID}"
_USER_TAG = f"recipeInstanceCollection-{INSTANCE_ID}"


class Datastore:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def fetch_recipes(self) -> list[Recipe]:
        """Public document holding every recipe (no login needed)."""
        doc = await self._transport.request_json(
            "GET", f"{_BASE}/{_SCOPE}/recipeInstanceCollection/public/"
        )
        try:
            raw: list[dict[str, Any]] = doc["data"]["recipes"]
        except (TypeError, KeyError) as err:
            raise ApiError("Recipe index has an unexpected shape") from err
        return [Recipe.from_api(r) for r in raw]

    async def load_user_data(self, session: Session) -> UserData:
        doc = await self._transport.request_json(
            "GET", f"{_BASE}/{_SCOPE}/{_USER_TAG}/{session.user_id}/"
        )
        data = doc.get("data") if isinstance(doc, dict) else None
        return UserData.from_api(data or {})

    async def save_user_data(self, session: Session, data: UserData) -> None:
        reply = await self._transport.request_json(
            "POST",
            f"{_BASE}/save/{_SCOPE}/{_USER_TAG}/{session.user_id}/",
            json_body={"data": data.to_api(), "userToken": session.user_id},
        )
        if not isinstance(reply, dict) or reply.get("status") != "saved":
            raise ApiError(f"Save was not acknowledged: {reply!r}")
