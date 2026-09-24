# app/modules/auth/oauth.py
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------
# Google OAuth endpoints (ثابتة — نتجنّب استدعاء discovery في كل طلب)
# ------------------------------------------------------------------
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

HTTP_TIMEOUT = 10.0


# ------------------------------------------------------------------
# (اختياري) جلب discovery doc — للاستخدام المستقبلي أو التحقق
# ------------------------------------------------------------------
async def get_google_discovery_doc() -> dict:
    """جلب OpenID configuration من Google (اختياري)."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(GOOGLE_DISCOVERY_URL, timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("google_discovery_failed", error=str(e))
        raise UnauthorizedError("Failed to reach Google discovery endpoint")
    return resp.json()


# ------------------------------------------------------------------
# 1) بناء رابط تسجيل الدخول
# ------------------------------------------------------------------
async def get_google_auth_url(state: str) -> str:
    """
    بناء رابط Google OAuth لتسجيل الدخول.

    - urlencode يرمّز المسافات في scope بشكل صحيح
    - prompt=select_account يعرض شاشة اختيار الحساب
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": settings.GOOGLE_SCOPE,
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    query = urlencode(params)
    url = f"{GOOGLE_AUTH_ENDPOINT}?{query}"

    logger.info("google_auth_url_generated", url=url)
    return url


# ------------------------------------------------------------------
# 2) تبادل code بـ tokens
# ------------------------------------------------------------------
async def exchange_code_for_tokens(code: str) -> dict:
    """تبادل authorization code بـ access_token و id_token."""
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_TOKEN_ENDPOINT,
                data=data,
                timeout=HTTP_TIMEOUT,
            )
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


# ------------------------------------------------------------------
# 3) جلب معلومات المستخدم
# ------------------------------------------------------------------
async def get_google_userinfo(access_token: str) -> dict:
    """جلب بيانات المستخدم من Google userinfo endpoint."""
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                GOOGLE_USERINFO_ENDPOINT,
                headers=headers,
                timeout=HTTP_TIMEOUT,
            )
    except httpx.HTTPError as e:
        logger.error("google_userinfo_network_error", error=str(e))
        raise UnauthorizedError("Failed to reach Google userinfo endpoint")

    if resp.status_code != 200:
        logger.error(
            "google_userinfo_failed",
            status=resp.status_code,
            body=resp.text,
        )
        raise UnauthorizedError("Failed to fetch user info from Google")

    return resp.json()
