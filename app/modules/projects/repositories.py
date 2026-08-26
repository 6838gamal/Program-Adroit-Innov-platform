from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import (
    Project,
    ProjectEvaluation,
    ProjectMilestone,
    ProjectSubmission,
    ProjectTask,
)


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: UUID) -> Project | None:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Project | None:
        result = await self.db.execute(select(Project).where(Project.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, data, user_id: UUID, org_id: UUID | None) -> Project:
        project = Project(**data.model_dump(), created_by=user_id, organization_id=org_id)
        self.db.add(project)
        await self.db.flush()
        return project

    async def update(self, project: Project, data) -> Project:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        await self.db.flush()
        return project

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Project]:
        result = await self.db.execute(select(Project).limit(limit).offset(offset))
        return list(result.scalars().all())


class ProjectTaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data) -> ProjectTask:
        task = ProjectTask(**data.model_dump())
        self.db.add(task)
        await self.db.flush()
        return task

    async def list_by_project(self, project_id: UUID) -> list[ProjectTask]:
        result = await self.db.execute(
            select(ProjectTask).where(ProjectTask.project_id == project_id).order_by(ProjectTask.order)
        )
        return list(result.scalars().all())


class ProjectMilestoneRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data) -> ProjectMilestone:
        milestone = ProjectMilestone(**data.model_dump())
        self.db.add(milestone)
        await self.db.flush()
        return milestone

    async def list_by_project(self, project_id: UUID) -> list[ProjectMilestone]:
        result = await self.db.execute(
            select(ProjectMilestone).where(ProjectMilestone.project_id == project_id).order_by(ProjectMilestone.order)
        )
        return list(result.scalars().all())


class ProjectSubmissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, project_id: UUID, repo_url: str | None, notes: str | None) -> ProjectSubmission:
        sub = ProjectSubmission(user_id=user_id, project_id=project_id, repo_url=repo_url, notes=notes)
        self.db.add(sub)
        await self.db.flush()
        return sub

    async def get_by_id(self, submission_id: UUID) -> ProjectSubmission | None:
        result = await self.db.execute(select(ProjectSubmission).where(ProjectSubmission.id == submission_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[ProjectSubmission]:
        result = await self.db.execute(
            select(ProjectSubmission).where(ProjectSubmission.user_id == user_id)
        )
        return list(result.scalars().all())

    async def list_by_project(self, project_id: UUID) -> list[ProjectSubmission]:
        result = await self.db.execute(
            select(ProjectSubmission).where(ProjectSubmission.project_id == project_id)
        )
        return list(result.scalars().all())


class ProjectEvaluationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, submission_id: UUID, evaluator_id: UUID | None, is_ai: bool, score: float, feedback: str | None, criteria_scores: dict | None) -> ProjectEvaluation:
        evaluation = ProjectEvaluation(
            submission_id=submission_id,
            evaluator_id=evaluator_id,
            is_ai_evaluation=is_ai,
            score=score,
            feedback=feedback,
            criteria_scores=criteria_scores,
        )
        self.db.add(evaluation)
        await self.db.flush()
        return evaluation

    async def list_by_submission(self, submission_id: UUID) -> list[ProjectEvaluation]:
        result = await self.db.execute(
            select(ProjectEvaluation).where(ProjectEvaluation.submission_id == submission_id)
        )
        return list(result.scalars().all())
