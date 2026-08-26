from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.schemas import IDMixin, TimestampMixin


class AssessmentBase(BaseModel):
    title: str
    description: str | None = None
    course_id: UUID | None = None
    module_id: UUID | None = None
    passing_score: float = 70.0
    time_limit_minutes: int | None = None


class AssessmentCreate(AssessmentBase):
    is_published: bool = True


class AssessmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    passing_score: float | None = None
    is_published: bool | None = None
    time_limit_minutes: int | None = None


class AssessmentRead(IDMixin, TimestampMixin, AssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    is_published: bool


class QuestionCreate(BaseModel):
    assessment_id: UUID
    question_text: str
    question_type: str = "multiple_choice"
    choices: list | None = None
    correct_answer: str
    points: int = 1
    order: int = 0


class QuestionRead(IDMixin, QuestionCreate):
    model_config = ConfigDict(from_attributes=True)


class SubmitAssessmentRequest(BaseModel):
    assessment_id: UUID
    answers: dict


class AssessmentResultRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    assessment_id: UUID
    score: float
    max_score: float
    passed: bool
