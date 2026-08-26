from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.schemas import IDMixin, TimestampMixin


class CourseBase(BaseModel):
    title: str
    slug: str
    description: str | None = None
    difficulty: str = "beginner"
    language: str = "python"
    cover_image_url: str | None = None


class CourseCreate(CourseBase):
    is_published: bool = False


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    language: str | None = None
    is_published: bool | None = None
    cover_image_url: str | None = None


class CourseRead(IDMixin, TimestampMixin, CourseBase):
    model_config = ConfigDict(from_attributes=True)
    is_published: bool
    organization_id: UUID | None = None
    created_by: UUID | None = None


class ModuleBase(BaseModel):
    title: str
    description: str | None = None
    order: int = 0


class ModuleCreate(ModuleBase):
    course_id: UUID


class ModuleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: int | None = None


class ModuleRead(IDMixin, TimestampMixin, ModuleBase):
    model_config = ConfigDict(from_attributes=True)
    course_id: UUID
    is_published: bool
