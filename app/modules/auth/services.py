# app/modules/auth/services.py
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
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

    # ------------------------------------------------------------------
    # OAuth Flow
    # ------------------------------------------------------------------

    async def get_login_redirect(self, state: str) -> str:
        """بناء رابط Google لتسجيل الدخول."""
        return await get_google_auth_url(state)

    async def handle_callback(self, code: str) -> User:
        """معالجة رد Google بعد تسجيل الدخول."""
        # 1) تبادل الكود بـ tokens
        tokens = await exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        if not access_token:
            raise UnauthorizedError("No access token in Google response")

        # 2) جلب معلومات المستخدم من Google
        userinfo = await get_google_userinfo(access_token)

        email = userinfo.get("email")
        google_sub = userinfo.get("sub")
        name = userinfo.get("name") or email
        avatar = userinfo.get("picture")

        # 3) التحقق من اكتمال البيانات
        if not email or not google_sub:
            raise UnauthorizedError("Incomplete Google user info")

        # 4) التأكد من أن البريد موثَّق لدى Google
        if not userinfo.get("email_verified", False):
            raise UnauthorizedError("Google email not verified")

        # 5) إنشاء/جلب المستخدم من قاعدة البيانات
        user = await self.user_service.get_or_create_from_google(
            email=email,
            name=name,
            google_sub=google_sub,
            avatar_url=avatar,
        )
        return user

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def create_session(self, request: Request, user: User) -> None:
        """حفظ بيانات المستخدم في الجلسة."""
        request.session["user_id"] = str(user.id)
        request.session["role"] = user.role.value
        request.session["email"] = user.email

    def destroy_session(self, request: Request) -> None:
        """حذف بيانات المستخدم من الجلسة (دون مسح الجلسة كاملة)."""
        for key in ("user_id", "role", "email"):
            request.session.pop(key, None)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def generate_state() -> str:
        """توليد state عشوائي لـ OAuth (حماية CSRF)."""
        return generate_token()
