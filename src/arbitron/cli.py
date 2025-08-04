import argparse
from pathlib import Path

from .config import load_competition
from .io import read_comparisons, write_comparisons
from .ranking import rank
from .runner import run


def cmd_run(args: argparse.Namespace) -> None:
    desc, agents, items, cpa, include_reasoning = load_competition(args.config)
    comparisons = run(desc, agents, items, comparisons_per_agent=cpa, include_reasoning=include_reasoning)
    output = args.output or Path("duels.csv")
    write_comparisons(output, comparisons)
    print(f"✅ {len(comparisons)} comparisons written to {output}")


def cmd_rank(args: argparse.Namespace) -> None:
    comparisons = read_comparisons(args.file)
    ranking = rank(comparisons)
    if not ranking:
        print("No comparisons found.")
        return
    for i, (item_id, score) in enumerate(ranking, 1):
        print(f"{i:2}. {item_id:<30} {score:.3f}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="arbitron")
    sub = p.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Execute a YAML competition")
    run_p.add_argument("config", help="YAML competition file")
    run_p.add_argument("--output", "-o", help="CSV file for results")
    run_p.set_defaults(func=cmd_run)

    rank_p = sub.add_parser("rank", help="Compute rankings from CSV")
    rank_p.add_argument("file", help="CSV file with comparisons")
    rank_p.set_defaults(func=cmd_rank)

    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
