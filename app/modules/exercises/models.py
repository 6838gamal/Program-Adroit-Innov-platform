import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin
from app.shared.enums import ExerciseType, SubmissionStatus


class Exercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "exercises"

    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exercise_type: Mapped[ExerciseType] = mapped_column(
        Enum(ExerciseType, name="exercise_type"), default=ExerciseType.CODE, nullable=False
    )
    difficulty: Mapped[str] = mapped_column(String(50), default="easy", nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="python", nullable=False)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    choices: Mapped[list | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True
    )

    lesson = relationship("Lesson", back_populates="exercises")
    tests = relationship("ExerciseTest", back_populates="exercise", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="exercise", cascade="all, delete-orphan")


class ExerciseTest(UUIDMixin, Base):
    __tablename__ = "exercise_tests"

    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    exercise = relationship("Exercise", back_populates="tests")


class Submission(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status"),
        default=SubmissionStatus.PENDING, nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    exercise = relationship("Exercise", back_populates="submissions")
    results = relationship("SubmissionResult", back_populates="submission", cascade="all, delete-orphan")


class SubmissionResult(UUIDMixin, Base):
    __tablename__ = "submission_results"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    submission = relationship("Submission", back_populates="results")
