from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lessons.models import Concept, Lesson
from app.modules.lessons.schemas import ConceptCreate, LessonCreate, LessonUpdate, ConceptUpdate


class LessonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, lesson_id: UUID) -> Lesson | None:
        result = await self.db.execute(select(Lesson).where(Lesson.id == lesson_id))
        return result.scalar_one_or_none()

    async def create(self, data: LessonCreate) -> Lesson:
        lesson = Lesson(**data.model_dump())
        self.db.add(lesson)
        await self.db.flush()
        return lesson

    async def update(self, lesson: Lesson, data: LessonUpdate) -> Lesson:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lesson, field, value)
        await self.db.flush()
        return lesson

    async def delete(self, lesson: Lesson) -> None:
        await self.db.delete(lesson)
        await self.db.flush()

    async def list_by_module(self, module_id: UUID) -> list[Lesson]:
        result = await self.db.execute(
            select(Lesson).where(Lesson.module_id == module_id).order_by(Lesson.order)
        )
        return list(result.scalars().all())


class ConceptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, concept_id: UUID) -> Concept | None:
        result = await self.db.execute(select(Concept).where(Concept.id == concept_id))
        return result.scalar_one_or_none()

    async def create(self, data: ConceptCreate) -> Concept:
        concept = Concept(**data.model_dump())
        self.db.add(concept)
        await self.db.flush()
        return concept

    async def update(self, concept: Concept, data: ConceptUpdate) -> Concept:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(concept, field, value)
        await self.db.flush()
        return concept

    async def delete(self, concept: Concept) -> None:
        await self.db.delete(concept)
        await self.db.flush()

    async def list_by_lesson(self, lesson_id: UUID) -> list[Concept]:
        result = await self.db.execute(
            select(Concept).where(Concept.lesson_id == lesson_id).order_by(Concept.order)
        )
        return list(result.scalars().all())
