from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.modules.skills.schemas import (
    SkillAssessmentCreate,
    SkillAssessmentRead,
    SkillCreate,
    SkillDependencyCreate,
    SkillProfile,
    SkillRead,
    SkillUpdate,
    StudentSkillRead,
)
from app.modules.skills.services import SkillService
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("/", response_model=SkillRead)
async def create_skill(data: SkillCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SkillService(db)
    return await service.create_skill(data)


@router.get("/", response_model=list[SkillRead])
async def list_skills(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SkillService(db)
    return await service.list_skills()


@router.get("/{skill_id}", response_model=SkillRead)
async def get_skill(skill_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SkillService(db)
    return await service.get_skill(skill_id)


@router.put("/{skill_id}", response_model=SkillRead)
async def update_skill(
    skill_id: UUID, data: SkillUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = SkillService(db)
    return await service.update_skill(skill_id, data)


@router.get("/me/profile", response_model=SkillProfile)
async def get_my_skill_profile(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SkillService(db)
    return await service.get_skill_profile(user.id)


@router.get("/me/all", response_model=list[StudentSkillRead])
async def get_my_skills(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SkillService(db)
    return await service.get_student_skills(user.id)


@router.post("/assessments", response_model=StudentSkillRead)
async def record_assessment(
    data: SkillAssessmentCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = SkillService(db)
    return await service.record_assessment(user.id, data)


@router.post("/dependencies", response_model=MessageResponse)
async def add_dependency(
    data: SkillDependencyCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = SkillService(db)
    await service.add_dependency(data)
    return MessageResponse(message="Skill dependency added")


@router.get("/{skill_id}/prerequisites")
async def get_prerequisites(skill_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = SkillService(db)
    deps = await service.get_prerequisites(skill_id)
    return [{"skill_id": str(d.skill_id), "prerequisite_skill_id": str(d.prerequisite_skill_id)} for d in deps]
