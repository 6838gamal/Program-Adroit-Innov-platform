"""create students table

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✅ استخدم SQL خام مع IF NOT EXISTS
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'student_role') THEN
                CREATE TYPE student_role AS ENUM ('student', 'teacher', 'admin');
            END IF;
        END $$;
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL,
            google_sub VARCHAR(255),
            hashed_password VARCHAR(255),
            full_name VARCHAR(150) NOT NULL,
            avatar_url VARCHAR(500),
            bio TEXT,
            role student_role NOT NULL DEFAULT 'student',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            last_login_at TIMESTAMPTZ,
            organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    # الفهارس — IF NOT EXISTS
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_students_email 
        ON students(email);
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_students_google_sub 
        ON students(google_sub);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_students_organization_id 
        ON students(organization_id);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS students CASCADE;")
    op.execute("DROP TYPE IF EXISTS student_role;")
