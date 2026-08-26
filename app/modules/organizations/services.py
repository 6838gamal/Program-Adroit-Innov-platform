from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.organizations.models import Organization
from app.modules.organizations.repositories import MembershipRepository, OrganizationRepository
from app.modules.organizations.schemas import OrganizationCreate, OrganizationUpdate
from app.modules.users.models import User
from app.modules.users.services import UserService
from app.shared.enums import MembershipRole, UserRole
from app.shared.permissions import role_to_membership


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.member_repo = MembershipRepository(db)
        self.user_service = UserService(db)

    async def create_organization(self, data: OrganizationCreate, owner: User) -> Organization:
        existing = await self.org_repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError("Organization slug already exists")
        org = await self.org_repo.create(data, owner.id)
        membership = await self.member_repo.create(
            user_id=owner.id,
            org_id=org.id,
            role=MembershipRole.ADMIN,
            invited_by=owner.id,
        )
        owner.organization_id = org.id
        if owner.role == UserRole.STUDENT:
            owner.role = UserRole.ORG_ADMIN
        await self.db.flush()
        return org

    async def get_organization(self, org_id: UUID) -> Organization:
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise NotFoundError("Organization not found")
        return org

    async def update_organization(self, org_id: UUID, data: OrganizationUpdate, user: User) -> Organization:
        org = await self.get_organization(org_id)
        await self._check_admin_access(org, user)
        return await self.org_repo.update(org, data)

    async def list_organizations(self) -> list[Organization]:
        return await self.org_repo.list_all()

    async def add_member(self, org_id: UUID, user_id: UUID, role: MembershipRole, actor: User) -> None:
        org = await self.get_organization(org_id)
        await self._check_admin_access(org, actor)
        existing = await self.member_repo.get_by_user_and_org(user_id, org_id)
        if existing:
            raise ConflictError("User is already a member")
        await self.member_repo.create(user_id, org_id, role, invited_by=actor.id)
        target_user = await self.user_service.get_profile(user_id)
        if not target_user.organization_id:
            target_user.organization_id = org_id
        await self.db.flush()

    async def remove_member(self, org_id: UUID, user_id: UUID, actor: User) -> None:
        org = await self.get_organization(org_id)
        await self._check_admin_access(org, actor)
        membership = await self.member_repo.get_by_user_and_org(user_id, org_id)
        if not membership:
            raise NotFoundError("Membership not found")
        await self.member_repo.delete(membership)
        target_user = await self.user_service.get_profile(user_id)
        if target_user.organization_id == org_id:
            target_user.organization_id = None
        await self.db.flush()

    async def list_members(self, org_id: UUID) -> list:
        return await self.member_repo.list_by_organization(org_id)

    async def list_my_organizations(self, user_id: UUID) -> list:
        return await self.member_repo.list_by_user(user_id)

    async def _check_admin_access(self, org: Organization, user: User) -> None:
        if user.role == UserRole.PLATFORM_ADMIN:
            return
        membership = await self.member_repo.get_by_user_and_org(user.id, org.id)
        if not membership or membership.role != MembershipRole.ADMIN:
            raise ForbiddenError("Only organization admins can perform this action")
