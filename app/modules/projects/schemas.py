from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import ProjectStatus
from app.shared.schemas import IDMixin, TimestampMixin


class ProjectBase(BaseModel):
    title: str
    slug: str
    description: str | None = None
    difficulty: str = "intermediate"
    language: str = "python"
    estimated_hours: int | None = None
    is_published: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    is_published: bool | None = None
    estimated_hours: int | None = None


class ProjectRead(IDMixin, TimestampMixin, ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    organization_id: UUID | None = None
    created_by: UUID | None = None


class ProjectTaskCreate(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    order: int = 0
    is_required: bool = True


class ProjectTaskRead(IDMixin, TimestampMixin, ProjectTaskCreate):
    model_config = ConfigDict(from_attributes=True)


class ProjectMilestoneCreate(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    target_date: str | None = None
    order: int = 0


class ProjectMilestoneRead(IDMixin, TimestampMixin, ProjectMilestoneCreate):
    model_config = ConfigDict(from_attributes=True)


class ProjectSubmissionCreate(BaseModel):
    project_id: UUID
    repo_url: str | None = None
    notes: str | None = None


class ProjectSubmissionRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    project_id: UUID
    status: ProjectStatus
    repo_url: str | None = None
    notes: str | None = None


class ProjectEvaluationRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    submission_id: UUID
    evaluator_id: UUID | None = None
    is_ai_evaluation: bool
    score: float
    feedback: str | None = None
