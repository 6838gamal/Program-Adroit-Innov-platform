from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assessments.models import Assessment, AssessmentQuestion, AssessmentResult


class AssessmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, assessment_id: UUID) -> Assessment | None:
        result = await self.db.execute(select(Assessment).where(Assessment.id == assessment_id))
        return result.scalar_one_or_none()

    async def create(self, data) -> Assessment:
        assessment = Assessment(**data.model_dump())
        self.db.add(assessment)
        await self.db.flush()
        return assessment

    async def update(self, assessment: Assessment, data) -> Assessment:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(assessment, field, value)
        await self.db.flush()
        return assessment

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Assessment]:
        result = await self.db.execute(select(Assessment).limit(limit).offset(offset))
        return list(result.scalars().all())


class QuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data) -> AssessmentQuestion:
        question = AssessmentQuestion(**data.model_dump())
        self.db.add(question)
        await self.db.flush()
        return question

    async def list_by_assessment(self, assessment_id: UUID) -> list[AssessmentQuestion]:
        result = await self.db.execute(
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment_id)
            .order_by(AssessmentQuestion.order)
        )
        return list(result.scalars().all())


class AssessmentResultRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, assessment_id: UUID, score: float, max_score: float, passed: bool, answers: dict) -> AssessmentResult:
        result = AssessmentResult(
            user_id=user_id,
            assessment_id=assessment_id,
            score=score,
            max_score=max_score,
            passed=passed,
            answers=answers,
        )
        self.db.add(result)
        await self.db.flush()
        return result

    async def list_by_user(self, user_id: UUID) -> list[AssessmentResult]:
        result = await self.db.execute(
            select(AssessmentResult).where(AssessmentResult.user_id == user_id)
        )
        return list(result.scalars().all())
