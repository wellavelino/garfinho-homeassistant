"""Browser-based login (device-code style).

Flow: request a one-time code, send the user to a URL where they sign in with
their provider, then poll until the backend hands back the session.
"""

from __future__ import annotations

import asyncio
import json
import time
from urllib.parse import urlencode

from .const import APP_ID, AUTH_URL, LOGIN_PROVIDER
from .exceptions import AuthError, LoginTimeoutError
from .http import Transport
from .models import Session

_SERVER = f"{AUTH_URL}/src/server.js"


class AuthClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def _rpc(self, method: str, params: dict[str, object]) -> object:
        payload = {"id": 1, "method": method, "params": params}
        reply = await self._transport.request_jsonp(_SERVER, {"data": json.dumps(payload)})
        if not isinstance(reply, dict):
            raise AuthError("Malformed auth reply")
        if reply.get("error"):
            raise AuthError(str(reply["error"]))
        return reply.get("result")

    async def request_code(self) -> str:
        result = await self._rpc("secretCode/request", {"externalAppId": APP_ID})
        if not isinstance(result, dict) or "code" not in result:
            raise AuthError("No login code returned")
        return str(result["code"])

    @staticmethod
    def login_url(code: str, provider: str = LOGIN_PROVIDER) -> str:
        query = urlencode(
            {
                "v": "2.0",
                "code": code,
                "loginProviderType": provider,
                "externalAppId": APP_ID,
                "isExternalWindow": "true",
                "appName": "Garfinho",
            }
        )
        return f"{AUTH_URL}/website/index.html?{query}"

    async def poll(self, code: str) -> Session | None:
        """Return the session once the user finished signing in, else ``None``."""
        result = await self._rpc(
            "users/secretCodeLogin",
            {"code": code, "deviceId": None, "osType": "android", "externalAppId": APP_ID},
        )
        if isinstance(result, dict) and result.get("userId"):
            return Session.from_api(result)
        return None

    async def wait_for_login(
        self, code: str, *, timeout: float = 300.0, interval: float = 2.0
    ) -> Session:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            session = await self.poll(code)
            if session is not None:
                return session
            await asyncio.sleep(interval)
        raise LoginTimeoutError("Login was not completed in time")
