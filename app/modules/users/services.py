# app/modules/users/services.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_profile(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def update_profile(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return await self.repo.update(user, data)

    async def get_or_create_from_google(
        self,
        email: str,
        name: str,
        google_sub: str,
        avatar_url: str | None = None,
    ) -> User:
        # 1) ابحث بـ google_sub
        user = await self.repo.get_by_google_sub(google_sub)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            await self.repo.db.flush()
            return user

        # 2) ابحث بالبريد (حساب قديم بدون google_sub)
        user = await self.repo.get_by_email(email)
        if user:
            user.google_sub = google_sub
            user.last_login_at = datetime.now(timezone.utc)
            if avatar_url:
                user.avatar_url = avatar_url
            await self.repo.db.flush()
            return user

        # 3) أنشئ مستخدماً/طالباً جديداً
        # ✅ full_name بدلاً من name
        create_data = UserCreate(
            email=email,
            full_name=name,
            google_sub=google_sub,
            avatar_url=avatar_url,
        )
        return await self.repo.create(create_data)

    async def list_users(
        self, limit: int = 50, offset: int = 0
    ) -> tuple[list[User], int]:
        return await self.repo.list_users(limit, offset)

    async def list_by_organization(self, org_id: UUID) -> list[User]:
        return await self.repo.list_by_organization(org_id)

    async def deactivate(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.is_active = False
        await self.repo.db.flush()
        return user
