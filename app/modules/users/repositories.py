from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_google_sub(self, google_sub: str) -> User | None:
        result = await self.db.execute(select(User).where(User.google_sub == google_sub))
        return result.scalar_one_or_none()

    async def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User, data: UserUpdate) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()

    async def list_users(self, limit: int = 50, offset: int = 0) -> tuple[list[User], int]:
        result = await self.db.execute(select(User).limit(limit).offset(offset))
        users = list(result.scalars().all())
        count_result = await self.db.execute(select(User))
        total = len(list(count_result.scalars().all()))
        return users, total

    async def list_by_organization(self, org_id: UUID, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.organization_id == org_id).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
