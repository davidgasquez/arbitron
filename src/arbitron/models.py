"""Pydantic models for Arbitron."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Item(BaseModel):
    """Represents an item to be ranked."""

    name: str = Field(..., description="Unique identifier for the item")
    description: str | None = Field(
        None, description="Optional description of the item"
    )


class Competition(BaseModel):
    """Represents a competition/contest configuration."""

    name: str = Field(..., description="Name of the competition")
    description: str = Field(..., description="Description and evaluation criteria")
    items: list[Item] = Field(..., description="Items to be ranked")


class ComparisonResult(BaseModel):
    """Result of a single pairwise comparison by an agent."""

    item_a: str = Field(..., description="First item in comparison")
    item_b: str = Field(..., description="Second item in comparison")
    winner: str = Field(..., description="Chosen item (must be item_a or item_b)")
    reasoning: str = Field(..., description="Agent's reasoning for the choice")
    agent_id: str = Field(
        ..., description="Identifier of the agent making the decision"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the comparison was made",
    )

    @model_validator(mode="after")
    def validate_winner(self) -> "ComparisonResult":
        """Ensure winner is exactly one of the two items being compared."""
        if self.winner not in [self.item_a, self.item_b]:
            raise ValueError(
                f"Winner '{self.winner}' must be exactly one of: "
                f"'{self.item_a}' or '{self.item_b}'"
            )
        return self


class RankingResult(BaseModel):
    """Final ranking results from a competition."""

    competition: Competition = Field(..., description="The competition that was run")
    ranking: list[str] = Field(..., description="Items in ranked order (best to worst)")
    scores: dict[str, float] = Field(
        ..., description="Bradley-Terry scores for each item"
    )
    comparisons: list[ComparisonResult] = Field(
        ..., description="All pairwise comparisons made"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
