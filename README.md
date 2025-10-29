# Arbitron ⚖️

Arbitron is an agentic _pairwise_ comparison engine. Multiple jurors, each with unique value systems, evaluate items head-to-head and produce a set of pairwise comparisons that can be used to [derive item's ranks and weights](https://choix.lum.li/en/latest/api.html#processing-pairwise-comparisons).

- **Why pairwise?** It's easier to compare two items than to assign absolute scores.
- **Why multi-juror?** Different models with different perspectives (instructions) lead to more balanced, less biased outcomes.

## ✨ Features

- 🎯 **Arbitrary Sets**. Evaluate text, code, products, ideas
- 🤖 **Customizable Jurors**. Specify custom instructions, tools, providers
- 🛡️ **Bias Reduction**. Ensemble decision-making
- 🧩 **Remixable** — Join data with human labels and apply personalized heuristics

## 🚀 Quickstart

Running your first Arbitron "contest" is easy!

```bash
pip install arbitron
```

Setup your favorite LLM provider's API keys in the environment (e.g: `OPENAI_API_KEY`) and then run the following code.

```python
from arbitron import Competition, Item, Juror

items = [
    Item(id="arrival"),
    Item(id="interstellar"),
    Item(id="inception"),
]

jurors = [
    Juror(id="SciFi Purist", model="openai:gpt-5-nano"),
]

competition = Competition(
    id="sci-fi-soundtracks",
    description="Which movie has the better soundtrack?",
    jurors=jurors,
    items=items,
)

for comparison in competition.run():
    print(comparison)

print(f"Total cost: {competition.cost}")
```

To stream results as soon as they are ready, consume the async generator returned by `competition.stream()`:

```python
import asyncio

async def main() -> None:
    # reuse the competition instance defined above
    async for comparison in competition.stream():
        print(comparison)

asyncio.run(main())
```

## 🏛️ License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- [DeepGov](https://www.deepgov.org/) and their use of AI for Democratic Capital Allocation and Governance.
- [Daniel Kronovet](https://kronosapiens.github.io/) for his many writings on the power of pairwise comparisons.

---

*Margur veit það sem einn veit ekki.*
*Many know what one does not know.*
