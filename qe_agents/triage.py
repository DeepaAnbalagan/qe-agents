from .llm import LLM
from .models import TestPlan, TestRun, TriagedDefect


class DefectTriageAgent:
    def __init__(self, llm: LLM):
        self.llm = llm

    def run(self, plan: TestPlan, run: TestRun) -> TriagedDefect:
        if run.final_status == "FLAKY":
            mock = TriagedDefect(
                classification="FLAKY", severity="P2", priority="P2", confidence=0.92,
                title="Potential flaky test failure", root_cause="The test passed on a subsequent retry.",
                evidence=["At least one execution failed and a later retry passed."], likely_owner="QE",
            )
        elif run.final_status == "FAILED":
            evidence = [a.stderr[-1200:] for a in run.attempts if a.stderr]
            mock = TriagedDefect(
                classification="REAL_BUG", severity="P1", priority="P1", confidence=0.90,
                title="Password reset accepts an expired token",
                root_cause="The system under test returns success for expired-token requests; the expected contract is HTTP 400.",
                evidence=evidence or ["PWD-002 failed consistently across retries."],
                likely_owner="Authentication team",
            )
        else:
            mock = TriagedDefect(
                classification="INVALID_TEST", severity="P3", priority="P3", confidence=0.85,
                title="No actionable defect detected", root_cause="The execution did not produce a deterministic application failure.",
                evidence=[run.final_status], likely_owner="QE",
            )

        return self.llm.structured(
            "You are a senior QE triage engineer. Classify the failure using the supplied evidence. Prefer precision over speculation. Never invent a root cause that is not supported by evidence.",
            run.model_dump_json(), TriagedDefect, mock,
        )
