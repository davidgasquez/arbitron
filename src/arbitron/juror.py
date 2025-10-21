import html
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.messages import ModelResponse

from .models import Comparison, ComparisonChoice, Item, Juror


def _default_instructions(juror: Juror) -> str:
    """Create the instructions shown to the juror when none are provided."""
    focus = juror.instructions or "Compare items according to the task requirements."
    return f"""
You are an expert juror.

## Goal

{focus}

## Output

Return `choice` as either "item_a" or "item_b".""".strip()


def _value_to_xml(tag: str, value: Any) -> str:
    """Render arbitrary JSON-like data into a simple XML fragment."""
    if value is None:
        return f"<{tag} />"

    if isinstance(value, Mapping):
        if not value:
            return f"<{tag} />"

        children = "\n".join(
            _value_to_xml(str(child_tag), child_value)
            for child_tag, child_value in value.items()
        )
        return f"<{tag}>\n{children}\n</{tag}>"

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if not value:
            return f"<{tag} />"

        children = "\n".join(
            _value_to_xml("item", child_value) for child_value in value
        )
        return f"<{tag}>\n{children}\n</{tag}>"

    return f"<{tag}>{html.escape(str(value))}</{tag}>"


def _format_item_block(tag: str, item: Item) -> str:
    """Return the XML-like block describing an item."""
    payload = item.prompt_payload()
    return _value_to_xml(tag, payload)


def _build_user_prompt(description: str, item_a: Item, item_b: Item) -> str:
    """Create the user prompt delivered to the juror."""
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
</instruction>"""


def _resolve_agent(juror: Juror, instructions: str) -> PydanticAgent:
    """Return a Juror-ready Agent, using defaults when needed."""
    if juror.agent is None:
        model = juror.model or "openai:gpt-5-nano"
        return PydanticAgent[None, ComparisonChoice](
            model=model,
            instructions=instructions,
            output_type=ComparisonChoice,
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
) -> Comparison:
    """Execute a pairwise comparison using the provided juror."""
    instructions = _default_instructions(juror)
    user_prompt = _build_user_prompt(description, item_a, item_b)
    agent = _resolve_agent(juror, instructions)

    result = await agent.run(user_prompt)
    try:
        choice: ComparisonChoice = ComparisonChoice(result.output)
    except ValueError as exc:  # pragma: no cover - defensive
        msg = "Juror output must be 'item_a' or 'item_b'"
        raise TypeError(msg) from exc

    winner = item_a.id if choice is ComparisonChoice.item_a else item_b.id

    total_cost = Decimal("0")
    for message in result.new_messages():
        if not isinstance(message, ModelResponse):
            continue

        try:
            price = message.cost()
        except LookupError:
            continue
        except Exception:
            continue

        if price is None:
            continue

        total_price = getattr(price, "total_price", None)
        if total_price is None:
            continue

        total_cost += (
            total_price
            if isinstance(total_price, Decimal)
            else Decimal(str(total_price))
        )

    comparison_cost = total_cost if total_cost != Decimal("0") else None

    return Comparison(
        juror_id=juror.id,
        item_a=item_a.id,
        item_b=item_b.id,
        winner=winner,
        created_at=datetime.now(timezone.utc),
        cost=comparison_cost,
    )
