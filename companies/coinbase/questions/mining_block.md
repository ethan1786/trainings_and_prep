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

```python
class Transaction:
    def __init__(self, id: str, size: int, fee: int):
        self.id = id
        self.size = size
        self.fee = fee

def mine_block(transactions: list[Transaction], block_size: int) -> list[str]:
    """
    Select transactions to maximize total fee within block_size.
    Scalable solution preferred over mathematically optimal.
    Returns list of selected transaction IDs.
    """
```

### Level 2: Transactions with Parent Dependencies

A child transaction cannot be mined unless its parent is also in the same block. Each child has at most one parent; a parent may have multiple children.

```python
class Transaction:
    def __init__(self, id: str, size: int, fee: int, parent_id: str | None = None):
        self.id = id
        self.size = size
        self.fee = fee
        self.parent_id = parent_id

def mine_block_with_deps(transactions: list[Transaction], block_size: int) -> list[str]:
    """
    Select transactions respecting parent dependencies to maximize fee.
    To include a child, all ancestors must also be included.
    """
```

---

## Solution Approach

### Level 1

**Core Idea:** Greedy by fee density (fee/size ratio descending). Not always optimal, but O(N log N) and practical for production-scale mempools.

**Key Decisions:** The mathematically optimal solution is 0/1 Knapsack DP at O(N × block_size). At Bitcoin's ~4MB block size with thousands of transactions, DP is infeasible. Greedy with fee density is the industry standard (and what Bitcoin Core actually uses as a starting heuristic).

```python
def mine_block(transactions: list[Transaction], block_size: int) -> list[str]:
    sorted_txs = sorted(transactions, key=lambda tx: tx.fee / tx.size, reverse=True)
    selected = []
    remaining = block_size
    for tx in sorted_txs:
        if tx.size <= remaining:
            selected.append(tx.id)
            remaining -= tx.size
    return selected
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

**Data Structures:** `tx_map` for O(1) parent lookup, `included` set to track what's already in the block.

**Key Decisions:** The iterative approach is necessary because after including a chain, descendants become cheaper (their ancestors are already paid for), which changes their ratios. You must re-evaluate after each pick.

```python
def mine_block_with_deps(transactions: list[Transaction], block_size: int) -> list[str]:
    tx_map = {tx.id: tx for tx in transactions}
    included = set()
    selected = []
    remaining = block_size

    def ancestor_chain(tx_id):
        """Walk up to the first already-included ancestor (exclusive)."""
        chain = []
        cur = tx_id
        while cur and cur not in included:
            chain.append(cur)
            cur = tx_map[cur].parent_id
        return list(reversed(chain))  # root-first

    while True:
        best_ratio, best_chain = -1, None
        for tx in transactions:
            if tx.id in included:
                continue
            chain = ancestor_chain(tx.id)
            if not chain:
                continue
            total_size = sum(tx_map[tid].size for tid in chain)
            total_fee  = sum(tx_map[tid].fee  for tid in chain)
            if total_size > remaining:
                continue
            ratio = total_fee / total_size
            if ratio > best_ratio:
                best_ratio, best_chain = ratio, chain

        if best_chain is None:
            break

        for tid in best_chain:
            included.add(tid)
            selected.append(tid)
            remaining -= tx_map[tid].size

    return selected
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
- **Not reversing the ancestor chain:** `ancestor_chain` walks child → root; you must insert root-first or the dependency order is violated.
- **Ancestor chain double-counting:** If tx1 and tx2 both appear as candidates, their shared ancestor (tx1) would be counted once when evaluating tx2's chain. The `included` check prevents this but candidates can still share ancestors — the algorithm handles this correctly because only one chain is selected per iteration.
- **Division by zero:** A transaction with `size=0` would panic. Worth noting as an edge case even if the interviewer doesn't ask.

### How to Push Forward as Staff+

- Mention DP trade-offs unprompted: "If block_size is small (say ≤ 10,000 bytes), DP becomes tractable at O(N × block_size) and gives the optimal solution. The right choice depends on the block size constant."
- Propose the priority queue optimization: rather than re-scanning all transactions each iteration, maintain a max-heap keyed on package fee rate. After selecting a package, only update the ratios for direct children — O(children × log N) instead of O(N).
- Connect to Coinbase context: Coinbase's exchange uses a similar problem space for order batching and gas fee optimization in Ethereum transactions. The dependency problem is isomorphic to Ethereum's EIP-1559 blob fee markets.
- Ask whether the interviewer wants approximate (greedy) or optimal (DP) — framing this as a conscious engineering trade-off signals seniority.
