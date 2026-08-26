from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_session_token
from app.modules.users.models import User
from app.shared.enums import UserRole
from app.shared.permissions import has_permission

DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(request: Request, db: DBSession) -> User:
    token = request.session.get("user_id")
    if not token:
        raise UnauthorizedError()

    try:
        user_id = UUID(token)
    except (ValueError, TypeError):
        raise UnauthorizedError()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(permission: str):
    async def checker(user: CurrentUser) -> User:
        if not has_permission(user.role, permission):
            raise ForbiddenError(f"Missing permission: {permission}")
        return user

    return checker


def require_role(*roles: UserRole):
    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise ForbiddenError("Insufficient role")
        return user

    return checker


async def get_current_user_optional(request: Request, db: DBSession) -> User | None:
    token = request.session.get("user_id")
    if not token:
        return None
    try:
        user_id = UUID(token)
    except (ValueError, TypeError):
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]


def get_tenant_filter(user: User) -> dict:
    """Return tenant scoping filters for the current user."""
    if user.role == UserRole.PLATFORM_ADMIN:
        return {}  # no filter
    if user.organization_id:
        return {"organization_id": user.organization_id}
    return {"user_id": user.id}
