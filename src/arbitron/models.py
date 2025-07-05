"""Pydantic models for Arbitron."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Represents an item to be ranked."""

    name: str = Field(..., description="Unique identifier for the item")
    description: Optional[str] = Field(
        None, description="Optional description of the item"
    )


class Competition(BaseModel):
    """Represents a competition/contest configuration."""

    name: str = Field(..., description="Name of the competition")
    description: str = Field(..., description="Description and evaluation criteria")
    items: List[Item] = Field(..., description="Items to be ranked")


class ComparisonResult(BaseModel):
    """Result of a single pairwise comparison by an agent."""

    item_a: str = Field(..., description="First item in comparison")
    item_b: str = Field(..., description="Second item in comparison")
    winner: str = Field(..., description="Chosen item (must be item_a or item_b)")
    reasoning: str = Field(..., description="Agent's reasoning for the choice")
    agent_id: str = Field(
        ..., description="Identifier of the agent making the decision"
    )


class RankingResult(BaseModel):
    """Final ranking results from a competition."""

    competition: Competition = Field(..., description="The competition that was run")
    ranking: List[str] = Field(..., description="Items in ranked order (best to worst)")
    scores: Dict[str, float] = Field(
        ..., description="Bradley-Terry scores for each item"
    )
    comparisons: List[ComparisonResult] = Field(
        ..., description="All pairwise comparisons made"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
