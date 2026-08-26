from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organizations.models import Membership, Organization
from app.modules.organizations.schemas import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        result = await self.db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self.db.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, data: OrganizationCreate, owner_id: UUID) -> Organization:
        org = Organization(**data.model_dump(), owner_id=owner_id)
        self.db.add(org)
        await self.db.flush()
        return org

    async def update(self, org: Organization, data: OrganizationUpdate) -> Organization:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(org, field, value)
        await self.db.flush()
        return org

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Organization]:
        result = await self.db.execute(select(Organization).limit(limit).offset(offset))
        return list(result.scalars().all())


class MembershipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_org(self, user_id: UUID, org_id: UUID) -> Membership | None:
        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == org_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, org_id: UUID) -> list[Membership]:
        result = await self.db.execute(
            select(Membership).where(Membership.organization_id == org_id)
        )
        return list(result.scalars().all())

    async def list_by_user(self, user_id: UUID) -> list[Membership]:
        result = await self.db.execute(
            select(Membership).where(Membership.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, user_id: UUID, org_id: UUID, role, invited_by: UUID | None = None) -> Membership:
        membership = Membership(
            user_id=user_id,
            organization_id=org_id,
            role=role,
            invited_by=invited_by,
        )
        self.db.add(membership)
        await self.db.flush()
        return membership

    async def delete(self, membership: Membership) -> None:
        await self.db.delete(membership)
        await self.db.flush()
