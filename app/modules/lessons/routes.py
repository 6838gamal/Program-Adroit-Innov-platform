from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.modules.lessons.schemas import (
    ConceptCreate,
    ConceptRead,
    ConceptUpdate,
    LessonCreate,
    LessonRead,
    LessonUpdate,
)
from app.modules.lessons.services import LessonService
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("/", response_model=LessonRead)
async def create_lesson(data: LessonCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LessonService(db)
    return await service.create_lesson(data, user)


@router.get("/{lesson_id}", response_model=LessonRead)
async def get_lesson(lesson_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LessonService(db)
    return await service.get_lesson(lesson_id)


@router.put("/{lesson_id}", response_model=LessonRead)
async def update_lesson(
    lesson_id: UUID, data: LessonUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = LessonService(db)
    return await service.update_lesson(lesson_id, data, user)


@router.delete("/{lesson_id}", response_model=MessageResponse)
async def delete_lesson(lesson_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LessonService(db)
    await service.delete_lesson(lesson_id, user)
    return MessageResponse(message="Lesson deleted")


@router.get("/module/{module_id}", response_model=list[LessonRead])
async def list_lessons(module_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LessonService(db)
    return await service.list_lessons(module_id)


@router.post("/{lesson_id}/concepts", response_model=ConceptRead)
async def create_concept(
    lesson_id: UUID, data: ConceptCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    data.lesson_id = lesson_id
    service = LessonService(db)
    return await service.create_concept(data, user)


@router.get("/{lesson_id}/concepts", response_model=list[ConceptRead])
async def list_concepts(lesson_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LessonService(db)
    return await service.list_concepts(lesson_id)


@router.put("/concepts/{concept_id}", response_model=ConceptRead)
async def update_concept(
    concept_id: UUID, data: ConceptUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = LessonService(db)
    return await service.update_concept(concept_id, data, user)


@router.delete("/concepts/{concept_id}", response_model=MessageResponse)
async def delete_concept(concept_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = LessonService(db)
    await service.delete_concept(concept_id, user)
    return MessageResponse(message="Concept deleted")
