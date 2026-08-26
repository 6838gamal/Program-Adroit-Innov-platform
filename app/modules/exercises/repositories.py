from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exercises.models import Exercise, ExerciseTest, Submission, SubmissionResult


class ExerciseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, exercise_id: UUID) -> Exercise | None:
        result = await self.db.execute(select(Exercise).where(Exercise.id == exercise_id))
        return result.scalar_one_or_none()

    async def create(self, data) -> Exercise:
        exercise = Exercise(**data.model_dump())
        self.db.add(exercise)
        await self.db.flush()
        return exercise

    async def update(self, exercise: Exercise, data) -> Exercise:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(exercise, field, value)
        await self.db.flush()
        return exercise

    async def delete(self, exercise: Exercise) -> None:
        await self.db.delete(exercise)
        await self.db.flush()

    async def list_by_lesson(self, lesson_id: UUID) -> list[Exercise]:
        result = await self.db.execute(
            select(Exercise).where(Exercise.lesson_id == lesson_id).order_by(Exercise.order)
        )
        return list(result.scalars().all())

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Exercise]:
        result = await self.db.execute(select(Exercise).limit(limit).offset(offset))
        return list(result.scalars().all())


class ExerciseTestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, exercise_id: UUID, data) -> ExerciseTest:
        test = ExerciseTest(exercise_id=exercise_id, **data.model_dump())
        self.db.add(test)
        await self.db.flush()
        return test

    async def list_by_exercise(self, exercise_id: UUID) -> list[ExerciseTest]:
        result = await self.db.execute(
            select(ExerciseTest).where(ExerciseTest.exercise_id == exercise_id).order_by(ExerciseTest.order)
        )
        return list(result.scalars().all())


class SubmissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, exercise_id: UUID, code: str | None, answer: str | None) -> Submission:
        sub = Submission(user_id=user_id, exercise_id=exercise_id, code=code, answer=answer)
        self.db.add(sub)
        await self.db.flush()
        return sub

    async def get_by_id(self, submission_id: UUID) -> Submission | None:
        result = await self.db.execute(select(Submission).where(Submission.id == submission_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[Submission]:
        result = await self.db.execute(
            select(Submission).where(Submission.user_id == user_id)
        )
        return list(result.scalars().all())

    async def list_by_exercise(self, exercise_id: UUID) -> list[Submission]:
        result = await self.db.execute(
            select(Submission).where(Submission.exercise_id == exercise_id)
        )
        return list(result.scalars().all())

    async def add_result(self, submission_id: UUID, data) -> SubmissionResult:
        result = SubmissionResult(submission_id=submission_id, **data.model_dump())
        self.db.add(result)
        await self.db.flush()
        return result

    async def list_results(self, submission_id: UUID) -> list[SubmissionResult]:
        result = await self.db.execute(
            select(SubmissionResult).where(SubmissionResult.submission_id == submission_id)
        )
        return list(result.scalars().all())
