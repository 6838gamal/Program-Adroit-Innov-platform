from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectEvaluationRead,
    ProjectMilestoneCreate,
    ProjectMilestoneRead,
    ProjectRead,
    ProjectSubmissionCreate,
    ProjectSubmissionRead,
    ProjectTaskCreate,
    ProjectTaskRead,
    ProjectUpdate,
)
from app.modules.projects.services import ProjectService
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead)
async def create_project(data: ProjectCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.create_project(data, user)


@router.get("/", response_model=list[ProjectRead])
async def list_projects(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_projects()


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.get_project(project_id)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID, data: ProjectUpdate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.update_project(project_id, data)


@router.post("/{project_id}/tasks", response_model=ProjectTaskRead)
async def add_task(
    project_id: UUID, data: ProjectTaskCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    data.project_id = project_id
    service = ProjectService(db)
    await service.add_task(data)
    tasks = await service.list_tasks(project_id)
    return tasks[-1]


@router.get("/{project_id}/tasks", response_model=list[ProjectTaskRead])
async def list_tasks(project_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_tasks(project_id)


@router.post("/{project_id}/milestones", response_model=ProjectMilestoneRead)
async def add_milestone(
    project_id: UUID, data: ProjectMilestoneCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    data.project_id = project_id
    service = ProjectService(db)
    await service.add_milestone(data)
    milestones = await service.list_milestones(project_id)
    return milestones[-1]


@router.get("/{project_id}/milestones", response_model=list[ProjectMilestoneRead])
async def list_milestones(project_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_milestones(project_id)


@router.post("/submit", response_model=ProjectSubmissionRead)
async def submit_project(
    data: ProjectSubmissionCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.submit_project(user.id, data)


@router.get("/submissions/me", response_model=list[ProjectSubmissionRead])
async def my_submissions(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_user_submissions(user.id)


@router.get("/{project_id}/submissions", response_model=list[ProjectSubmissionRead])
async def project_submissions(project_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_project_submissions(project_id)


@router.post("/submissions/{submission_id}/evaluate", response_model=MessageResponse)
async def evaluate_submission(
    submission_id: UUID,
    score: float,
    feedback: str,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.evaluate_submission(submission_id, user.id, score, feedback)
    return MessageResponse(message="Evaluation submitted")


@router.get("/submissions/{submission_id}/evaluations", response_model=list[ProjectEvaluationRead])
async def list_evaluations(submission_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.list_evaluations(submission_id)
