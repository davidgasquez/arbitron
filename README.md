# Arbitron ⚖️

Arbitron is an agentic _pairwise_ comparison engine. Multiple agents, each with unique value systems, evaluate items head-to-head and produce a set of pairwise comparisons that can be used to [derive item's ranks and weights](https://choix.lum.li/en/latest/api.html#processing-pairwise-comparisons).

- **Why pairwise?** It's easier to compare two items than to assign absolute scores.
- **Why multi-agent?** Different models with different perspectives (system prompts) lead to more balanced, less biased outcomes.

## ✨ Features

- 🎯 **Arbitrary Sets**. Evaluate text, code, products, ideas
- 🤖 **Customizable Agents**. Specify custom personas, tools, providers
- 🛡️ **Bias Reduction**. Ensemble decision-making
- 🧩 **Remixable** — Join data with human labels and apply personalized heuristics

## 🚀 Quickstart

Running your first Arbitron "contest" is easy!

```bash
pip install arbitron
```

Setup your favorite LLM provider's API keys in the environment (e.g: `OPENAI_API_KEY`) and then run the following code.

```python
import arbitron

movies = [
    arbitron.Item(id="arrival"),
    arbitron.Item(id="blade_runner"),
    arbitron.Item(id="interstellar"),
    arbitron.Item(id="inception"),
    arbitron.Item(id="the_dark_knight"),
    arbitron.Item(id="dune"),
    arbitron.Item(id="the_matrix"),
    arbitron.Item(id="2001_space_odyssey"),
    arbitron.Item(id="the_fifth_element"),
    arbitron.Item(id="the_martian"),
]

agents = [
    arbitron.Agent(
        id="SciFi Purist",
        prompt="Compare based on scientific accuracy and hard sci-fi concepts.",
        model="openai:gpt-5-nano",
    ),
    arbitron.Agent(
        id="Nolan Fan",
        prompt="Compare based on complex narratives and emotional depth.",
        model="openai:gpt-5-nano",
    ),
    arbitron.Agent(
        id="Critics Choice",
        prompt="Compare based on artistic merit and cinematic excellence.",
        model="openai:gpt-5-nano",
    ),
]

description = "Rank the movies based on their soundtrack quality."

comparisons = arbitron.run(description, agents, movies)

print(comparisons)
```

## 🏛️ License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- [DeepGov](https://www.deepgov.org/) and their use of AI for Democratic Capital Allocation and Governance.
- [Daniel Kronovet](https://kronosapiens.github.io/) for his many writings on the power of pairwise comparisons.

---

*Margur veit það sem einn veit ekki.*
*Many know what one does not know.*
