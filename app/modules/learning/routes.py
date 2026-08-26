from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.exceptions import ForbiddenError
from app.modules.learning.schemas import (
    EnrollmentCreate,
    EnrollmentRead,
    LearningPathCreate,
    LearningPathRead,
    LearningPathUpdate,
    ProgressRead,
    ProgressUpdate,
)
from app.modules.learning.services import LearningPathService
from app.shared.enums import UserRole
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/learning-paths", tags=["learning"])


@router.post("/", response_model=LearningPathRead)
async def create_path(data: LearningPathCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user.role not in (UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN):
        raise ForbiddenError()
    service = LearningPathService(db)
    return await service.create_path(data, user)


@router.get("/", response_model=list[LearningPathRead])
async def list_paths(user: CurrentUser, db: AsyncSession = Depends(get_db), published: bool = Query(True)):
    service = LearningPathService(db)
    only_published = published and user.role == UserRole.STUDENT
    return await service.list_paths(published_only=only_published)


@router.get("/{path_id}", response_model=LearningPathRead)
async def get_path(path_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LearningPathService(db)
    return await service.get_path(path_id)


@router.put("/{path_id}", response_model=LearningPathRead)
async def update_path(
    path_id: UUID, data: LearningPathUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    if user.role not in (UserRole.INSTRUCTOR, UserRole.ORG_ADMIN, UserRole.PLATFORM_ADMIN):
        raise ForbiddenError()
    service = LearningPathService(db)
    return await service.update_path(path_id, data, user)


@router.post("/enroll", response_model=EnrollmentRead)
async def enroll(data: EnrollmentCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LearningPathService(db)
    return await service.enroll(user.id, data.learning_path_id)


@router.get("/enrollments/me", response_model=list[EnrollmentRead])
async def my_enrollments(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LearningPathService(db)
    return await service.list_user_enrollments(user.id)


@router.get("/{path_id}/progress", response_model=list[ProgressRead])
async def get_progress(path_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LearningPathService(db)
    return await service.get_progress(user.id, path_id)


@router.post("/{path_id}/progress/{lesson_id}", response_model=ProgressRead)
async def update_progress(
    path_id: UUID,
    lesson_id: UUID,
    data: ProgressUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = LearningPathService(db)
    return await service.update_progress(user.id, path_id, lesson_id, data)
