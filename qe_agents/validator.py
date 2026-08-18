from __future__ import annotations
import ast
from .models import GeneratedTest, ValidationResult


class TestValidator:
    BLOCKED = ["os.system", "subprocess.Popen", "subprocess.run", "socket.", "requests.get(\"http://169.254.169.254"]

    def validate(self, tests: list[GeneratedTest]) -> ValidationResult:
        errors: list[str] = []
        for test in tests:
            try:
                ast.parse(test.code)
            except SyntaxError as exc:
                errors.append(f"{test.id}: syntax error: {exc}")
            for token in self.BLOCKED:
                if token in test.code:
                    errors.append(f"{test.id}: blocked operation: {token}")
        return ValidationResult(valid=not errors, errors=errors)
