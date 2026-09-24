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
    - يحوّل postgres:// و postgresql:// إلى postgresql+asyncpg://
    - يضيف ssl=require إذا لم يكن موجوداً
    """
    # 1) توحيد الـ scheme
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # 2) إضافة ssl=require إذا لم يكن موجوداً
    if "+asyncpg://" in url and "ssl=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}ssl=require"

    return url


DATABASE_URL = _normalize_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_recycle=1800,
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
    async with async_session_factory() as session:
        yield session
