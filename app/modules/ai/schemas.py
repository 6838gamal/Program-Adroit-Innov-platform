from uuid import UUID

from pydantic import BaseModel


class TutorRequest(BaseModel):
    question: str
    course_id: UUID | None = None
    lesson_id: UUID | None = None
    exercise_id: UUID | None = None
    current_code: str | None = None


class TutorResponse(BaseModel):
    response: str
    context_used: dict | None = None


class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    exercise_context: str | None = None


class CodeReviewResponse(BaseModel):
    analysis: dict
    summary: str


class DebugRequest(BaseModel):
    code: str
    error: str | None = None
    expected_output: str | None = None
    actual_output: str | None = None
    language: str = "python"


class DebugResponse(BaseModel):
    analysis: str
    explanation: str
    steps: list[str]
    hint: str
    solution: str | None = None


class RecommendationResponse(BaseModel):
    recommendations: list[dict]


class ProjectMentorRequest(BaseModel):
    project_id: UUID
    submission_id: UUID | None = None
    question: str
    code: str | None = None


class ProjectMentorResponse(BaseModel):
    response: str
