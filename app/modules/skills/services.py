from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.skills.models import Skill, StudentSkill
from app.modules.skills.repositories import (
    SkillAssessmentRepository,
    SkillDependencyRepository,
    SkillRepository,
    StudentSkillRepository,
)
from app.modules.skills.schemas import (
    SkillAssessmentCreate,
    SkillCreate,
    SkillDependencyCreate,
    SkillProfile,
    SkillUpdate,
)


class SkillService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.skill_repo = SkillRepository(db)
        self.student_skill_repo = StudentSkillRepository(db)
        self.assessment_repo = SkillAssessmentRepository(db)
        self.dependency_repo = SkillDependencyRepository(db)

    async def create_skill(self, data: SkillCreate) -> Skill:
        existing = await self.skill_repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError("Skill slug already exists")
        return await self.skill_repo.create(data)

    async def get_skill(self, skill_id: UUID) -> Skill:
        skill = await self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise NotFoundError("Skill not found")
        return skill

    async def update_skill(self, skill_id: UUID, data: SkillUpdate) -> Skill:
        skill = await self.get_skill(skill_id)
        return await self.skill_repo.update(skill, data)

    async def list_skills(self) -> list[Skill]:
        return await self.skill_repo.list_all()

    async def record_assessment(self, user_id: UUID, data: SkillAssessmentCreate) -> StudentSkill:
        await self.get_skill(data.skill_id)
        await self.assessment_repo.create(user_id, data)
        return await self.student_skill_repo.upsert(user_id, data.skill_id, data.score)

    async def get_student_skills(self, user_id: UUID) -> list[StudentSkill]:
        return await self.student_skill_repo.list_by_user(user_id)

    async def get_skill_profile(self, user_id: UUID) -> SkillProfile:
        skills = await self.student_skill_repo.list_by_user(user_id)
        strong = [s for s in skills if s.mastery_score >= 0.7]
        weak = [s for s in skills if s.mastery_score < 0.5]
        recommended = await self._recommend_next_skills(user_id, skills)
        return SkillProfile(
            user_id=user_id,
            strong_skills=strong,
            weak_skills=weak,
            recommended_next=recommended,
        )

    async def add_dependency(self, data: SkillDependencyCreate) -> None:
        await self.get_skill(data.skill_id)
        await self.get_skill(data.prerequisite_skill_id)
        await self.dependency_repo.create(data)

    async def get_prerequisites(self, skill_id: UUID) -> list:
        return await self.dependency_repo.list_prerequisites(skill_id)

    async def _recommend_next_skills(self, user_id: UUID, current_skills: list[StudentSkill]) -> list[Skill]:
        mastered_ids = {s.skill_id for s in current_skills if s.mastery_score >= 0.7}
        all_skills = await self.skill_repo.list_all()
        recommended = []
        for skill in all_skills:
            if skill.id in mastered_ids:
                continue
            deps = await self.dependency_repo.list_prerequisites(skill.id)
            if not deps or all(d.prerequisite_skill_id in mastered_ids for d in deps):
                recommended.append(skill)
            if len(recommended) >= 5:
                break
        return recommended
