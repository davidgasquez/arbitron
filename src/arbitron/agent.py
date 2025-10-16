from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent

from .models import Agent as AgentConfig
from .models import Comparison, Item


def _build_system_prompt(config: AgentConfig, include_reasoning: bool) -> str:
    """Create the system prompt shown to the evaluation agent."""
    return f"""
You are {config.id}, an expert evaluation agent.

## Your Role
{config.prompt}

## Your Task
You will compare two items and determine which one better fulfills the requirements of a given task.

## Evaluation Process
1. Carefully read and understand the task requirements
2. Analyze each item's characteristics against the task requirements
3. Think and make a choice based on how well each item meets the requirements
4. Select the item that best fulfills the task requirements

## Important Guidelines
- Try to be objective and unbiased in your evaluation
- Focus solely on how well each item meets the task requirements

## Output Format
You must respond with:
- choice: Either "item_a" or "item_b" (required)
{"- reasoning: Brief explanation of your decision (required)" if include_reasoning else ""}"""


def _format_item_block(tag: str, item: Item) -> str:
    """Return the XML-like block describing an item."""
    description_line = (
        f"<description>{item.description}</description>" if item.description else ""
    )
    return f"<{tag}>\n<id>{item.id}</id>\n{description_line}\n</{tag}>"


def _build_user_prompt(
    description: str, item_a: Item, item_b: Item, include_reasoning: bool
) -> str:
    """Create the user prompt delivered to the agent."""
    return f"""<task>
{description}
</task>

<comparison>
{_format_item_block("item_a", item_a)}

{_format_item_block("item_b", item_b)}
</comparison>

<instruction>
Compare the two items above and determine which one better fulfills the task requirements.
Return your choice as either "item_a" or "item_b".
{"Include a brief reasoning explaining your decision." if include_reasoning else ""}
</instruction>"""


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

        system_prompt = _build_system_prompt(self.config, include_reasoning)

        # Create agent with appropriate configuration
        agent = Agent(
            model=self.config.model,
            system_prompt=system_prompt,
            output_type=ComparisonResult,
            retries=3,
        )

        user_prompt = _build_user_prompt(description, item_a, item_b, include_reasoning)

        result = await agent.run(user_prompt)

        output = result.output
        assert isinstance(output, ComparisonResult), (
            "Agent output must match ComparisonResult"
        )

        winner = {"item_a": item_a.id, "item_b": item_b.id}[output.choice]

        return Comparison(
            agent_id=self.config.id,
            item_a=item_a.id,
            item_b=item_b.id,
            winner=winner,
            rationale=output.reasoning if include_reasoning else None,
            created_at=datetime.now(timezone.utc),
        )
