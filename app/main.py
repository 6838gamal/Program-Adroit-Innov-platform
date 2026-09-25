# app/main.py
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.dependencies import get_current_user_optional
from app.core.logging import setup_logging, get_logger

# ===== Routers =====
from app.modules.ai.routes import router as ai_router
from app.modules.assessments.routes import router as assessments_router
from app.modules.auth.routes import router as auth_router
from app.modules.code_execution.routes import router as code_exec_router
from app.modules.courses.routes import router as courses_router
from app.modules.exercises.routes import router as exercises_router
from app.modules.learning.routes import router as learning_router
from app.modules.lessons.routes import router as lessons_router
from app.modules.organizations.routes import router as org_router
from app.modules.projects.routes import router as projects_router
from app.modules.skills.routes import router as skills_router
from app.modules.users.routes import router as users_router

# ===== استيراد كل الموديلات ليتعرّف عليها SQLAlchemy و Alembic =====
from app.modules.organizations.models import (  # noqa: F401
    Membership,
    Organization,
    Permission,
    Role,
    RolePermission,
)
from app.modules.users.models import User  # noqa: F401  ← جدول students
from app.modules.courses.models import (  # noqa: F401
    Course,
    CourseSkill,
    Module,
    learning_path_courses,
)
from app.modules.lessons.models import Concept, Lesson  # noqa: F401
from app.modules.skills.models import (  # noqa: F401
    Skill,
    SkillAssessment,
    SkillDependency,
    StudentSkill,
)
from app.modules.exercises.models import (  # noqa: F401
    Exercise,
    ExerciseTest,
    Submission,
    SubmissionResult,
)
from app.modules.assessments.models import (  # noqa: F401
    Assessment,
    AssessmentQuestion,
    AssessmentResult,
)
from app.modules.learning.models import (  # noqa: F401
    Enrollment,
    LearningPath,
    Progress,
)
from app.modules.projects.models import (  # noqa: F401
    Project,
    ProjectEvaluation,
    ProjectMilestone,
    ProjectSubmission,
    ProjectTask,
)

setup_logging()
logger = get_logger(__name__)

templates = Jinja2Templates(directory="app/templates")


# =========================================================
# 1) إنشاء الجداول الناقصة (طبقة أمان)
# =========================================================
async def _ensure_tables() -> None:
    """
    إنشاء الجداول الناقصة من الموديلات.
    ⚠️ ملاحظة: create_all لا يعدّل الجداول الموجودة.
    """
    logger.info("ensure_tables_starting")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("ensure_tables_success")
    except Exception as exc:
        logger.error("ensure_tables_failed", error=str(exc), exc_info=True)
        raise


# =========================================================
# 2) طباعة الجداول للتشخيص
# =========================================================
async def _check_tables() -> None:
    """اطبع الجداول الموجودة للتأكد من الترحيل."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            tables = [row[0] for row in result]
            logger.info("db_tables_list", count=len(tables), tables=tables)

            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM pg_tables "
                    "WHERE schemaname = 'public' AND tablename = 'students')"
                )
            )
            students_exists = bool(result.scalar())
            logger.info("students_table_exists", exists=students_exists)

            if students_exists:
                result = await conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'students' ORDER BY ordinal_position"
                    )
                )
                cols = [row[0] for row in result]
                logger.info("students_columns", columns=cols)
    except Exception as exc:
        logger.error("db_check_failed", error=str(exc), exc_info=True)


# =========================================================
# 3) lifespan
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", app=settings.APP_NAME, env=settings.APP_ENV)

    # ✅ 1) أنشئ الجداول الناقصة (بما فيها students)
    await _ensure_tables()

    # ✅ 2) اطبع الجداول للتشخيص
    await _check_tables()

    yield

    logger.info("app_stopping")


# =========================================================
# 4) إنشاء التطبيق
# =========================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered multi-user programming learning platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE,
    https_only=settings.is_production,
)

# =========================================================
# 5) Routes
# =========================================================
api_prefix = "/api/v1"
app.include_router(auth_router)
app.include_router(users_router, prefix=api_prefix)
app.include_router(org_router, prefix=api_prefix)
app.include_router(learning_router, prefix=api_prefix)
app.include_router(courses_router, prefix=api_prefix)
app.include_router(lessons_router, prefix=api_prefix)
app.include_router(skills_router, prefix=api_prefix)
app.include_router(exercises_router, prefix=api_prefix)
app.include_router(code_exec_router, prefix=api_prefix)
app.include_router(assessments_router, prefix=api_prefix)
app.include_router(projects_router, prefix=api_prefix)
app.include_router(ai_router, prefix=api_prefix)


# =========================================================
# 6) Page routes (Jinja2)
# =========================================================
_DASHBOARD_EMPTY = {
    "enrollments": [],
    "skills": [],
    "submissions": [],
    "recommended_paths": [],
    "courses": [],
    "students_count": 0,
    "submissions_count": 0,
    "members_count": 0,
    "courses_count": 0,
    "users_count": 0,
    "orgs_count": 0,
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user=Depends(get_current_user_optional)):
    template = "dashboard/student.html" if user else "auth/login.html"
    return templates.TemplateResponse(
        template,
        {"request": request, "current_user": user, **_DASHBOARD_EMPTY},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(get_current_user_optional)):
    if user:
        return templates.TemplateResponse(
            "dashboard/student.html",
            {"request": request, "current_user": user, **_DASHBOARD_EMPTY},
        )
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "current_user": None}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, user=Depends(get_current_user_optional)
):
    if not user:
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "current_user": None}
        )

    template_map = {
        "student": "dashboard/student.html",
        "instructor": "dashboard/instructor.html",
        "org_admin": "dashboard/organization.html",
        "platform_admin": "dashboard/admin.html",
    }
    template = template_map.get(
        user.role.value if hasattr(user.role, "value") else str(user.role),
        "dashboard/student.html",
    )
    return templates.TemplateResponse(
        template,
        {"request": request, "current_user": user, **_DASHBOARD_EMPTY},
    )


@app.get("/courses", response_class=HTMLResponse)
async def courses_page(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.courses.services import CourseService

    service = CourseService(db)
    published_only = user.role.value == "student" if user else True
    courses = await service.list_courses(published_only=published_only)
    return templates.TemplateResponse(
        "courses/list.html",
        {"request": request, "current_user": user, "courses": courses},
    )


@app.get("/courses/{course_id}", response_class=HTMLResponse)
async def course_detail_page(
    course_id: str,
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID

    from app.modules.courses.services import CourseService

    service = CourseService(db)
    course = await service.get_course(UUID(course_id))
    modules = await service.list_modules(UUID(course_id))
    return templates.TemplateResponse(
        "courses/detail.html",
        {
            "request": request,
            "current_user": user,
            "course": course,
            "modules": modules,
        },
    )


@app.get("/exercises/{exercise_id}", response_class=HTMLResponse)
async def exercise_detail_page(
    exercise_id: str,
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID

    from app.modules.exercises.services import ExerciseService

    service = ExerciseService(db)
    exercise = await service.get_exercise(UUID(exercise_id))
    return templates.TemplateResponse(
        "exercises/detail.html",
        {"request": request, "current_user": user, "exercise": exercise},
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects_page(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.projects.services import ProjectService

    service = ProjectService(db)
    projects = await service.list_projects()
    return templates.TemplateResponse(
        "projects/list.html",
        {"request": request, "current_user": user, "projects": projects},
    )


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user=Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "current_user": None}
        )
    from app.modules.skills.services import SkillService

    service = SkillService(db)
    skills = await service.get_student_skills(user.id)
    return templates.TemplateResponse(
        "profile/profile.html",
        {"request": request, "current_user": user, "skills": skills},
    )


@app.get("/instructor", response_class=HTMLResponse)
async def instructor_page(
    request: Request, user=Depends(get_current_user_optional)
):
    if not user or user.role.value not in (
        "instructor",
        "org_admin",
        "platform_admin",
    ):
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "current_user": None}
        )
    return templates.TemplateResponse(
        "instructor/dashboard.html",
        {
            "request": request,
            "current_user": user,
            "courses": [],
            "students": [],
        },
    )


@app.get("/organization", response_class=HTMLResponse)
async def organization_page(
    request: Request, user=Depends(get_current_user_optional)
):
    if not user or user.role.value not in ("org_admin", "platform_admin"):
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "current_user": None}
        )
    return templates.TemplateResponse(
        "organization/dashboard.html",
        {
            "request": request,
            "current_user": user,
            "members": [],
            "courses": [],
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request, user=Depends(get_current_user_optional)
):
    if not user or user.role.value != "platform_admin":
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "current_user": None}
        )
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": user,
            "users": [],
            "organizations": [],
        },
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }
