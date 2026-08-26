from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.courses.models import Course, Module
from app.modules.exercises.models import Exercise, Submission
from app.modules.lessons.models import Lesson
from app.modules.skills.models import StudentSkill
from app.modules.analytics.models import LearningEvent


@dataclass
class TutorContext:
    user_id: UUID
    user_name: str
    course_title: str | None = None
    lesson_title: str | None = None
    exercise_title: str | None = None
    skill_level: str = "beginner"
    attempts: int = 0
    previous_errors: list[str] = None
    current_code: str | None = None
    learning_history: list[dict] = None

    def to_prompt_kwargs(self) -> dict:
        return {
            "course_title": self.course_title or "N/A",
            "lesson_title": self.lesson_title or "N/A",
            "skill_level": self.skill_level,
            "attempts": self.attempts,
            "previous_errors": ", ".join(self.previous_errors or []) or "None",
            "question": "{question}",
            "current_code": self.current_code or "N/A",
        }


class ContextBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_context(
        self,
        user_id: UUID,
        user_name: str,
        course_id: UUID | None = None,
        lesson_id: UUID | None = None,
        exercise_id: UUID | None = None,
        current_code: str | None = None,
    ) -> TutorContext:
        ctx = TutorContext(user_id=user_id, user_name=user_name, previous_errors=[], learning_history=[])

        if course_id:
            result = await self.db.execute(select(Course).where(Course.id == course_id))
            course = result.scalar_one_or_none()
            if course:
                ctx.course_title = course.title

        if lesson_id:
            result = await self.db.execute(select(Lesson).where(Lesson.id == lesson_id))
            lesson = result.scalar_one_or_none()
            if lesson:
                ctx.lesson_title = lesson.title

        if exercise_id:
            result = await self.db.execute(select(Exercise).where(Exercise.id == exercise_id))
            exercise = result.scalar_one_or_none()
            if exercise:
                ctx.exercise_title = exercise.title

        skills = await self.db.execute(
            select(StudentSkill).where(StudentSkill.user_id == user_id)
        )
        skill_records = list(skills.scalars().all())
        if skill_records:
            avg = sum(s.mastery_score for s in skill_records) / len(skill_records)
            ctx.skill_level = "beginner" if avg < 0.4 else "intermediate" if avg < 0.7 else "advanced"

        submissions = await self.db.execute(
            select(Submission).where(Submission.user_id == user_id).order_by(Submission.created_at.desc()).limit(5)
        )
        subs = list(submissions.scalars().all())
        ctx.attempts = len(subs)
        ctx.previous_errors = [s.feedback for s in subs if s.feedback and s.status.value == "failed"][:5]

        events = await self.db.execute(
            select(LearningEvent).where(LearningEvent.user_id == user_id).order_by(LearningEvent.created_at.desc()).limit(10)
        )
        for ev in events.scalars().all():
            ctx.learning_history.append({"event": ev.event_type.value, "timestamp": str(ev.created_at)})

        ctx.current_code = current_code
        return ctx
