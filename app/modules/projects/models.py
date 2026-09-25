# app/modules/projects/models.py
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin
from app.shared.enums import ProjectStatus


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(50), default="intermediate", nullable=False
    )
    language: Mapped[str] = mapped_column(
        String(20), default="python", nullable=False
    )
    estimated_hours: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # ✅ created_by → students.id
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ⚠️ لا relationships


class ProjectTask(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # ⚠️ لا relationships


class ProjectMilestone(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_milestones"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ⚠️ لا relationships


class ProjectSubmission(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_submissions"

    # ✅ student_id بدلاً من user_id
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.NOT_STARTED,
        nullable=False,
    )
    repo_url: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    files: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ⚠️ لا relationships


class ProjectEvaluation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_evaluations"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # ✅ evaluator_id → students.id
    evaluator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_ai_evaluation: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ⚠️ لا relationships
