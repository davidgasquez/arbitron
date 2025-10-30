import asyncio
import itertools
import random
from collections.abc import Sequence
from datetime import datetime, timezone

import pytest
from pydantic import BaseModel
from pydantic_ai import Agent, models
from pydantic_ai.models.test import TestModel

from arbitron import Competition, Item, Juror
from arbitron.juror import _build_user_prompt, _format_item_block, _resolve_agent
from arbitron.models import Comparison, ComparisonChoice, ComparisonVerdict
from arbitron.pairing import AllPairsSampler, PairSampler, RandomPairsSampler
from arbitron.runner import _randomize_pair_orientations


@pytest.fixture(autouse=True)
def disable_real_models():
    with models.override_allow_model_requests(False):
        yield


def _build_test_juror(juror_id: str = "unit-test") -> Juror:
    agent = Agent(
        model=TestModel(),
        instructions="Fake juror used for unit tests.",
        output_type=ComparisonVerdict,
    )
    return Juror(id=juror_id, agent=agent)


def test_competition_runs_with_test_model():
    competition = Competition(
        id="sci-fi-soundtracks",
        description="Which movie has the better soundtrack?",
        jurors=[_build_test_juror()],
        items=[
            Item(id="arrival"),
            Item(id="interstellar"),
            Item(id="inception"),
        ],
    )

    comparisons = list(competition.run())

    assert len(comparisons) == 3
    assert {comparison.juror_id for comparison in comparisons} == {"unit-test"}
    winners = {comparison.winner for comparison in comparisons}
    expected_ids = {"arrival", "interstellar", "inception"}

    assert winners <= expected_ids
    assert all(comparison.created_at for comparison in comparisons)
    assert competition.comparisons == comparisons


def test_stream_async_iteration_collects_results():
    competition = Competition(
        id="async-stream",
        description="Asynchronous stream collects results",
        jurors=[_build_test_juror()],
        items=[
            Item(id="arrival"),
            Item(id="interstellar"),
            Item(id="inception"),
        ],
    )

    streamed: list[Comparison] = []

    async def _consume() -> None:
        async for comparison in competition.stream():
            streamed.append(comparison)

    asyncio.run(_consume())

    assert len(streamed) == competition.total_comparisons
    assert streamed == competition.comparisons


def test_stream_reports_progress(capfd: pytest.CaptureFixture[str]):
    competition = Competition(
        id="progress-stream",
        description="Progress reporting",
        jurors=[_build_test_juror()],
        items=[
            Item(id="A"),
            Item(id="B"),
            Item(id="C"),
        ],
    )

    async def _consume() -> None:
        async for _ in competition.stream(progress=True):
            pass

    asyncio.run(_consume())
    _, err = capfd.readouterr()
    progress_updates = [line for line in err.split("\r") if line]
    assert progress_updates, "Expected progress output on stderr."

    total = competition.total_comparisons
    expected_final = (
        f"Competition {competition.id}: {total}/{total} comparisons (100.00%)"
    )
    assert progress_updates[-1].strip() == expected_final


def test_stream_silent_without_progress(capfd: pytest.CaptureFixture[str]):
    competition = Competition(
        id="silent-stream",
        description="No progress output by default",
        jurors=[_build_test_juror()],
        items=[
            Item(id="A"),
            Item(id="B"),
        ],
    )

    async def _consume() -> None:
        async for _ in competition.stream():
            pass

    asyncio.run(_consume())
    stdout, stderr = capfd.readouterr()
    assert stdout == ""
    assert stderr == ""


def test_item_payload_serialises_custom_data():
    class Movie(BaseModel):
        title: str
        year: int

    item = Item(id="arrival", payload=Movie(title="Arrival", year=2016))

    assert item.prompt_payload() == {
        "title": "Arrival",
        "year": 2016,
        "id": "arrival",
    }


def test_item_prompt_renders_payload_as_xml():
    item = Item(
        id="arrival",
        payload={"title": "Arrival", "genres": ["scifi", "drama"]},
    )

    xml = _format_item_block("item_a", item)

    assert "<item_a>" in xml
    assert "<title>Arrival</title>" in xml
    assert "<genres>" in xml
    assert xml.count("<item>") == 2


def test_build_user_prompt_escapes_task_description():
    prompt = _build_user_prompt("Compare & rank A < B", Item(id="A"), Item(id="B"))

    assert "<task>\nCompare &amp; rank A &lt; B\n</task>" in prompt


def test_total_pairs_and_comparisons_are_exposed():
    competition = Competition(
        id="numbers",
        description="Which number wins?",
        jurors=[_build_test_juror("one"), _build_test_juror("two")],
        items=[
            Item(id="1"),
            Item(id="2"),
            Item(id="3"),
            Item(id="4"),
        ],
    )

    assert competition.total_pairs == 6
    assert competition.total_comparisons == 12

    pair_ids = {tuple(item.id for item in pair) for pair in competition.pairs}
    assert pair_ids == {
        ("1", "2"),
        ("1", "3"),
        ("1", "4"),
        ("2", "3"),
        ("2", "4"),
        ("3", "4"),
    }


def test_competition_seed_controls_pair_order():
    items = [Item(id=str(value)) for value in range(4)]
    competition = Competition(
        id="seeded-order",
        description="Check pair order",
        jurors=[_build_test_juror()],
        items=items,
        seed=7,
    )

    sampler = AllPairsSampler(seed=7)
    expected = sampler.sample(items)
    assert competition.pairs == expected


def test_random_sampler_pairs_are_cached_and_reused():
    sampler = RandomPairsSampler(count=2, seed=99)
    competition = Competition(
        id="letters",
        description="Pick a letter",
        jurors=[_build_test_juror("alpha"), _build_test_juror("beta")],
        items=[
            Item(id="A"),
            Item(id="B"),
            Item(id="C"),
        ],
        pair_sampler=sampler,
    )

    initial_pairs = competition.pairs
    assert initial_pairs == competition.pairs
    assert competition.total_pairs == 2
    assert competition.total_comparisons == 4

    comparisons = list(competition.run())

    assert len(comparisons) == competition.total_comparisons
    produced_pairs = {
        frozenset((comparison.item_a, comparison.item_b)) for comparison in comparisons
    }
    expected_pairs = {frozenset((pair[0].id, pair[1].id)) for pair in initial_pairs}
    assert produced_pairs == expected_pairs


def test_random_sampler_shuffles_when_requesting_all_pairs():
    items = [
        Item(id="A"),
        Item(id="B"),
        Item(id="C"),
        Item(id="D"),
    ]
    sampler = RandomPairsSampler(count=10, seed=0)
    competition = Competition(
        id="letters-shuffled",
        description="Pick a letter",
        jurors=[_build_test_juror("alpha")],
        items=items,
        pair_sampler=sampler,
    )

    shuffled_pairs = competition.pairs
    all_pairs = list(itertools.combinations(items, 2))

    assert len(shuffled_pairs) == len(all_pairs)
    assert shuffled_pairs != all_pairs
    assert {(item_a.id, item_b.id) for item_a, item_b in shuffled_pairs} == {
        (item_a.id, item_b.id) for item_a, item_b in all_pairs
    }


def test_competition_resamples_pairs_between_runs():
    class CountingSampler(PairSampler):
        def __init__(self) -> None:
            self.calls = 0

        def sample(
            self,
            items: Sequence[Item],
            seed: int | None = None,
        ) -> list[tuple[Item, Item]]:
            self.calls += 1
            return list(itertools.combinations(items, 2))

    items = [
        Item(id="A"),
        Item(id="B"),
        Item(id="C"),
    ]
    sampler = CountingSampler()
    competition = Competition(
        id="resample-pairs",
        description="Ensure pairs refresh each run",
        jurors=[_build_test_juror("alpha")],
        items=items,
        pair_sampler=sampler,
    )

    list(competition.run())
    assert sampler.calls == 1

    list(competition.run())
    assert sampler.calls == 2


def test_pair_orientation_randomization_uses_seed():
    pairs = [
        (Item(id="A"), Item(id="B")),
        (Item(id="C"), Item(id="D")),
        (Item(id="E"), Item(id="F")),
    ]

    rng = random.Random(0)
    randomized = _randomize_pair_orientations(pairs, rng)

    assert [(item_a.id, item_b.id) for item_a, item_b in randomized] == [
        ("B", "A"),
        ("D", "C"),
        ("E", "F"),
    ]
    # Ensure the original list remains unchanged
    assert [(item_a.id, item_b.id) for item_a, item_b in pairs] == [
        ("A", "B"),
        ("C", "D"),
        ("E", "F"),
    ]


def test_competition_seed_reproducible(monkeypatch: pytest.MonkeyPatch):
    items = [
        Item(id="A"),
        Item(id="B"),
        Item(id="C"),
    ]

    orientations: list[tuple[str, str]] = []

    async def fake_run_juror(
        juror: Juror,
        description: str,
        item_a: Item,
        item_b: Item,
    ) -> Comparison:
        orientations.append((item_a.id, item_b.id))
        return Comparison(
            juror_id=juror.id,
            item_a=item_a.id,
            item_b=item_b.id,
            winner=item_a.id,
            confidence=0.75,
            created_at=datetime.now(timezone.utc),
            cost=None,
        )

    monkeypatch.setattr("arbitron.runner.run_juror", fake_run_juror)

    juror = Juror(id="deterministic")

    competition = Competition(
        id="letters-orientation-seed",
        description="Pick a letter",
        jurors=[juror],
        items=items,
        seed=123,
    )

    first_winners = list(competition.run())
    first_orientations = orientations.copy()
    orientations.clear()

    second_winners = list(competition.run())
    second_orientations = orientations.copy()

    orientation_seed = competition.seed + 1 if competition.seed is not None else None
    expected_rng = random.Random(orientation_seed)
    expected_orientations = [
        (pair[1].id, pair[0].id)
        if expected_rng.randrange(2)
        else (pair[0].id, pair[1].id)
        for pair in competition.pairs
    ]

    assert first_orientations == expected_orientations
    assert second_orientations == expected_orientations
    assert sorted(first_orientations) == sorted(second_orientations)
    assert sorted(
        (comp.item_a, comp.item_b, comp.winner) for comp in first_winners
    ) == [(*pair, pair[0]) for pair in sorted(first_orientations)]
    assert sorted(
        (comp.item_a, comp.item_b, comp.winner) for comp in second_winners
    ) == [(*pair, pair[0]) for pair in sorted(second_orientations)]


def test_to_csv_creates_parent_directories(tmp_path):
    competition = Competition(
        id="export",
        description="Pick a letter",
        jurors=[_build_test_juror()],
        items=[Item(id="A"), Item(id="B")],
    )

    list(competition.run())

    output_path = tmp_path / "nested" / "results" / "comparisons.csv"

    competition.to_csv(output_path)

    assert output_path.exists()


def test_competition_rejects_duplicate_item_ids():
    with pytest.raises(ValueError, match=r"Duplicate item ids: \['A'\]"):
        Competition(
            id="dupe-items",
            description="Pick a letter",
            jurors=[_build_test_juror()],
            items=[Item(id="A"), Item(id="A")],
        )


def test_competition_rejects_duplicate_juror_ids():
    with pytest.raises(ValueError, match=r"Duplicate juror ids: \['unit-test'\]"):
        Competition(
            id="dupe-jurors",
            description="Pick a letter",
            jurors=[_build_test_juror(), _build_test_juror()],
            items=[Item(id="A"), Item(id="B")],
        )


def test_juror_rejects_agent_and_model():
    agent = Agent(
        model=TestModel(),
        instructions="Fake juror used for unit tests.",
        output_type=ComparisonVerdict,
    )

    with pytest.raises(ValueError, match="either `agent` or `model`"):
        Juror(id="conflicted", agent=agent, model="custom:model")


def test_resolve_agent_defaults_to_openai_model():
    juror = Juror(id="defaults")

    agent = _resolve_agent(juror, "Instructions")

    assert juror.model is None
    assert getattr(agent.model, "model_name", None) == "gpt-5-nano"
