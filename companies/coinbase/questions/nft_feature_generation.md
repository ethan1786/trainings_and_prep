# NFT Feature Generation

**Category:** Coding / OA
**Difficulty:** Medium
**Time Estimate:** 45-60 min
**Key Topics:** Cartesian Product, Backtracking/DFS, Weighted Random Sampling, Deduplication

---

## Problem Statement

Build a tool that generates NFT trait combinations for a collection. Each NFT is defined by K categories (e.g., Ears, Eyes, Hat), and each category has a list of possible values. The tool must enumerate all valid unique combinations, and later sample random NFTs with weighted probabilities per trait.

Input is read from stdin in a structured format.

## Requirements

### Level 1: Enumerate All Combinations
Generate the Cartesian product of all category values. Print total count, then each combination as `Name=Value,...`.

```
Input:
2
Ears
2
Pointy
Wide
Eyes
2
Blue
Green

Output:
4
Ears=Pointy,Eyes=Blue
Ears=Pointy,Eyes=Green
Ears=Wide,Eyes=Blue
Ears=Wide,Eyes=Green
```

### Level 2: Deduplicate Within Categories
If a category lists a value twice, treat it as one. Count and output must reflect deduplicated values only.

```
Eyes: [Blue, Blue, Green]  ->  [Blue, Green]  (2x2=4 combos, not 2x3=6)
```

### Level 3: Weighted Random Sampling
Each value has a weight. Duplicate values in the same category have their weights summed. After printing all unique combinations (Level 2), print one randomly sampled NFT:

```
Input value format: "value weight" per line
Output: RANDOM: Ears=Wide,Eyes=Green
```

---

## Solution Approach

### Level 1
**Core Idea:** Parse K categories, compute Cartesian product with `itertools.product` (or DFS backtracking).

```python
import sys
from itertools import product

def solve():
    data = sys.stdin.read().split('\n')
    idx = 0
    k = int(data[idx]); idx += 1
    categories = []
    for _ in range(k):
        name = data[idx].strip(); idx += 1
        m = int(data[idx]); idx += 1
        values = [data[idx + i].strip() for i in range(m)]
        idx += m
        categories.append((name, values))

    combos = list(product(*[cat[1] for cat in categories]))
    print(len(combos))
    for combo in combos:
        print(",".join(f"{categories[i][0]}={v}" for i, v in enumerate(combo)))

solve()
```

**DFS alternative (no itertools):**
```python
def generate_combos(categories):
    results = []
    def dfs(idx, current):
        if idx == len(categories):
            results.append(current[:])
            return
        for v in categories[idx][1]:
            current.append(v)
            dfs(idx + 1, current)
            current.pop()
    dfs(0, [])
    return results
```

**Complexity:** O(prod(Mi)) time and space — Mi = values in category i

### Level 2
**Core Idea:** Deduplicate each category's values before computing the product. Use `dict.fromkeys()` to preserve insertion order while removing duplicates.

```python
unique_values = list(dict.fromkeys(values))
```

Drop-in replacement for the values list in Level 1. The rest of the logic is unchanged.

**Complexity:** O(prod(Ui)) — Ui = unique values in category i

### Level 3
**Core Idea:** Aggregate weights for duplicate values using a dict, then use `random.choices` (Python 3.6+) for weighted sampling.

```python
import random

def weighted_sample(values_with_weights):
    values = [v for v, _ in values_with_weights]
    weights = [w for _, w in values_with_weights]
    return random.choices(values, weights=weights, k=1)[0]

def solve():
    data = sys.stdin.read().split('\n')
    idx = 0
    k = int(data[idx]); idx += 1
    categories = []
    for _ in range(k):
        name = data[idx].strip(); idx += 1
        m = int(data[idx]); idx += 1
        weight_map = {}
        for _ in range(m):
            parts = data[idx].strip().split()
            v, w = parts[0], float(parts[1])
            weight_map[v] = weight_map.get(v, 0) + w
            idx += 1
        unique_values = list(weight_map.keys())
        weighted = list(weight_map.items())
        categories.append((name, unique_values, weighted))

    combos = list(product(*[cat[1] for cat in categories]))
    print(len(combos))
    for combo in combos:
        print(",".join(f"{categories[i][0]}={v}" for i, v in enumerate(combo)))

    random_parts = [f"{name}={weighted_sample(weighted)}"
                    for name, _, weighted in categories]
    print(f"RANDOM: {','.join(random_parts)}")

solve()
```

**Complexity:** O(sum(Mi)) parse + O(prod(Ui)) enumerate + O(K * max(Ui)) sample

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Combinatorial explosion:** With 20 categories of 50 values each, there are 50^20 combinations — printing them is infeasible. For large collections, generate lazily or only generate the random sample.
- **Lazy generation:** Use `itertools.product` as a generator (don't call `list()` on it) to stream one combination at a time without holding the entire space in memory.
- **Unique random NFT minting:** To generate N distinct NFTs without collision, use a set of seen combinations and retry on collision. For high-uniqueness-ratio collections (few collisions), rejection sampling works. For near-saturation, track remaining valid combos explicitly.
- **Reproducible randomness:** NFT collections need auditable randomness. The `random` module is not cryptographically secure. Use a CSPRNG seed (committed before reveal) or verifiable randomness (Chainlink VRF) for production NFT drops.
- **Weight normalization:** Weights don't need to sum to 1 — `random.choices` normalizes internally. But floating-point weights can accumulate rounding errors; work in integers when possible.

### Common Interview Traps
- **Duplicate weight aggregation:** "Blue" appearing twice with weight 1 each should yield total weight 2, not two separate entries. Forgetting to aggregate means overrepresentation of duplicated traits.
- **Empty category:** If any category has zero values after dedup, the product is empty (0 combos). Handle this gracefully.
- **Floating-point rounding in `weighted_sample`:** The manual cumulative-sum approach can miss the last item due to float precision. Always include a fallback `return values_with_weights[-1][0]` or use `random.choices` which handles this.
- **Output ordering:** The problem implies deterministic ordering for the enumeration. `itertools.product` respects insertion order — make sure dedup preserves order (`dict.fromkeys`, not `set`).

### How to Push Forward as Staff+
- **Name the pattern:** "This is a Cartesian product problem. The DFS solution generalizes to any combinatorial search with pruning — useful if we add constraints like 'Laser Eyes cannot appear with Sunglasses'."
- **Constraint satisfaction:** Forbidden combinations are a natural extension. Implement a conflict registry and prune during DFS to avoid generating invalid combos entirely, rather than filtering after the fact.
- **Connect to Coinbase domain:** Coinbase NFT marketplace (now sunset, but relevant to the interview context) needed exactly this — generative collection tooling with rarity weighting. The weighted sampling directly maps to rarity tier systems (Common/Rare/Legendary).
- **Statistical verification:** "To verify the weights are correct, I'd run the sampler 100K times and compare empirical frequencies to expected probabilities using a chi-squared test. In CI, I'd assert the p-value stays above a threshold."
- **Proactively raise the scale concern:** "Before I implement the enumeration, I want to flag: if this collection has many categories with many values, printing all combinations is infeasible. Should I implement a lazy iterator instead, or assume the combo count fits in memory?"
