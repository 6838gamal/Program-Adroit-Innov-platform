from datetime import datetime, timezone
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_token
from app.modules.auth.oauth import (
    exchange_code_for_tokens,
    get_google_auth_url,
    get_google_userinfo,
)
from app.modules.users.models import User
from app.modules.users.services import UserService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def get_login_redirect(self, state: str) -> str:
        return await get_google_auth_url(state)

    async def handle_callback(self, code: str) -> User:
        tokens = await exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        if not access_token:
            from app.core.exceptions import UnauthorizedError

            raise UnauthorizedError("No access token in Google response")

        userinfo = await get_google_userinfo(access_token, tokens.get("id_token"))
        email = userinfo.get("email")
        name = userinfo.get("name", email)
        google_sub = userinfo.get("sub")
        avatar = userinfo.get("picture")

        if not email or not google_sub:
            from app.core.exceptions import UnauthorizedError

            raise UnauthorizedError("Incomplete Google user info")

        user = await self.user_service.get_or_create_from_google(
            email=email, name=name, google_sub=google_sub, avatar_url=avatar
        )
        return user

    def create_session(self, request: Request, user: User) -> None:
        request.session["user_id"] = str(user.id)
        request.session["role"] = user.role.value
        request.session["email"] = user.email

    def destroy_session(self, request: Request) -> None:
        request.session.clear()

    @staticmethod
    def generate_state() -> str:
        return generate_token()
