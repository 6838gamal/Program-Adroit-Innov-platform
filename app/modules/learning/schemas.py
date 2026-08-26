from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import EnrollmentStatus
from app.shared.schemas import IDMixin, TimestampMixin


class LearningPathBase(BaseModel):
    title: str
    slug: str
    description: str | None = None
    difficulty: str = "beginner"
    estimated_hours: int | None = None
    cover_image_url: str | None = None


class LearningPathCreate(LearningPathBase):
    is_published: bool = False


class LearningPathUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    estimated_hours: int | None = None
    is_published: bool | None = None
    cover_image_url: str | None = None


class LearningPathRead(IDMixin, TimestampMixin, LearningPathBase):
    model_config = ConfigDict(from_attributes=True)
    is_published: bool
    organization_id: UUID | None = None
    created_by: UUID | None = None


class EnrollmentCreate(BaseModel):
    learning_path_id: UUID


class EnrollmentRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    learning_path_id: UUID
    status: EnrollmentStatus
    progress_percent: int
    enrolled_at: datetime
    completed_at: datetime | None = None


class ProgressRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    enrollment_id: UUID
    lesson_id: UUID
    is_completed: bool
    completed_at: datetime | None
    time_spent_seconds: int


class ProgressUpdate(BaseModel):
    is_completed: bool = False
    time_spent_seconds: int = 0
