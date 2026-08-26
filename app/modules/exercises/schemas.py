from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.enums import ExerciseType, SubmissionStatus
from app.shared.schemas import IDMixin, TimestampMixin


class ExerciseBase(BaseModel):
    title: str
    description: str | None = None
    exercise_type: ExerciseType = ExerciseType.CODE
    difficulty: str = "easy"
    language: str = "python"
    starter_code: str | None = None
    solution_code: str | None = None
    expected_output: str | None = None
    choices: list | None = None
    correct_answer: str | None = None
    points: int = 10
    is_published: bool = True
    order: int = 0
    skill_id: UUID | None = None


class ExerciseCreate(ExerciseBase):
    lesson_id: UUID | None = None


class ExerciseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    exercise_type: ExerciseType | None = None
    difficulty: str | None = None
    starter_code: str | None = None
    solution_code: str | None = None
    expected_output: str | None = None
    choices: list | None = None
    correct_answer: str | None = None
    points: int | None = None
    is_published: bool | None = None
    order: int | None = None
    skill_id: UUID | None = None


class ExerciseRead(IDMixin, TimestampMixin, ExerciseBase):
    model_config = ConfigDict(from_attributes=True)
    lesson_id: UUID | None = None


class ExerciseTestCreate(BaseModel):
    test_name: str
    input_data: str | None = None
    expected_output: str
    is_hidden: bool = False
    order: int = 0


class ExerciseTestRead(IDMixin, ExerciseTestCreate):
    model_config = ConfigDict(from_attributes=True)
    exercise_id: UUID


class SubmissionCreate(BaseModel):
    exercise_id: UUID
    code: str | None = None
    answer: str | None = None


class SubmissionRead(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    exercise_id: UUID
    code: str | None = None
    answer: str | None = None
    status: SubmissionStatus
    score: int
    feedback: str | None = None
    attempts: int


class SubmissionResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    test_name: str
    passed: bool
    output: str | None = None
    expected: str | None = None
    error: str | None = None
    execution_time_ms: int | None = None
