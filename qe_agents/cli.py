from __future__ import annotations
import argparse
import json
from pathlib import Path
from .orchestrator import QEOrchestrator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--executor", choices=["docker", "local"], default="docker")
    args = parser.parse_args()

    artifact = Path(args.artifact).read_text()
    state = QEOrchestrator(args.executor).run(artifact)
    report_path = state.report_path
    print(f"Workflow: {state.workflow_id}")
    print(f"Status: {state.test_run.final_status if state.test_run else 'NOT_RUN'}")
    if state.triaged_defect:
        print(f"Triage: {state.triaged_defect.classification} / {state.triaged_defect.severity} / {state.triaged_defect.confidence:.0%}")
    if report_path:
        print(f"HTML report: {report_path}")
    else:
        print("HTML report: not generated")


if __name__ == "__main__":
    main()
