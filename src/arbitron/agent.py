from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent

from .models import Agent as AgentConfig
from .models import Comparison, Item


class ComparisonResult(BaseModel):
    choice: Literal["item_a", "item_b"]
    reasoning: str | None = None


class ArbitronAgent:
    def __init__(self, config: AgentConfig):
        self.config = config

    async def compare(
        self,
        description: str,
        item_a: Item,
        item_b: Item,
        include_reasoning: bool = False,
    ) -> Comparison:
        """Run a comparison between two items."""

        base_prompt = f"""
        You are {self.config.id}. {self.config.prompt}

        You will be given two items to compare for a specific task.
        Your goal is to compare the two items and choose which one is better according to the evaluation criteria of the task.
        """

        if include_reasoning:
            base_prompt += "Provide a brief reasoning."

        # Create agent with appropriate configuration
        agent = Agent(
            model=self.config.model,
            system_prompt=base_prompt,
            output_type=ComparisonResult,
        )

        user_prompt = f"""
        Task: {description}

        Compare these two items:

        <item_a>
        ID: {item_a.id}
        {f"Description: {item_a.description}" if item_a.description else ""}
        </item_a>

        <item_b>
        ID: {item_b.id}
        {f"Description: {item_b.description}" if item_b.description else ""}
        </item_b>

        Choose which item is better for the given task.
        You MUST respond with either "item_a" or "item_b" as the choice.
        """

        result = await agent.run(user_prompt)

        winner_item = result.output.choice
        winner = item_a.id if winner_item == "item_a" else item_b.id

        return Comparison(
            agent_id=self.config.id,
            item_a=item_a.id,
            item_b=item_b.id,
            winner=winner,
            rationale=result.output.reasoning if include_reasoning else None,
            created_at=datetime.now(timezone.utc),
        )
