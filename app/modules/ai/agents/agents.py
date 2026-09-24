from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.schemas import (
    CodeReviewRequest,
    DebugRequest,
    ProjectMentorRequest,
    TutorRequest,
)


class TutorAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def tutor(self, user_id, user_name, data: TutorRequest):
        # منطق الوكيل هنا
        return {
            "response": f"مرحباً {user_name}، سأساعدك في: {data.question}",
        }


class CodeReviewAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def review(self, data: CodeReviewRequest):
        return {
            "response": "تمت مراجعة الكود",
            "issues": [],
        }


class DebuggingAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def debug(self, data: DebugRequest):
        return {
            "response": "تم تحليل الخطأ",
            "solution": "",
        }


class RecommendationAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def recommend(self, user_id):
        return {
            "recommendations": [],
        }


class ProjectMentorAgent:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def mentor(self, user_id, data: ProjectMentorRequest):
        return {
            "response": "إرشادات المشروع",
        }
