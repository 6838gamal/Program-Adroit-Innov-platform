# alembic/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import Base

# ⚠️ استيراد كل الموديلات ليتعرّف عليها Alembic
from app.modules.users.models import User  # noqa
from app.modules.organizations.models import (  # noqa
    Membership,
    Organization,
    Permission,
    Role,
    RolePermission,
)
from app.modules.learning.models import (  # noqa
    Enrollment,
    LearningPath,
    Progress,
)
from app.modules.courses.models import (  # noqa
    Course,
    CourseSkill,
    Module,
    learning_path_courses,
)
from app.modules.lessons.models import Concept, Lesson  # noqa
from app.modules.skills.models import (  # noqa
    Skill,
    SkillAssessment,
    SkillDependency,
    StudentSkill,
)
from app.modules.exercises.models import (  # noqa
    Exercise,
    ExerciseTest,
    Submission,
    SubmissionResult,
)
from app.modules.assessments.models import (  # noqa
    Assessment,
    AssessmentQuestion,
    AssessmentResult,
)
from app.modules.projects.models import (  # noqa
    Project,
    ProjectEvaluation,
    ProjectMilestone,
    ProjectSubmission,
    ProjectTask,
)

config = context.config

# املأ sqlalchemy.url (لا يُستخدم فعلياً في الحل الجديد، لكنه مطلوب)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,          # ← يرصد تغييرات نوع الأعمدة
        compare_server_default=True, # ← يرصد تغييرات القيم الافتراضية
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    ✅ الحل: أنشئ async engine مباشرة من settings.DATABASE_URL
    بدلاً من async_engine_from_config التي تفشل مع asyncpg.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args={"ssl": True},   # ← نفس إعدادات التطبيق
    )

    async def _run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
