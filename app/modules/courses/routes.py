from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.exceptions import ForbiddenError
from app.modules.courses.schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    ModuleCreate,
    ModuleRead,
    ModuleUpdate,
)
from app.modules.courses.services import CourseService
from app.shared.enums import UserRole
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseRead)
async def create_course(data: CourseCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user.role not in (UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN):
        raise ForbiddenError()
    service = CourseService(db)
    return await service.create_course(data, user)


@router.get("/", response_model=list[CourseRead])
async def list_courses(user: CurrentUser, db: AsyncSession = Depends(get_db), published: bool = Query(True)):
    service = CourseService(db)
    only_published = published and user.role == UserRole.STUDENT
    return await service.list_courses(published_only=only_published)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = CourseService(db)
    return await service.get_course(course_id)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: UUID, data: CourseUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = CourseService(db)
    return await service.update_course(course_id, data, user)


@router.post("/{course_id}/modules", response_model=ModuleRead)
async def create_module(
    course_id: UUID, data: ModuleCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    data.course_id = course_id
    service = CourseService(db)
    return await service.create_module(data, user)


@router.get("/{course_id}/modules", response_model=list[ModuleRead])
async def list_modules(course_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = CourseService(db)
    return await service.list_modules(course_id)


@router.put("/modules/{module_id}", response_model=ModuleRead)
async def update_module(
    module_id: UUID, data: ModuleUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = CourseService(db)
    return await service.update_module(module_id, data, user)


@router.delete("/modules/{module_id}", response_model=MessageResponse)
async def delete_module(module_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = CourseService(db)
    await service.delete_module(module_id, user)
    return MessageResponse(message="Module deleted")
