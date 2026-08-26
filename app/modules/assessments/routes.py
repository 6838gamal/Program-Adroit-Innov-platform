from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.modules.assessments.schemas import (
    AssessmentCreate,
    AssessmentRead,
    AssessmentResultRead,
    AssessmentUpdate,
    QuestionCreate,
    QuestionRead,
    SubmitAssessmentRequest,
)
from app.modules.assessments.services import AssessmentService
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/", response_model=AssessmentRead)
async def create_assessment(data: AssessmentCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    return await service.create_assessment(data)


@router.get("/", response_model=list[AssessmentRead])
async def list_assessments(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    return await service.list_assessments()


@router.get("/{assessment_id}", response_model=AssessmentRead)
async def get_assessment(assessment_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    return await service.get_assessment(assessment_id)


@router.put("/{assessment_id}", response_model=AssessmentRead)
async def update_assessment(
    assessment_id: UUID, data: AssessmentUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    return await service.update_assessment(assessment_id, data)


@router.post("/{assessment_id}/questions", response_model=QuestionRead)
async def add_question(
    assessment_id: UUID, data: QuestionCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    data.assessment_id = assessment_id
    service = AssessmentService(db)
    return await service.add_question(data)


@router.get("/{assessment_id}/questions", response_model=list[QuestionRead])
async def list_questions(assessment_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    return await service.list_questions(assessment_id)


@router.post("/submit", response_model=AssessmentResultRead)
async def submit_assessment(
    data: SubmitAssessmentRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    return await service.submit_assessment(user.id, data)


@router.get("/results/me", response_model=list[AssessmentResultRead])
async def my_results(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    return await service.list_user_results(user.id)
