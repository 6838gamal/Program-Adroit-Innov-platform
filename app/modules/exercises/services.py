from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.exercises.models import Exercise, Submission
from app.modules.exercises.repositories import (
    ExerciseRepository,
    ExerciseTestRepository,
    SubmissionRepository,
)
from app.modules.exercises.schemas import (
    ExerciseCreate,
    ExerciseTestCreate,
    ExerciseUpdate,
    SubmissionCreate,
    SubmissionResultRead,
)
from app.modules.skills.services import SkillService
from app.modules.skills.schemas import SkillAssessmentCreate
from app.shared.enums import ExerciseType, SubmissionStatus


class ExerciseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.exercise_repo = ExerciseRepository(db)
        self.test_repo = ExerciseTestRepository(db)
        self.submission_repo = SubmissionRepository(db)
        self.skill_service = SkillService(db)

    async def create_exercise(self, data: ExerciseCreate) -> Exercise:
        return await self.exercise_repo.create(data)

    async def get_exercise(self, exercise_id: UUID) -> Exercise:
        exercise = await self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise NotFoundError("Exercise not found")
        return exercise

    async def update_exercise(self, exercise_id: UUID, data: ExerciseUpdate) -> Exercise:
        exercise = await self.get_exercise(exercise_id)
        return await self.exercise_repo.update(exercise, data)

    async def delete_exercise(self, exercise_id: UUID) -> None:
        exercise = await self.get_exercise(exercise_id)
        await self.exercise_repo.delete(exercise)

    async def list_exercises(self) -> list[Exercise]:
        return await self.exercise_repo.list_all()

    async def list_by_lesson(self, lesson_id: UUID) -> list[Exercise]:
        return await self.exercise_repo.list_by_lesson(lesson_id)

    async def add_test(self, exercise_id: UUID, data: ExerciseTestCreate) -> None:
        await self.get_exercise(exercise_id)
        await self.test_repo.create(exercise_id, data)

    async def list_tests(self, exercise_id: UUID) -> list:
        return await self.test_repo.list_by_exercise(exercise_id)

    async def submit(
        self, user_id: UUID, data: SubmissionCreate
    ) -> tuple[Submission, list[SubmissionResultRead]]:
        exercise = await self.get_exercise(data.exercise_id)
        submission = await self.submission_repo.create(
            user_id, data.exercise_id, data.code, data.answer
        )

        if exercise.exercise_type == ExerciseType.CODE:
            results = await self._evaluate_code(submission, exercise)
        else:
            results = await self._evaluate_non_code(submission, exercise)

        all_passed = all(r.passed for r in results) if results else False
        submission.status = SubmissionStatus.PASSED if all_passed else SubmissionStatus.FAILED
        submission.score = exercise.points if all_passed else 0
        await self.db.flush()

        if all_passed and exercise.skill_id:
            await self.skill_service.record_assessment(
                user_id,
                SkillAssessmentCreate(
                    skill_id=exercise.skill_id,
                    score=1.0,
                    source="exercise",
                    exercise_id=exercise.id,
                ),
            )

        result_reads = [SubmissionResultRead.model_validate(r) for r in results]
        return submission, result_reads

    async def list_user_submissions(self, user_id: UUID) -> list[Submission]:
        return await self.submission_repo.list_by_user(user_id)

    async def list_exercise_submissions(self, exercise_id: UUID) -> list[Submission]:
        return await self.submission_repo.list_by_exercise(exercise_id)

    async def _evaluate_code(self, submission: Submission, exercise: Exercise) -> list:
        from app.modules.code_execution.services import CodeExecutionService

        runner = CodeExecutionService(self.db)
        tests = await self.test_repo.list_by_exercise(exercise.id)
        results = []
        for test in tests:
            exec_result = await runner.execute(
                code=submission.code or "",
                language=exercise.language,
                stdin=test.input_data,
                expected_output=test.expected_output,
            )
            from app.modules.exercises.models import SubmissionResult

            result = SubmissionResult(
                submission_id=submission.id,
                test_name=test.test_name,
                passed=exec_result.get("passed", False),
                output=exec_result.get("output", ""),
                expected=test.expected_output,
                error=exec_result.get("error"),
                execution_time_ms=exec_result.get("execution_time_ms"),
            )
            self.db.add(result)
            results.append(result)
        await self.db.flush()
        return results

    async def _evaluate_non_code(self, submission: Submission, exercise: Exercise) -> list:
        from app.modules.exercises.models import SubmissionResult

        is_correct = submission.answer == exercise.correct_answer
        result = SubmissionResult(
            submission_id=submission.id,
            test_name="answer_check",
            passed=is_correct,
            output=submission.answer,
            expected=exercise.correct_answer,
        )
        self.db.add(result)
        await self.db.flush()
        return [result]
