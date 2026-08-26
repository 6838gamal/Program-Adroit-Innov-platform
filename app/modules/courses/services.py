from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.courses.models import Course, Module
from app.modules.courses.repositories import CourseRepository, ModuleRepository
from app.modules.courses.schemas import CourseCreate, CourseUpdate, ModuleCreate, ModuleUpdate
from app.modules.users.models import User
from app.shared.enums import UserRole


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.module_repo = ModuleRepository(db)

    async def create_course(self, data: CourseCreate, user: User) -> Course:
        existing = await self.course_repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError("Course slug already exists")
        org_id = user.organization_id if user.role != UserRole.PLATFORM_ADMIN else None
        return await self.course_repo.create(data, user.id, org_id)

    async def get_course(self, course_id: UUID) -> Course:
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        return course

    async def update_course(self, course_id: UUID, data: CourseUpdate, user: User) -> Course:
        course = await self.get_course(course_id)
        await self._check_edit_access(course, user)
        return await self.course_repo.update(course, data)

    async def list_courses(self, published_only: bool = True) -> list[Course]:
        if published_only:
            return await self.course_repo.list_published()
        return await self.course_repo.list_all()

    async def create_module(self, data: ModuleCreate, user: User) -> Module:
        course = await self.get_course(data.course_id)
        await self._check_edit_access(course, user)
        return await self.module_repo.create(data)

    async def update_module(self, module_id: UUID, data: ModuleUpdate, user: User) -> Module:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            raise NotFoundError("Module not found")
        course = await self.get_course(module.course_id)
        await self._check_edit_access(course, user)
        return await self.module_repo.update(module, data)

    async def delete_module(self, module_id: UUID, user: User) -> None:
        module = await self.module_repo.get_by_id(module_id)
        if not module:
            raise NotFoundError("Module not found")
        course = await self.get_course(module.course_id)
        await self._check_edit_access(course, user)
        await self.module_repo.delete(module)

    async def list_modules(self, course_id: UUID) -> list[Module]:
        return await self.module_repo.list_by_course(course_id)

    async def _check_edit_access(self, course: Course, user: User) -> None:
        if user.role == UserRole.PLATFORM_ADMIN:
            return
        if user.role == UserRole.INSTRUCTOR and course.created_by == user.id:
            return
        if user.role == UserRole.ORG_ADMIN and course.organization_id == user.organization_id:
            return
        raise ForbiddenError("You cannot edit this course")
