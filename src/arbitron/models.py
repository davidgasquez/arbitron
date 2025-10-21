from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    id: str
    payload: Mapping[str, Any] | BaseModel | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def prompt_payload(self) -> dict[str, Any]:
        """Return a JSON-serializable mapping ready for prompt rendering."""
        data: dict[str, Any] = {}
        if self.payload is not None:
            data = self._serialise_payload(self.payload)

        data["id"] = self.id
        return data

    @staticmethod
    def _serialise_payload(payload: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
        converted = Item._convert(payload)
        if isinstance(converted, Mapping):
            return {str(key): value for key, value in converted.items()}

        msg = "Item payload must serialise to a mapping"
        raise TypeError(msg)

    @staticmethod
    def _convert(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")

        if isinstance(value, Mapping):
            return {str(key): Item._convert(val) for key, val in value.items()}

        if isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            return [Item._convert(item) for item in value]

        return value


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
