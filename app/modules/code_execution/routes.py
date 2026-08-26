from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import CurrentUser
from app.modules.code_execution.services import CodeExecutionService

router = APIRouter(prefix="/code-execution", tags=["code-execution"])


class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: str | None = None
    expected_output: str | None = None


@router.post("/run")
async def run_code(data: ExecuteRequest, user: CurrentUser):
    service = CodeExecutionService()
    result = await service.execute(
        code=data.code,
        language=data.language,
        stdin=data.stdin,
        expected_output=data.expected_output,
    )
    return result
