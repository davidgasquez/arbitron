"""Agent wrapper for PydanticAI agents."""

import logging
import threading
import time
from collections import deque

from pydantic_ai import Agent as PydanticAgent

from .models import ComparisonResult, Item

logger = logging.getLogger(__name__)


class Agent:
    """Wrapper for PydanticAI agents that perform pairwise comparisons."""

    def __init__(
        self,
        system_prompt: str,
        agent_id: str | None = None,
        model: str = "google-gla:gemini-2.0-flash-lite",
    ):
        """Initialize an Arbitron agent.

        Args:
            system_prompt: The agent's value system and decision criteria
            agent_id: Optional identifier for the agent
            model: The LLM model to use
        """
        self.system_prompt = system_prompt
        self.agent_id = agent_id or f"agent_{id(self)}"

        # Rate limiting: 15 requests per minute
        self._rate_limit = 15
        self._rate_window = 60  # seconds
        self._request_times = deque()
        self._rate_lock = threading.Lock()

        # Create the PydanticAI agent with structured output
        self._agent = PydanticAgent(
            model=model,
            output_type=ComparisonResult,
            system_prompt=self._build_system_prompt(),
        )

        logger.info(f"Initialized agent {self.agent_id}")

    def _build_system_prompt(self) -> str:
        """Build the full system prompt for the agent."""
        base_prompt = """You are an expert evaluator participating in a pairwise comparison task.
Your role is to compare two items and choose which one is better according to your specific evaluation criteria.

IMPORTANT: You must respond with a structured comparison that includes:
1. The names of both items being compared (item_a and item_b)
2. Your chosen winner (must be exactly one of the two items)
3. Clear reasoning explaining your choice

Your specific evaluation criteria:
"""
        return base_prompt + self.system_prompt

    def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        with self._rate_lock:
            current_time = time.time()

            # Remove old requests outside the time window
            while (
                self._request_times
                and current_time - self._request_times[0] > self._rate_window
            ):
                self._request_times.popleft()

            # Always wait at least 4 seconds between requests (15 requests/60 seconds = 1 request per 4 seconds)
            if self._request_times:
                time_since_last = current_time - self._request_times[-1]
                min_interval = self._rate_window / self._rate_limit
                if time_since_last < min_interval:
                    wait_time = min_interval - time_since_last
                    logger.debug(
                        f"Waiting {wait_time:.2f} seconds to maintain rate limit"
                    )
                    time.sleep(wait_time)

            # Record this request
            self._request_times.append(time.time())

    def compare(
        self, item_a: Item, item_b: Item, contest_description: str
    ) -> ComparisonResult:
        """Compare two items and return the agent's decision.

        Args:
            item_a: First item to compare
            item_b: Second item to compare
            contest_description: Description of what's being evaluated

        Returns:
            ComparisonResult with the agent's choice and reasoning
        """
        # Apply rate limiting
        self._wait_for_rate_limit()

        prompt = f"""Contest: {contest_description}

Please compare these two options:

Option A: {item_a.name}
{f"Description: {item_a.description}" if item_a.description else ""}

Option B: {item_b.name}
{f"Description: {item_b.description}" if item_b.description else ""}

Choose which option is better according to your evaluation criteria. You must set:
- item_a: "{item_a.name}"
- item_b: "{item_b.name}"
- winner: EXACTLY "{item_a.name}" OR EXACTLY "{item_b.name}" (copy the exact spelling)
- reasoning: your explanation
- agent_id: "{self.agent_id}"

CRITICAL: The winner field must be an exact character-for-character match of one of the two option names above. Do not modify, rephrase, or add any characters.
"""

        logger.debug(f"Agent {self.agent_id} comparing {item_a.name} vs {item_b.name}")

        # Run the comparison
        result = self._agent.run_sync(prompt)

        # The agent returns a ComparisonResult directly due to output_type
        comparison = result.output

        # Ensure agent_id is set correctly
        comparison.agent_id = self.agent_id

        logger.info(
            f"Agent {self.agent_id} chose {comparison.winner} "
            f"over {item_a.name if comparison.winner == item_b.name else item_b.name}"
        )

        return comparison
