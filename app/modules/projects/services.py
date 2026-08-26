from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.projects.models import Project, ProjectSubmission
from app.modules.projects.repositories import (
    ProjectEvaluationRepository,
    ProjectMilestoneRepository,
    ProjectRepository,
    ProjectSubmissionRepository,
    ProjectTaskRepository,
)
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectMilestoneCreate,
    ProjectSubmissionCreate,
    ProjectTaskCreate,
    ProjectUpdate,
)
from app.modules.users.models import User
from app.shared.enums import ProjectStatus, UserRole


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.task_repo = ProjectTaskRepository(db)
        self.milestone_repo = ProjectMilestoneRepository(db)
        self.submission_repo = ProjectSubmissionRepository(db)
        self.evaluation_repo = ProjectEvaluationRepository(db)

    async def create_project(self, data: ProjectCreate, user: User) -> Project:
        existing = await self.project_repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError("Project slug already exists")
        org_id = user.organization_id if user.role != UserRole.PLATFORM_ADMIN else None
        return await self.project_repo.create(data, user.id, org_id)

    async def get_project(self, project_id: UUID) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    async def update_project(self, project_id: UUID, data: ProjectUpdate) -> Project:
        project = await self.get_project(project_id)
        return await self.project_repo.update(project, data)

    async def list_projects(self) -> list[Project]:
        return await self.project_repo.list_all()

    async def add_task(self, data: ProjectTaskCreate) -> None:
        await self.get_project(data.project_id)
        await self.task_repo.create(data)

    async def list_tasks(self, project_id: UUID) -> list:
        return await self.task_repo.list_by_project(project_id)

    async def add_milestone(self, data: ProjectMilestoneCreate) -> None:
        await self.get_project(data.project_id)
        await self.milestone_repo.create(data)

    async def list_milestones(self, project_id: UUID) -> list:
        return await self.milestone_repo.list_by_project(project_id)

    async def submit_project(self, user_id: UUID, data: ProjectSubmissionCreate) -> ProjectSubmission:
        await self.get_project(data.project_id)
        submission = await self.submission_repo.create(user_id, data.project_id, data.repo_url, data.notes)
        submission.status = ProjectStatus.SUBMITTED
        await self.db.flush()
        return submission

    async def list_user_submissions(self, user_id: UUID) -> list[ProjectSubmission]:
        return await self.submission_repo.list_by_user(user_id)

    async def list_project_submissions(self, project_id: UUID) -> list[ProjectSubmission]:
        return await self.submission_repo.list_by_project(project_id)

    async def evaluate_submission(
        self, submission_id: UUID, evaluator_id: UUID, score: float, feedback: str, criteria_scores: dict | None = None
    ) -> None:
        submission = await self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise NotFoundError("Submission not found")
        await self.evaluation_repo.create(submission_id, evaluator_id, False, score, feedback, criteria_scores)
        submission.status = ProjectStatus.REVIEWED
        await self.db.flush()

    async def list_evaluations(self, submission_id: UUID) -> list:
        return await self.evaluation_repo.list_by_submission(submission_id)
