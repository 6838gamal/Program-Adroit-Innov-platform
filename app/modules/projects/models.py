import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin
from app.shared.enums import ProjectStatus


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="intermediate", nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="python", nullable=False)
    estimated_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan")
    submissions = relationship("ProjectSubmission", back_populates="project", cascade="all, delete-orphan")


class ProjectTask(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project = relationship("Project", back_populates="tasks")


class ProjectMilestone(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_milestones"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project = relationship("Project", back_populates="milestones")


class ProjectSubmission(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.NOT_STARTED, nullable=False
    )
    repo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    files: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project = relationship("Project", back_populates="submissions")
    evaluations = relationship("ProjectEvaluation", back_populates="submission", cascade="all, delete-orphan")


class ProjectEvaluation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_evaluations"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evaluator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_ai_evaluation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    submission = relationship("ProjectSubmission", back_populates="evaluations")
