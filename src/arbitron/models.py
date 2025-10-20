from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent as PydanticAgent

class Item(BaseModel):
    id: str
    description: str | None = None


class Juror(BaseModel):
    id: str
    instructions: str | None = None
    model: str | None = "openai:gpt-5-nano"
    agent: Any = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Comparison(BaseModel):
    juror_id: str
    item_a: str
    item_b: str
    winner: str
    rationale: str | None = None
    created_at: datetime


class ComparisonDecision(BaseModel):
    choice: Literal["item_a", "item_b"]
    reasoning: str | None = None
