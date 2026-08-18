# QE Agents — Running Instructions

## Overview

This document covers detailed instructions for running **QE Agents** in two modes:
- **Real LLM Mode** (default, production submission)
- **Mock LLM Mode** (demo/rehearsal, local development only)

The QE Agents system is an end-to-end assessment prototype that takes a product artifact and generates a risk-based test plan, executable tests, validates and executes them in a sandbox, and triages any defects found.

---

## System Requirements

### Prerequisites

- **Python 3.9+** (tested with Python 3.11)
- **pip** (Python package manager)
- **Docker** (only if using `--executor docker` for sandboxed execution)
- **Terminal/Shell** (bash, zsh, or equivalent)

### Supported Operating Systems

- macOS
- Linux
- Windows (with WSL2 or Git Bash recommended)

---

## Project Structure

```
qe-agents/
├── README.md                    # Project overview
├── RUNNING_INSTRUCTIONS.md      # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment configuration
├── pytest.ini                   # Test runner configuration
├── docker-compose.yml           # Docker setup for demo API
│
├── qe_agents/                   # Main package
│   ├── models.py               # Data models (Pydantic schemas)
│   ├── llm.py                  # LLM adapter (real/mock modes)
│   ├── security.py             # Artifact sanitization
│   ├── planner.py              # Planning agent
│   ├── generator.py            # Test generation agent
│   ├── validator.py            # Deterministic validation
│   ├── executor.py             # Sandbox/local execution
│   ├── triage.py               # Triage agent
│   ├── state.py                # Workflow state management
│   ├── report.py               # HTML report generation
│   ├── orchestrator.py         # Main workflow orchestrator
│   └── cli.py                  # Command-line interface
│
├── demo_api/                    # Deliberately buggy FastAPI system under test
│   └── app.py
│
├── sample_artifacts/            # Example test artifacts
│   └── password_reset.md        # Sample requirement
│
└── tests/                       # Unit tests
```

---

## Quick Start

### Step 1: Clone/Navigate to Repository

```bash
cd /Users/admain/Documents/agents/qe-agents
```

### Step 2: Create Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 3: Choose Your Mode

Continue with either **Real LLM Mode** or **Mock LLM Mode** below.

---

## Mode 1: Real LLM Mode (Submission/Production)

Real LLM mode uses OpenAI's GPT API to power the planning, generation, and triage agents. This is the **default and required mode for production submission**.

### Configuration

#### 1. Create Environment File

```bash
cp .env.example .env
```

#### 2. Set Your OpenAI API Key

Edit `.env` and add your OpenAI API key:

```bash
# Submission mode: use the real model by default.
OPENAI_API_KEY=sk-proj-your_actual_key_here
QE_LLM_MODE=openai
QE_MODEL=gpt-5.6

# Local system under test
QE_SUT_URL=http://127.0.0.1:8000
```

**Important:** 
- `OPENAI_API_KEY` is **required** for real mode. The application will fail fast if it is missing.
- Never commit `.env` to version control (it's already in `.gitignore`).
- You can generate API keys at [OpenAI Platform](https://platform.openai.com/account/api-keys).

### Running the Workflow

#### Terminal 1: Start the System Under Test (Demo API)

```bash
source .venv/bin/activate
uvicorn demo_api.app:app --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### Terminal 2: Run the QE Workflow

**Option A: Local Execution** (runs tests on your machine)

```bash
source .venv/bin/activate
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor local
```

**Option B: Docker Sandboxed Execution** (runs tests in isolated container)

```bash
source .venv/bin/activate
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor docker
```

### Understanding the Workflow

The CLI executes the following steps:

```
1. Artifact Ingestion & Sanitization
   ↓
2. LLM Planning Agent (generates risk-based test plan)
   ↓
3. LLM Test Generation Agent (generates executable pytest code)
   ↓
4. Deterministic Validation (syntax, policy, security checks)
   ↓
5. Test Execution (local or Docker sandbox)
   ↓
6. Retry & Flaky Classification (if tests fail)
   ↓
7. LLM Triage Agent (classifies defects with root cause)
   ↓
8. HTML Report Generation
```

### Output and Report

The CLI prints a summary:

```
Workflow: ab12cd34
LLM mode: openai
Status: FAILED
Triage: REAL_BUG / P1 / 92%
HTML report: reports/qe-report-ab12cd34.html
```

Open the HTML report in your browser:

```bash
open reports/qe-report-ab12cd34.html
```

The report includes:
- Test plan (scenarios, risks, priorities)
- Generated test code
- Test execution results and logs
- Defect triage analysis with confidence scores
- Root cause analysis and evidence

---

## Mode 2: Mock LLM Mode (Demo/Development Only)

Mock mode replaces LLM calls with deterministic, pre-built responses. Use this for:
- Local development and testing
- Repeatable demonstrations
- Understanding the workflow without API costs
- Unit testing
- Debugging specific components

**Important:** Mock mode is **not** suitable for submission or production use. It must be **explicitly enabled**.

### Configuration

Mock mode requires only one environment variable:

```bash
QE_LLM_MODE=mock
```

No API key is required.

### Running the Workflow

#### Terminal 1: Start the System Under Test (Demo API)

```bash
source .venv/bin/activate
uvicorn demo_api.app:app --port 8000
```

#### Terminal 2: Run with Mock LLM

**Option A: Local Execution**

```bash
source .venv/bin/activate
QE_LLM_MODE=mock \
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor local
```

**Option B: Docker Sandboxed Execution**

```bash
source .venv/bin/activate
QE_LLM_MODE=mock \
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor docker
```

### Mock Mode Behavior

In mock mode:
- The planning agent returns a fixed `TestPlan` covering password reset scenarios
- The generation agent returns fixed, validated test code
- The triage agent returns a fixed `TriagedDefect` classification
- All responses are instant (no API latency)
- Results are **deterministic** — same output every run

This determinism makes mock mode ideal for:
- Testing orchestrator and validation logic
- Verifying workflow state transitions
- Rehearsing demonstrations
- Iterating on report generation

---

## Using Custom Artifacts

To test with your own requirements:

```bash
./.venv/bin/python -m qe_agents.cli \
  --artifact path/to/your/artifact.md \
  --executor local
```

The artifact should be a markdown file describing:
- Product feature requirements
- API endpoints or user flows
- Acceptance criteria
- Known constraints or limitations

**Security Note:** Artifacts are sanitized before entering agent prompts to mitigate prompt injection. This is defense-in-depth; always treat artifacts as untrusted input.

---

## Common Environment Variables

| Variable | Mode | Default | Required | Description |
|----------|------|---------|----------|-------------|
| `QE_LLM_MODE` | Both | `openai` | No | Set to `mock` for demo mode; `openai` for production |
| `OPENAI_API_KEY` | Real | N/A | **Yes** (real mode only) | Your OpenAI API key (starts with `sk-`) |
| `QE_MODEL` | Real | `gpt-5.6` | No | OpenAI model name (e.g., `gpt-4-turbo`, `gpt-5.6`) |
| `QE_SUT_URL` | Both | `http://127.0.0.1:8000` | No | System under test URL |

### Loading Environment Variables

#### Using `.env` File

Create a `.env` file in the repository root (see `.env.example`), then environment variables are automatically loaded via `python-dotenv`.

#### Using Command Line

```bash
OPENAI_API_KEY=sk-proj-xxx QE_LLM_MODE=openai \
./.venv/bin/python -m qe_agents.cli --artifact <artifact> --executor local
```

#### Using Shell Export

```bash
export OPENAI_API_KEY=sk-proj-xxx
export QE_LLM_MODE=openai
./.venv/bin/python -m qe_agents.cli --artifact <artifact> --executor local
```

---

## LLM Mode Details

### Real Mode (openai)

**`llm.py` Implementation:**

```python
class LLM:
    def __init__(self) -> None:
        self.mode = os.getenv("QE_LLM_MODE", "openai").lower()
        self.model = os.getenv("QE_MODEL", "gpt-5.6")
        self.client = None

        if self.mode == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is required in real LLM mode. "
                    "Set QE_LLM_MODE=mock only when you intentionally want the local demo."
                )
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
```

**Agent Calls:**

All agent reasoning uses the OpenAI Responses API with structured JSON output:

```python
def structured(self, system: str, user: str, schema: Type[T], mock_value: T) -> T:
    assert self.client is not None
    response = self.client.responses.create(
        model=self.model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": schema.__name__,
                "strict": True,
                "schema": schema.model_json_schema(),
            }
        },
    )
    return schema.model_validate_json(response.output_text)
```

**Key Features:**
- Strict JSON Schema validation
- Double validation: OpenAI + Pydantic
- Fails fast if API key is missing
- Real reasoning from LLM

### Mock Mode

**`llm.py` Implementation:**

```python
def structured(self, system: str, user: str, schema: Type[T], mock_value: T) -> T:
    if self.mode == "mock":
        return mock_value
    # ... (real mode handling)
```

**Agent Calls:**

Mock responses are returned instantly without API calls:
- `planner.py`: Returns a fixed `TestPlan`
- `generator.py`: Returns fixed `GeneratedTests`
- `triage.py`: Returns a fixed `TriagedDefect`

**Key Features:**
- No API calls
- Instant responses
- Deterministic output
- Useful for development and demos
- Must be explicitly enabled

---

## Execution Modes

### Local Execution (`--executor local`)

Tests run directly on your machine using the system Python environment.

```bash
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor local
```

**Advantages:**
- Fast iteration
- Easy debugging
- No Docker overhead

**Disadvantages:**
- No security isolation
- Generated code runs on your machine
- Dependencies must match your environment

### Docker Sandboxed Execution (`--executor docker`)

Tests run in an isolated Docker container with strict resource limits.

```bash
./.venv/bin/python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor docker
```

**Prerequisites:**
- Docker installed and running
- `docker-compose.yml` available

**Sandbox Protections:**
- CPU limits
- Memory limits
- Execution timeout
- Read-only filesystem (except `/tmp`)
- Restricted networking
- No access to host system

**Advantages:**
- Security isolation for generated code
- Reproducible environment
- Prevents accidental damage to host

**Disadvantages:**
- Slower execution (container startup)
- Requires Docker
- Harder to debug

**Recommended:** Use Docker for production assessment; local for development.

---

## Running Tests

### Run Unit Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_validator.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=qe_agents --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting

### Error: "OPENAI_API_KEY is required in real LLM mode"

**Problem:** You're trying to run with the default real LLM mode, but no API key is set.

**Solution:**
1. Check `.env` file has `OPENAI_API_KEY=sk-proj-...`
2. Or run with mock mode: `QE_LLM_MODE=mock python -m qe_agents.cli ...`

### Error: "Connection refused" on port 8000

**Problem:** The demo API (system under test) is not running.

**Solution:**
1. Open a separate terminal
2. Run: `source .venv/bin/activate && uvicorn demo_api.app:app --port 8000`
3. Verify output shows: `Uvicorn running on http://127.0.0.1:8000`

### Error: "Docker daemon is not running"

**Problem:** You're using `--executor docker` but Docker isn't running.

**Solution:**
1. Start Docker Desktop (macOS/Windows) or Docker daemon (Linux)
2. Verify with: `docker ps`
3. Or switch to local execution: `--executor local`

### API rate limits or "429 Too Many Requests"

**Problem:** OpenAI API rate limit exceeded.

**Solution:**
1. Wait 60 seconds before retrying
2. Check your account usage at platform.openai.com
3. Reduce request frequency or upgrade your OpenAI plan
4. Switch to mock mode for testing: `QE_LLM_MODE=mock`

### Tests fail with "ModuleNotFoundError"

**Problem:** Dependencies not installed.

**Solution:**
```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Virtual environment not activating

**Problem:** Shell doesn't recognize `.venv/bin/activate`.

**Solution (macOS/Linux):**
```bash
source .venv/bin/activate  # bash/zsh
```

**Solution (Windows):**
```bash
.venv\Scripts\activate
```

---

## Development Workflow

### Adding a Custom Artifact

1. Create a markdown file in `sample_artifacts/`:
   ```bash
   cat > sample_artifacts/my_feature.md << 'EOF'
   # Feature: User Authentication
   
   ## Requirements
   - Users can log in with email and password
   - Passwords must be at least 12 characters
   - Sessions expire after 30 minutes
   
   ## API Endpoints
   - POST /auth/login (email, password)
   - POST /auth/logout
   EOF
   ```

2. Run the workflow:
   ```bash
   ./.venv/bin/python -m qe_agents.cli \
     --artifact sample_artifacts/my_feature.md \
     --executor local
   ```

### Debugging an Agent

Enable verbose logging by examining `qe_agents/orchestrator.py`:

```python
# Add logging statements to understand agent behavior
import json
print("=== Planning Agent Input ===")
print(json.dumps({"system": system_prompt, "user": user_prompt}, indent=2))
```

Use mock mode for repeatable debugging:
```bash
QE_LLM_MODE=mock python -m qe_agents.cli --artifact <artifact> --executor local
```

### Modifying Validation Rules

Edit `qe_agents/validator.py` to change what test code is allowed. The validator checks:
- Syntax (must be valid Python)
- Imports (must be whitelisted)
- Test structure (must follow pytest conventions)
- Security (blocks dangerous functions)

---

## Report Interpretation

### HTML Report Structure

The generated report includes:

1. **Summary Section**
   - Workflow ID, run timestamp
   - LLM mode and model used
   - Overall status (PASSED/FAILED/ERROR)

2. **Test Plan Section**
   - Generated scenarios with risk/priority labels
   - Identified ambiguities
   - Test coverage analysis

3. **Generated Tests Section**
   - Full pytest code generated by the agent
   - Syntax validation results

4. **Execution Results Section**
   - Per-test pass/fail status
   - Retry attempts and flaky classification
   - Stdout/stderr logs

5. **Triage Section**
   - Defect classification (REAL_BUG, FLAKY, ENVIRONMENT, etc.)
   - Severity and priority (P0-P3)
   - Confidence score (0-100%)
   - Root cause analysis
   - Evidence from test logs
   - Likely owner/team

---

## Performance Tuning

### Speed Up Mock Mode Testing

Mock mode is already instant, but you can skip report generation:

```bash
QE_LLM_MODE=mock python -m qe_agents.cli \
  --artifact sample_artifacts/password_reset.md \
  --executor local \
  --skip-report  # (if supported)
```

### Reduce OpenAI API Costs

1. Use mock mode for development/testing
2. Use smaller models: `QE_MODEL=gpt-4-turbo` (adjust as needed)
3. Batch multiple artifacts into one run
4. Use local executor to avoid Docker container startup

### Parallel Execution

The orchestrator runs agents sequentially for reproducibility. To speed up:
- Use mock mode (instant responses)
- Reduce Docker startup overhead (reuse containers)

---

## Production Checklist

Before submitting with real LLM mode:

- [ ] `.env` contains valid `OPENAI_API_KEY`
- [ ] `QE_LLM_MODE=openai` (or default)
- [ ] Run at least one end-to-end workflow successfully
- [ ] Verify report is generated in `reports/` directory
- [ ] Check for any validation errors in test generation
- [ ] Test with both `--executor local` and `--executor docker`
- [ ] Document any custom artifacts or assumptions
- [ ] Verify Docker is running (if using Docker executor)

---

## Support and Questions

- **README.md** — High-level architecture and quick start
- **design-notes.md** — Design decisions and tradeoffs
- **qe_agents/models.py** — Data model definitions
- **qe_agents/llm.py** — LLM adapter implementation
- **qe_agents/cli.py** — Command-line entry point

---

## License and Attribution

See README.md and project documentation for license information.
