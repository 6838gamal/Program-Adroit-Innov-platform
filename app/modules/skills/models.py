# app/modules/skills/models.py
import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin
from app.shared.enums import ProficiencyLevel


class Skill(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    parent_skill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ⚠️ لا relationships — استعلامات صريحة فقط


class StudentSkill(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "student_skills"

    # ✅ student_id بدلاً من user_id
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # ✅ students.id بدلاً من users.id
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    proficiency: Mapped[ProficiencyLevel] = mapped_column(
        Enum(ProficiencyLevel, name="proficiency_level"),
        default=ProficiencyLevel.NONE,
        nullable=False,
    )
    mastery_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    assessments_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_assessed_at: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # ⚠️ لا relationships


class SkillAssessment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "skill_assessments"

    # ✅ student_id بدلاً من user_id
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # ✅ students.id بدلاً من users.id
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(
        String(50), default="exercise", nullable=False
    )
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ⚠️ لا relationships


class SkillDependency(UUIDMixin, Base):
    __tablename__ = "skill_dependencies"

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prerequisite_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ⚠️ لا relationships
