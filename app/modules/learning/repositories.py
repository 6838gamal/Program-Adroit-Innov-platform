from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.learning.models import Enrollment, LearningPath, Progress
from app.modules.learning.schemas import LearningPathCreate, LearningPathUpdate


class LearningPathRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, path_id: UUID) -> LearningPath | None:
        result = await self.db.execute(select(LearningPath).where(LearningPath.id == path_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> LearningPath | None:
        result = await self.db.execute(select(LearningPath).where(LearningPath.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, data: LearningPathCreate, user_id: UUID, org_id: UUID | None) -> LearningPath:
        path = LearningPath(**data.model_dump(), created_by=user_id, organization_id=org_id)
        self.db.add(path)
        await self.db.flush()
        return path

    async def update(self, path: LearningPath, data: LearningPathUpdate) -> LearningPath:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(path, field, value)
        await self.db.flush()
        return path

    async def list_published(self, limit: int = 50, offset: int = 0) -> list[LearningPath]:
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.is_published.is_(True)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[LearningPath]:
        result = await self.db.execute(select(LearningPath).limit(limit).offset(offset))
        return list(result.scalars().all())


class EnrollmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, enrollment_id: UUID) -> Enrollment | None:
        result = await self.db.execute(select(Enrollment).where(Enrollment.id == enrollment_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_path(self, user_id: UUID, path_id: UUID) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.learning_path_id == path_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID, path_id: UUID) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, learning_path_id=path_id)
        self.db.add(enrollment)
        await self.db.flush()
        return enrollment

    async def list_by_user(self, user_id: UUID) -> list[Enrollment]:
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.user_id == user_id)
        )
        return list(result.scalars().all())


class ProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_enrollment_and_lesson(self, enrollment_id: UUID, lesson_id: UUID) -> Progress | None:
        result = await self.db.execute(
            select(Progress).where(
                Progress.enrollment_id == enrollment_id,
                Progress.lesson_id == lesson_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, enrollment_id: UUID, lesson_id: UUID, is_completed: bool, time_spent: int) -> Progress:
        progress = await self.get_by_enrollment_and_lesson(enrollment_id, lesson_id)
        if progress:
            progress.is_completed = is_completed
            progress.time_spent_seconds += time_spent
            if is_completed and not progress.completed_at:
                from datetime import datetime, timezone
                progress.completed_at = datetime.now(timezone.utc)
        else:
            from datetime import datetime, timezone
            progress = Progress(
                enrollment_id=enrollment_id,
                lesson_id=lesson_id,
                is_completed=is_completed,
                time_spent_seconds=time_spent,
                completed_at=datetime.now(timezone.utc) if is_completed else None,
            )
            self.db.add(progress)
        await self.db.flush()
        return progress

    async def list_by_enrollment(self, enrollment_id: UUID) -> list[Progress]:
        result = await self.db.execute(
            select(Progress).where(Progress.enrollment_id == enrollment_id)
        )
        return list(result.scalars().all())
