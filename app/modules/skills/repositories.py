from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.skills.models import Skill, SkillAssessment, SkillDependency, StudentSkill


class SkillRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        result = await self.db.execute(select(Skill).where(Skill.id == skill_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Skill | None:
        result = await self.db.execute(select(Skill).where(Skill.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, data) -> Skill:
        skill = Skill(**data.model_dump())
        self.db.add(skill)
        await self.db.flush()
        return skill

    async def update(self, skill: Skill, data) -> Skill:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(skill, field, value)
        await self.db.flush()
        return skill

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Skill]:
        result = await self.db.execute(select(Skill).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def list_by_category(self, category: str) -> list[Skill]:
        result = await self.db.execute(select(Skill).where(Skill.category == category))
        return list(result.scalars().all())


class StudentSkillRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_skill(self, user_id: UUID, skill_id: UUID) -> StudentSkill | None:
        result = await self.db.execute(
            select(StudentSkill).where(
                StudentSkill.user_id == user_id,
                StudentSkill.skill_id == skill_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[StudentSkill]:
        result = await self.db.execute(
            select(StudentSkill).where(StudentSkill.user_id == user_id)
        )
        return list(result.scalars().all())

    async def upsert(self, user_id: UUID, skill_id: UUID, score: float) -> StudentSkill:
        record = await self.get_by_user_and_skill(user_id, skill_id)
        if record:
            record.mastery_score = (record.mastery_score * record.assessments_count + score) / (record.assessments_count + 1)
            record.assessments_count += 1
            record.proficiency = _score_to_proficiency(record.mastery_score)
        else:
            record = StudentSkill(
                user_id=user_id,
                skill_id=skill_id,
                mastery_score=score,
                assessments_count=1,
                proficiency=_score_to_proficiency(score),
            )
            self.db.add(record)
        await self.db.flush()
        return record


class SkillAssessmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, data) -> SkillAssessment:
        assessment = SkillAssessment(user_id=user_id, **data.model_dump())
        self.db.add(assessment)
        await self.db.flush()
        return assessment

    async def list_by_user(self, user_id: UUID) -> list[SkillAssessment]:
        result = await self.db.execute(
            select(SkillAssessment).where(SkillAssessment.user_id == user_id)
        )
        return list(result.scalars().all())


class SkillDependencyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data) -> SkillDependency:
        dep = SkillDependency(**data.model_dump())
        self.db.add(dep)
        await self.db.flush()
        return dep

    async def list_prerequisites(self, skill_id: UUID) -> list[SkillDependency]:
        result = await self.db.execute(
            select(SkillDependency).where(SkillDependency.skill_id == skill_id)
        )
        return list(result.scalars().all())


def _score_to_proficiency(score: float):
    from app.shared.enums import ProficiencyLevel
    if score >= 0.9:
        return ProficiencyLevel.EXPERT
    if score >= 0.75:
        return ProficiencyLevel.ADVANCED
    if score >= 0.5:
        return ProficiencyLevel.INTERMEDIATE
    if score >= 0.25:
        return ProficiencyLevel.BEGINNER
    return ProficiencyLevel.NONE
