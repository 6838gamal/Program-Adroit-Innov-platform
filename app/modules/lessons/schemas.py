from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.schemas import IDMixin, TimestampMixin


class LessonBase(BaseModel):
    title: str
    slug: str
    description: str | None = None
    content: str | None = None
    content_type: str = "text"
    video_url: str | None = None
    order: int = 0
    estimated_minutes: int = 10


class LessonCreate(LessonBase):
    module_id: UUID
    is_published: bool = True


class LessonUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    content: str | None = None
    content_type: str | None = None
    video_url: str | None = None
    order: int | None = None
    is_published: bool | None = None
    estimated_minutes: int | None = None


class LessonRead(IDMixin, TimestampMixin, LessonBase):
    model_config = ConfigDict(from_attributes=True)
    module_id: UUID
    is_published: bool


class ConceptBase(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None
    order: int = 0
    skill_id: UUID | None = None


class ConceptCreate(ConceptBase):
    lesson_id: UUID


class ConceptUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    content: str | None = None
    order: int | None = None
    skill_id: UUID | None = None


class ConceptRead(IDMixin, TimestampMixin, ConceptBase):
    model_config = ConfigDict(from_attributes=True)
    lesson_id: UUID
