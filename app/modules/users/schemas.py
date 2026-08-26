from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.shared.enums import UserRole
from app.shared.schemas import IDMixin, TimestampMixin


class UserBase(BaseModel):
    email: EmailStr
    name: str
    avatar_url: str | None = None
    role: UserRole = UserRole.STUDENT
    bio: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    avatar_url: str | None = None
    google_sub: str | None = None
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None


class UserRead(IDMixin, TimestampMixin, UserBase):
    model_config = ConfigDict(from_attributes=True)
    organization_id: UUID | None = None
    is_active: bool = True
    last_login_at: datetime | None = None


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    name: str
    avatar_url: str | None = None
    role: UserRole
    organization_id: UUID | None = None
    bio: str | None = None
    is_active: bool
    last_login_at: datetime | None = None
