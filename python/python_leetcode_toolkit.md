
# Python Companion to the LeetCode Study Plan

> Use alongside your existing 4-week plan (same ~106 problems, same priorities, same companies). This layer swaps Java idioms for Python: the stdlib toolkit per topic, ready templates, and Python-specific gotchas. Problem numbers are unchanged — only the language mechanics differ.

---

## The Interview Import Header

Start every Python solution with what you'll actually reach for:

```python
from collections import defaultdict, Counter, deque, OrderedDict
import heapq
import bisect
from functools import lru_cache
import math   # math.inf, math.isclose, math.gcd
```

State the assumption if you use `sortedcontainers` (SortedList/SortedDict) — it's the `TreeMap`/`TreeSet` replacement and not in the stdlib.

---

## Per-Topic Python Toolkit

| Topic (from your plan) | Python tools | Watch out |
|---|---|---|
| Hash Maps / Counting | `dict`, `defaultdict`, `Counter`, `set` | Don't rely on dict order being *sorted*; it's insertion order |
| Design (LRU/LFU/etc.) | `OrderedDict`, `dict`+DLL, `deque(maxlen=)` | `OrderedDict.move_to_end` / `popitem(last=False)` = LRU in 10 lines |
| Sliding Window | `Counter`, two indices, `enumerate` | Shrink with `while`, not `if`; track a `formed` count |
| Prefix Sum | `defaultdict(int)`, running sum | Python `%` is already non-negative — no `((x%k)+k)%k` |
| Graphs (BFS/DFS/Topo) | `deque`, `defaultdict(list)`, `set` visited | Recursion limit 1000 — deep DFS needs explicit stack or `setrecursionlimit` |
| Union Find | parent `list` / `dict` + path compression | Implement `find`/`union` by hand; no stdlib DSU |
| Intervals / Greedy | `sorted(key=lambda x: x[0])`, `heapq` | `.sort()` returns `None`; sort in place then iterate |
| Heaps / Top-K | `heapq`, `nlargest`/`nsmallest` | Min-heap only; negate for max; add tie-break counter |
| Binary Search | `bisect_left`/`bisect_right`, hand-rolled | No overflow — `(lo+hi)//2` is safe |
| DP | `list`, 2D via `[[0]*n for _ in range(m)]`, `@lru_cache` | `[[0]*n]*m` aliases rows — bug; memo args must be hashable |
| Backtracking | recursion + `path` list, `nonlocal`/append | Copy the path (`res.append(path[:])`) — don't store the mutable ref |
| Linked List | build a small `ListNode` class | No stdlib; dummy-head node simplifies edges |
| Matrix | `[[...] for _ in range(m)]`, `zip(*grid)` transpose | `list(zip(*grid))` transposes; rotate = transpose + reverse rows |
| Bit Manipulation | `bin(n).count("1")`, `n & (n-1)`, `x ^ y` | Ints are arbitrary precision; no unsigned shift |
| Concurrency | `threading` (Sem/Lock/Barrier/Condition), `asyncio` | GIL: threads = concurrency not parallelism; see playbook |

---

## Week-by-Week Python Notes

### Week 1 — Hash Maps + Sliding Window + Prefix Sum

* **Counting:** `Counter(iterable)` beats manual dicts; `.most_common(k)` for top-K frequency (LC 347).
* **Group anagrams (49):** `defaultdict(list)` keyed by `"".join(sorted(s))`.
* **LRU (146):** `OrderedDict` (see patterns doc) — the cleanest Python answer.
* **GetRandom O(1) (380):** `dict` val→index + `list`, swap-with-last on delete, `random.choice(self.list)`.
* **Subarray sum = k (560):** prefix sum + `defaultdict(int)`; remember Python modulo is non-negative (helps 523/974).

### Week 2 — Graphs + Topo Sort + Union Find

* **Adjacency:** `graph = defaultdict(list); graph[u].append(v)` — no null checks.
* **BFS:** always `collections.deque` + `popleft()`, never `list.pop(0)`.
* **DFS depth:** watch the 1000-frame recursion limit on large inputs (Word Ladder, big grids) — convert to an iterative stack or raise it.
* **Union Find:** hand-roll `find` with path compression and `union` by rank; store parents in a `list` (index nodes) or `dict` (string nodes like Accounts Merge 721).
* **Trie (208/212/1166):** dict-of-dicts with `setdefault` (see playbook). Visited sets over `(r, c)` tuples for grids.

### Week 3 — DP + Intervals + Greedy

* **Memoization:** top-down `@lru_cache(maxsize=None)` on a recursive function is often the fastest to write — ensure args are hashable (pass indices/tuples, not lists).
* **2D tables:** `dp = [[0]*(n+1) for _ in range(m+1)]` — never `[[0]*n]*m` (row aliasing bug).
* **Intervals:** `intervals.sort(key=lambda x: x[0])`; Meeting Rooms II (253) = min-heap of end times.
* **Greedy tie-breaks:** sort with tuple keys, negating numeric fields for mixed asc/desc order.

### Week 4 — Heaps + Stacks + Binary Search + Backtracking + Concurrency

* **Heaps:** `heapq` min-heap; max-heap via negation; `(priority, counter, payload)` tuples to avoid comparing payloads (Merge K Lists 23, Median Stream 295).
* **Top-K:** `heapq.nlargest(k, data, key=...)` is a one-liner.
* **Monotonic stack (84/739):** a `list`; store indices; a trailing sentinel simplifies the flush.
* **Binary search on answer (Koko 875, Split Array 410):** clean in Python — no overflow, `//` for mid.
* **Backtracking:** append a **copy** of the path (`res.append(path[:])`); pop on the way out.
* **Concurrency (1188/1117/1116):** use `threading` semaphores/barriers (full solutions in the Python Playbook). For OpenAI-style async questions, mention `asyncio` primitives too.

---

## Python-Specific Gotchas That Cost Points

* `list.pop(0)` is O(n) — use `deque` for queues/BFS.
* `[[0]*n]*m` aliases every row — use a comprehension.
* `.sort()` returns `None`; `sorted()` returns a new list.
* Deep recursion hits the 1000-frame limit — say so and handle it.
* Floor division `//` floors toward −∞ (`-7//2 == -4`); use `int(a/b)` for truncate-toward-zero (RPN, Calculator).
* Modulo is already non-negative — simpler than Java for prefix-sum-mod problems.
* No `TreeMap`/`TreeSet` in stdlib — use `bisect`+list, `sortedcontainers`, or a heap, and state the choice.
* Backtracking must store copies of the mutable path, not the reference.

---

## Study Tips (Python edition)

1. **Time yourself** — 25 min Medium, 35 min Hard.
2. **Lean on the stdlib** — reaching for `Counter`/`deque`/`heapq`/`bisect` is a fluency signal, not cheating. Know each one's complexity.
3. **Explain out loud** — at staff+ level, communication matters as much as the solution.
4. **Clean Medium > messy Hard.**
5. **Re-solve 2–3 earlier problems weekly** without notes.

Same review-exam set and scoring guide from your existing plan apply unchanged — just solve them in Python using the toolkit above.
