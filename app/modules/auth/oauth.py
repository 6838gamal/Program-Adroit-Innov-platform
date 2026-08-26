import httpx

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger

logger = get_logger(__name__)

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


async def get_google_discovery_doc() -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(GOOGLE_DISCOVERY_URL, timeout=10)
        resp.raise_for_status()
        return resp.json()


async def get_google_auth_url(state: str) -> str:
    doc = await get_google_discovery_doc()
    auth_endpoint = doc.get("authorization_endpoint", "https://accounts.google.com/o/oauth2/v2/auth")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": settings.GOOGLE_SCOPE,
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{auth_endpoint}?{query}"


async def exchange_code_for_tokens(code: str) -> dict:
    doc = await get_google_discovery_doc()
    token_endpoint = doc.get("token_endpoint", "https://oauth2.googleapis.com/token")
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_endpoint, data=data, timeout=10)
    if resp.status_code != 200:
        logger.error("google_token_exchange_failed", status=resp.status_code, body=resp.text)
        raise UnauthorizedError("Failed to exchange authorization code")
    return resp.json()


async def get_google_userinfo(access_token: str, id_token: str | None = None) -> dict:
    doc = await get_google_discovery_doc()
    userinfo_endpoint = doc.get("userinfo_endpoint", "https://openidconnect.googleapis.com/v1/userinfo")
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(userinfo_endpoint, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise UnauthorizedError("Failed to fetch user info from Google")
    return resp.json()
