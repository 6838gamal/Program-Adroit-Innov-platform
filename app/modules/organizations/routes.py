from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.exceptions import ForbiddenError
from app.modules.organizations.schemas import (
    MembershipCreate,
    MembershipRead,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from app.modules.organizations.services import OrganizationService
from app.shared.enums import UserRole
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationRead)
async def create_organization(data: OrganizationCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = OrganizationService(db)
    return await service.create_organization(data, user)


@router.get("/", response_model=list[OrganizationRead])
async def list_organizations(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user.role not in (UserRole.PLATFORM_ADMIN, UserRole.ORG_ADMIN):
        raise ForbiddenError()
    service = OrganizationService(db)
    return await service.list_organizations()


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(org_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = OrganizationService(db)
    return await service.get_organization(org_id)


@router.put("/{org_id}", response_model=OrganizationRead)
async def update_organization(
    org_id: UUID, data: OrganizationUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    return await service.update_organization(org_id, data, user)


@router.get("/{org_id}/members", response_model=list[MembershipRead])
async def list_members(org_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = OrganizationService(db)
    return await service.list_members(org_id)


@router.post("/{org_id}/members", response_model=MembershipRead)
async def add_member(
    org_id: UUID, data: MembershipCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    await service.add_member(org_id, data.user_id, data.role, user)
    return await service.list_members(org_id)


@router.delete("/{org_id}/members/{user_id}", response_model=MessageResponse)
async def remove_member(
    org_id: UUID, user_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    await service.remove_member(org_id, user_id, user)
    return MessageResponse(message="Member removed")
