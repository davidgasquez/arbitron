# Arbitron ⚖️

Arbitron is a multi-agent consensus ranking system that determines winners through pairwise comparisons. Instead of relying on individual ratings or single perspectives, multiple agents—each with unique value systems—evaluate items head-to-head to produce robust, fair rankings.

**Why pairwise?** It's easier to compare two items than to assign absolute scores.

**Why multi-agent?** Different perspectives lead to more balanced, less biased outcomes.

**Why consensus?** Aggregated judgments are more reliable than individual ones.

## ✨ Features

- 🎯 **Arbitrary Sets** — text, code, products, ideas
- 🤖 **Customizable Agents** — unique personas, tools, providers
- 🗳️ **Consistent Aggregation** — diverse perspectives into rankings
- 🛡️ **Bias Reduction** — ensemble decision-making
- 🧩 **Remixable** — join data with human labels or other heuristics

## 🚀 Quickstart

Running your first Arbitron contest is easy!

```bash
pip install arbitron
```

Setup your favorite LLM provider's API keys in the environment and then run the following code.

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
    ),
    arbitron.Agent(
        id="Nolan Fan",
        prompt="Compare based on complex narratives and emotional depth.",
    ),
    arbitron.Agent(
        id="Critics Choice",
        prompt="Compare based on artistic merit and cinematic excellence.",
    ),
]

description = "Rank the movies based on their soundtrack quality."

comparisons = arbitron.run(description, agents, movies)
ranking = arbitron.rank(comparisons)
```

### YAML Based Configuration

Arbitron can read the configuration from YAML files for easier management and scalability.

```yaml
description: "Rank the movies based on their soundtrack quality."
comparisons_per_agent: 20
agents:
  - id: "SciFi Purist"
    prompt: "Compare based on scientific accuracy and hard sci-fi concepts."
    model: "google-gla:gemini-2.5-flash-lite"
  - id: "Nolan Fan"
    prompt: "Compare based on complex narratives and emotional depth."
    model: "openai:gpt-4.1-nano"
  - id: "Critics Choice"
    prompt: "Compare based on artistic merit and cinematic excellence."
    model: "groq:moonshotai/kimi-k2-instruct"
items:
  - id: "arrival"
  - id: "blade_runner"
  - id: "interstellar"
  - id: "inception"
  - id: "the_dark_knight"
  - id: "dune"
  - id: "the_matrix"
  - id: "2001_space_odyssey"
  - id: "the_fifth_element"
  - id: "the_martian"
```

You can then run the pairwise comparisons using the following command:

```bash
arbitron run competition.yaml --output duels.csv
```
This will create a file `duels.csv` with the results of the pairwise comparisons.

```bash
arbitron rank duels.csv
```

## 🏛️ License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- [DeepGov](https://www.deepgov.org/) and their use of AI for Democratic Capital Allocation and Governance.
- [Daniel Kronovet](https://kronosapiens.github.io/) for his many writings on the power of pairwise comparisons.

---

*Margur veit það sem einn veit ekki.*
*Many know what one does not know.*
