from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_tenant_filter
from app.core.exceptions import ForbiddenError
from app.modules.users.schemas import UserRead, UserProfile, UserUpdate
from app.modules.users.services import UserService
from app.shared.enums import UserRole
from app.shared.schemas import MessageResponse, PaginatedResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_my_profile(user: CurrentUser):
    return user


@router.put("/me", response_model=UserRead)
async def update_my_profile(user: CurrentUser, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.update_profile(user.id, data)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user_id != user.id and user.role not in (UserRole.PLATFORM_ADMIN, UserRole.ORG_ADMIN):
        raise ForbiddenError()
    service = UserService(db)
    return await service.get_profile(user_id)


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    if user.role not in (UserRole.PLATFORM_ADMIN, UserRole.ORG_ADMIN):
        raise ForbiddenError()
    service = UserService(db)
    if user.role == UserRole.ORG_ADMIN and user.organization_id:
        users = await service.list_by_organization(user.organization_id)
        return PaginatedResponse(items=[UserRead.model_validate(u) for u in users], total=len(users), page=page, page_size=page_size)
    users, total = await service.list_users(page_size, (page - 1) * page_size)
    return PaginatedResponse(items=[UserRead.model_validate(u) for u in users], total=total, page=page, page_size=page_size)


@router.delete("/{user_id}", response_model=MessageResponse)
async def deactivate_user(user_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user.role != UserRole.PLATFORM_ADMIN and user_id != user.id:
        raise ForbiddenError()
    service = UserService(db)
    await service.deactivate(user_id)
    return MessageResponse(message="User deactivated")
