import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin


class Assessment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessments"

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    module_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    passing_score: Mapped[float] = mapped_column(
        Float, default=70.0, nullable=False
    )
    time_limit_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # ⚠️ لا يوجد أي relationship هنا


class AssessmentQuestion(UUIDMixin, Base):
    __tablename__ = "assessment_questions"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50), default="multiple_choice", nullable=False
    )
    choices: Mapped[list | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ⚠️ لا يوجد أي relationship هنا


class AssessmentResult(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessment_results"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    answers: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # ⚠️ لا يوجد أي relationship هنا
