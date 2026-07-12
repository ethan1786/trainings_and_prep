
# LC Patterns — Python Quick Reference

> Skim for pattern recognition. Same pattern map as the Java version, with idiomatic Python templates and stdlib callouts.

---

## Quick Reference — "What pattern is this?"

| Signal in problem | Pattern | Python tools |
|---|---|---|
| "Substring"/"subarray" with constraint | Sliding window | `dict`/`Counter`, two indices |
| "All pairs" or "sorted input" | Two pointers | `l`, `r` indices |
| "Nested"/"matching brackets" | Stack | `list` |
| "Top K"/"Kth largest" | Heap | `heapq`, `heapq.nlargest` |
| "Shortest path"/"level by level" | BFS | `collections.deque` |
| "All paths"/"combinations" | DFS / backtracking | recursion + `nonlocal`/list |
| "Dependencies"/"ordering" | Topological sort | `deque` + in-degree `dict` |
| "Overlapping intervals" | Sort + sweep | `sorted(key=...)` |
| "Lookup/grouping" | HashMap | `dict`, `defaultdict`, `Counter` |
| "Sorted + search" | Binary search | `bisect` |
| "Optimal substructure" | DP | `list`, `@lru_cache` |

---

## String Parsing

| LC # | Problem | Key Insight (Python) |
|---|---|---|
| 71 | Simplify Path | `path.split("/")`, push to `list`, skip `""`/`"."`, `pop()` for `".."` |
| 468 | Validate IP Address | `s.split(".")` / `s.split(":")`, validate each segment |
| 8 | String to Integer | Strip, sign, accumulate; ints don't overflow but clamp to `[-2**31, 2**31-1]` |
| 394 | Decode String | Stack of `(str, count)`; on `]` pop and repeat |
| 227 | Basic Calculator II | Stack of values; apply `*`/`/` immediately, `sum()` at end. Use `int(a/b)` for trunc-toward-zero division (not `//`, which floors) |
| 722 | Remove Comments | State machine across lines for block comments |

Note: `"abc"[1:1] == ""` (empty slice, no error). `s.split(".")` splits on the literal `.` (not regex, unlike Java).

---

## HashMap / Counting

| LC # | Problem | Key Insight (Python) |
|---|---|---|
| 1 | Two Sum | `dict` value→index; check `complement in seen` before inserting |
| 49 | Group Anagrams | `defaultdict(list)`, key = `"".join(sorted(s))` |
| 347 | Top K Frequent | `Counter(nums).most_common(k)`, or bucket sort O(N) |
| 560 | Subarray Sum = K | Prefix sum + `defaultdict(int)`; `count += seen[prefix - k]` |
| 128 | Longest Consecutive | `set(nums)`; start counting only when `num-1 not in s` |
| 380 | Insert Delete GetRandom O(1) | `dict` val→index + `list`; swap-with-last before pop; `random.choice` |

---

## Stack

| LC # | Problem | Key Insight (Python) |
|---|---|---|
| 20 | Valid Parentheses | `list` as stack + `dict` of pairs; empty at end = valid |
| 155 | Min Stack | Store `(val, cur_min)` tuples in one `list` |
| 739 | Daily Temperatures | Monotonic-decreasing stack of indices |
| 84 | Largest Rectangle | Monotonic-increasing stack; sentinel `0` simplifies flush |
| 150 | Evaluate RPN | Push nums; on op pop two, compute (`int(a/b)` for division) |

---

## Sliding Window

| LC # | Problem | Key Insight |
|---|---|---|
| 3 | Longest Substring w/o Repeating | `set` + left pointer; shrink until dup removed |
| 76 | Minimum Window Substring | `Counter` target; expand right, shrink left; track `formed` |
| 424 | Longest Repeating Char Replacement | window − max_freq ≤ k |
| 239 | Sliding Window Maximum | Monotonic-decreasing `deque` of indices |
| 567 | Permutation in String | Fixed window; compare `Counter`s |

**Template:**
```python
from collections import Counter
need = Counter(t)
window = Counter()
left = formed = 0
for right, ch in enumerate(s):
    window[ch] += 1
    if window[ch] <= need[ch]:
        formed += 1
    while formed == len(t):          # window valid → try to shrink
        update_answer(left, right)
        window[s[left]] -= 1
        if window[s[left]] < need[s[left]]:
            formed -= 1
        left += 1
```

---

## Two Pointers

| LC # | Problem | Key Insight |
|---|---|---|
| 15 | 3Sum | `nums.sort()`; fix one, two pointers; skip dups |
| 11 | Container With Most Water | Move the shorter side inward |
| 42 | Trapping Rain Water | Two pointers + `left_max`/`right_max` |
| 125 | Valid Palindrome | `l`/`r` inward; `c.isalnum()`, `.lower()` |
| 167 | Two Sum II (sorted) | `l`/`r`; sum too small → `l += 1`, too big → `r -= 1` |

---

## Intervals

| LC # | Problem | Key Insight |
|---|---|---|
| 56 | Merge Intervals | `intervals.sort(key=lambda x: x[0])`; extend if overlap |
| 57 | Insert Interval | Add before, merge overlapping, add after |
| 253 | Meeting Rooms II | Sort starts; min-heap of end times; heap size = rooms |
| 435 | Non-overlapping | Sort by end; greedily keep earliest-ending |

---

## Graph / BFS / DFS

| LC # | Problem | Key Insight |
|---|---|---|
| 200 | Number of Islands | DFS/BFS each `'1'`; mark visited (mutate grid or `set`) |
| 207 | Course Schedule | Topo sort; in-degree `dict`; BFS from in-degree 0 |
| 994 | Rotting Oranges | Multi-source BFS; seed all rotten in the `deque` |
| 133 | Clone Graph | BFS/DFS + `dict` original→clone |
| 210 | Course Schedule II | Topo sort collecting order |

**BFS template:**
```python
from collections import deque
q = deque([start])
visited = {start}
while q:
    node = q.popleft()
    for nb in graph[node]:
        if nb not in visited:
            visited.add(nb)
            q.append(nb)
```

**Topological sort template:**
```python
from collections import deque, defaultdict
indeg = defaultdict(int)
for u in graph:
    for v in graph[u]:
        indeg[v] += 1
q = deque([n for n in graph if indeg[n] == 0])
order = []
while q:
    n = q.popleft(); order.append(n)
    for v in graph[n]:
        indeg[v] -= 1
        if indeg[v] == 0:
            q.append(v)
# len(order) != num_nodes → cycle
```

Remember: default recursion limit is 1000 — for deep DFS use an explicit stack or raise the limit.

---

## Binary Search

| LC # | Problem | Key Insight |
|---|---|---|
| 33 | Search in Rotated Array | Find sorted half; decide side |
| 34 | First/Last Position | `bisect_left` and `bisect_right` |
| 153 | Find Min in Rotated | If `mid > right` → min in right half |
| 981 | Time-Based KV Store | `dict` + `bisect` on timestamp list |

**Template (no overflow concerns — ints are arbitrary precision):**
```python
lo, hi = 0, len(a) - 1
while lo <= hi:
    mid = (lo + hi) // 2          # safe in Python; still fine to write lo + (hi-lo)//2
    if condition(a[mid]):
        hi = mid - 1
    else:
        lo = mid + 1
```
The stdlib `bisect` module often replaces hand-rolled search: `bisect_left`/`bisect_right`.

---

## Heap / Priority Queue

| LC # | Problem | Key Insight (Python) |
|---|---|---|
| 347 | Top K Frequent | `heapq.nlargest(k, cnt, key=cnt.get)` or bucket sort |
| 253 | Meeting Rooms II | Min-heap of end times |
| 295 | Median from Stream | Max-heap (negated) left + min-heap right |
| 23 | Merge K Sorted Lists | Heap of `(val, i, node)` — include index to break ties |
| 215 | Kth Largest | Min-heap size k, or `heapq.nlargest`, or quickselect |

Tie-break tuples with an index/counter so Python never compares non-orderable payloads: `heapq.heappush(h, (priority, next(counter), item))`.

---

## Tree / Recursion

| LC # | Problem | Key Insight |
|---|---|---|
| 104 | Max Depth | `1 + max(left, right)`; base `None → 0` |
| 226 | Invert Tree | Swap children recursively |
| 236 | LCA | If root is p or q → root; both sides non-None → root |
| 98 | Validate BST | Pass `(low, high)` bounds down |
| 102 | Level Order | BFS; `len(queue)` at each level start |

---

## Dynamic Programming

| LC # | Problem | Key Insight (Python) |
|---|---|---|
| 70 | Climbing Stairs | `dp[i] = dp[i-1] + dp[i-2]` |
| 322 | Coin Change | `dp[a] = min(dp[a-c]+1)`; init `float("inf")` |
| 139 | Word Break | `dp[i] |= dp[j] and s[j:i] in words` |
| 300 | LIS | O(n²) DP, or `bisect.insort` patience sort O(n log n) |
| 53 | Max Subarray | Kadane: `cur = max(x, cur + x)` |

Top-down memo is often cleanest in Python: `@functools.lru_cache(maxsize=None)` on a recursive function (make args hashable — tuples, not lists).

---

## Design / OOD

| LC # | Problem | Key Insight (Python) |
|---|---|---|
| 146 | LRU Cache | `collections.OrderedDict` + `move_to_end` / `popitem(last=False)` |
| 460 | LFU Cache | `dict` key→node + `defaultdict(OrderedDict)` freq→nodes + `min_freq` |
| 355 | Design Twitter | `defaultdict` followees + tweets; `heapq.merge` for feed |
| 362 | Design Hit Counter | `deque(maxlen=...)` of timestamps, or ring buffer `[0]*300` |
| 1166 | Design File System | `dict` path→value; check parent exists on create |

**LRU in ~10 lines with `OrderedDict`:**
```python
from collections import OrderedDict
class LRUCache:
    def __init__(self, cap): self.cap = cap; self.d = OrderedDict()
    def get(self, k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        if k in self.d: self.d.move_to_end(k)
        self.d[k] = v
        if len(self.d) > self.cap: self.d.popitem(last=False)
```
