from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.base_models import UUIDMixin
from app.shared.enums import MembershipRole
from app.shared.schemas import IDMixin, TimestampMixin


class OrganizationBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None


class OrganizationRead(IDMixin, TimestampMixin, OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    owner_id: UUID | None = None
    is_active: bool = True


class MembershipRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    organization_id: UUID
    role: MembershipRole
    joined_at: datetime


class MembershipCreate(BaseModel):
    user_id: UUID
    organization_id: UUID
    role: MembershipRole = MembershipRole.STUDENT
