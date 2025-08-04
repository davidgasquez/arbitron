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
You are {self.config.id}, an expert evaluation agent.

## Your Role
{self.config.prompt}

## Your Task
You will compare two items and determine which one better fulfills the requirements of a given task.

## Evaluation Process
1. Carefully read and understand the task requirements
2. Analyze each item's characteristics against the task requirements
3. Make an objective comparison based on how well each item meets the requirements
4. Select the item that best fulfills the task

## Important Guidelines
- Be objective and unbiased in your evaluation
- Focus solely on how well each item meets the task requirements
- Do not let item order (A vs B) influence your decision
- Base your choice on the information provided, not assumptions

## Output Format
You must respond with:
- choice: Either "item_a" or "item_b" (required)
{"- reasoning: Brief explanation of your decision (required)" if include_reasoning else ""}"""

        # Create agent with appropriate configuration
        agent = Agent(
            model=self.config.model,
            system_prompt=base_prompt,
            output_type=ComparisonResult,
        )

        # Optimized user prompt with clearer structure
        user_prompt = f"""<task>
{description}
</task>

<comparison>
<item_a>
<id>{item_a.id}</id>
{f"<description>{item_a.description}</description>" if item_a.description else ""}
</item_a>

<item_b>
<id>{item_b.id}</id>
{f"<description>{item_b.description}</description>" if item_b.description else ""}
</item_b>
</comparison>

<instruction>
Compare the two items above and determine which one better fulfills the task requirements.
Return your choice as either "item_a" or "item_b".
{"Include a brief reasoning explaining your decision." if include_reasoning else ""}
</instruction>"""

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
