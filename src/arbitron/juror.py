from datetime import datetime, timezone
from pydantic_ai import Agent as PydanticAgent

from .models import Comparison, ComparisonDecision, Item, Juror


def _default_instructions(juror: Juror, include_reasoning: bool) -> str:
    """Create the instructions shown to the juror when none are provided."""
    focus = juror.instructions or "Compare items according to the task requirements."
    reasoning_text = (
        "- reasoning: Brief explanation of your decision (required)"
        if include_reasoning
        else ""
    )
    return f"""
You are {juror.id}, an expert evaluation juror.

## Guidance
{focus}

## Task
You will compare two items and determine which one better fulfills the requirements of a given task.

## Process
1. Read and understand the task requirements.
2. Analyze each item against those requirements.
3. Decide which item better meets the task.

## Output
Return:
- choice: Either "item_a" or "item_b" (required)
{reasoning_text}""".strip()


def _format_item_block(tag: str, item: Item) -> str:
    """Return the XML-like block describing an item."""
    description_line = (
        f"<description>{item.description}</description>" if item.description else ""
    )
    return f"<{tag}>\n<id>{item.id}</id>\n{description_line}\n</{tag}>"


def _build_user_prompt(
    description: str, item_a: Item, item_b: Item, include_reasoning: bool
) -> str:
    """Create the user prompt delivered to the juror."""
    reasoning_line = (
        "Include a brief reasoning explaining your decision." if include_reasoning else ""
    )
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
{reasoning_line}
</instruction>"""


def _resolve_agent(
    juror: Juror, instructions: str
) -> PydanticAgent:
    """Return a Juror-ready Agent, using defaults when needed."""
    if juror.agent is None:
        model = juror.model or "openai:gpt-5-nano"
        return PydanticAgent(
            model=model,
            instructions=instructions,
            output_type=ComparisonDecision,
            retries=3,
        )

    if isinstance(juror.agent, PydanticAgent):
        return juror.agent

    msg = "juror.agent must be a pydantic_ai.Agent instance"
    raise TypeError(msg)


async def run_juror(
    juror: Juror,
    description: str,
    item_a: Item,
    item_b: Item,
    include_reasoning: bool = False,
) -> Comparison:
    """Execute a pairwise comparison using the provided juror."""
    instructions = _default_instructions(juror, include_reasoning)
    user_prompt = _build_user_prompt(description, item_a, item_b, include_reasoning)
    agent = _resolve_agent(juror, instructions)

    result = await agent.run(user_prompt)
    output = result.output

    if not isinstance(output, ComparisonDecision):
        raise TypeError("Juror output must match ComparisonDecision")

    winner = {"item_a": item_a.id, "item_b": item_b.id}[output.choice]

    return Comparison(
        juror_id=juror.id,
        item_a=item_a.id,
        item_b=item_b.id,
        winner=winner,
        rationale=output.reasoning if include_reasoning else None,
        created_at=datetime.now(timezone.utc),
    )
