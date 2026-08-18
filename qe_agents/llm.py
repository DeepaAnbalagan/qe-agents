from __future__ import annotations
import json
import os
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLM:
    def __init__(self):
        self.mode = os.getenv("QE_LLM_MODE", "mock").lower()
        self.model = os.getenv("QE_MODEL", "gpt-5.6")
        self.client = None
        if self.mode == "openai":
            from openai import OpenAI
            self.client = OpenAI()

    def structured(self, system: str, user: str, schema: Type[T], mock_value: T) -> T:
        if self.mode != "openai":
            return mock_value

        # Keep the model response contract simple for this assessment prototype.
        # Production should use Structured Outputs / JSON Schema and validate again server-side.
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = response.output_text
        data = json.loads(text)
        return schema.model_validate(data)

    def text(self, system: str, user: str, mock_value: str) -> str:
        if self.mode != "openai":
            return mock_value
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.output_text
