import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.base_models import TimestampMixin, UUIDMixin


class Lesson(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "lessons"

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    video_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    module = relationship("Module", back_populates="lessons")
    concepts = relationship("Concept", back_populates="lesson", cascade="all, delete-orphan", order_by="Concept.order")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")


class Concept(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "concepts"

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True
    )

    lesson = relationship("Lesson", back_populates="concepts")
    skill = relationship("Skill")
