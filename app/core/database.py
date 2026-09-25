# app/core/database.py
from collections.abc import AsyncGenerator
import ssl
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ⚠️ المعاملات التي لا يقبلها asyncpg ويجب حذفها من الرابط
_UNSUPPORTED_QUERY_PARAMS = {"sslmode", "ssl", "channel_binding"}


def _normalize_async_url(url: str) -> str:
    """
    - يحوّل postgres:// و postgresql:// إلى postgresql+asyncpg://
    - يحذف أي معاملات SSL لا يقبلها asyncpg (sslmode, ssl, channel_binding)
    """
    # 1) توحيد الـ scheme
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # 2) حذف معاملات SSL غير المدعومة من query string
    parsed = urlparse(url)
    if parsed.query:
        params = parse_qs(parsed.query, keep_blank_values=True)
        for key in list(params.keys()):
            if key.lower() in _UNSUPPORTED_QUERY_PARAMS:
                del params[key]
        # إعادة بناء الـ query
        new_query = urlencode(
            {k: v[0] for k, v in params.items()},
            doseq=False,
        )
        parsed = parsed._replace(query=new_query)
        url = urlunparse(parsed)

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
