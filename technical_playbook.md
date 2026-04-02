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
19. [Java Concurrency](#java-concurrency)

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
| LC 42 (Trapping Rain Water) | Track leftMax/rightMax from both ends. **Note**: more naturally a monotonic stack problem (find nearest greater on each side). The two-pointer approach here is a space optimization from O(n) → O(1) |
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
| LC 42 (Trapping Rain Water) | Monotonic decreasing stack — find boundaries on each side, compute water when popping |
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

**How it works**: Think of it as a battle royale. Maintain a `candidate` and a `count`. When count drops to 0, pick the current element as the new candidate. If the next element matches, increment; otherwise, decrement. Since the majority element has more than n/2 occurrences, it can't be fully canceled out by all other elements combined — it always survives as the final candidate.

**Generalized: find all elements appearing more than n/k times (LC 229 for k=3)**

At most **k-1 elements** can appear more than n/k times. Maintain **k-1 candidates** with k-1 counters:
```java
// LC 229: elements appearing more than n/3 times (k=3, so 2 candidates)
int c1 = 0, c2 = 0, count1 = 0, count2 = 0;
for (int num : nums) {
    if (num == c1)           count1++;
    else if (num == c2)      count2++;
    else if (count1 == 0)  { c1 = num; count1 = 1; }
    else if (count2 == 0)  { c2 = num; count2 = 1; }
    else                   { count1--; count2--; }  // three-way cancellation
}
// MUST verify — unlike LC 169, majority is not guaranteed
count1 = 0; count2 = 0;
for (int num : nums) {
    if (num == c1) count1++;
    else if (num == c2) count2++;
}
List<Integer> result = new ArrayList<>();
if (count1 > nums.length / 3) result.add(c1);
if (count2 > nums.length / 3) result.add(c2);
```
The `if/else if` ordering matters — check existing candidates *before* checking empty slots to avoid assigning the same value to both candidates.

**When you'll see this in interviews**:
- LC 169/229 directly
- Streaming/big data: "find dominant element with O(1) memory" — single-pass + constant space is the key selling point
- Follow-up to a hash map solution: "can you do it without extra space?"

### Kadane's Algorithm (LC 53 — Maximum Subarray)
```java
int maxHere = nums[0], maxSoFar = nums[0];
for (int i = 1; i < nums.length; i++) {
    maxHere = Math.max(nums[i], maxHere + nums[i]);
    maxSoFar = Math.max(maxSoFar, maxHere);
}
```

**How it works**: At each index, decide: **extend the previous subarray or start fresh here?** `maxHere` = max subarray sum ending at current index. If the running sum has gone negative, it's dragging you down — start fresh. This is really 1D DP with space optimization: `dp[i] = max(nums[i], dp[i-1] + nums[i])`, compressed to a single variable since `dp[i]` only depends on `dp[i-1]`.

**Variants**:

*LC 152 — Maximum Product Subarray*: a negative × negative = positive, so track both max AND min:
```java
int maxHere = nums[0], minHere = nums[0], result = nums[0];
for (int i = 1; i < nums.length; i++) {
    int temp = maxHere;
    maxHere = Math.max(nums[i], Math.max(maxHere * nums[i], minHere * nums[i]));
    minHere = Math.min(nums[i], Math.min(temp * nums[i], minHere * nums[i]));
    result = Math.max(result, maxHere);
}
```

*LC 918 — Maximum Circular Subarray*: max circular subarray is either a normal max subarray, or the total sum minus the **minimum** subarray (wrap-around case): `answer = max(maxKadane, totalSum - minKadane)`. Edge case: if all negative, `totalSum - minKadane = 0`, so use `maxKadane`.

*2D — Max sum path (right/down)*: same "extend or restart" in two directions:
`dp[i][j] = matrix[i][j] + max(0, dp[i-1][j], dp[i][j-1])`

*2D — Max sum subrectangle*: fix two rows (top/bottom), compress each column into a sum, run 1D Kadane's on the compressed array. O(m² × n):
```java
for (int top = 0; top < m; top++) {
    int[] colSum = new int[n];
    for (int bot = top; bot < m; bot++) {
        for (int j = 0; j < n; j++) colSum[j] += matrix[bot][j];
        maxSum = Math.max(maxSum, kadane(colSum));
    }
}
```

### Dutch National Flag (LC 75 — Sort Colors)
```java
int lo = 0, mid = 0, hi = nums.length - 1;
while (mid <= hi) {
    if (nums[mid] == 0) swap(nums, lo++, mid++);
    else if (nums[mid] == 2) swap(nums, mid, hi--);
    else mid++;
}
```
**How it works**: Maintain three pointers that partition the array into four regions: `[0..lo-1]` = 0s, `[lo..mid-1]` = 1s, `[mid..hi]` = unprocessed, `[hi+1..n-1]` = 2s. All regions start empty (`lo=0, mid=0, hi=n-1` — entire array is unprocessed). `mid` scans forward, placing each element into its region:
- `nums[mid] == 0`: swap with `nums[lo]`, advance both — the swapped-in value is a confirmed 1
- `nums[mid] == 2`: swap with `nums[hi]`, shrink `hi` — do NOT advance `mid`, the swapped-in value is unprocessed
- `nums[mid] == 1`: already in place, advance `mid`

No preconditions needed. Works with fewer than 3 distinct values (missing regions stay empty), arrays of any size.

**Beyond 3 partitions**: DNF doesn't extend cleanly to k > 3 (only 2 ends to work from). Options:
- **k = 2**: standard two-pointer partition
- **k = 3**: Dutch National Flag — single pass, O(1) space
- **k > 3**: counting sort — O(n) time, O(k) space, two passes (count then fill)

**Real-world use**: 3-way quicksort — partition into `< pivot | == pivot | > pivot`. Avoids reprocessing equal elements when there are many duplicates.

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

**How it works**: The answer must be in `[1, n+1]` (at most n positive values in n slots). Use the array itself as a hash map: swap each value `v` to index `v-1` until every valid value is "home." Then scan — first index where `nums[i] != i+1` is the answer.

**Why `while` not `if`**: a single swap places one value home, but the swapped-in value may also need placement. The `while` chains swaps until the current position holds an invalid or already-homed value.

**Three guards**: `nums[i] > 0` (ignore negatives/zero — no home), `nums[i] <= n` (ignore values > n — answer is at most n+1), `nums[nums[i]-1] != nums[i]` (destination already correct — prevents infinite loop on duplicates).

**O(n) despite nested loops**: each swap places exactly one value in its final position (never moves again). At most n total swaps across all iterations.

**Interview signal**: "values in range [1..n]" + "O(1) space" → use indices as a hash map.

**Related — LC 268 (Missing Number)**: simpler variant (find one missing from `[0..n]`). Two O(n)/O(1) approaches:
- **Sum**: `n*(n+1)/2 - sum(nums)` — intuitive but risks integer overflow for large n
- **XOR**: `xor = n; for (i=0..n-1) xor ^= i ^ nums[i]` — paired values cancel (`a^a=0`), the missing value survives. No overflow risk. Same principle as LC 136 (Single Number).

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

**How it works**: For each node at position `count`, keep it with probability `1/count`. Proof every element gets `1/n`: node `i` must be picked at step `i` (prob `1/i`) AND survive all later replacements (prob `i/(i+1) × ... × (n-1)/n`). Terms telescope to `1/n`.

**Generalized (k items)**: fill reservoir with first k items, then for each subsequent item `i`, replace a random reservoir slot with probability `k/(i+1)`. Same telescoping proof gives `k/n` per element.

**Tradeoff vs array**: both are O(n) total time. Array approach pays O(n) space once, then O(1) per pick. Reservoir pays O(1) space but O(n) on **every pick**. Reservoir only wins when you can't store the data (stream too large, unknown length, single pass required).

### Bucket Sort (LC 164 — Maximum Gap)
When value range is bounded, sort in O(n) by distributing into buckets. For Maximum Gap: bucket size = `(max - min) / (n - 1)`, then max gap is between consecutive non-empty buckets.

**How it works**: By pigeonhole principle, the max gap among n numbers in range `[min, max]` is at least `(max-min)/(n-1)`. Create buckets of that size — the max gap can never be *within* a bucket, only *between* consecutive non-empty buckets. So only track min/max per bucket, then scan:
```java
int bucketSize = Math.max(1, (max - min) / (n - 1));
int bucketCount = (max - min) / bucketSize + 1;
int[] bMin = new int[bucketCount], bMax = new int[bucketCount];
Arrays.fill(bMin, Integer.MAX_VALUE); Arrays.fill(bMax, Integer.MIN_VALUE);
for (int num : nums) {
    int idx = (num - min) / bucketSize;
    bMin[idx] = Math.min(bMin[idx], num);
    bMax[idx] = Math.max(bMax[idx], num);
}
int maxGap = 0, prevMax = min;
for (int i = 0; i < bucketCount; i++) {
    if (bMin[i] == Integer.MAX_VALUE) continue;
    maxGap = Math.max(maxGap, bMin[i] - prevMax);
    prevMax = bMax[i];
}
```

**Edge cases**: n < 2 → return 0. All equal → bucket size floors to 0, so use `Math.max(1, ...)`.

**Bucket sort beyond LC 164**: the pigeonhole trick is specific to this problem, but distributing into buckets for O(n) sorting applies elsewhere:
- **LC 347 (Top K Frequent)**: bucket by frequency — index = count, value = list of elements with that count. Scan from highest bucket. Avoids heap's O(n log k)
- **LC 220 (Contains Duplicate III)**: bucket by value range — elements in the same or adjacent bucket are within distance `t`. Sliding window of buckets checks both value and index constraints
- **General pattern**: when values are bounded or you need to group by a computable key, buckets give O(n) vs comparison-based O(n log n)

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

---

## Java Concurrency

### Thread Lifecycle
```
NEW → (start()) → RUNNABLE → (scheduler) → RUNNING
  ↓                                          ↓
  └──────────────────────────────────────── TERMINATED
                                             ↑
RUNNING → (wait/sleep/block) → WAITING/BLOCKED → (notify/timeout/unlock) → RUNNABLE
```

### Primitives Overview

| Primitive | What It Does | When to Use |
|---|---|---|
| `synchronized` | Mutual exclusion on object's intrinsic lock | Simple critical sections |
| `volatile` | Guarantees visibility across threads (no caching) | Flags, status fields (no atomicity for compound ops) |
| `ReentrantLock` | Explicit lock with tryLock, fairness, multiple Conditions | Need timeout, interruptibility, or multiple conditions |
| `Condition` | `await()`/`signal()` — like wait/notify but tied to a Lock | Producer-consumer with separate "not full" / "not empty" signals |
| `Semaphore` | Counting permits: `acquire()` blocks if 0, `release()` adds 1 | Bounded resources, rate limiting, group coordination |
| `CountDownLatch` | One-shot: N threads count down, waiters unblock at 0 | "Wait for N tasks to finish" |
| `CyclicBarrier` | Reusable: N threads wait at barrier, all released together | "All N threads must reach this point before any continue" |
| `AtomicInteger` / `AtomicReference` | Lock-free CAS operations | Counters, flags, lock-free data structures |

### `synchronized` — Intrinsic Locks

```java
// Method-level: locks `this` (or Class object for static)
public synchronized void method() { /* critical section */ }

// Block-level: locks specific object
synchronized (lockObject) {
    // critical section
}
```

**`wait()` / `notify()` / `notifyAll()`** — must be called inside `synchronized` block on the same object:
```java
synchronized (lock) {
    while (!condition) {    // MUST be while, not if (spurious wakeups)
        lock.wait();        // releases lock, suspends thread
    }
    // ... do work ...
    lock.notifyAll();       // wake all waiting threads
}
```

**Why `synchronized` can be problematic**:
- Blocks the calling thread entirely — no timeout, no interruptibility
- Only one condition per lock — can't have separate "not full" and "not empty"
- `notify()` wakes one arbitrary thread — often need `notifyAll()` which wakes all (thundering herd)
- Deadlock-prone with multiple locks — no tryLock mechanism

### `ReentrantLock` + `Condition` — The Better Monitor

```java
private final ReentrantLock lock = new ReentrantLock();
private final Condition notFull  = lock.newCondition();  // separate signal for "space available"
private final Condition notEmpty = lock.newCondition();  // separate signal for "data available"

// Producer
lock.lock();
try {
    while (queue.size() == capacity)
        notFull.await();            // releases lock, waits for space
    queue.offer(item);
    notEmpty.signal();              // wake ONE consumer (efficient)
} finally {
    lock.unlock();                  // ALWAYS in finally
}

// Consumer
lock.lock();
try {
    while (queue.isEmpty())
        notEmpty.await();           // releases lock, waits for data
    int val = queue.poll();
    notFull.signal();               // wake ONE producer
    return val;
} finally {
    lock.unlock();
}
```

**Advantages over `synchronized`**:
- **Multiple conditions**: separate signals avoid waking wrong threads
- **`signal()` not `signalAll()`**: wake exactly one waiter (no thundering herd)
- **`tryLock(timeout)`**: non-blocking attempt, avoids deadlock
- **Fairness option**: `new ReentrantLock(true)` → longest-waiting thread goes first

### `Semaphore` — Counting Permits

```java
Semaphore sem = new Semaphore(3);  // 3 permits available

sem.acquire();      // blocks if 0 permits, otherwise decrements
// ... use resource ...
sem.release();      // increments permits, wakes a waiter
```

**Key insight**: A Semaphore(1) ≈ a Lock. Semaphore(N) = "allow N concurrent accessors."

**Bounded Blocking Queue with Semaphores** (LC 1188 — cleanest approach):
```java
class BoundedBlockingQueue {
    private final Queue<Integer> queue = new LinkedList<>();
    private final Semaphore enqPermits;  // how many more items can be added
    private final Semaphore deqPermits;  // how many items available to consume

    public BoundedBlockingQueue(int capacity) {
        enqPermits = new Semaphore(capacity);  // starts full
        deqPermits = new Semaphore(0);         // starts empty
    }

    public void enqueue(int element) throws InterruptedException {
        enqPermits.acquire();                  // blocks if queue full
        synchronized (queue) { queue.offer(element); }
        deqPermits.release();                  // signal: item available
    }

    public int dequeue() throws InterruptedException {
        deqPermits.acquire();                  // blocks if queue empty
        int val;
        synchronized (queue) { val = queue.poll(); }
        enqPermits.release();                  // signal: space available
        return val;
    }

    public int size() { return deqPermits.availablePermits(); }
}
```
The semaphores handle all blocking/signaling. The `synchronized(queue)` is **only** for thread-safe access to the LinkedList itself (not for blocking). No deadlock risk because we never hold both locks.

### `CyclicBarrier` — Group Synchronization

```java
// 3 threads must arrive before any proceed. Resets automatically.
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    // optional action runs when all 3 arrive
});

// Each thread:
doWork();
barrier.await();  // blocks until all 3 threads reach here
// ... all proceed together ...
```

**LC 1117 (Building H2O)** — must release 2H + 1O as a group:
```java
class H2O {
    private final Semaphore hSem = new Semaphore(2);
    private final Semaphore oSem = new Semaphore(1);
    private final CyclicBarrier barrier = new CyclicBarrier(3, () -> {
        hSem.release(2);   // refill H permits
        oSem.release(1);   // refill O permit
    });

    public void hydrogen(Runnable releaseHydrogen) throws Exception {
        hSem.acquire();
        releaseHydrogen.run();
        barrier.await();
    }

    public void oxygen(Runnable releaseOxygen) throws Exception {
        oSem.acquire();
        releaseOxygen.run();
        barrier.await();
    }
}
```

### Semaphore vs CountDownLatch vs CyclicBarrier

These are **coordination tools**, not locks. They control *when* threads proceed, not *mutual exclusion*.

| | Semaphore | CountDownLatch | CyclicBarrier |
|---|---|---|---|
| **Mental model** | Bouncer: N permits, ongoing | One-time gate: opens at 0 | Group photo: all arrive → all go |
| **Reusable** | Yes (acquire/release cycle) | No (one-shot, cannot reset) | Yes (auto-resets each trip) |
| **Who blocks** | `acquire()` blocks if 0 permits | `await()` blocks until count=0 | `await()` blocks until N threads arrive |
| **Who unblocks** | `release()` from any thread | `countDown()` from workers | Last thread to `await()` |
| **Count direction** | Up and down (permits) | Down only (to 0) | Up (arrivals to N) |
| **Typical use** | Rate limiting, bounded pools | Wait for N tasks to finish | Sync N threads at checkpoint |
| **Production equivalent** | `CompletableFuture` + throttling | `CompletableFuture.allOf()` | Rare — phased pipelines |

**When to use which**:
- "Limit concurrent access to N" → **Semaphore**
- "Wait for N things to finish, then proceed once" → **CountDownLatch** (or `CompletableFuture.allOf()`)
- "N threads must sync at a barrier repeatedly" → **CyclicBarrier**
- **In production**: `CompletableFuture` handles most coordination. These primitives appear in interview problems and framework internals.

### `volatile` — Visibility Without Locking

```java
private volatile boolean running = true;

// Thread 1:
while (running) { doWork(); }

// Thread 2:
running = false;  // Thread 1 sees this immediately
```

**What `volatile` does**: forces read/write to main memory (no CPU cache stale reads).
**What `volatile` does NOT do**: atomicity for compound operations. `count++` on a volatile int is NOT thread-safe (read-modify-write is 3 steps).

Use `AtomicInteger` for atomic compound operations:
```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet();  // atomic
count.compareAndSet(expected, newValue);  // CAS — lock-free
```

### `Future` and `CompletableFuture`

**`Future<T>`** — handle to an async result (Java 5). Limited: can only `get()` (blocking) or `cancel()`.
```java
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<String> future = pool.submit(() -> fetchData());
String result = future.get();           // blocks until done
String result = future.get(5, SECONDS); // blocks with timeout
```

**`CompletableFuture<T>`** — composable, non-blocking async (Java 8). This is what you use in production.

**Creating**:
```java
// Run async task
CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> fetchData());

// With custom executor
CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> fetchData(), myExecutor);

// Already-completed future (useful for tests / base cases)
CompletableFuture<String> cf = CompletableFuture.completedFuture("value");
```

**Chaining (non-blocking pipeline)**:
```java
CompletableFuture<String> pipeline = CompletableFuture
    .supplyAsync(() -> fetchUserId())          // async: () → T
    .thenApply(id -> lookupUser(id))           // sync transform: T → U
    .thenApplyAsync(user -> enrichUser(user))  // async transform: T → U
    .thenCompose(user -> fetchOrders(user))    // flatMap: T → CompletableFuture<U>
    .exceptionally(ex -> fallbackValue());     // error handler
```

**Key methods**:
| Method | Signature | Use |
|---|---|---|
| `thenApply` | `T → U` | Sync transform (like `map`) |
| `thenApplyAsync` | `T → U` (on pool) | Async transform |
| `thenCompose` | `T → CF<U>` | FlatMap — avoids `CF<CF<U>>` |
| `thenAccept` | `T → void` | Consume result (side effects) |
| `thenRun` | `() → void` | Run action after completion |
| `exceptionally` | `Throwable → T` | Recover from error |
| `handle` | `(T, Throwable) → U` | Transform result or error |
| `whenComplete` | `(T, Throwable) → void` | Side effect on result or error |

**Combining multiple futures** (replaces CountDownLatch in production):
```java
// Wait for ALL — like CountDownLatch
CompletableFuture<Void> all = CompletableFuture.allOf(cf1, cf2, cf3);
all.thenRun(() -> {
    // all 3 are done — extract results
    String r1 = cf1.join();  // non-blocking here, already complete
    String r2 = cf2.join();
    String r3 = cf3.join();
});

// Wait for ANY — first one wins
CompletableFuture<Object> any = CompletableFuture.anyOf(cf1, cf2, cf3);
```

**Common pattern — fan-out/fan-in**:
```java
List<CompletableFuture<Result>> futures = ids.stream()
    .map(id -> CompletableFuture.supplyAsync(() -> process(id), pool))
    .collect(Collectors.toList());

CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
    .thenApply(v -> futures.stream()
        .map(CompletableFuture::join)
        .collect(Collectors.toList()));
```

**`thenApply` vs `thenCompose`** (the most confusing part):
```java
// thenApply: transform the value. Like Stream.map()
CF<String> name = cf.thenApply(user -> user.getName());     // CF<User> → CF<String>

// thenCompose: chain another async call. Like Stream.flatMap()
CF<Order> order = cf.thenCompose(user -> fetchOrder(user));  // CF<User> → CF<Order>
// If you used thenApply here, you'd get CF<CF<Order>> — wrong!
```

**`join()` vs `get()`**:
- `join()` — throws unchecked `CompletionException`. Use in lambdas.
- `get()` — throws checked `ExecutionException` + `InterruptedException`. Use when you need timeout.

### Lock Implementations Summary

Java has only **3 lock mechanisms** (everything else is coordination, not locking):

| Lock | What | When |
|---|---|---|
| **`synchronized`** | Intrinsic lock on any object | Simple critical sections. Most common in production |
| **`ReentrantLock`** | Explicit lock: tryLock, fairness, multiple Conditions | Need timeout, interruptibility, or separate conditions |
| **`ReentrantReadWriteLock`** | Shared read lock + exclusive write lock | Read-heavy workloads (caches, config) |

`StampedLock` (Java 8+) exists — optimistic read variant of ReadWriteLock — but rarely used.

### `ReadWriteLock` — Multiple Readers, One Writer

```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();

// Readers (concurrent):
rwLock.readLock().lock();
try { return cache.get(key); }
finally { rwLock.readLock().unlock(); }

// Writer (exclusive):
rwLock.writeLock().lock();
try { cache.put(key, value); }
finally { rwLock.writeLock().unlock(); }
```

Use when reads >> writes (e.g., caches, config stores).

### Concurrent Collections

| Collection | What | When |
|---|---|---|
| `ConcurrentHashMap` | Thread-safe map, lock striping (segment-level locks) | Shared map, high concurrency |
| `CopyOnWriteArrayList` | Snapshot on write, lock-free reads | Read-heavy, write-rare (listeners, config) |
| `BlockingQueue` (`LinkedBlockingQueue`, `ArrayBlockingQueue`) | Built-in blocking put/take | Production producer-consumer (don't roll your own) |
| `ConcurrentLinkedQueue` | Lock-free FIFO queue (CAS-based) | Non-blocking producer-consumer |

**`ConcurrentHashMap` key details**:
- `putIfAbsent(k, v)` — atomic check-and-insert
- `compute(k, (key, val) -> ...)` — atomic read-modify-write
- **NOT** safe for compound operations across multiple calls (e.g., check-then-act still needs external sync)

### Deadlock — Four Conditions (ALL must hold)

1. **Mutual exclusion**: resource held exclusively
2. **Hold and wait**: hold one lock, wait for another
3. **No preemption**: can't force-release a lock
4. **Circular wait**: A waits for B, B waits for A

**Prevention**: break any one condition. Most practical: **lock ordering** (always acquire locks in the same global order) or **tryLock with timeout**.

### Common Pitfalls

- **`if` instead of `while` for wait conditions** — spurious wakeups can resume a thread even when the condition is still false
- **`notify()` vs `notifyAll()`** — `notify()` wakes one arbitrary thread; if the wrong one wakes, the right one stays sleeping. Use `notifyAll()` with `synchronized`, or `signal()` with separate `Condition` objects
- **Forgetting `lock.unlock()` in finally** — exception in critical section leaves lock held forever → deadlock
- **`volatile` for compound ops** — `volatile int count; count++` is NOT atomic. Use `AtomicInteger`
- **Nested `synchronized` blocks** — deadlock risk if lock ordering isn't consistent across all code paths
- **Holding locks during I/O or long operations** — blocks all other threads. Minimize critical section scope
