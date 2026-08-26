from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.courses.models import Module
from app.modules.courses.services import CourseService
from app.modules.lessons.models import Concept, Lesson
from app.modules.lessons.repositories import ConceptRepository, LessonRepository
from app.modules.lessons.schemas import ConceptCreate, ConceptUpdate, LessonCreate, LessonUpdate
from app.modules.users.models import User


class LessonService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lesson_repo = LessonRepository(db)
        self.concept_repo = ConceptRepository(db)
        self.course_service = CourseService(db)

    async def create_lesson(self, data: LessonCreate, user: User) -> Lesson:
        await self._check_module_access(data.module_id, user)
        return await self.lesson_repo.create(data)

    async def get_lesson(self, lesson_id: UUID) -> Lesson:
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundError("Lesson not found")
        return lesson

    async def update_lesson(self, lesson_id: UUID, data: LessonUpdate, user: User) -> Lesson:
        lesson = await self.get_lesson(lesson_id)
        await self._check_module_access(lesson.module_id, user)
        return await self.lesson_repo.update(lesson, data)

    async def delete_lesson(self, lesson_id: UUID, user: User) -> None:
        lesson = await self.get_lesson(lesson_id)
        await self._check_module_access(lesson.module_id, user)
        await self.lesson_repo.delete(lesson)

    async def list_lessons(self, module_id: UUID) -> list[Lesson]:
        return await self.lesson_repo.list_by_module(module_id)

    async def create_concept(self, data: ConceptCreate, user: User) -> Concept:
        lesson = await self.get_lesson(data.lesson_id)
        await self._check_module_access(lesson.module_id, user)
        return await self.concept_repo.create(data)

    async def update_concept(self, concept_id: UUID, data: ConceptUpdate, user: User) -> Concept:
        concept = await self.concept_repo.get_by_id(concept_id)
        if not concept:
            raise NotFoundError("Concept not found")
        lesson = await self.get_lesson(concept.lesson_id)
        await self._check_module_access(lesson.module_id, user)
        return await self.concept_repo.update(concept, data)

    async def delete_concept(self, concept_id: UUID, user: User) -> None:
        concept = await self.concept_repo.get_by_id(concept_id)
        if not concept:
            raise NotFoundError("Concept not found")
        lesson = await self.get_lesson(concept.lesson_id)
        await self._check_module_access(lesson.module_id, user)
        await self.concept_repo.delete(concept)

    async def list_concepts(self, lesson_id: UUID) -> list[Concept]:
        return await self.concept_repo.list_by_lesson(lesson_id)

    async def _check_module_access(self, module_id: UUID, user: User) -> None:
        result = await self.db.execute(
            select(Module).where(Module.id == module_id)
        )
        module = result.scalar_one_or_none()
        if not module:
            raise NotFoundError("Module not found")
        course = await self.course_service.get_course(module.course_id)
        await self.course_service._check_edit_access(course, user)
