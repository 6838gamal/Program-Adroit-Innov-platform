import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.core.database import Base

# Import all models so they are registered on Base.metadata
from app.modules.users.models import User  # noqa
from app.modules.organizations.models import Organization, Membership, Role, Permission, RolePermission  # noqa
from app.modules.learning.models import LearningPath, Enrollment, Progress  # noqa
from app.modules.courses.models import Course, Module, CourseSkill, learning_path_courses  # noqa
from app.modules.lessons.models import Lesson, Concept  # noqa
from app.modules.skills.models import Skill, StudentSkill, SkillAssessment, SkillDependency  # noqa
from app.modules.exercises.models import Exercise, ExerciseTest, Submission, SubmissionResult  # noqa
from app.modules.assessments.models import Assessment, AssessmentQuestion, AssessmentResult  # noqa
from app.modules.projects.models import Project, ProjectTask, ProjectMilestone, ProjectSubmission, ProjectEvaluation  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async def _run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    asyncio.run(_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
