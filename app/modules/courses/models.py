# app/modules/courses/models.py
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin


# ===== جدول ربط Many-to-Many (بدون ORM relationship) =====
learning_path_courses = Table(
    "learning_path_courses",
    Base.metadata,
    Column(
        "learning_path_id",
        UUID(as_uuid=True),
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "course_id",
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("order", Integer, default=0),
)


class Course(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(50), default="beginner", nullable=False
    )
    language: Mapped[str] = mapped_column(
        String(20), default="python", nullable=False
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    cover_image_url: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # ملاحظة: created_by يشير إلى users (احتياطي)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ⚠️ لا relationships — استعلامات صريحة فقط


class Module(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "modules"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # ⚠️ لا relationships


class CourseSkill(UUIDMixin, Base):
    __tablename__ = "course_skills"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ⚠️ لا relationships
