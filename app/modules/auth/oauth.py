from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger

logger = get_logger(__name__)

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# قيم ثابتة (Google نادراً ما يغيّرها) — تجنّب استدعاء discovery في كل طلب
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


async def get_google_auth_url(state: str) -> str:
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": settings.GOOGLE_SCOPE,
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",   # ← يعرض شاشة اختيار الحساب
    }
    query = urlencode(params)         # ← يُرمّز المسافات وغيرها
    url = f"{GOOGLE_AUTH_ENDPOINT}?{query}"
    logger.info("google_auth_url_generated", url=url)
    return url


async def exchange_code_for_tokens(code: str) -> dict:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data, timeout=10)
    except httpx.HTTPError as e:
        logger.error("google_token_exchange_network_error", error=str(e))
        raise UnauthorizedError("Failed to reach Google token endpoint")

    if resp.status_code != 200:
        logger.error(
            "google_token_exchange_failed",
            status=resp.status_code,
            body=resp.text,
        )
        raise UnauthorizedError("Failed to exchange authorization code")
    return resp.json()


async def get_google_userinfo(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                GOOGLE_USERINFO_ENDPOINT, headers=headers, timeout=10
            )
    except httpx.HTTPError as e:
        logger.error("google_userinfo_network_error", error=str(e))
        raise UnauthorizedError("Failed to reach Google userinfo endpoint")

    if resp.status_code != 200:
        raise UnauthorizedError("Failed to fetch user info from Google")
    return resp.json()
