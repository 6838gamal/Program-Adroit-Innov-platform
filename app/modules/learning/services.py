from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.learning.models import Enrollment, LearningPath, Progress
from app.modules.learning.repositories import (
    EnrollmentRepository,
    LearningPathRepository,
    ProgressRepository,
)
from app.modules.learning.schemas import LearningPathCreate, LearningPathUpdate, ProgressUpdate
from app.modules.users.models import User
from app.shared.enums import EnrollmentStatus, UserRole


class LearningPathService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.path_repo = LearningPathRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.progress_repo = ProgressRepository(db)

    async def create_path(self, data: LearningPathCreate, user: User) -> LearningPath:
        existing = await self.path_repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError("Learning path slug already exists")
        org_id = user.organization_id if user.role != UserRole.PLATFORM_ADMIN else None
        return await self.path_repo.create(data, user.id, org_id)

    async def get_path(self, path_id: UUID) -> LearningPath:
        path = await self.path_repo.get_by_id(path_id)
        if not path:
            raise NotFoundError("Learning path not found")
        return path

    async def update_path(self, path_id: UUID, data: LearningPathUpdate, user: User) -> LearningPath:
        path = await self.get_path(path_id)
        return await self.path_repo.update(path, data)

    async def list_paths(self, published_only: bool = True) -> list[LearningPath]:
        if published_only:
            return await self.path_repo.list_published()
        return await self.path_repo.list_all()

    async def enroll(self, user_id: UUID, path_id: UUID) -> Enrollment:
        await self.get_path(path_id)
        existing = await self.enrollment_repo.get_by_user_and_path(user_id, path_id)
        if existing:
            raise ConflictError("Already enrolled")
        return await self.enrollment_repo.create(user_id, path_id)

    async def get_enrollment(self, user_id: UUID, path_id: UUID) -> Enrollment:
        enrollment = await self.enrollment_repo.get_by_user_and_path(user_id, path_id)
        if not enrollment:
            raise NotFoundError("Enrollment not found")
        return enrollment

    async def list_user_enrollments(self, user_id: UUID) -> list[Enrollment]:
        return await self.enrollment_repo.list_by_user(user_id)

    async def update_progress(
        self, user_id: UUID, path_id: UUID, lesson_id: UUID, data: ProgressUpdate
    ) -> Progress:
        enrollment = await self.get_enrollment(user_id, path_id)
        progress = await self.progress_repo.upsert(
            enrollment.id, lesson_id, data.is_completed, data.time_spent_seconds
        )
        await self._recalculate_progress(enrollment)
        return progress

    async def get_progress(self, user_id: UUID, path_id: UUID) -> list[Progress]:
        enrollment = await self.get_enrollment(user_id, path_id)
        return await self.progress_repo.list_by_enrollment(enrollment.id)

    async def _recalculate_progress(self, enrollment: Enrollment) -> None:
        records = await self.progress_repo.list_by_enrollment(enrollment.id)
        if not records:
            enrollment.progress_percent = 0
            return
        completed = sum(1 for r in records if r.is_completed)
        enrollment.progress_percent = int((completed / len(records)) * 100)
        if enrollment.progress_percent == 100:
            enrollment.status = EnrollmentStatus.COMPLETED
            enrollment.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
