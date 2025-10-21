import itertools

import pytest
from pydantic import BaseModel
from pydantic_ai import Agent, models
from pydantic_ai.models.test import TestModel

from arbitron import Competition, Item, Juror
from arbitron.juror import _format_item_block
from arbitron.models import ComparisonChoice
from arbitron.pairing import RandomPairsSampler


@pytest.fixture(autouse=True)
def disable_real_models():
    with models.override_allow_model_requests(False):
        yield


def _build_test_juror(juror_id: str = "unit-test") -> Juror:
    agent = Agent(
        model=TestModel(),
        instructions="Fake juror used for unit tests.",
        output_type=ComparisonChoice,
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
        (comparison.item_a, comparison.item_b) for comparison in comparisons
    }
    expected_pairs = {(pair[0].id, pair[1].id) for pair in initial_pairs}
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
