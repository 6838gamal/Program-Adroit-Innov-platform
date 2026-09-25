# app/core/database.py
from collections.abc import AsyncGenerator
import ssl

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _normalize_async_url(url: str) -> str:
    """
    يحوّل postgres:// و postgresql:// إلى postgresql+asyncpg://
    ⚠️ لا يضيف أي معاملات SSL في الرابط — asyncpg لا يقبلها
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # ✅ إزالة أي ssl= أو sslmode= موجودة في الرابط
    # لأننا سنمررها عبر connect_args
    if "?" in url:
        base, query = url.split("?", 1)
        params = [
            p for p in query.split("&")
            if not p.startswith(("ssl=", "sslmode="))
        ]
        url = base + ("?" + "&".join(params) if params else "")

    return url


def _make_ssl_context() -> ssl.SSLContext:
    """
    SSL context مطلوب للاتصال بقاعدة بيانات Render من خارج شبكتها.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


DATABASE_URL = _normalize_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_recycle=1800,
    connect_args={"ssl": _make_ssl_context()},  # ✅ الطريقة الصحيحة لـ asyncpg
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
