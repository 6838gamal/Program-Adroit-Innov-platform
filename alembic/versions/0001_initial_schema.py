"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(1024), nullable=True),
        sa.Column("google_sub", sa.String(255), unique=True, nullable=True, index=True),
        sa.Column("role", sa.Enum("student", "instructor", "org_admin", "platform_admin", name="user_role"), nullable=False, server_default="student"),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("logo_url", sa.String(1024), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Memberships
    op.create_table(
        "memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.Enum("student", "instructor", "admin", name="membership_role"), nullable=False, server_default="student"),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Roles & Permissions
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "role_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True),
    )

    # Learning Paths
    op.create_table(
        "learning_paths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False, index=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("difficulty", sa.String(50), nullable=False, server_default="beginner"),
        sa.Column("estimated_hours", sa.Integer, nullable=True),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("cover_image_url", sa.String(1024), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Skills
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=True, index=True),
        sa.Column("parent_skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Courses
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False, index=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("difficulty", sa.String(50), nullable=False, server_default="beginner"),
        sa.Column("language", sa.String(20), nullable=False, server_default="python"),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("cover_image_url", sa.String(1024), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Learning Path <-> Course junction
    op.create_table(
        "learning_path_courses",
        sa.Column("learning_path_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("order", sa.Integer, server_default="0"),
    )

    # Modules
    op.create_table(
        "modules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Lessons
    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("content_type", sa.String(50), nullable=False, server_default="text"),
        sa.Column("video_url", sa.String(1024), nullable=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Concepts
    op.create_table(
        "concepts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Course Skills
    op.create_table(
        "course_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True),
    )

    # Enrollments
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("learning_path_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.Enum("active", "completed", "dropped", "paused", name="enrollment_status"), nullable=False, server_default="active"),
        sa.Column("progress_percent", sa.Integer, nullable=False, server_default="0"),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Progress
    op.create_table(
        "progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Student Skills
    op.create_table(
        "student_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("proficiency", sa.Enum("none", "beginner", "intermediate", "advanced", "expert", name="proficiency_level"), nullable=False, server_default="none"),
        sa.Column("mastery_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("assessments_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_assessed_at", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Skill Assessments
    op.create_table(
        "skill_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="exercise"),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Skill Dependencies
    op.create_table(
        "skill_dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("prerequisite_skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True),
    )

    # Exercises
    op.create_table(
        "exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("title", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("exercise_type", sa.Enum("code", "multiple_choice", "debugging", "output_prediction", "short_answer", name="exercise_type"), nullable=False, server_default="code"),
        sa.Column("difficulty", sa.String(50), nullable=False, server_default="easy"),
        sa.Column("language", sa.String(20), nullable=False, server_default="python"),
        sa.Column("starter_code", sa.Text, nullable=True),
        sa.Column("solution_code", sa.Text, nullable=True),
        sa.Column("expected_output", sa.Text, nullable=True),
        sa.Column("choices", postgresql.JSON, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=True),
        sa.Column("points", sa.Integer, nullable=False, server_default="10"),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Exercise Tests
    op.create_table(
        "exercise_tests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("test_name", sa.String(255), nullable=False),
        sa.Column("input_data", sa.Text, nullable=True),
        sa.Column("expected_output", sa.Text, nullable=False),
        sa.Column("is_hidden", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
    )

    # Submissions
    op.create_table(
        "submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("code", sa.Text, nullable=True),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("pending", "running", "passed", "failed", "error", name="submission_status"), nullable=False, server_default="pending"),
        sa.Column("score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Submission Results
    op.create_table(
        "submission_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("test_name", sa.String(255), nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False),
        sa.Column("output", sa.Text, nullable=True),
        sa.Column("expected", sa.Text, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("execution_time_ms", sa.Integer, nullable=True),
    )

    # Assessments
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("passing_score", sa.Float, nullable=False, server_default="70.0"),
        sa.Column("time_limit_minutes", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Assessment Questions
    op.create_table(
        "assessment_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("question_type", sa.String(50), nullable=False, server_default="multiple_choice"),
        sa.Column("choices", postgresql.JSON, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=False),
        sa.Column("points", sa.Integer, nullable=False, server_default="1"),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
    )

    # Assessment Results
    op.create_table(
        "assessment_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("max_score", sa.Float, nullable=False, server_default="100.0"),
        sa.Column("passed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("answers", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Projects
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False, index=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("difficulty", sa.String(50), nullable=False, server_default="intermediate"),
        sa.Column("language", sa.String(20), nullable=False, server_default="python"),
        sa.Column("estimated_hours", sa.Integer, nullable=True),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Project Tasks
    op.create_table(
        "project_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_required", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Project Milestones
    op.create_table(
        "project_milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target_date", sa.String(50), nullable=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Project Submissions
    op.create_table(
        "project_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.Enum("not_started", "in_progress", "submitted", "reviewed", "completed", name="project_status"), nullable=False, server_default="not_started"),
        sa.Column("repo_url", sa.String(1024), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("files", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Project Evaluations
    op.create_table(
        "project_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_submissions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("evaluator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_ai_evaluation", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("criteria_scores", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("project_evaluations")
    op.drop_table("project_submissions")
    op.drop_table("project_milestones")
    op.drop_table("project_tasks")
    op.drop_table("projects")
    op.drop_table("assessment_results")
    op.drop_table("assessment_questions")
    op.drop_table("assessments")
    op.drop_table("submission_results")
    op.drop_table("submissions")
    op.drop_table("exercise_tests")
    op.drop_table("exercises")
    op.drop_table("skill_dependencies")
    op.drop_table("skill_assessments")
    op.drop_table("student_skills")
    op.drop_table("progress")
    op.drop_table("enrollments")
    op.drop_table("course_skills")
    op.drop_table("concepts")
    op.drop_table("lessons")
    op.drop_table("modules")
    op.drop_table("learning_path_courses")
    op.drop_table("courses")
    op.drop_table("skills")
    op.drop_table("learning_paths")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")
