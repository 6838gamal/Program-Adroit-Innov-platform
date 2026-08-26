from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.modules.exercises.schemas import (
    ExerciseCreate,
    ExerciseRead,
    ExerciseTestCreate,
    ExerciseTestRead,
    ExerciseUpdate,
    SubmissionCreate,
    SubmissionRead,
    SubmissionResultRead,
)
from app.modules.exercises.services import ExerciseService
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.post("/", response_model=ExerciseRead)
async def create_exercise(data: ExerciseCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.create_exercise(data)


@router.get("/", response_model=list[ExerciseRead])
async def list_exercises(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.list_exercises()


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(exercise_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.get_exercise(exercise_id)


@router.put("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
    exercise_id: UUID, data: ExerciseUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = ExerciseService(db)
    return await service.update_exercise(exercise_id, data)


@router.delete("/{exercise_id}", response_model=MessageResponse)
async def delete_exercise(exercise_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    await service.delete_exercise(exercise_id)
    return MessageResponse(message="Exercise deleted")


@router.get("/lesson/{lesson_id}", response_model=list[ExerciseRead])
async def list_by_lesson(lesson_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.list_by_lesson(lesson_id)


@router.post("/{exercise_id}/tests", response_model=ExerciseTestRead)
async def add_test(
    exercise_id: UUID, data: ExerciseTestCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = ExerciseService(db)
    await service.add_test(exercise_id, data)
    tests = await service.list_tests(exercise_id)
    return tests[-1]


@router.get("/{exercise_id}/tests", response_model=list[ExerciseTestRead])
async def list_tests(exercise_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.list_tests(exercise_id)


@router.post("/submit", response_model=SubmissionRead)
async def submit_exercise(data: SubmissionCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    submission, results = await service.submit(user.id, data)
    return submission


@router.get("/submissions/me", response_model=list[SubmissionRead])
async def my_submissions(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.list_user_submissions(user.id)


@router.get("/{exercise_id}/submissions", response_model=list[SubmissionRead])
async def exercise_submissions(exercise_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ExerciseService(db)
    return await service.list_exercise_submissions(exercise_id)
