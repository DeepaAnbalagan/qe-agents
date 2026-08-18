from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Requirement(BaseModel):
    text: str
    source: str = "artifact"


class Scenario(BaseModel):
    id: str
    title: str
    description: str
    risk: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    priority: Literal["P0", "P1", "P2", "P3"]
    type: Literal["positive", "negative", "boundary", "security", "reliability"]


class TestPlan(BaseModel):
    summary: str
    scenarios: list[Scenario]
    ambiguities: list[str] = Field(default_factory=list)


class GeneratedTest(BaseModel):
    id: str
    scenario_id: str
    filename: str
    code: str


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)


class TestAttempt(BaseModel):
    attempt: int
    exit_code: int
    stdout: str
    stderr: str


class TestRun(BaseModel):
    attempts: list[TestAttempt]
    final_status: Literal["PASSED", "FAILED", "FLAKY", "ERROR"]


class TriagedDefect(BaseModel):
    classification: Literal["REAL_BUG", "FLAKY", "ENVIRONMENT", "INVALID_TEST", "DUPLICATE"]
    severity: Literal["P0", "P1", "P2", "P3"]
    priority: Literal["P0", "P1", "P2", "P3"]
    confidence: float = Field(ge=0, le=1)
    title: str
    root_cause: str
    evidence: list[str]
    likely_owner: str
    duplicate_of: Optional[str] = None


class WorkflowState(BaseModel):
    workflow_id: str
    artifact: str
    requirement: Requirement
    test_plan: Optional[TestPlan] = None
    generated_tests: list[GeneratedTest] = Field(default_factory=list)
    validation: Optional[ValidationResult] = None
    test_run: Optional[TestRun] = None
    triaged_defect: Optional[TriagedDefect] = None
    report_path: Optional[str] = None
    audit_log: list[str] = Field(default_factory=list)
