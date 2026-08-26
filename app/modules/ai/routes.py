from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.modules.ai.agents import (
    CodeReviewAgent,
    DebuggingAgent,
    ProjectMentorAgent,
    RecommendationAgent,
    TutorAgent,
)
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

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/tutor", response_model=TutorResponse)
async def ai_tutor(data: TutorRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    agent = TutorAgent(db)
    return await agent.tutor(user.id, user.name, data)


@router.post("/code-review", response_model=CodeReviewResponse)
async def ai_code_review(data: CodeReviewRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    agent = CodeReviewAgent(db)
    return await agent.review(data)


@router.post("/debugging", response_model=DebugResponse)
async def ai_debug(data: DebugRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    agent = DebuggingAgent(db)
    return await agent.debug(data)


@router.get("/recommendations", response_model=RecommendationResponse)
async def ai_recommendations(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    agent = RecommendationAgent(db)
    return await agent.recommend(user.id)


@router.post("/project-mentor", response_model=ProjectMentorResponse)
async def ai_project_mentor(data: ProjectMentorRequest, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    agent = ProjectMentorAgent(db)
    return await agent.mentor(user.id, data)
