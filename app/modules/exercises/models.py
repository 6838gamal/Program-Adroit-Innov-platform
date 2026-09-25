# app/modules/exercises/models.py
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin
from app.shared.enums import ExerciseType, SubmissionStatus


class Exercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "exercises"

    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exercise_type: Mapped[ExerciseType] = mapped_column(
        Enum(ExerciseType, name="exercise_type"),
        default=ExerciseType.CODE,
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50), default="easy", nullable=False
    )
    language: Mapped[str] = mapped_column(
        String(20), default="python", nullable=False
    )
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    choices: Mapped[list | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ⚠️ لا relationships


class ExerciseTest(UUIDMixin, Base):
    __tablename__ = "exercise_tests"

    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ⚠️ لا relationships


class Submission(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "submissions"

    # ✅ student_id بدلاً من user_id
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status"),
        default=SubmissionStatus.PENDING,
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # ⚠️ لا relationships


class SubmissionResult(UUIDMixin, Base):
    __tablename__ = "submission_results"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ⚠️ لا relationships
