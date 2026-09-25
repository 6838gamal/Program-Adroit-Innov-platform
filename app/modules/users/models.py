# app/modules/students/models.py
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin
from app.shared.enums import UserRole


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "students"

    # ===== المصادقة =====
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    google_sub: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # ===== البيانات الشخصية =====
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ===== الدور =====
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="student_role"),
        default=UserRole.STUDENT,
        nullable=False,
    )

    # ===== الحالة =====
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ===== المنظمة (اختياري) =====
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ⚠️ لا علاقات ORM — استعلامات صريحة فقط
