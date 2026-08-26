import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AIRuntimeError
from app.modules.ai.context import ContextBuilder, TutorContext
from app.modules.ai.prompts import (
    CODE_REVIEW_SYSTEM,
    DEBUGGING_SYSTEM,
    RECOMMENDATION_SYSTEM,
    TUTOR_HINT,
    TUTOR_SYSTEM,
)
from app.modules.ai.providers import get_provider
from app.modules.ai.schemas import (
    CodeReviewRequest,
    CodeReviewResponse,
    DebugRequest,
    DebugResponse,
    ProjectMentorRequest,
    ProjectMentorResponse,
    RecommendationResponse,
    TutorRequest,
    TutorResponse,
)


class TutorAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_provider()
        self.context_builder = ContextBuilder(db)

    async def tutor(self, user_id: UUID, user_name: str, data: TutorRequest) -> TutorResponse:
        ctx = await self.context_builder.build_context(
            user_id=user_id,
            user_name=user_name,
            course_id=data.course_id,
            lesson_id=data.lesson_id,
            exercise_id=data.exercise_id,
            current_code=data.current_code,
        )

        kwargs = ctx.to_prompt_kwargs()
        hint_prompt = TUTOR_HINT.format(**{**kwargs, "question": data.question})

        messages = [
            {"role": "system", "content": TUTOR_SYSTEM},
            {"role": "user", "content": hint_prompt},
        ]

        response = await self.provider.chat_completion(
            messages=messages,
            max_tokens=settings.AI_TUTOR_MAX_TOKENS,
            temperature=0.7,
        )

        return TutorResponse(
            response=response.content,
            context_used={"course": ctx.course_title, "lesson": ctx.lesson_title, "skill_level": ctx.skill_level},
        )


class CodeReviewAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_provider()

    async def review(self, data: CodeReviewRequest) -> CodeReviewResponse:
        user_msg = f"Review this {data.language} code:\n```{data.language}\n{data.code}\n```"
        if data.exercise_context:
            user_msg += f"\n\nContext: {data.exercise_context}"

        messages = [
            {"role": "system", "content": CODE_REVIEW_SYSTEM},
            {"role": "user", "content": user_msg},
        ]

        response = await self.provider.chat_completion(
            messages=messages,
            max_tokens=settings.AI_CODE_REVIEW_MAX_TOKENS,
            temperature=0.3,
        )

        try:
            analysis = json.loads(response.content)
        except json.JSONDecodeError:
            analysis = {"raw": response.content}

        return CodeReviewResponse(
            analysis=analysis,
            summary=analysis.get("summary", "Code review completed"),
        )


class DebuggingAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_provider()

    async def debug(self, data: DebugRequest) -> DebugResponse:
        user_msg = f"Code:\n```{data.language}\n{data.code}\n```"
        if data.error:
            user_msg += f"\n\nError: {data.error}"
        if data.expected_output:
            user_msg += f"\nExpected output: {data.expected_output}"
        if data.actual_output:
            user_msg += f"\nActual output: {data.actual_output}"

        messages = [
            {"role": "system", "content": DEBUGGING_SYSTEM},
            {"role": "user", "content": user_msg},
        ]

        response = await self.provider.chat_completion(
            messages=messages,
            max_tokens=settings.AI_DEBUG_MAX_TOKENS,
            temperature=0.5,
        )

        content = response.content
        return DebugResponse(
            analysis=content,
            explanation=content,
            steps=[],
            hint="Review the error message and trace the execution flow.",
        )


class RecommendationAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_provider()

    async def recommend(self, user_id: UUID) -> RecommendationResponse:
        from app.modules.skills.services import SkillService

        skill_service = SkillService(self.db)
        profile = await skill_service.get_skill_profile(user_id)

        profile_text = (
            f"Strong skills: {[s.skill_id for s in profile.strong_skills]}\n"
            f"Weak skills: {[s.skill_id for s in profile.weak_skills]}\n"
            f"Recommended: {[s.id for s in profile.recommended_next]}"
        )

        messages = [
            {"role": "system", "content": RECOMMENDATION_SYSTEM},
            {"role": "user", "content": profile_text},
        ]

        response = await self.provider.chat_completion(messages=messages, max_tokens=512, temperature=0.5)

        try:
            recs = json.loads(response.content)
            if not isinstance(recs, list):
                recs = [recs]
        except json.JSONDecodeError:
            recs = [{"title": "Continue practicing", "reason": "Keep up the good work"}]

        return RecommendationResponse(recommendations=recs)


class ProjectMentorAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_provider()

    async def mentor(self, user_id: UUID, data: ProjectMentorRequest) -> ProjectMentorResponse:
        from app.modules.projects.services import ProjectService

        project_service = ProjectService(self.db)
        project = await project_service.get_project(data.project_id)

        user_msg = f"Project: {project.title}\nDescription: {project.description}\n\nQuestion: {data.question}"
        if data.code:
            user_msg += f"\n\nCode:\n```\n{data.code}\n```"

        messages = [
            {"role": "system", "content": "You are a project mentor. Guide the student through their project. Provide hints, architectural guidance, and code suggestions without doing the work for them."},
            {"role": "user", "content": user_msg},
        ]

        response = await self.provider.chat_completion(messages=messages, max_tokens=1024, temperature=0.6)

        return ProjectMentorResponse(response=response.content)
