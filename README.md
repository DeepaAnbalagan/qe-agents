# QE Agents — End-to-End Assessment Prototype

A deliberately small end-to-end implementation for the QE Agents design challenge:

**artifact → risk-based test plan → executable tests → validation → sandboxed execution → triaged defect**

The implementation uses a **deterministic orchestrator**. LLM calls are isolated behind an adapter so the workflow remains predictable and testable.

## What is implemented

- Artifact ingestion and basic prompt-injection sanitization
- Test Planning Agent
- Test Generation Agent
- Deterministic test validation
- Sandboxed test execution with Docker, with a local fallback for demos
- Retry + flaky classification
- Defect Triage Agent
- Persistent JSON workflow state for the demo
- Mock LLM mode so the project runs without an API key
- OpenAI Responses API adapter for real LLM mode
- Deliberately buggy FastAPI system under test

The challenge asks for a working end-to-end slice rather than a production platform, and explicitly allows stubbing parts of the lifecycle. This prototype focuses on one complete vertical slice.

## Architecture

```text
Artifact
   |
   v
Ingestion/Sanitizer
   |
   v
Deterministic Orchestrator
   |
   +--> Planning Agent --------> TestPlan
   |                              |
   +--> Generation Agent --------> Executable Tests
   |                              |
   +--> Validator ----------------+
   |                              |
   +--> Sandbox Executor --------> Test Results
   |                              |
   +--> Triage Agent ------------> Triaged Defect
   |
   +--> JSON State / Artifacts
```

## Quick start

### 1. Create environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the demo API

```bash
uvicorn demo_api.app:app --port 8000
```

The API intentionally contains a password-reset bug: an expired reset token is accepted.

### 3. Run the QE workflow in mock mode

In another terminal:

```bash
python -m qe_agents.cli --artifact sample_artifacts/password_reset.md --executor local
```

This needs no model/API key and demonstrates the complete workflow.

### 4. Run with Docker sandbox

Make sure Docker is running:

```bash
python -m qe_agents.cli --artifact sample_artifacts/password_reset.md --executor docker
```

The executor starts the generated tests inside an ephemeral Python container with CPU/memory limits, timeout, read-only filesystem and a restricted network policy. The test reaches the local demo API through `host.docker.internal`.

### 5. Use a real LLM

Set:

```bash
export OPENAI_API_KEY="..."
export QE_LLM_MODE="openai"
export QE_MODEL="gpt-5.6"
```

Then:

```bash
python -m qe_agents.cli --artifact sample_artifacts/password_reset.md --executor docker
```

The current OpenAI Python SDK supports `client.responses.create(...)` through the Responses API. See the official platform documentation for the current API surface. 

## Project structure

```text
qe-agents/
├── README.md
├── requirements.txt
├── .env.example
├── qe_agents/
│   ├── models.py
│   ├── llm.py
│   ├── security.py
│   ├── planner.py
│   ├── generator.py
│   ├── validator.py
│   ├── executor.py
│   ├── triage.py
│   ├── state.py
│   ├── orchestrator.py
│   └── cli.py
├── demo_api/
│   └── app.py
├── sample_artifacts/
│   └── password_reset.md
└── tests/
    └── test_security.py
```

## Design tradeoffs

### Deterministic orchestration vs autonomous swarm

The orchestrator owns transitions, retries, approvals and execution policy. Agents only reason inside their bounded task. This improves reproducibility and makes failures explainable.

### LLM vs deterministic validation

The model can propose tests, but it cannot bypass syntax, schema and security validation.

### Local execution vs sandbox

Local mode is convenient for development. Docker mode is the intended security boundary for untrusted generated code.

### Recall vs precision

Test generation should favor coverage/recall. Defect creation should favor precision to avoid developer alert fatigue.

### Human-in-the-loop

The prototype surfaces ambiguities. A production system would pause for approval on ambiguous requirements, privileged actions and high-severity defects.

## Important production gaps

This is intentionally not a production platform. Next steps would include:

- Postgres instead of JSON state
- object storage for logs/screenshots/videos
- queue-based execution for parallelism
- stronger container isolation / microVMs
- OIDC/RBAC and secrets management
- audit logging and tracing
- evaluation dataset with labeled failures
- mutation testing and coverage measurement
- historical failure embeddings for triage/deduplication
- policy engine for tool permissions

## HTML triage report

The end-to-end workflow now writes a self-contained HTML report after triage. The CLI prints only the workflow status and the report path. Reports are written to `reports/qe-report-<workflow-id>.html`.

Example:

```bash
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor local
```

Open the generated HTML file in a browser. The report contains the triaged defect, confidence, evidence, test-plan scenarios, ambiguities, validation results, execution attempts, and workflow audit trail.
