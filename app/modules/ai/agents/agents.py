from sqlalchemy.ext.asyncio import AsyncSession

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

    async def tutor(self, user_id, user_name: str, data: TutorRequest) -> TutorResponse:
        # TODO: استبدل هذا بالمنطق الحقيقي (استدعاء LLM مثلاً)
        context_used = {}
        if data.course_id:
            context_used["course_id"] = str(data.course_id)
        if data.lesson_id:
            context_used["lesson_id"] = str(data.lesson_id)
        if data.exercise_id:
            context_used["exercise_id"] = str(data.exercise_id)

        return TutorResponse(
            response=f"مرحباً {user_name}، سأساعدك في: {data.question}",
            context_used=context_used or None,
        )


class CodeReviewAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def review(self, data: CodeReviewRequest) -> CodeReviewResponse:
        # TODO: استبدل بالتحليل الحقيقي
        analysis = {
            "language": data.language,
            "issues": [],
            "score": 100,
        }
        return CodeReviewResponse(
            analysis=analysis,
            summary="الكود يبدو سليماً من الناحية الأولية.",
        )


class DebuggingAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def debug(self, data: DebugRequest) -> DebugResponse:
        # TODO: استبدل بمنطق التصحيح الحقيقي
        return DebugResponse(
            analysis=f"تحليل الخطأ في كود {data.language}",
            explanation=data.error or "لا يوجد خطأ محدد.",
            steps=[
                "افحص السطر الذي ظهر فيه الخطأ",
                "تأكد من أنواع المتغيرات",
                "جرّب تشغيل الكود خطوة بخطوة",
            ],
            hint="راجع السطر الذي يحتوي على الخطأ أولاً.",
            solution=None,
        )


class RecommendationAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def recommend(self, user_id) -> RecommendationResponse:
        # TODO: استبدل بالتوصيات الحقيقية بناءً على بيانات المستخدم
        return RecommendationResponse(
            recommendations=[
                {"type": "lesson", "title": "مراجعة أساسيات Python", "reason": "تحسين المهارات"},
                {"type": "exercise", "title": "تمارين الحلقات", "reason": "تعزيز الفهم"},
            ]
        )


class ProjectMentorAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def mentor(self, user_id, data: ProjectMentorRequest) -> ProjectMentorResponse:
        # TODO: استبدل بمنطق الإرشاد الحقيقي
        return ProjectMentorResponse(
            response=f"بخصوص مشروعك ({data.project_id}): {data.question}",
        )
