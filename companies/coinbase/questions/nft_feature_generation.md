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
**Core Idea:** Parse K categories, compute Cartesian product with DFS backtracking.

```java
import java.util.*;

class NFTGenerator {
    static void solve(Scanner sc) {
        int k = sc.nextInt(); sc.nextLine();
        List<String> names = new ArrayList<>();
        List<List<String>> categories = new ArrayList<>();

        for (int i = 0; i < k; i++) {
            names.add(sc.nextLine().trim());
            int m = Integer.parseInt(sc.nextLine().trim());
            List<String> values = new ArrayList<>();
            for (int j = 0; j < m; j++) values.add(sc.nextLine().trim());
            categories.add(values);
        }

        List<List<String>> combos = new ArrayList<>();
        generateCombos(categories, 0, new ArrayList<>(), combos);
        System.out.println(combos.size());
        for (List<String> combo : combos) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < combo.size(); i++) {
                if (i > 0) sb.append(',');
                sb.append(names.get(i)).append('=').append(combo.get(i));
            }
            System.out.println(sb);
        }
    }

    static void generateCombos(List<List<String>> categories, int idx,
                                List<String> current, List<List<String>> results) {
        if (idx == categories.size()) {
            results.add(new ArrayList<>(current));
            return;
        }
        for (String v : categories.get(idx)) {
            current.add(v);
            generateCombos(categories, idx + 1, current, results);
            current.remove(current.size() - 1);
        }
    }
}
```

**Complexity:** O(prod(Mi)) time and space — Mi = values in category i

### Level 2
**Core Idea:** Deduplicate each category's values before computing the product. Use `LinkedHashMap` to preserve insertion order while removing duplicates.

```java
// Dedup preserving order — drop-in replacement for values list in Level 1
List<String> dedup(List<String> values) {
    return new ArrayList<>(new LinkedHashSet<>(values));
}
```

Drop-in replacement for the values list in Level 1. The rest of the logic is unchanged.

**Complexity:** O(prod(Ui)) — Ui = unique values in category i

### Level 3
**Core Idea:** Aggregate weights for duplicate values using a `LinkedHashMap`, then use weighted random sampling via cumulative distribution.

```java
import java.util.*;

class NFTGenerator {
    static void solve(Scanner sc) {
        int k = sc.nextInt(); sc.nextLine();
        List<String> names = new ArrayList<>();
        List<List<String>> uniqueValues = new ArrayList<>();
        List<List<double[]>> weightedValues = new ArrayList<>(); // {value_index, weight}

        for (int i = 0; i < k; i++) {
            names.add(sc.nextLine().trim());
            int m = Integer.parseInt(sc.nextLine().trim());
            LinkedHashMap<String, Double> weightMap = new LinkedHashMap<>();
            for (int j = 0; j < m; j++) {
                String[] parts = sc.nextLine().trim().split(" ");
                String v = parts[0];
                double w = Double.parseDouble(parts[1]);
                weightMap.merge(v, w, Double::sum);
            }
            List<String> vals = new ArrayList<>(weightMap.keySet());
            List<double[]> weighted = new ArrayList<>();
            for (Map.Entry<String, Double> e : weightMap.entrySet()) {
                weighted.add(new double[]{vals.indexOf(e.getKey()), e.getValue()});
            }
            uniqueValues.add(vals);
            weightedValues.add(weighted);
        }

        List<List<String>> combos = new ArrayList<>();
        generateCombos(uniqueValues, 0, new ArrayList<>(), combos);
        System.out.println(combos.size());
        for (List<String> combo : combos) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < combo.size(); i++) {
                if (i > 0) sb.append(',');
                sb.append(names.get(i)).append('=').append(combo.get(i));
            }
            System.out.println(sb);
        }

        StringBuilder random = new StringBuilder("RANDOM: ");
        for (int i = 0; i < k; i++) {
            if (i > 0) random.append(',');
            random.append(names.get(i)).append('=')
                  .append(weightedSample(uniqueValues.get(i), weightedValues.get(i)));
        }
        System.out.println(random);
    }

    static String weightedSample(List<String> values, List<double[]> weighted) {
        double total = weighted.stream().mapToDouble(e -> e[1]).sum();
        double r = Math.random() * total;
        double cumulative = 0;
        for (double[] entry : weighted) {
            cumulative += entry[1];
            if (r <= cumulative) return values.get((int) entry[0]);
        }
        return values.get(values.size() - 1); // fallback for float precision
    }
}
```

**Complexity:** O(sum(Mi)) parse + O(prod(Ui)) enumerate + O(K * max(Ui)) sample

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Combinatorial explosion:** With 20 categories of 50 values each, there are 50^20 combinations — printing them is infeasible. For large collections, generate lazily or only generate the random sample.
- **Lazy generation:** Instead of collecting all combos into a list, use an iterator or stream that yields one combination at a time without holding the entire space in memory.
- **Unique random NFT minting:** To generate N distinct NFTs without collision, use a set of seen combinations and retry on collision. For high-uniqueness-ratio collections (few collisions), rejection sampling works. For near-saturation, track remaining valid combos explicitly.
- **Reproducible randomness:** NFT collections need auditable randomness. `Math.random()` is not cryptographically secure. Use `SecureRandom` with a committed seed or verifiable randomness (Chainlink VRF) for production NFT drops.
- **Weight normalization:** Weights don't need to sum to 1 — the cumulative sampling normalizes internally. But floating-point weights can accumulate rounding errors; work in integers when possible.

### Common Interview Traps
- **Duplicate weight aggregation:** "Blue" appearing twice with weight 1 each should yield total weight 2, not two separate entries. Forgetting to aggregate means overrepresentation of duplicated traits.
- **Empty category:** If any category has zero values after dedup, the product is empty (0 combos). Handle this gracefully.
- **Floating-point rounding in `weightedSample`:** The manual cumulative-sum approach can miss the last item due to float precision. Always include a fallback `return values.get(values.size() - 1)` or pre-normalize weights.
- **Output ordering:** The problem implies deterministic ordering for the enumeration. `LinkedHashSet`/`LinkedHashMap` respects insertion order — make sure dedup preserves order (not `HashSet`).

### How to Push Forward as Staff+
- **Name the pattern:** "This is a Cartesian product problem. The DFS solution generalizes to any combinatorial search with pruning — useful if we add constraints like 'Laser Eyes cannot appear with Sunglasses'."
- **Constraint satisfaction:** Forbidden combinations are a natural extension. Implement a conflict registry and prune during DFS to avoid generating invalid combos entirely, rather than filtering after the fact.
- **Connect to Coinbase domain:** Coinbase NFT marketplace (now sunset, but relevant to the interview context) needed exactly this — generative collection tooling with rarity weighting. The weighted sampling directly maps to rarity tier systems (Common/Rare/Legendary).
- **Statistical verification:** "To verify the weights are correct, I'd run the sampler 100K times and compare empirical frequencies to expected probabilities using a chi-squared test. In CI, I'd assert the p-value stays above a threshold."
- **Proactively raise the scale concern:** "Before I implement the enumeration, I want to flag: if this collection has many categories with many values, printing all combinations is infeasible. Should I implement a lazy iterator instead, or assume the combo count fits in memory?"
