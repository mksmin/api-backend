import json
from typing import Any

import aiohttp
import jwt
from jwt import ExpiredSignatureError
from jwt import InvalidIssuerError
from jwt import PyJWKClient
from pydantic import HttpUrl

from app_exceptions import InvalidSignatureError
from auth.verifiers.base import AuthStrategy
from config import settings
from config.auth_bots import BotsEnum


class TelegramOIDCVerifier(AuthStrategy):
    def __init__(
        self,
        client_id: int | str,
        oid_server: HttpUrl | str,
    ) -> None:
        self._client_id = str(client_id)
        self._oid_server = str(oid_server)
        self._tg_jwks_uri = self._oid_server + "/.well-known/jwks.json"
        self._tg_oid_config_uri = self._oid_server + "/.well-known/openid-configuration"

    @classmethod
    def factory(
        cls,
        bot_name: BotsEnum,
        **kwargs: str,
    ) -> "TelegramOIDCVerifier":
        config = settings.bots[bot_name]
        if not config.client_id:
            error_msg = "client_id is required"
            raise ValueError(error_msg)

        oid_server = kwargs.get("oid_server")
        if not oid_server:
            error_msg = "oid_server is required"
            raise ValueError(error_msg)
        return cls(
            client_id=config.client_id,
            oid_server=oid_server,
        )

    async def verify(
        self,
        tg_access_key: str,
    ) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            response = await session.get(self._tg_jwks_uri)
            oid_specs = json.loads(await response.text())
            keys_algs = oid_specs.get("id_token_signing_alg_values_supported")

        jwk_client = PyJWKClient(self._tg_jwks_uri)
        signing_key = jwk_client.get_signing_key_from_jwt(tg_access_key)

        try:
            payload = jwt.decode(
                tg_access_key,
                key=signing_key,
                algorithms=keys_algs,
                audience=self._client_id,
                issuer=self._oid_server,
            )
        except ExpiredSignatureError:
            error_msg = "JWT token has expired"
            raise InvalidSignatureError(error_msg) from None
        except InvalidIssuerError:
            error_msg = "JWT token has invalid issuer"
            raise InvalidSignatureError(error_msg) from None
        else:
            return self.map_to_user(payload)

    @classmethod
    def map_to_user(
        cls,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        name = payload.get("name", "")
        first_name, *last_name_parts = name.split(" ")
        last_name = " ".join(last_name_parts) if last_name_parts else ""
        payload.update(
            first_name=first_name,
            last_name=last_name,
            tg_id=payload.get("id"),
            username=payload.get("preferred_username"),
        )
        return payload
