# Arbitron ⚖️

Arbitron is an _agentic pairwise comparison engine_ that estimates the latent "utilities" of a set of items. Useful when you need consensus ranking (or relative weights) over multiple items where objective measures are hard. Multiple jurors, each with unique value systems, evaluate items head-to-head and produce a set of pairwise comparisons that can be used to derive item's ranks and weights.

### ❓ FAQ

- **Why pairwise?** It's easier to compare two items than to assign absolute scores.
- **Why multi-juror?** Different models with different perspectives (instructions) lead to more balanced, less biased outcomes.

## ✨ Features

- 🎯 **Compare Arbitrary Sets of Items**. Text, code, products, ideas, papers, names
- 🤖 **Customizable Jurors**. Specify custom instructions, tools, skills, and providers
- 🛡️ **Bias Resistant**. Ensemble decision-making across diverse instructions, temperature, and model providers
- 🧩 **Remixable**. Join data with human labels or apply personalized heuristics to derive meaningful ranks and weights

## 🚀 Quickstart

Running your first Arbitron "contest" is easy!

```bash
pip install arbitron

# Alternatively, with `uv`
uv add arbitron
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

## 🏛️ License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- [DeepGov](https://www.deepgov.org/) and their use of AI for Democratic Capital Allocation and Governance.
- [Daniel Kronovet](https://kronosapiens.github.io/) for his many writings on the power of pairwise comparisons.

---

*Margur veit það sem einn veit ekki.*
*Many know what one does not know.*
