from __future__ import annotations
import json
from pathlib import Path
from .models import WorkflowState


class StateStore:
    def __init__(self, directory: str = ".qe-state"):
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=True)

    def save(self, state: WorkflowState) -> None:
        (self.directory / f"{state.workflow_id}.json").write_text(state.model_dump_json(indent=2))

    def load(self, workflow_id: str) -> WorkflowState:
        return WorkflowState.model_validate_json((self.directory / f"{workflow_id}.json").read_text())
