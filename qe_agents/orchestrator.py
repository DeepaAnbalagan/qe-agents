from __future__ import annotations
import uuid
from .generator import TestGenerationAgent
from .llm import LLM
from .models import Requirement, WorkflowState
from .planner import TestPlanningAgent
from .security import sanitize_artifact
from .state import StateStore
from .triage import DefectTriageAgent
from .validator import TestValidator
from .executor import TestExecutor
from .report import write_html_report


class QEOrchestrator:
    """Deterministic workflow controller; agents do bounded reasoning only."""

    def __init__(self, executor_mode: str = "docker", report_dir: str = "reports"):
        llm = LLM()
        self.planner = TestPlanningAgent(llm)
        self.generator = TestGenerationAgent(llm)
        self.validator = TestValidator()
        self.executor = TestExecutor(executor_mode)
        self.triage = DefectTriageAgent(llm)
        self.store = StateStore()
        self.report_dir = report_dir

    def run(self, artifact: str) -> WorkflowState:
        workflow_id = str(uuid.uuid4())[:8]
        safe_artifact = sanitize_artifact(artifact)
        state = WorkflowState(
            workflow_id=workflow_id,
            artifact=safe_artifact,
            requirement=Requirement(text=safe_artifact),
        )
        self._log(state, "INGEST")

        self._log(state, "PLAN")
        state.test_plan = self.planner.run(state.requirement)
        self.store.save(state)

        self._log(state, "GENERATE")
        state.generated_tests = self.generator.run(state.test_plan)
        self.store.save(state)

        self._log(state, "VALIDATE")
        state.validation = self.validator.validate(state.generated_tests)
        if not state.validation.valid:
            self._log(state, "STOP: validation failed")
            self.store.save(state)
            return state

        self._log(state, "EXECUTE")
        state.test_run = self.executor.run(state.generated_tests)
        self.store.save(state)

        self._log(state, "TRIAGE")
        state.triaged_defect = self.triage.run(state.test_plan, state.test_run)
        self.store.save(state)
        report_path = write_html_report(state, self.report_dir)
        state.report_path = str(report_path)
        self._log(state, f"REPORT: {report_path}")
        self._log(state, "DONE")
        self.store.save(state)
        return state

    @staticmethod
    def _log(state: WorkflowState, message: str) -> None:
        state.audit_log.append(message)
