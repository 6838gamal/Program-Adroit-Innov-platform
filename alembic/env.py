# alembic/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import (
    Base,
    _normalize_async_url,   # ✅ استيراد الدالة
    _make_ssl_context,      # ✅ استيراد SSL context
)

# ⚠️ استيراد كل الموديلات ليتعرّف عليها Alembic
# لا تحذف أي استيراد حتى لو بدا غير مستخدم
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

# ✅ استخدم نفس الدالة التي يستخدمها التطبيق
# هذا يضمن أن الرابط يحتوي +asyncpg
DATABASE_URL = _normalize_async_url(settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

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
        compare_type=True,            # ← يرصد تغييرات نوع الأعمدة
        compare_server_default=True,  # ← يرصد تغييرات القيم الافتراضية
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    ✅ الحل النهائي: استخدم DATABASE_URL المحوَّل صراحةً.
    لم يعد SQLAlchemy يحاول psycopg2.
    """
    connectable = create_async_engine(
        DATABASE_URL,                          # ← URL محوَّل (asyncpg)
        poolclass=pool.NullPool,
        connect_args={"ssl": _make_ssl_context()},  # ← نفس SSL context
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
