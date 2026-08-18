from __future__ import annotations
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from .models import GeneratedTest, TestAttempt, TestRun


class TestExecutor:
    def __init__(self, mode: str = "docker", retries: int = 2):
        self.mode = mode
        self.retries = retries

    def run(self, tests: list[GeneratedTest]) -> TestRun:
        if self.mode == "docker" and shutil.which("docker"):
            return self._docker(tests)
        return self._local(tests)

    def _local(self, tests: list[GeneratedTest]) -> TestRun:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for t in tests:
                (root / t.filename).write_text(t.code)
            attempts: list[TestAttempt] = []
            for i in range(1, self.retries + 2):
                p = subprocess.run(
                    [os.environ.get("PYTHON", sys.executable), "-m", "pytest", "-q"],
                    cwd=root, capture_output=True, text=True, timeout=30, env={**os.environ, "QE_SUT_URL": "http://127.0.0.1:8000"},
                )
                attempts.append(TestAttempt(attempt=i, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
                if p.returncode == 0:
                    break
            return self._classify(attempts)

    def _docker(self, tests: list[GeneratedTest]) -> TestRun:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for t in tests:
                (root / t.filename).write_text(t.code)
            attempts: list[TestAttempt] = []
            for i in range(1, self.retries + 2):
                cmd = [
                    "docker", "run", "--rm",
                    "--network=bridge",
                    "-e", "QE_SUT_URL=http://host.docker.internal:8000",
                    "--add-host=host.docker.internal:host-gateway",
                    "--cpus=1", "--memory=512m",
                    "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
                    "-v", f"{root}:/tests:ro",
                    "python:3.12-slim",
                    "sh", "-c",
                    "pip install -q pytest requests && cd /tests && pytest -q",
                ]
                try:
                    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    attempts.append(TestAttempt(attempt=i, exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr))
                except subprocess.TimeoutExpired as exc:
                    attempts.append(TestAttempt(attempt=i, exit_code=124, stdout=exc.stdout or "", stderr="sandbox timeout"))
                if attempts[-1].exit_code == 0:
                    break
            return self._classify(attempts)

    @staticmethod
    def _classify(attempts: list[TestAttempt]) -> TestRun:
        codes = [a.exit_code for a in attempts]
        if codes[-1] == 0 and any(c != 0 for c in codes[:-1]):
            status = "FLAKY"
        elif codes[-1] == 0:
            status = "PASSED"
        elif any(c == 124 for c in codes):
            status = "ERROR"
        else:
            status = "FAILED"
        return TestRun(attempts=attempts, final_status=status)
