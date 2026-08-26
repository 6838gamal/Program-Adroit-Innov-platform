import httpx

from app.core.config import settings
from app.core.exceptions import CodeExecutionError
from app.core.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_LANGUAGES = {"python"}


class CodeExecutionService:
    def __init__(self, db=None):
        self.db = db

    async def execute(
        self,
        code: str,
        language: str = "python",
        stdin: str | None = None,
        expected_output: str | None = None,
    ) -> dict:
        if language not in SUPPORTED_LANGUAGES:
            raise CodeExecutionError(f"Language '{language}' is not supported")

        payload = {
            "code": code,
            "language": language,
            "stdin": stdin,
            "expected_output": expected_output,
            "timeout": settings.RUNNER_TIMEOUT,
            "memory_limit": settings.RUNNER_MEMORY_LIMIT,
            "cpu_limit": settings.RUNNER_CPU_LIMIT,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    settings.RUNNER_URL,
                    json=payload,
                    timeout=settings.RUNNER_TIMEOUT + 5,
                )
        except httpx.ConnectError:
            logger.warning("runner_unavailable", runner_url=settings.RUNNER_URL)
            return {
                "passed": False,
                "output": "",
                "error": "Code runner service is not available",
                "execution_time_ms": None,
            }

        if resp.status_code != 200:
            raise CodeExecutionError(f"Runner returned status {resp.status_code}")

        result = resp.json()
        if expected_output is not None:
            actual = (result.get("output") or "").strip()
            expected = expected_output.strip()
            result["passed"] = actual == expected
        return result

    async def execute_raw(self, code: str, language: str = "python", stdin: str | None = None) -> dict:
        return await self.execute(code, language, stdin, expected_output=None)
