from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import ProficiencyLevel
from app.shared.schemas import IDMixin, TimestampMixin


class SkillBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    category: str | None = None


class SkillCreate(SkillBase):
    parent_skill_id: UUID | None = None


class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None


class SkillRead(IDMixin, TimestampMixin, SkillBase):
    model_config = ConfigDict(from_attributes=True)
    parent_skill_id: UUID | None = None


class StudentSkillRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    skill_id: UUID
    proficiency: ProficiencyLevel
    mastery_score: float
    assessments_count: int


class SkillAssessmentCreate(BaseModel):
    skill_id: UUID
    score: float
    source: str = "exercise"
    exercise_id: UUID | None = None
    notes: str | None = None


class SkillAssessmentRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    skill_id: UUID
    score: float
    source: str
    exercise_id: UUID | None = None
    notes: str | None = None


class SkillDependencyCreate(BaseModel):
    skill_id: UUID
    prerequisite_skill_id: UUID


class SkillProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    strong_skills: list[StudentSkillRead] = []
    weak_skills: list[StudentSkillRead] = []
    recommended_next: list[SkillRead] = []
