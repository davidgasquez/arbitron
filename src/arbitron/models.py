from datetime import datetime

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    description: str | None = None


class Agent(BaseModel):
    id: str
    prompt: str
    model: str = "openai:gpt-4.1-nano"
    max_calls_per_min: int = 60
    max_tokens: int | None = None


class Comparison(BaseModel):
    agent_id: str
    item_a: str
    item_b: str
    winner: str
    rationale: str | None = None
    created_at: datetime
