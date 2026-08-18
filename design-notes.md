# Design Notes

## Core principle

Use AI for reasoning and deterministic software for control, validation and safety.

## Agent boundaries

1. Planning: risk, coverage, ambiguities.
2. Generation: executable tests and test data.
3. Triage: failure classification, root cause, severity and ownership.

Execution is deliberately deterministic and is not an AI agent.

## State

The demo uses JSON state so it is easy to inspect. Production should use Postgres for workflow metadata and object storage for execution artifacts.

## Safety

Artifacts are treated as untrusted data. Generated tests are validated before execution. Docker mode adds resource limits, a read-only filesystem, a temporary filesystem and a restricted network configuration.

## Evaluation

Recommended evaluation set: labeled historical failures with ground truth classes REAL_BUG, FLAKY, ENVIRONMENT, INVALID_TEST and DUPLICATE. Measure precision, recall, false-positive rate, duplicate clustering quality, requirement coverage and mutation score.
