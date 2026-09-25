# app/modules/users/schemas.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.shared.enums import UserRole
from app.shared.schemas import IDMixin, TimestampMixin


class UserBase(BaseModel):
    email: EmailStr
    full_name: str                          # ✅ full_name بدلاً من name
    avatar_url: str | None = None
    role: UserRole = UserRole.STUDENT
    bio: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str                          # ✅ full_name بدلاً من name
    avatar_url: str | None = None
    google_sub: str | None = None
    hashed_password: str | None = None      # ✅ أُضيف (اختياري، لـ OAuth)
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    full_name: str | None = None            # ✅ full_name بدلاً من name
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
    full_name: str                          # ✅ full_name بدلاً من name
    avatar_url: str | None = None
    role: UserRole
    organization_id: UUID | None = None
    bio: str | None = None
    is_active: bool
    last_login_at: datetime | None = None
