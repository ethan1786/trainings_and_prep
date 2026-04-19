# Mining Block

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 45 min
**Key Topics:** Greedy, Knapsack, Dependency Graph, Tree Traversal, Fee Density

---

## Problem Statement

You are a miner selecting transactions from a mempool to include in the next block. Each transaction has an `id`, `size` (bytes), and `fee`. A block has a fixed `block_size` capacity. Your goal is to maximize total fee without exceeding capacity.

This problem has two parts: transactions without dependencies, then with parent-child dependencies (as in real UTXO-based blockchains like Bitcoin).

## Requirements

### Level 1: Independent Transactions

```java
class Transaction {
    String id;
    int size;
    int fee;
    Transaction(String id, int size, int fee) { ... }
}

List<String> mineBlock(List<Transaction> transactions, int blockSize);
// Select transactions to maximize total fee within blockSize.
// Scalable solution preferred over mathematically optimal.
// Returns list of selected transaction IDs.
```

### Level 2: Transactions with Parent Dependencies

A child transaction cannot be mined unless its parent is also in the same block. Each child has at most one parent; a parent may have multiple children.

```java
class Transaction {
    String id;
    int size;
    int fee;
    String parentId; // null if no parent

    Transaction(String id, int size, int fee, String parentId) { ... }
}

List<String> mineBlockWithDeps(List<Transaction> transactions, int blockSize);
// Select transactions respecting parent dependencies to maximize fee.
// To include a child, all ancestors must also be included.
```

---

## Solution Approach

### Level 1

**Core Idea:** Greedy by fee density (fee/size ratio descending). Not always optimal, but O(N log N) and practical for production-scale mempools.

**Key Decisions:** The mathematically optimal solution is 0/1 Knapsack DP at O(N × block_size). At Bitcoin's ~4MB block size with thousands of transactions, DP is infeasible. Greedy with fee density is the industry standard (and what Bitcoin Core actually uses as a starting heuristic).

```java
List<String> mineBlock(List<Transaction> transactions, int blockSize) {
    List<Transaction> sorted = new ArrayList<>(transactions);
    sorted.sort((a, b) -> Double.compare((double) b.fee / b.size, (double) a.fee / a.size));

    List<String> selected = new ArrayList<>();
    int remaining = blockSize;
    for (Transaction tx : sorted) {
        if (tx.size <= remaining) {
            selected.add(tx.id);
            remaining -= tx.size;
        }
    }
    return selected;
}
```

**Example:**
```
tx1: size=30, fee=60  → ratio 2.0
tx2: size=50, fee=200 → ratio 4.0
tx3: size=40, fee=100 → ratio 2.5
tx4: size=20, fee=30  → ratio 1.5
tx5: size=10, fee=50  → ratio 5.0

block_size=100
Sorted: tx5, tx2, tx3, tx1, tx4
Pick tx5 (rem=90) → tx2 (rem=40) → tx3 (rem=0)
Result: ["tx5", "tx2", "tx3"], fee=350
```

**Complexity:** O(N log N) time, O(N) space.

### Level 2

**Core Idea:** To include a transaction, you must include its entire ancestor chain (up to the first already-included ancestor). Evaluate each candidate as a `(chain, ratio)` pair where ratio = sum(fees in chain) / sum(sizes in chain). Greedily pick the chain with the best ratio, then repeat (picking one chain changes the effective cost of descendant chains).

**Data Structures:** `txMap` for O(1) parent lookup, `included` set to track what's already in the block.

**Key Decisions:** The iterative approach is necessary because after including a chain, descendants become cheaper (their ancestors are already paid for), which changes their ratios. You must re-evaluate after each pick.

```java
List<String> mineBlockWithDeps(List<Transaction> transactions, int blockSize) {
    Map<String, Transaction> txMap = new HashMap<>();
    for (Transaction tx : transactions) txMap.put(tx.id, tx);

    Set<String> included = new HashSet<>();
    List<String> selected = new ArrayList<>();
    int remaining = blockSize;

    while (true) {
        double bestRatio = -1;
        List<String> bestChain = null;

        for (Transaction tx : transactions) {
            if (included.contains(tx.id)) continue;
            List<String> chain = ancestorChain(tx.id, txMap, included);
            if (chain.isEmpty()) continue;

            int totalSize = 0, totalFee = 0;
            for (String tid : chain) {
                totalSize += txMap.get(tid).size;
                totalFee  += txMap.get(tid).fee;
            }
            if (totalSize > remaining) continue;

            double ratio = (double) totalFee / totalSize;
            if (ratio > bestRatio) {
                bestRatio = ratio;
                bestChain = chain;
            }
        }

        if (bestChain == null) break;

        for (String tid : bestChain) {
            included.add(tid);
            selected.add(tid);
            remaining -= txMap.get(tid).size;
        }
    }
    return selected;
}

private List<String> ancestorChain(String txId, Map<String, Transaction> txMap, Set<String> included) {
    List<String> chain = new ArrayList<>();
    String cur = txId;
    while (cur != null && !included.contains(cur)) {
        chain.add(cur);
        cur = txMap.get(cur).parentId;
    }
    Collections.reverse(chain); // root-first
    return chain;
}
```

**Step-through example:**
```
Tree:
  tx1(30,10) ─┬─ tx2(20,80) ─┬─ tx3(10,50)
               │               └─ tx4(10,40)
               └─ tx5(20,20)
tx6(15,90)  [independent]

block_size=100

Iteration 1: Best chain by ratio
  tx6 alone → ratio 6.0     ← winner
  tx3 via [tx1,tx2,tx3] → 140/60 = 2.33
Pick tx6. remaining=85.

Iteration 2:
  [tx1,tx2,tx3] → ratio 2.33  ← winner
Pick chain. remaining=25. tx1,tx2,tx3 now included.

Iteration 3: tx1,tx2 already included, so:
  tx4 costs just itself → ratio 40/10 = 4.0  ← winner
  tx5 costs just itself → ratio 20/20 = 1.0
Pick tx4. remaining=15.

Iteration 4: tx5 needs size 20 > 15. Stop.

Result: ["tx6","tx1","tx2","tx3","tx4"]
```

**Complexity:** O(N² × D) where D = max tree depth. In practice D is small (Bitcoin's typical mempool trees are shallow).

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Mempool scale:** Real mempools hold tens of thousands of transactions. The O(N²×D) dependency solution is too slow for a full mempool scan per iteration. Bitcoin Core uses a modified approach: pre-compute "package fee rates" for all ancestor sets, store them in a sorted structure, and update only the affected descendants when a package is selected.
- **Conflicts (double-spend):** Real transactions can conflict — two transactions spending the same UTXO. The miner must pick at most one. This adds a constraint satisfaction layer on top of the knapsack.
- **Dynamic arrivals:** The mempool is constantly changing. The selection algorithm runs under time pressure (Bitcoin has ~10s to mine a block). This favors faster heuristics over exact algorithms.
- **Fee bumping (RBF/CPFP):** Bitcoin supports Replace-By-Fee (a child with higher fee can "pull in" a stuck parent) and Child-Pays-For-Parent. Both are exactly the dependency logic in Level 2 but with replacement semantics.

### Common Interview Traps

- **Forgetting to re-evaluate after picking a chain:** Ratios change when ancestors become free. A single-pass greedy sort doesn't work for Level 2.
- **Not reversing the ancestor chain:** `ancestorChain` walks child → root; you must insert root-first or the dependency order is violated.
- **Ancestor chain double-counting:** If tx1 and tx2 both appear as candidates, their shared ancestor (tx1) would be counted once when evaluating tx2's chain. The `included` check prevents this but candidates can still share ancestors — the algorithm handles this correctly because only one chain is selected per iteration.
- **Division by zero:** A transaction with `size=0` would panic. Worth noting as an edge case even if the interviewer doesn't ask.

### How to Push Forward as Staff+

- Mention DP trade-offs unprompted: "If block_size is small (say ≤ 10,000 bytes), DP becomes tractable at O(N × block_size) and gives the optimal solution. The right choice depends on the block size constant."
- Propose the priority queue optimization: rather than re-scanning all transactions each iteration, maintain a max-heap keyed on package fee rate. After selecting a package, only update the ratios for direct children — O(children × log N) instead of O(N).
- Connect to Coinbase context: Coinbase's exchange uses a similar problem space for order batching and gas fee optimization in Ethereum transactions. The dependency problem is isomorphic to Ethereum's EIP-1559 blob fee markets.
- Ask whether the interviewer wants approximate (greedy) or optimal (DP) — framing this as a conscious engineering trade-off signals seniority.
