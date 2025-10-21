from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    id: str
    description: str | None = None


class Juror(BaseModel):
    id: str
    instructions: str | None = None
    model: str | None = "openai:gpt-5-nano"
    agent: Any = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ComparisonChoice(str, Enum):
    item_a = "item_a"
    item_b = "item_b"


class Comparison(BaseModel):
    juror_id: str
    item_a: str
    item_b: str
    winner: str
    created_at: datetime
    cost: Decimal | None = None
