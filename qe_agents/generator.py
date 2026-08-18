from .llm import LLM
from .models import GeneratedTest, TestPlan


class TestGenerationAgent:
    def __init__(self, llm: LLM):
        self.llm = llm

    def run(self, plan: TestPlan) -> list[GeneratedTest]:
        # The mock implementation intentionally generates executable pytest code.
        tests = [
            GeneratedTest(
                id="T-PWD-001", scenario_id="PWD-001", filename="test_valid_reset.py",
                code='''import os\nimport requests\n\ndef test_valid_reset():\n    base = os.getenv("QE_SUT_URL", "http://127.0.0.1:8000")\n    r = requests.post(base + "/reset-password", json={"token":"valid-token","password":"NewPassword123"})\n    assert r.status_code == 200\n'''
            ),
            GeneratedTest(
                id="T-PWD-002", scenario_id="PWD-002", filename="test_expired_token.py",
                code='''import os\nimport requests\n\ndef test_expired_token():\n    base = os.getenv("QE_SUT_URL", "http://127.0.0.1:8000")\n    r = requests.post(base + "/reset-password", json={"token":"expired-token","password":"NewPassword123"})\n    assert r.status_code == 400\n'''
            ),
            GeneratedTest(
                id="T-PWD-003", scenario_id="PWD-003", filename="test_invalid_token.py",
                code='''import os\nimport requests\n\ndef test_invalid_token():\n    base = os.getenv("QE_SUT_URL", "http://127.0.0.1:8000")\n    r = requests.post(base + "/reset-password", json={"token":"not-a-real-token","password":"NewPassword123"})\n    assert r.status_code == 400\n'''
            ),
            GeneratedTest(
                id="T-PWD-004", scenario_id="PWD-004", filename="test_password_boundary.py",
                code='''import os\nimport requests\n\ndef test_password_too_short():\n    base = os.getenv("QE_SUT_URL", "http://127.0.0.1:8000")\n    r = requests.post(base + "/reset-password", json={"token":"valid-token","password":"short"})\n    assert r.status_code == 400\n'''
            ),
        ]
        return tests
