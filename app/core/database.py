# app/core/database.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _normalize_async_url(url: str) -> str:
    """
    تأكد من أن DATABASE_URL يستخدم asyncpg driver.
    يدعم:
      - postgresql://  → postgresql+asyncpg://
      - postgres://    → postgresql+asyncpg://
      - postgresql+asyncpg:// (كما هو)
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


DATABASE_URL = _normalize_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=5,          # ⚠️ Render free tier يسمح بعدد اتصالات محدود
    max_overflow=5,       #    خفّضها من 20/10 لتجنّب "too many connections"
    pool_recycle=1800,    # إعادة تدوير الاتصالات كل 30 دقيقة
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_no_commit() -> AsyncGenerator[AsyncSession, None]:
    """For read-only operations; commit handled by caller if needed."""
    async with async_session_factory() as session:
        yield session
