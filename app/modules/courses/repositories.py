from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.courses.models import Course, Module
from app.modules.courses.schemas import CourseCreate, CourseUpdate, ModuleCreate, ModuleUpdate


class CourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, course_id: UUID) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, data: CourseCreate, user_id: UUID, org_id: UUID | None) -> Course:
        course = Course(**data.model_dump(), created_by=user_id, organization_id=org_id)
        self.db.add(course)
        await self.db.flush()
        return course

    async def update(self, course: Course, data: CourseUpdate) -> Course:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(course, field, value)
        await self.db.flush()
        return course

    async def list_published(self, limit: int = 50, offset: int = 0) -> list[Course]:
        result = await self.db.execute(
            select(Course).where(Course.is_published.is_(True)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Course]:
        result = await self.db.execute(select(Course).limit(limit).offset(offset))
        return list(result.scalars().all())


class ModuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, module_id: UUID) -> Module | None:
        result = await self.db.execute(select(Module).where(Module.id == module_id))
        return result.scalar_one_or_none()

    async def create(self, data: ModuleCreate) -> Module:
        module = Module(**data.model_dump())
        self.db.add(module)
        await self.db.flush()
        return module

    async def update(self, module: Module, data: ModuleUpdate) -> Module:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(module, field, value)
        await self.db.flush()
        return module

    async def delete(self, module: Module) -> None:
        await self.db.delete(module)
        await self.db.flush()

    async def list_by_course(self, course_id: UUID) -> list[Module]:
        result = await self.db.execute(
            select(Module).where(Module.course_id == course_id).order_by(Module.order)
        )
        return list(result.scalars().all())
