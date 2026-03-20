# Interview Playbook — Patterns, Data Structures & Tricks

> Quick-reference for staff+ level SWE interviews. Organized by **pattern** first, **data structure** second.

---

## Table of Contents

1. [Pattern Recognition Decision Tree](#pattern-recognition-decision-tree)
2. [Two Pointers](#two-pointers)
3. [Sliding Window](#sliding-window)
4. [Binary Search](#binary-search)
5. [Intervals](#intervals)
6. [Greedy](#greedy)
7. [Dynamic Programming](#dynamic-programming)
8. [Backtracking](#backtracking)
9. [Graph Algorithms](#graph-algorithms)
10. [Union-Find](#union-find)
11. [Topological Sort](#topological-sort)
12. [Linked List Tricks](#linked-list-tricks)
13. [Stack Patterns](#stack-patterns)
14. [Heap / Priority Queue Patterns](#heap--priority-queue-patterns)
15. [Bit Manipulation](#bit-manipulation)
16. [Matrix Tricks](#matrix-tricks)
17. [Minor Patterns & One-Trick Techniques](#minor-patterns--one-trick-techniques)
18. [Data Structures Reference](#data-structures-reference)

---

## Pattern Recognition Decision Tree

```
What does the problem ask?
│
├── "Optimal path / min cost / count ways" + indices only go forward
│   └── DP (define state → recurrence → base case → fill table)
│
├── "Find pair / subarray" in sorted or linear data
│   ├── Sorted → Two Pointers
│   └── Contiguous subarray with constraint → Sliding Window
│
├── "Search in sorted / monotonic" space
│   └── Binary Search
│
├── "Merge / overlap / schedule" time ranges
│   ├── Combine overlapping → Sort by start + merge
│   ├── Max concurrent → Sweep line or min-heap
│   └── Max non-overlapping → Sort by end + greedy
│
├── "Shortest path / reachability / connectivity"
│   ├── Unweighted → BFS
│   ├── Weighted, no negative → Dijkstra
│   ├── Weighted, negative → Bellman-Ford
│   └── Connectivity / grouping → Union-Find
│
├── "Dependencies / ordering"
│   └── Topological Sort (Kahn's BFS)
│
├── "Generate all valid combinations / permutations"
│   └── Backtracking
│
├── "Next greater / smaller element" or "largest rectangle"
│   └── Monotonic Stack
│
└── "Top K / median / merge K sorted"
    └── Heap (PriorityQueue)
```

---

## Two Pointers

### When to Use
- Sorted array: find pair with target sum, remove duplicates, merge
- Linked list: find middle, detect cycle, find kth from end
- String: palindrome check, reverse

### Patterns

**Opposite ends** (sorted array, target sum):
```java
int lo = 0, hi = nums.length - 1;
while (lo < hi) {
    int sum = nums[lo] + nums[hi];
    if (sum == target) return new int[]{lo, hi};
    else if (sum < target) lo++;
    else hi--;
}
```

**Same direction** (remove duplicates in-place):
```java
int slow = 0;
for (int fast = 1; fast < nums.length; fast++) {
    if (nums[fast] != nums[slow]) {
        nums[++slow] = nums[fast];
    }
}
return slow + 1;
```

**Trapping Rain Water** (LC 42 — two pointer with max tracking):
```java
int lo = 0, hi = n - 1, leftMax = 0, rightMax = 0, water = 0;
while (lo < hi) {
    if (height[lo] < height[hi]) {
        leftMax = Math.max(leftMax, height[lo]);
        water += leftMax - height[lo++];
    } else {
        rightMax = Math.max(rightMax, height[hi]);
        water += rightMax - height[hi--];
    }
}
```

### Key Problems
| Problem | Trick |
|---|---|
| LC 1 (Two Sum) | HashMap for unsorted; two pointers if sorted |
| LC 11 (Container With Most Water) | Shrink the shorter side |
| LC 42 (Trapping Rain Water) | Track leftMax/rightMax from both ends |
| LC 15 (3Sum) | Sort + fix one + two pointers for remaining |

### Common Pitfalls
- **Forgetting to sort first** — two pointers on unsorted array gives wrong results
- **Off-by-one with `lo < hi` vs `lo <= hi`** — use `lo < hi` when pointers must be distinct elements
- **Skipping duplicates in 3Sum** — must skip *after* finding a match, not before: `while (lo < hi && nums[lo] == nums[lo+1]) lo++`
- **Modifying array when you shouldn't** — sorting mutates input; check if that's allowed

---

## Sliding Window

### When to Use
- "Longest/shortest **contiguous** subarray/substring with constraint"
- The constraint can be checked incrementally (add right, shrink left)

### Template

```java
int left = 0;
// expand right boundary
for (int right = 0; right < n; right++) {
    // add nums[right] to window state

    // shrink from left while constraint is violated
    while (/* constraint violated */) {
        // remove nums[left] from window state
        left++;
    }
    // update answer (window is [left, right])
}
```

### Key Problems
| Problem | Window Condition |
|---|---|
| LC 3 (Longest Substring Without Repeating) | All chars unique (use Set or freq map) |
| LC 76 (Minimum Window Substring) | Window contains all chars of t (use freq map + count) |
| LC 239 (Sliding Window Maximum) | Fixed-size window, use monotonic deque |
| LC 1438 (Longest Subarray with Abs Diff ≤ K) | Use two TreeMaps or two monotonic deques |

### Trick: Fixed vs Variable Window
- **Variable**: shrink left when constraint violated → find min/max length
- **Fixed** (size k): just slide, no shrinking logic

### Common Pitfalls
- **Forgetting to remove left element from state** when shrinking — e.g., decrement freq map, remove from set
- **Updating answer at the wrong place** — for "longest", update *after* shrinking; for "shortest", update *during* shrinking
- **Using `if` instead of `while` for shrinking** — may need to shrink multiple times
- **Off-by-one in window size** — window `[left, right]` has size `right - left + 1`

---

## Binary Search

### When to Use
- Sorted array search
- "Minimize the maximum" / "maximize the minimum" → binary search on answer
- Find boundary (first/last occurrence)

### Templates

**Standard** (find exact value):
```java
int lo = 0, hi = nums.length - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (nums[mid] == target) return mid;
    else if (nums[mid] < target) lo = mid + 1;
    else hi = mid - 1;
}
return -1;
```

**Left boundary** (first element ≥ target):
```java
int lo = 0, hi = nums.length;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (nums[mid] < target) lo = mid + 1;
    else hi = mid;
}
return lo;  // first index where nums[i] >= target
```

**Binary search on answer** (LC 410, 875, etc.):
```java
int lo = minPossible, hi = maxPossible;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (feasible(mid)) hi = mid;    // try smaller
    else lo = mid + 1;              // need bigger
}
return lo;
```

### Key Problems
| Problem | Trick |
|---|---|
| LC 33 (Search Rotated Sorted Array) | Determine which half is sorted, then narrow |
| LC 4 (Median of Two Sorted Arrays) | Binary search on partition of shorter array |
| LC 528 (Random Pick with Weight) | Prefix sum + binary search for random value |

### Trick: Rotated Array (LC 33)
One half is always sorted. Check which, then decide if target is in that half.
```java
if (nums[lo] <= nums[mid]) {  // left half sorted
    if (nums[lo] <= target && target < nums[mid]) hi = mid - 1;
    else lo = mid + 1;
} else {                       // right half sorted
    if (nums[mid] < target && target <= nums[hi]) lo = mid + 1;
    else hi = mid - 1;
}
```

### Common Pitfalls
- **`lo <= hi` vs `lo < hi`** — exact search uses `<=`; boundary search uses `<`. Mixing them causes infinite loops or missed elements
- **Integer overflow in `lo + hi`** — always use `lo + (hi - lo) / 2`
- **Wrong initial `hi`** — `nums.length - 1` (inclusive) vs `nums.length` (exclusive). Must match your loop condition
- **Rotated array: `<=` vs `<`** in `nums[lo] <= nums[mid]` — the `=` handles the case where `lo == mid` (2-element subarray)
- **Search on answer: wrong feasibility direction** — if `feasible(mid)` means "mid is big enough", then `hi = mid`; if "mid is too small", then `lo = mid + 1`

---

## Intervals

### Rule #1: Always Sort First

### Four Patterns

**1. Merge overlapping** (LC 56) — sort by start:
```java
Arrays.sort(intervals, (a, b) -> a[0] - b[0]);
List<int[]> result = new ArrayList<>();
int[] curr = intervals[0];
result.add(curr);
for (int i = 1; i < intervals.length; i++) {
    if (intervals[i][0] <= curr[1]) curr[1] = Math.max(curr[1], intervals[i][1]);
    else { curr = intervals[i]; result.add(curr); }
}
```

**2. Insert interval** (LC 57) — three phases:
```java
// Phase 1: add all before newInterval
// Phase 2: merge all overlapping with newInterval
// Phase 3: add all after
```

**3. Count max concurrent / sweep line** (LC 253) — sort starts and ends separately:
```java
Arrays.sort(start);
Arrays.sort(end);
int s = 0, e = 0, count = 0, max = 0;
while (s < n) {
    if (start[s] < end[e]) { count++; max = Math.max(max, count); s++; }
    else { count--; e++; }
}
```

**4. Greedy selection** (LC 435) — sort by END time:
```java
Arrays.sort(intervals, (a, b) -> a[1] - b[1]);  // sort by END
int kept = 1, lastEnd = intervals[0][1];
for (int i = 1; i < intervals.length; i++) {
    if (intervals[i][0] >= lastEnd) { kept++; lastEnd = intervals[i][1]; }
}
return intervals.length - kept;
```

### Sort by Start vs End
| Sort By | Pattern | Use When |
|---|---|---|
| **Start** | Merge / sweep | Combine overlapping, count concurrent |
| **End** | Greedy selection | Maximize kept / minimize removals |

### Key Problems
| Problem | Pattern |
|---|---|
| LC 56 (Merge Intervals) | Sort by start + merge |
| LC 57 (Insert Interval) | Three-phase insert |
| LC 253 (Meeting Rooms II) | Sweep line or min-heap |
| LC 435 (Non-overlapping) | Sort by end + greedy |
| LC 1235 (Job Scheduling) | Sort by end + DP + binary search |

### Common Pitfalls
- **Forgetting to sort** — interval problems almost always need sorting first
- **Sort by start vs end** — wrong sort order gives wrong results. Merge = start, greedy selection = end
- **`<=` vs `<` for overlap** — `[1,3]` and `[3,5]`: do they overlap? Depends on problem definition. Check carefully
- **Mutating the input array** during merge — the `curr[1] = Math.max(...)` trick works because `result` holds a reference to `curr`
- **Sweep line: `<` vs `<=` for simultaneous start/end** — if a meeting ends at 10 and another starts at 10, do they need the same room? Read the problem

---

## Greedy

### When to Use
- Locally optimal choice leads to globally optimal — **no need to explore all options**
- Often involves sorting + single pass

### Key Insight
Greedy works when **you can prove** the local choice never hurts the global answer. If items have different values/weights, you usually need DP instead.

### Key Problems
| Problem | Greedy Choice |
|---|---|
| LC 435 (Non-overlapping Intervals) | Keep earliest-ending interval |
| LC 621 (Task Scheduler) | Schedule most frequent task first, fill gaps |
| LC 134 (Gas Station) | If total gas ≥ total cost, solution exists. Start where running sum is lowest |
| LC 55 (Jump Game) | Track farthest reachable index |

### Common Pitfalls
- **Can't prove the greedy choice is safe** — if you can't explain in one sentence why the local choice doesn't hurt, it's probably DP instead
- **Greedy on the wrong dimension** — e.g., sorting by start instead of end for interval scheduling
- **Missing the "total feasibility" check** — LC 134: must verify `totalGas >= totalCost` before claiming a solution exists

---

## Dynamic Programming

### The Mental Model

```
1. Define state:  dp[i] or dp[i][j] — what subproblem does this represent?
2. Recurrence:    dp[i][j] = f(smaller subproblems) — how to build from known answers?
3. Base case:     dp[0] = ? — what are the trivial answers?
4. Answer:        dp[n] or dp[m][n] — where is the final answer?
```

**Key rule**: Express the answer as the **return value**, not a parameter passed down. Each state is computed exactly once.

### Top-Down vs Bottom-Up

| | Top-Down (recursive + memo) | Bottom-Up (iterative table) |
|---|---|---|
| Thinking | "What are my choices?" → recurse | "Fill table in order" |
| Visits | Only reachable states | Entire table |
| Space optimization | Harder | Easy (keep prev row) |
| Interview | Easier to derive | Shorter code |

### Five Core Patterns

**1. 1D DP (sequence/decision)** — `dp[i]` = answer for first `i` elements
```java
// LC 198 (House Robber): rob or skip
dp[i] = Math.max(dp[i-1], dp[i-2] + nums[i]);

// LC 300 (LIS): longest increasing subsequence ending at i
for (int j = 0; j < i; j++)
    if (nums[j] < nums[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
```

**2. 2D DP (grid/string)** — `dp[i][j]` = answer for `X[0..i-1]` and `Y[0..j-1]`
```java
// LC 72 (Edit Distance)
if (word1[i-1] == word2[j-1]) dp[i][j] = dp[i-1][j-1];
else dp[i][j] = 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]);

// LC 1143 (LCS)
if (text1[i-1] == text2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;
else dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
```

**3. Knapsack (0/1)** — each item used at most once → iterate **right to left**
```java
// LC 416 (Partition Equal Subset Sum)
for (int num : nums)
    for (int j = target; j >= num; j--)  // RIGHT to LEFT
        dp[j] = dp[j] || dp[j - num];
```

**4. Knapsack (unbounded)** — items reusable → iterate **left to right**
```java
// LC 322 (Coin Change)
for (int coin : coins)
    for (int j = coin; j <= amount; j++)  // LEFT to RIGHT
        dp[j] = Math.min(dp[j], dp[j - coin] + 1);
```

**5. DP + Binary Search** (sorted intervals/sequences)
```java
// LC 1235 (Job Scheduling): sort by end, binary search for last non-overlapping
dp[i] = max(dp[i-1], profit[i] + dp[lastNonOverlapping(i)]);
```

### DP is Shortest Path on a DAG
Every DP recurrence defines a DAG. Table-filling = topological sort. If cycles exist → can't use DP, need BFS/Dijkstra.

### Common Pitfalls
- **Wrong base case** — `dp[0] = 0` vs `dp[0] = 1` vs `dp[0] = true` depends on what the state represents
- **Off-by-one in table size** — if `dp[i]` represents "first i elements", you need `dp[n+1]`
- **Knapsack direction** — 0/1 knapsack: iterate capacity **right to left**. Unbounded: **left to right**. Reversing this silently gives wrong answers
- **Forgetting to initialize `dp` array** — `Arrays.fill(dp, Integer.MAX_VALUE)` for min problems, but then check for MAX_VALUE before adding to avoid overflow
- **Integer overflow** — `dp[j - coin] + 1` when `dp[j - coin]` is `Integer.MAX_VALUE` wraps to negative
- **Top-down: returning void instead of a value** — memoization requires the recursive function to *return* the answer, not accumulate it in a parameter
- **Top-down: forgetting the memo check** — must check and return cached value *before* computing

---

## Backtracking

### When to Use
- "Generate **all** valid combinations / permutations / subsets"
- "Find **any** valid configuration" (N-Queens, Sudoku)
- State space is a tree; prune invalid branches early

### Template

```java
void backtrack(List<List<Integer>> result, List<Integer> path, /* state */) {
    if (/* goal reached */) {
        result.add(new ArrayList<>(path));  // copy!
        return;
    }
    for (/* each choice */) {
        if (/* invalid */) continue;  // prune
        path.add(choice);             // choose
        backtrack(result, path, /* updated state */);
        path.remove(path.size() - 1); // un-choose
    }
}
```

### Key Problems
| Problem | Key Trick |
|---|---|
| LC 46 (Permutations) | `used[]` boolean array |
| LC 78 (Subsets) | Start index to avoid duplicates |
| LC 39 (Combination Sum) | Stay at same index (reuse allowed) |
| LC 51 (N-Queens) | Track columns + diagonals with sets |
| LC 79 (Word Search) | Mark visited in grid, restore on backtrack |
| LC 17 (Letter Combinations) | Map digit → letters, recurse |

### Trick: Avoiding Duplicates
For arrays with duplicate elements (LC 40, 47), sort first, then skip `nums[i] == nums[i-1]` at the same recursion level.

### Common Pitfalls
- **Forgetting to copy the path** — `result.add(path)` adds a *reference*; the list gets modified later. Must do `new ArrayList<>(path)`
- **Not restoring state** — every `choose` must have a matching `un-choose`. Forgetting `board[i][j] = c` in word search breaks everything
- **Duplicate results** — sort the input + skip `nums[i] == nums[i-1]` at the *same level*. Skipping across levels removes valid answers
- **Start index confusion** — subsets/combinations: pass `i` (or `i+1`) as start. Permutations: always start from 0 with `used[]` array

---

## Graph Algorithms

### Algorithm Overview

| Algorithm | Problem | Time | Data Structure |
|---|---|---|---|
| **BFS** | Shortest path (unweighted) | O(V + E) | Queue |
| **Dijkstra's** | Shortest path (non-neg weights) | O(E log V) | PriorityQueue |
| **Bellman-Ford** | Shortest path (neg weights ok) | O(V × E) | Array |
| **Kruskal's** | Minimum Spanning Tree | O(E log E) | Union-Find |
| **Prim's** | Minimum Spanning Tree | O(E log V) | PriorityQueue |

### BFS Template
```java
Queue<int[]> queue = new ArrayDeque<>();
queue.offer(start);
visited.add(start);
int level = 0;
while (!queue.isEmpty()) {
    int size = queue.size();  // process level by level
    for (int i = 0; i < size; i++) {
        var curr = queue.poll();
        for (var next : neighbors(curr)) {
            if (!visited.contains(next)) {
                visited.add(next);
                queue.offer(next);
            }
        }
    }
    level++;
}
```

### Dijkstra's
```java
int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
pq.offer(new int[]{0, src});

while (!pq.isEmpty()) {
    int[] curr = pq.poll();
    int d = curr[0], u = curr[1];
    if (d > dist[u]) continue;  // stale entry
    for (int[] edge : graph.getOrDefault(u, List.of())) {
        int v = edge[0], w = edge[1];
        if (dist[u] + w < dist[v]) {
            dist[v] = dist[u] + w;
            pq.offer(new int[]{dist[v], v});
        }
    }
}
```

### Bellman-Ford
```java
int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;
for (int i = 0; i < n - 1; i++)       // V-1 rounds
    for (int[] e : edges)               // relax all edges
        if (dist[e[0]] != Integer.MAX_VALUE && dist[e[0]] + e[2] < dist[e[1]])
            dist[e[1]] = dist[e[0]] + e[2];
```

### Kruskal's (MST)
```java
Arrays.sort(edges, (a, b) -> a[2] - b[2]);  // sort by weight
UnionFind uf = new UnionFind(n);
int total = 0, count = 0;
for (int[] e : edges) {
    if (uf.union(e[0], e[1])) {
        total += e[2];
        if (++count == n - 1) break;
    }
}
```

### Prim's (MST)
```java
boolean[] inMST = new boolean[n];
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
pq.offer(new int[]{0, 0});
int total = 0, count = 0;
while (!pq.isEmpty() && count < n) {
    int[] curr = pq.poll();
    if (inMST[curr[1]]) continue;
    inMST[curr[1]] = true;
    total += curr[0];
    count++;
    for (int[] edge : graph.getOrDefault(curr[1], List.of()))
        if (!inMST[edge[0]]) pq.offer(new int[]{edge[1], edge[0]});
}
```

### When to Use Which
```
Shortest path?
├── Unweighted → BFS
├── Non-negative weights → Dijkstra's
└── Negative weights → Bellman-Ford

MST?
├── Edge list / sparse → Kruskal's
└── Adjacency list / dense → Prim's
```

### Common Pitfalls
- **BFS: adding to visited when polling instead of when offering** — causes duplicates in queue, TLE or wrong results
- **Dijkstra: not skipping stale entries** — without `if (d > dist[u]) continue`, you process nodes multiple times
- **Dijkstra with negative weights** — silently gives wrong answers. Use Bellman-Ford instead
- **Bellman-Ford: off-by-one in rounds** — V-1 rounds for standard; K+1 rounds for "at most K stops" variant
- **Building adjacency list: forgetting bidirectional edges** — undirected graph needs `graph[u].add(v)` AND `graph[v].add(u)`

---

## Union-Find

### Template
```java
class UnionFind {
    int[] parent, rank;
    int components;

    UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        components = n;
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);  // path compression
        return parent[x];
    }

    boolean union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rank[px] < rank[py]) parent[px] = py;
        else if (rank[px] > rank[py]) parent[py] = px;
        else { parent[py] = px; rank[px]++; }
        components--;
        return true;
    }
}
```

### When to Use
- **Merge groups that share a common element** (LC 721 Accounts Merge)
- **Detect redundant connections** (LC 684)
- **Count connected components** (LC 323)
- **Dynamic connectivity** — edges added one by one

### String-Keyed Union-Find
For problems where nodes are strings (emails, words), use `Map<String, String> parent` instead of `int[]`.

### Key Signal
"Group things together by shared attribute" → Union-Find.

### Common Pitfalls
- **Forgetting path compression** — without it, `find()` degrades to O(n)
- **Union without rank/size** — creates degenerate chains
- **Counting components wrong** — don't count `parent[i] == i`; use the `components` field updated during `union()`
- **Off-by-one in node numbering** — if nodes are 1-indexed, allocate `parent[n+1]`

---

## Topological Sort

### Kahn's Algorithm (BFS) — Preferred
```java
int[] inDegree = new int[n];
for (var neighbors : graph.values())
    for (int next : neighbors) inDegree[next]++;

Queue<Integer> queue = new ArrayDeque<>();
for (int i = 0; i < n; i++)
    if (inDegree[i] == 0) queue.offer(i);

List<Integer> order = new ArrayList<>();
while (!queue.isEmpty()) {
    int curr = queue.poll();
    order.add(curr);
    for (int next : graph.getOrDefault(curr, List.of()))
        if (--inDegree[next] == 0) queue.offer(next);
}
return order.size() == n ? order : List.of();  // empty = cycle
```

### DFS Post-Order (Alternative)
```java
int[] state = new int[n];  // 0=unvisited, 1=visiting, 2=visited
List<Integer> order = new ArrayList<>();
for (int i = 0; i < n; i++)
    if (state[i] == 0 && hasCycle(i, graph, state, order)) return List.of();
Collections.reverse(order);
return order;
```

### When to Use
- **Prerequisites / dependencies**: LC 207, 210
- **Alien dictionary**: LC 269 (compare adjacent words → edges)
- **Build order / compilation**

### Common Mistakes
- Reversing edge direction: "prereq → course", not "course → prereq"
- Forgetting isolated nodes
- Not checking for cycles (`order.size() == n`)

### Variant: Lexicographic Order
Replace `ArrayDeque` with `PriorityQueue` — always picks smallest available node. O(V log V) instead of O(V).

### Common Pitfalls
- **Edge direction reversed** — "A is prerequisite of B" means edge A→B, `inDegree[B]++`. Not B→A
- **Forgetting isolated nodes** — nodes with no edges still need to be in the graph and the result
- **Not checking for cycles** — if `order.size() != n`, there's a cycle and no valid ordering exists
- **DFS: forgetting to reverse** — DFS post-order gives reverse topological order

---

## Linked List Tricks

### Core Patterns

**Fast/Slow pointers** (Floyd's cycle detection):
```java
ListNode slow = head, fast = head;
while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) return true;  // cycle
}
// slow is at middle when fast reaches end
```

**Reverse a linked list**:
```java
ListNode prev = null, curr = head;
while (curr != null) {
    ListNode next = curr.next;
    curr.next = prev;
    prev = curr;
    curr = next;
}
return prev;
```

**Dummy head** (simplifies edge cases):
```java
ListNode dummy = new ListNode(0);
dummy.next = head;
// ... manipulate list ...
return dummy.next;
```

### Key Problems
| Problem | Trick |
|---|---|
| LC 206 (Reverse Linked List) | Three-pointer iteration |
| LC 141/142 (Cycle Detection) | Fast/slow, then entry point |
| LC 21 (Merge Two Sorted) | Dummy head + compare |
| LC 25 (Reverse Nodes in k-Group) | Count k, reverse segment, connect |
| LC 23 (Merge K Sorted Lists) | Min-heap of list heads |

### Finding Cycle Entry (LC 142)
After fast and slow meet, reset one pointer to head. Move both one step at a time — they meet at the cycle entry. Mathematical proof: both travel the same distance to the entry point.

### Common Pitfalls
- **Losing the head reference** — always keep a reference to dummy or head before manipulating
- **Not using a dummy node** — leads to special-casing when the head itself changes (delete head, insert before head)
- **Forgetting to null-terminate** — after reversing or rearranging, the last node's `.next` may still point to its old successor, creating a cycle
- **Modifying `node.next` before saving it** — always do `ListNode next = curr.next` *before* `curr.next = prev`

---

## Stack Patterns

### Monotonic Stack
Maintain a stack where elements are in sorted order. Used for "next greater/smaller element" problems.

**Decreasing stack** (next greater element):
```java
Deque<Integer> stack = new ArrayDeque<>();
for (int i = 0; i < nums.length; i++) {
    while (!stack.isEmpty() && nums[stack.peek()] < nums[i]) {
        result[stack.pop()] = nums[i];
    }
    stack.push(i);
}
```

**Largest rectangle in histogram** (LC 84):
```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(-1);  // sentinel
int maxArea = 0;
for (int i = 0; i <= heights.length; i++) {
    int h = (i == heights.length) ? 0 : heights[i];
    while (stack.peek() != -1 && heights[stack.peek()] >= h) {
        int height = heights[stack.pop()];
        int width = i - stack.peek() - 1;
        maxArea = Math.max(maxArea, height * width);
    }
    stack.push(i);
}
```

### Stack-Based Parsing
For expression evaluation, calculators, nested structures:

```java
// LC 224 (Basic Calculator) pattern:
// Use stack to save state when entering parentheses
Deque<Integer> stack = new ArrayDeque<>();
int result = 0, num = 0, sign = 1;
for (char c : s.toCharArray()) {
    if (Character.isDigit(c)) num = num * 10 + (c - '0');
    else if (c == '+' || c == '-') {
        result += sign * num;
        num = 0;
        sign = (c == '+') ? 1 : -1;
    } else if (c == '(') {
        stack.push(result);
        stack.push(sign);
        result = 0; sign = 1;
    } else if (c == ')') {
        result += sign * num;
        num = 0;
        result = stack.pop() * result + stack.pop();
    }
}
result += sign * num;
```

### Monotonic Deque (Sliding Window Max/Min)
```java
Deque<Integer> deque = new ArrayDeque<>();
for (int i = 0; i < nums.length; i++) {
    while (!deque.isEmpty() && nums[deque.peekLast()] <= nums[i])
        deque.pollLast();
    deque.offerLast(i);
    if (deque.peekFirst() <= i - k) deque.pollFirst();  // evict out-of-window
    if (i >= k - 1) result[i - k + 1] = nums[deque.peekFirst()];
}
```

### Key Problems
| Problem | Pattern |
|---|---|
| LC 739 (Daily Temperatures) | Monotonic decreasing stack |
| LC 84 (Largest Rectangle) | Monotonic stack with sentinel |
| LC 224 (Basic Calculator) | Stack for parentheses state |
| LC 895 (Max Frequency Stack) | HashMap + stack per frequency |

### Common Pitfalls
- **Forgetting elements remaining in the stack after the loop** — for "next greater element", leftover items have no next greater (set to -1 or default). For histogram, use a sentinel value (height 0) at the end to flush the stack
- **Pushing values vs indices** — push indices when you need position info (width calculation in histogram); push values when you only need comparison
- **Wrong monotonic direction** — decreasing stack for "next greater", increasing stack for "next smaller"
- **Calculator: not flushing the last number** — after the loop, `result += sign * num` is needed for the last pending number
- **Calculator: operator precedence in LC 227** — `*` and `/` must be applied immediately, while `+` and `-` are deferred

---

## Heap / Priority Queue Patterns

### Patterns

**Top K elements** (keep heap of size k):
```java
PriorityQueue<Integer> pq = new PriorityQueue<>();  // min-heap
for (int num : nums) {
    pq.offer(num);
    if (pq.size() > k) pq.poll();  // evict smallest → keeps k largest
}
// pq.peek() = kth largest
```

**Two heaps for median** (LC 295):
```java
PriorityQueue<Integer> lo = new PriorityQueue<>(Comparator.reverseOrder()); // max-heap: smaller half
PriorityQueue<Integer> hi = new PriorityQueue<>();  // min-heap: larger half
// Balance: lo.size() == hi.size() or lo.size() == hi.size() + 1
// Median = lo.peek() or (lo.peek() + hi.peek()) / 2.0
```

**Merge K sorted lists** (LC 23):
```java
PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> a.val - b.val);
for (ListNode head : lists) if (head != null) pq.offer(head);
ListNode dummy = new ListNode(0), curr = dummy;
while (!pq.isEmpty()) {
    ListNode node = pq.poll();
    curr.next = node;
    curr = curr.next;
    if (node.next != null) pq.offer(node.next);
}
```

### Key Problems
| Problem | Pattern |
|---|---|
| LC 215 (Kth Largest) | Min-heap of size k |
| LC 347 (Top K Frequent) | Frequency map + min-heap |
| LC 295 (Find Median) | Two heaps (max + min) |
| LC 23 (Merge K Sorted) | Min-heap of heads |
| LC 253 (Meeting Rooms II) | Min-heap of end times |

### PriorityQueue Gotchas
- `remove(obj)` is **O(n)** — prefer `TreeMap` when you need arbitrary removal
- Iterator is **NOT sorted** — only `peek()/poll()` gives min
- Duplicates allowed (unlike TreeMap)

### Common Pitfalls
- **Using max-heap when you need min-heap** (or vice versa) — for "top K largest", use a **min**-heap of size K (evict smallest)
- **Two-heap median: wrong insertion order** — always add to one heap first, then rebalance. Don't try to decide which heap upfront
- **Null check on list heads** — `for (ListNode head : lists) if (head != null) pq.offer(head)` — input may contain null lists
- **Comparator overflow** — `(a, b) -> a - b` overflows for large ints. Use `Integer.compare(a, b)` for safety

---

## Bit Manipulation

### Essential Tricks

| Operation | Code | What It Does |
|---|---|---|
| Check bit i | `(n >> i) & 1` | Is bit i set? |
| Set bit i | `n \| (1 << i)` | Turn on bit i |
| Clear bit i | `n & ~(1 << i)` | Turn off bit i |
| Toggle bit i | `n ^ (1 << i)` | Flip bit i |
| Clear lowest set bit | `n & (n - 1)` | Remove rightmost 1 |
| Isolate lowest set bit | `n & (-n)` | Keep only rightmost 1 |
| Check power of 2 | `n > 0 && (n & (n-1)) == 0` | Only one bit set |

### Key Problems
| Problem | Trick |
|---|---|
| LC 191 (Number of 1 Bits) | `n & (n-1)` in loop, count iterations |
| LC 338 (Counting Bits) | `dp[i] = dp[i & (i-1)] + 1` |
| LC 136 (Single Number) | XOR all elements — duplicates cancel |

### Common Pitfalls
- **Signed right shift `>>` vs unsigned `>>>`** — for negative numbers, `>>` fills with 1s, `>>>` fills with 0s
- **Shift amount > 31** — `1 << 32` wraps to `1 << 0` in Java. Use `1L << i` for long
- **Forgetting `n > 0` check** for power of 2 — `0 & (0-1) == 0` is true but 0 is not a power of 2

---

## Matrix Tricks

### Rotate Image 90° CW (LC 48)
```java
// Step 1: Transpose (swap [i][j] with [j][i])
// Step 2: Reverse each row
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        swap(matrix[i][j], matrix[j][i]);
for (int[] row : matrix)
    reverse(row);
```

### Spiral Matrix (LC 54)
```java
int top = 0, bot = m - 1, left = 0, right = n - 1;
while (top <= bot && left <= right) {
    for (int j = left; j <= right; j++) result.add(matrix[top][j]);  // →
    top++;
    for (int i = top; i <= bot; i++) result.add(matrix[i][right]);   // ↓
    right--;
    if (top <= bot) { for (int j = right; j >= left; j--) result.add(matrix[bot][j]); bot--; }  // ←
    if (left <= right) { for (int i = bot; i >= top; i--) result.add(matrix[i][left]); left++; } // ↑
}
```

### 4-Directional Traversal
```java
int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};
for (int[] d : dirs) {
    int ni = i + d[0], nj = j + d[1];
    if (ni >= 0 && ni < m && nj >= 0 && nj < n) { /* valid */ }
}
```

### Common Pitfalls
- **Rows vs columns confusion** — `matrix[row][col]`, `m` = rows, `n` = cols. Transpose swaps `[i][j]` with `[j][i]`
- **Spiral: not checking `top <= bot` and `left <= right`** before the bottom-row and left-column traversals — causes duplicate visits on single-row/column matrices
- **In-place modification losing data** — when rotating or transforming, process in the right order or use a temp variable
- **BFS/DFS on grid: not marking visited early enough** — mark when adding to queue, not when processing, to avoid duplicate visits

---

## Minor Patterns & One-Trick Techniques

One-trick patterns — know the technique and you can solve them instantly.

### Boyer-Moore Voting (LC 169 — Majority Element)
```java
int candidate = 0, count = 0;
for (int num : nums) {
    if (count == 0) candidate = num;
    count += (num == candidate) ? 1 : -1;
}
return candidate;  // guaranteed majority exists
```
Cancel different elements pairwise — the majority element always survives. O(n) time, O(1) space.

### Kadane's Algorithm (LC 53 — Maximum Subarray)
```java
int maxHere = nums[0], maxSoFar = nums[0];
for (int i = 1; i < nums.length; i++) {
    maxHere = Math.max(nums[i], maxHere + nums[i]);
    maxSoFar = Math.max(maxSoFar, maxHere);
}
```
**Variant** (LC 152 — Maximum Product Subarray): track both `maxHere` and `minHere` because a negative × negative can become the max.

### Dutch National Flag (LC 75 — Sort Colors)
```java
int lo = 0, mid = 0, hi = nums.length - 1;
while (mid <= hi) {
    if (nums[mid] == 0) swap(nums, lo++, mid++);
    else if (nums[mid] == 2) swap(nums, mid, hi--);
    else mid++;
}
```
3-way partition in a single pass. Generalizes to any 3-category sort.

### In-Place Array Marking (LC 41 — First Missing Positive)
Use array indices as a hash map — place each value `v` at index `v - 1`:
```java
for (int i = 0; i < n; i++)
    while (nums[i] > 0 && nums[i] <= n && nums[nums[i] - 1] != nums[i])
        swap(nums, i, nums[i] - 1);
for (int i = 0; i < n; i++)
    if (nums[i] != i + 1) return i + 1;
return n + 1;
```

### Reservoir Sampling (LC 382 — Linked List Random Node)
Select a random element from a stream of unknown length:
```java
int result = 0, count = 0;
ListNode curr = head;
while (curr != null) {
    count++;
    if (rand.nextInt(count) == 0) result = curr.val;  // keep with prob 1/count
    curr = curr.next;
}
```

### Bucket Sort (LC 164 — Maximum Gap)
When value range is bounded, sort in O(n) by distributing into buckets. For Maximum Gap: bucket size = `(max - min) / (n - 1)`, then max gap is between consecutive non-empty buckets.

### Next Permutation (LC 31)
Four steps — memorize the procedure:
1. **Find dip**: scan right-to-left, find first `i` where `nums[i] < nums[i+1]`
2. **Find swap**: scan right-to-left, find first `j` where `nums[j] > nums[i]`
3. **Swap** `nums[i]` and `nums[j]`
4. **Reverse** the suffix after index `i`

If no dip found → array is last permutation → reverse entire array.

### Trie + Wildcard DFS (LC 211 — Add and Search Words)
Standard Trie insert, but search branches at `.` to explore **all** children:
```java
boolean search(TrieNode node, String word, int i) {
    if (i == word.length()) return node.isEnd;
    char c = word.charAt(i);
    if (c == '.') {
        for (TrieNode child : node.children)
            if (child != null && search(child, word, i + 1)) return true;
        return false;
    }
    return node.children[c - 'a'] != null && search(node.children[c - 'a'], word, i + 1);
}
```

### Reference-Only Techniques

| Technique | What It Does | When You'd See It |
|---|---|---|
| **Segment Tree / BIT** | Range update + range query O(log n) | "Update index AND query range sum" — very rare |
| **KMP / Rabin-Karp** | String pattern matching O(n) | "Find pattern in text" — almost never asked |
| **Manacher's** | Longest palindromic substring O(n) | Expand-around-center O(n²) is always sufficient |
| **A\* Search** | Heuristic shortest path | Game pathfinding, not SWE interviews |
| **Suffix Array** | All suffixes sorted | Advanced string problems — never asked |
| **Heavy-Light Decomp** | Tree path queries | Competitive programming only |

---

## Data Structures Reference

### TreeMap<K, V>

Sorted map backed by Red-Black tree. All operations **O(log n)**.

| Method | Description |
|---|---|
| `put(k, v)` / `get(k)` / `remove(k)` | Standard map ops |
| `firstKey()` / `lastKey()` | Min / max key |
| `pollFirstEntry()` / `pollLastEntry()` | Remove + return min / max |
| `floorKey(k)` / `ceilingKey(k)` | Largest ≤ k / smallest ≥ k |
| `lowerKey(k)` / `higherKey(k)` | Strict < k / strict > k |
| `subMap(from, to)` | Live view of keys in range |

**When to use**: Sliding window needing sorted access, nearest neighbor queries, O(log n) arbitrary removal (vs PriorityQueue's O(n)).

---

### ArrayDeque<E>

O(1) amortized stack/queue/deque. Faster than `LinkedList`. No `null` elements.

| Use As | Key Methods |
|---|---|
| **Stack** | `push(e)`, `pop()`, `peek()` |
| **Queue** | `offer(e)`, `poll()`, `peek()` |
| **Deque** | `offerFirst/Last`, `pollFirst/Last`, `peekFirst/Last` |

Use `poll`/`peek`/`offer` family (returns null) over `remove`/`get`/`add` (throws).

---

### PriorityQueue<E>

Min-heap. Use `Comparator.reverseOrder()` for max-heap.

| Method | Time |
|---|---|
| `offer(e)` / `poll()` | O(log n) |
| `peek()` | O(1) |
| `remove(obj)` | **O(n)** — linear scan! |
| `new PriorityQueue<>(collection)` | O(n) heapify |

**Gotchas**: `remove(obj)` is O(n), iterator is NOT sorted, duplicates allowed.

---

### Trie (Prefix Tree)

```java
class TrieNode {
    TrieNode[] children = new TrieNode[26];
    boolean isEnd;
}
```

| Operation | Time |
|---|---|
| Insert / Search / Prefix check | O(L) where L = word length |

**When to use**: Prefix matching, autocomplete, word search in grids (LC 212), file system design.

**Gotchas**: `isEnd` is critical (without it, "app" matches when only "apple" was inserted). Use `Map<Character, TrieNode>` for non-lowercase-English character sets.

**Trie + DFS** (LC 212 — Word Search II):
```java
// Build trie from word list, DFS from each grid cell
// Follow trie children instead of checking all words → prunes search
void dfs(char[][] board, int i, int j, TrieNode node, List<String> result) {
    char c = board[i][j];
    if (c == '#' || node.children[c - 'a'] == null) return;
    node = node.children[c - 'a'];
    if (node.isEnd) { result.add(node.word); node.isEnd = false; }
    board[i][j] = '#';
    for (int[] d : DIRS) dfs(board, i+d[0], j+d[1], node, result);
    board[i][j] = c;
}
```

---

### Quick Comparison

| | TreeMap | ArrayDeque | PriorityQueue |
|---|---|---|---|
| **Order** | Sorted by key | Insertion order | Heap (min default) |
| **Min access** | O(log n) | O(1) head | O(1) peek |
| **Arbitrary remove** | O(log n) | O(n) | O(n) |
| **Neighbor query** | O(log n) `floor`/`ceiling` | N/A | N/A |
| **Best for** | Sorted access + removal | Stack / Queue / Deque | Pure min/max stream |
