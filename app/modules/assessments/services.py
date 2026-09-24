from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.assessments.models import Assessment ,AssessmentResult
from app.modules.assessments.repositories import (
    AssessmentRepository,
    AssessmentResultRepository,
    QuestionRepository,
)
from app.modules.assessments.schemas import (
    AssessmentCreate,
    AssessmentUpdate,
    QuestionCreate,
    SubmitAssessmentRequest,
)


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.assessment_repo = AssessmentRepository(db)
        self.question_repo = QuestionRepository(db)
        self.result_repo = AssessmentResultRepository(db)

    async def create_assessment(self, data: AssessmentCreate) -> Assessment:
        return await self.assessment_repo.create(data)

    async def get_assessment(self, assessment_id: UUID) -> Assessment:
        assessment = await self.assessment_repo.get_by_id(assessment_id)
        if not assessment:
            raise NotFoundError("Assessment not found")
        return assessment

    async def update_assessment(self, assessment_id: UUID, data: AssessmentUpdate):
        assessment = await self.get_assessment(assessment_id)
        return await self.assessment_repo.update(assessment, data)

    async def list_assessments(self) -> list:
        return await self.assessment_repo.list_all()

    async def add_question(self, data: QuestionCreate):
        await self.get_assessment(data.assessment_id)
        return await self.question_repo.create(data)

    async def list_questions(self, assessment_id: UUID) -> list:
        return await self.question_repo.list_by_assessment(assessment_id)

    async def submit_assessment(self, user_id: UUID, data: SubmitAssessmentRequest) -> AssessmentResult:
        assessment = await self.get_assessment(data.assessment_id)
        questions = await self.question_repo.list_by_assessment(assessment.id)
        total_points = sum(q.points for q in questions)
        earned_points = 0
        for q in questions:
            user_answer = data.answers.get(str(q.id), "")
            if user_answer == q.correct_answer:
                earned_points += q.points
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score >= assessment.passing_score
        return await self.result_repo.create(
            user_id, assessment.id, score, 100.0, passed, data.answers
        )

    async def list_user_results(self, user_id: UUID) -> list[AssessmentResult]:
        return await self.result_repo.list_by_user(user_id)
