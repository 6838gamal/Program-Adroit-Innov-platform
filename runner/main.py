import resource
import subprocess
import tempfile
import os

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Code Runner Sandbox")

SUPPORTED_LANGUAGES = {
    "python": {"ext": ".py", "cmd": ["python3"]},
}


class RunRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: str | None = None
    expected_output: str | None = None
    timeout: int = 15
    memory_limit: str = "256m"
    cpu_limit: str = "1.0"


@app.post("/run")
async def run_code(req: RunRequest):
    lang = SUPPORTED_LANGUAGES.get(req.language)
    if not lang:
        return {"passed": False, "output": "", "error": f"Unsupported language: {req.language}", "execution_time_ms": None}

    with tempfile.NamedTemporaryFile(suffix=lang["ext"], delete=False, mode="w") as f:
        f.write(req.code)
        f.flush()
        filepath = f.name

    try:
        mem_bytes = int(req.memory_limit.replace("m", "")) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

        stdin_data = req.stdin.encode() if req.stdin else None
        cmd = lang["cmd"] + [filepath]

        import time
        start = time.monotonic()
        proc = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            timeout=req.timeout,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        output = proc.stdout.decode("utf-8", errors="replace")
        error = proc.stderr.decode("utf-8", errors="replace") if proc.returncode != 0 else None

        passed = None
        if req.expected_output is not None:
            passed = output.strip() == req.expected_output.strip()

        return {
            "passed": passed,
            "output": output,
            "error": error,
            "execution_time_ms": elapsed_ms,
            "exit_code": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "", "error": "Execution timed out", "execution_time_ms": None}
    except Exception as e:
        return {"passed": False, "output": "", "error": str(e), "execution_time_ms": None}
    finally:
        os.unlink(filepath)
