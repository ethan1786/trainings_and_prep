# Interview Playbook — Patterns, Data Structures & Tricks

> Quick-reference for staff+ level SWE interviews. Organized by **pattern** first, **data structure** second.

---

## Table of Contents

1. [Pattern Recognition Decision Tree](#pattern-recognition-decision-tree)
2. [Two Pointers](#two-pointers)
3. [Sliding Window](#sliding-window)
4. [Prefix Sum + HashMap](#prefix-sum--hashmap)
5. [Binary Search](#binary-search)
6. [Intervals](#intervals)
7. [Greedy](#greedy)
8. [Dynamic Programming](#dynamic-programming)
9. [Backtracking](#backtracking)
10. [Tree](#tree)
11. [Graph Algorithms](#graph-algorithms)
12. [Union-Find](#union-find)
13. [Topological Sort](#topological-sort)
14. [Linked List Tricks](#linked-list-tricks)
15. [Stack Patterns](#stack-patterns)
16. [Heap / Priority Queue Patterns](#heap--priority-queue-patterns)
17. [Bit Manipulation](#bit-manipulation)
18. [Matrix Tricks](#matrix-tricks)
19. [Minor Patterns & One-Trick Techniques](#minor-patterns--one-trick-techniques)
20. [Data Structures Reference](#data-structures-reference)
21. [Java Concurrency](#java-concurrency)

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

### Template 1: Variable Window — Find Longest

Shrink with `while` — the window may need to shrink multiple steps per expansion.

```java
int left = 0, ans = 0;
for (int right = 0; right < n; right++) {
    // add nums[right] to window state

    while (/* constraint violated */) {
        // remove nums[left] from window state
        left++;
    }
    // window [left, right] is valid — update answer
    ans = Math.max(ans, right - left + 1);
}
```

**Update answer AFTER shrinking** — the window is valid at this point.

### Template 2: Variable Window — Find Shortest

Same structure, but update answer DURING shrinking (inside the `while`).

```java
int left = 0, ans = Integer.MAX_VALUE;
for (int right = 0; right < n; right++) {
    // add nums[right] to window state

    while (/* constraint satisfied */) {
        ans = Math.min(ans, right - left + 1);  // update INSIDE
        // remove nums[left] from window state
        left++;
    }
}
```

**Key difference**: for longest, shrink while *violated*; for shortest, shrink while *satisfied* (greedily shrink valid windows).

### Template 3: Fixed Window (size k)

Shrink with `if`, not `while` — window grows by 1 each step, so at most 1 shrink needed.

```java
int left = 0;
for (int right = 0; right < n; right++) {
    // add nums[right] to window state

    if (right - left + 1 > k) {       // "if", not "while"
        // remove nums[left] from window state
        left++;
    }
    if (right - left + 1 == k) {
        // window is exactly size k — process/update answer
    }
}
```

### Trick: `if` vs `while` for Shrinking

| Scenario | Use | Why |
|---|---|---|
| Fixed window size k | `if` | Window overshoots by at most 1 per step |
| Variable — find longest/shortest | `while` | One expansion can violate constraint by many steps |
| Variable — with `atMost(k)` counting | `while` | Same reason |

**Rule of thumb**: if the window size is predetermined, `if`. If the window size depends on content, `while`.

### Pattern: LC 76 — Minimum Window Substring

Classic "find shortest window covering a target" pattern. Combines variable-shortest template + freq map + `valid` counter. This pattern recurs in LC 438, LC 567, LC 30, and any "window must contain all of X" variant.

**Setup**: two maps — `need` (what we must have) and `window` (what we currently have). A `valid` counter tracks how many distinct characters have fully met their required count — avoids scanning the map every step.

```java
public String minWindow(String s, String t) {
    // 1. Build the "need" map
    Map<Character, Integer> need = new HashMap<>(), window = new HashMap<>();
    for (char c : t.toCharArray()) need.merge(c, 1, Integer::sum);

    int left = 0, valid = 0;
    int start = 0, minLen = Integer.MAX_VALUE;

    for (int right = 0; right < s.length(); right++) {
        // 2. Expand: add s[right] into window
        char c = s.charAt(right);
        if (need.containsKey(c)) {
            window.merge(c, 1, Integer::sum);
            // only increment valid when count exactly matches (not every time)
            if (window.get(c).equals(need.get(c))) valid++;
        }

        // 3. Shrink: window satisfies constraint → try to minimize
        //    "shortest" pattern: update answer INSIDE the while loop
        while (valid == need.size()) {
            // update answer
            if (right - left + 1 < minLen) {
                minLen = right - left + 1;
                start = left;
            }
            // remove s[left] from window
            char d = s.charAt(left);
            if (need.containsKey(d)) {
                // must check BEFORE decrementing — if counts match, we're about to lose validity
                if (window.get(d).equals(need.get(d))) valid--;
                window.merge(d, -1, Integer::sum);
            }
            left++;
        }
    }
    return minLen == Integer.MAX_VALUE ? "" : s.substring(start, start + minLen);
}
```

**Step-by-step breakdown**:

| Step | What | Why |
|---|---|---|
| Build `need` map | Count required frequency of each char in `t` | Baseline to compare against |
| Expand right | Add char to `window` map, bump `valid` when a char's count reaches required | Grow window until constraint is met |
| Shrink left (while valid) | Record answer, remove left char, decrement `valid` if count drops below required | Greedily find shortest valid window |
| `valid` counter | Tracks # of distinct chars fully satisfied | O(1) check instead of comparing two maps |

**Why `equals()` not `==`**: `window.get(c)` returns `Integer` objects. For values > 127, `==` compares references and can return false even when values match. Always use `.equals()`.

**Adapting this pattern to other problems**:
- **LC 567 (Permutation in String)**: same structure, but fixed window size = `s1.length()`. Use `if` for shrinking, return true when `valid == need.size()` and window size matches
- **LC 438 (Find All Anagrams)**: same as LC 567 but collect all `start` indices instead of returning early
- **LC 30 (Substring with Concatenation of All Words)**: same idea but `need` map counts words, and you slide in word-sized steps

### Trick: Exactly K = atMost(K) − atMost(K − 1)

When asked "subarrays with **exactly** K distinct values" (LC 992), a direct sliding window is tricky because shrinking skips valid windows. Instead:

```java
// LC 992 — Subarrays with Exactly K Distinct Integers
return atMost(nums, k) - atMost(nums, k - 1);
```

```java
int atMost(int[] nums, int k) {
    Map<Integer, Integer> freq = new HashMap<>();
    int left = 0, count = 0;
    for (int right = 0; right < nums.length; right++) {
        freq.merge(nums[right], 1, Integer::sum);
        while (freq.size() > k) {
            int d = nums[left++];
            freq.merge(d, -1, Integer::sum);
            if (freq.get(d) == 0) freq.remove(d);
        }
        count += right - left + 1;  // all subarrays ending at right with ≤ k distinct
    }
    return count;
}
```

**Why `count += right - left + 1`**: every subarray `[left..right], [left+1..right], ..., [right..right]` is valid. This counts all of them.

### Trick: Monotonic Deque for Sliding Window Max/Min

For maintaining max or min in a sliding window (LC 239, LC 1438):

```java
// LC 239 — Sliding Window Maximum
Deque<Integer> deque = new ArrayDeque<>();  // stores indices, values are decreasing
int[] result = new int[n - k + 1];
for (int i = 0; i < n; i++) {
    // remove elements smaller than current from back (they can never be the max)
    while (!deque.isEmpty() && nums[deque.peekLast()] <= nums[i])
        deque.pollLast();
    deque.offerLast(i);
    // remove front if out of window
    if (deque.peekFirst() <= i - k) deque.pollFirst();
    // record answer
    if (i >= k - 1) result[i - k + 1] = nums[deque.peekFirst()];
}
```

For **both max and min** (LC 1438), use two deques — one decreasing (max), one increasing (min). Shrink left when `max - min > limit`.

### Key Problems

| Problem | Type | Window Condition |
|---|---|---|
| LC 3 (Longest Substring Without Repeating) | Variable — longest | All chars unique (use Set or freq map) |
| LC 76 (Minimum Window Substring) | Variable — shortest | Contains all chars of t (freq map + valid counter) |
| LC 209 (Minimum Size Subarray Sum) | Variable — shortest | Sum ≥ target |
| LC 239 (Sliding Window Maximum) | Fixed | Monotonic deque |
| LC 567 (Permutation in String) | Fixed | Freq map matches (window size = len(s1)) |
| LC 992 (Subarrays with Exactly K Distinct) | Variable — count | Use atMost(K) − atMost(K−1) trick |
| LC 1438 (Longest Subarray Abs Diff ≤ K) | Variable — longest | Two monotonic deques (max and min) |

### Common Pitfalls
- **Forgetting to remove left element from state** when shrinking — e.g., decrement freq map, remove from set
- **Updating answer at the wrong place** — for "longest", update *after* shrinking; for "shortest", update *during* shrinking
- **Using `if` instead of `while` for variable windows** — may need to shrink multiple times
- **Using `while` for fixed windows** — wasteful and confusing; `if` is sufficient
- **Off-by-one in window size** — window `[left, right]` has size `right - left + 1`
- **Not cleaning up freq map** — after decrementing, remove key if freq hits 0 (especially for `.size()` checks)

---

## Prefix Sum + HashMap

### When to Use
- "Subarray with sum equals / divisible by K"
- "Longest/shortest subarray with some sum property"
- "Count subarrays where sum satisfies condition"

The core idea: `sum(i..j) = prefix[j] - prefix[i-1]`. Instead of checking all O(n²) pairs, store prefix sums in a hashmap and look up the complement in O(1).

### Variant 1: Count Subarrays with Sum = K (LC 560)

Store `prefix -> count`. For each position, look up how many previous prefixes equal `prefix - k`.

```java
Map<Integer, Integer> map = new HashMap<>();
map.put(0, 1);  // empty prefix — handles subarrays starting from index 0
int prefix = 0, count = 0;

for (int num : nums) {
    prefix += num;
    count += map.getOrDefault(prefix - k, 0);  // how many earlier prefixes make sum = k
    map.merge(prefix, 1, Integer::sum);
}
```

**Why `map.put(0, 1)` is critical**: without it, you miss subarrays that start from the beginning (where `prefix` itself equals `k`).

### Variant 2: Subarray Sum Divisible by K (LC 523, LC 974)

If `prefix[i] % k == prefix[j] % k`, then `sum(j+1..i)` is divisible by `k`. Store `prefix % k` instead of raw prefix.

```java
// LC 523 — Continuous Subarray Sum (length >= 2, sum is multiple of k)
// Store prefix % k -> earliest index
Map<Integer, Integer> map = new HashMap<>();
map.put(0, -1);  // empty prefix at "index -1"
int prefix = 0;

for (int i = 0; i < nums.length; i++) {
    prefix = ((prefix + nums[i]) % k + k) % k;  // handle negatives
    if (map.containsKey(prefix)) {
        if (i - map.get(prefix) >= 2) return true;  // length >= 2 check
    } else {
        map.put(prefix, i);  // only store FIRST occurrence (want longest/earliest)
    }
}
return false;
```

```java
// LC 974 — Count subarrays with sum divisible by k
// Store prefix % k -> count (not earliest index, since we're counting)
Map<Integer, Integer> map = new HashMap<>();
map.put(0, 1);
int prefix = 0, count = 0;

for (int num : nums) {
    prefix = ((prefix + num) % k + k) % k;
    count += map.getOrDefault(prefix, 0);  // all previous same-remainder prefixes
    map.merge(prefix, 1, Integer::sum);
}
```

### Variant 3: Transform + Prefix Sum (LC 525)

When the problem isn't directly about sums, transform it into one. LC 525 (longest subarray with equal 0s and 1s): treat 0 as -1, then "equal 0s and 1s" becomes "subarray sum = 0".

```java
// LC 525 — Contiguous Array (longest subarray with equal 0 and 1)
Map<Integer, Integer> map = new HashMap<>();
map.put(0, -1);  // empty prefix at index -1
int prefix = 0, maxLen = 0;

for (int i = 0; i < nums.length; i++) {
    prefix += (nums[i] == 0) ? -1 : 1;  // transform: 0 → -1
    if (map.containsKey(prefix)) {
        maxLen = Math.max(maxLen, i - map.get(prefix));  // don't update map — want earliest
    } else {
        map.put(prefix, i);
    }
}
```

### What to Store in the HashMap

| Goal | Key | Value | Initial Entry |
|---|---|---|---|
| Count subarrays (LC 560, 974) | prefix (or prefix % k) | count | `(0, 1)` |
| Longest subarray (LC 525) | prefix | earliest index | `(0, -1)` |
| Existence + min length (LC 523) | prefix % k | earliest index | `(0, -1)` |

**Earliest index vs count** — if you're counting, store count. If you want longest/shortest, store earliest index (and never overwrite it).

### Common Pitfalls
- **Forgetting the base case** — `map.put(0, 1)` or `map.put(0, -1)` depending on variant. Without it, subarrays starting from index 0 are missed
- **Negative modulo in Java** — `(-3) % 5 == -3` in Java, not `2`. Fix: `((prefix % k) + k) % k`
- **Overwriting earliest index** — for longest subarray problems, only store the first occurrence. Use `putIfAbsent` or check `containsKey` before putting
- **Order of operations** — look up the complement *before* inserting current prefix, otherwise you'd match the current index with itself

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

### Non-Obvious DP: LC 727 — Minimum Window Subsequence

This problem doesn't scream DP — the natural instinct is two pointers (forward scan to find a window, optionally backward scan to tighten). But it has an elegant DP formulation.

**State**: `dp[i][j]` = rightmost starting index `k` such that `s2[0..j]` is a subsequence of `s1[k..i]`. Rightmost `k` = shortest window.

**Recurrence**:
- `s1[i] == s2[j]` → match them: `dp[i][j] = dp[i-1][j-1]` (or `i` if `j == 0`)
- `s1[i] != s2[j]` → skip `s1[i]`: `dp[i][j] = dp[i-1][j]`

**Space optimization**: only depends on previous row → use 1D array, iterate `j` backwards (same trick as 0/1 knapsack).

```java
int n = s1.length(), m = s2.length();
int[] dp = new int[m];
Arrays.fill(dp, -1);
int start = 0, minLen = Integer.MAX_VALUE;

for (int i = 0; i < n; i++) {
    for (int j = m - 1; j >= 0; j--) {   // backwards — 0/1 knapsack trick
        if (s1.charAt(i) == s2.charAt(j)) {
            dp[j] = (j == 0) ? i : dp[j - 1];
        }
    }
    if (dp[m - 1] != -1 && i - dp[m - 1] + 1 < minLen) {
        minLen = i - dp[m - 1] + 1;
        start = dp[m - 1];
    }
}
return minLen == Integer.MAX_VALUE ? "" : s1.substring(start, start + minLen);
```

**Why it's interesting**: the state is not "optimal value" but "optimal starting position" — tracking *where* a subsequence match begins rather than *whether* it exists. This is a useful DP trick when the answer involves position/range, not just count/boolean.

**Two-pointer alternative**: forward scan from each starting char, early termination if s2 can't be fully matched. Simpler to reason about, same O(n*m) complexity. Either approach is fine in an interview.

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

## Tree

### Traversal Templates

**DFS — Recursive** (preorder/inorder/postorder just move the "process" line):
```java
void dfs(TreeNode node) {
    if (node == null) return;
    // process(node)       ← preorder
    dfs(node.left);
    // process(node)       ← inorder
    dfs(node.right);
    // process(node)       ← postorder
}
```

**DFS — Iterative preorder** (simplest iterative — just stack with right-then-left push):
```java
Deque<TreeNode> stack = new ArrayDeque<>();
stack.push(root);
while (!stack.isEmpty()) {
    TreeNode node = stack.pop();
    // process(node)
    if (node.right != null) stack.push(node.right);  // right first
    if (node.left != null) stack.push(node.left);     // so left is popped first
}
```

**DFS — Iterative inorder** (useful when you need to stop early, e.g., kth smallest):
```java
Deque<TreeNode> stack = new ArrayDeque<>();
TreeNode curr = root;
while (curr != null || !stack.isEmpty()) {
    while (curr != null) {
        stack.push(curr);
        curr = curr.left;
    }
    curr = stack.pop();
    // process(curr) — nodes come out in sorted order for BST
    curr = curr.right;
}
```

**DFS — Iterative postorder** (trickiest — two approaches):

Approach 1: modified preorder (root→right→left) then reverse. Simple but uses O(n) extra space.
```java
Deque<TreeNode> stack = new ArrayDeque<>();
List<Integer> result = new ArrayList<>();
stack.push(root);
while (!stack.isEmpty()) {
    TreeNode node = stack.pop();
    result.add(node.val);
    if (node.left != null) stack.push(node.left);    // left first
    if (node.right != null) stack.push(node.right);  // so right is popped first
}
Collections.reverse(result);  // root→right→left reversed = left→right→root = postorder
```

Approach 2: track previous node to know if we're returning from right child. True O(1) extra space (besides stack).
```java
Deque<TreeNode> stack = new ArrayDeque<>();
TreeNode curr = root, prev = null;
while (curr != null || !stack.isEmpty()) {
    while (curr != null) {
        stack.push(curr);
        curr = curr.left;
    }
    curr = stack.peek();
    if (curr.right == null || curr.right == prev) {
        // process(curr) — right subtree done or doesn't exist
        stack.pop();
        prev = curr;
        curr = null;       // don't go left again
    } else {
        curr = curr.right; // visit right subtree first
    }
}
```

**BFS — Level order** (LC 102):
```java
Queue<TreeNode> queue = new ArrayDeque<>();
queue.offer(root);
while (!queue.isEmpty()) {
    int size = queue.size();
    for (int i = 0; i < size; i++) {
        TreeNode node = queue.poll();
        // process(node)
        if (node.left != null) queue.offer(node.left);
        if (node.right != null) queue.offer(node.right);
    }
}
```

### Pattern: Recursive DFS with Return Value

Most tree problems follow one pattern: recurse on children, combine results, return to parent.

```java
// LC 104 — Maximum Depth
int maxDepth(TreeNode node) {
    if (node == null) return 0;
    return 1 + Math.max(maxDepth(node.left), maxDepth(node.right));
}

// LC 543 — Diameter of Binary Tree
// Trick: answer isn't the return value — track it in a global variable
int diameter = 0;
int depth(TreeNode node) {
    if (node == null) return 0;
    int left = depth(node.left), right = depth(node.right);
    diameter = Math.max(diameter, left + right);  // update answer as side effect
    return 1 + Math.max(left, right);             // return depth to parent
}

// LC 124 — Binary Tree Maximum Path Sum (same trick)
int maxSum = Integer.MIN_VALUE;
int maxGain(TreeNode node) {
    if (node == null) return 0;
    int left = Math.max(0, maxGain(node.left));   // drop negative branches
    int right = Math.max(0, maxGain(node.right));
    maxSum = Math.max(maxSum, node.val + left + right);  // path through this node
    return node.val + Math.max(left, right);              // single branch to parent
}
```

**The "global answer vs return value" trick**: when the answer is a path that might not pass through the root (LC 543, 124), the return value serves the parent (single branch), but the actual answer is updated as a side effect (both branches).

### Pattern: Build Tree from Traversals (LC 105, LC 106)

**Preorder + Inorder (LC 105)**: preorder[0] is root. Find root in inorder → everything left of it is left subtree, right is right subtree.

```java
Map<Integer, Integer> inMap = new HashMap<>();  // value -> index in inorder
int preIdx = 0;

TreeNode build(int[] preorder, int[] inorder, int inLeft, int inRight) {
    if (inLeft > inRight) return null;
    int rootVal = preorder[preIdx++];
    TreeNode root = new TreeNode(rootVal);
    int inIdx = inMap.get(rootVal);
    root.left = build(preorder, inorder, inLeft, inIdx - 1);    // left FIRST (preorder)
    root.right = build(preorder, inorder, inIdx + 1, inRight);
    return root;
}
```

**Postorder + Inorder (LC 106)**: same idea but postorder's last element is root. Process right subtree FIRST (reverse postorder).

```java
int postIdx = postorder.length - 1;
// same structure, but:
root.right = build(...);  // right FIRST
root.left = build(...);
```

**Why the HashMap**: finding root in inorder by linear scan is O(n) per call → O(n²) total. HashMap makes it O(1) → O(n) total.

### Pattern: Lowest Common Ancestor (LCA)

**LCA in a Binary Tree (LC 236):**

```java
TreeNode lca(TreeNode root, TreeNode p, TreeNode q) {
    if (root == null || root == p || root == q) return root;
    TreeNode left = lca(root.left, p, q);
    TreeNode right = lca(root.right, p, q);
    if (left != null && right != null) return root;  // p and q on different sides
    return left != null ? left : right;               // both on same side
}
```

**How it works**:
- If current node is `p` or `q`, return it (found one target)
- Recurse both sides. If both return non-null → current node is LCA (targets are split)
- If only one side returns non-null → LCA is deeper on that side

**LCA in a BST (LC 235)** — use BST property, no need to search both sides:

```java
TreeNode lcaBST(TreeNode root, TreeNode p, TreeNode q) {
    while (root != null) {
        if (p.val < root.val && q.val < root.val) root = root.left;       // both left
        else if (p.val > root.val && q.val > root.val) root = root.right; // both right
        else return root;  // split point = LCA
    }
    return null;
}
```

**LCA with parent pointers (LC 1650)** — treat it like finding the intersection of two linked lists:

```java
TreeNode lcaWithParent(Node p, Node q) {
    Node a = p, b = q;
    while (a != b) {
        a = (a != null) ? a.parent : q;  // when a reaches root, jump to q
        b = (b != null) ? b.parent : p;  // when b reaches root, jump to p
    }
    return a;  // they meet at LCA
}
```

**Why this works**: same trick as LC 160 (Intersection of Two Linked Lists). Path lengths from p and q to root may differ, but `path(p→root→q→LCA)` and `path(q→root→p→LCA)` are equal length.

### Pattern: Serialize / Deserialize (LC 297)

Preorder DFS with null markers. Use a queue for deserialization to track position.

```java
// Serialize: preorder with "null" markers
String serialize(TreeNode root) {
    if (root == null) return "null";
    return root.val + "," + serialize(root.left) + "," + serialize(root.right);
}

// Deserialize: consume from queue in preorder
TreeNode deserialize(String data) {
    Queue<String> queue = new ArrayDeque<>(Arrays.asList(data.split(",")));
    return buildTree(queue);
}

TreeNode buildTree(Queue<String> queue) {
    String val = queue.poll();
    if (val.equals("null")) return null;
    TreeNode node = new TreeNode(Integer.parseInt(val));
    node.left = buildTree(queue);   // left first (preorder)
    node.right = buildTree(queue);
    return node;
}
```

### Pattern: Validate BST (LC 98)

Pass down valid range. Common mistake: using `int` bounds overflows — use `Long` or `TreeNode`.

```java
boolean isValid(TreeNode node, long min, long max) {
    if (node == null) return true;
    if (node.val <= min || node.val >= max) return false;
    return isValid(node.left, min, node.val) && isValid(node.right, node.val, max);
}
// call: isValid(root, Long.MIN_VALUE, Long.MAX_VALUE)
```

Alternative: iterative inorder and check that values are strictly increasing.

### Key Problems

| Problem | Pattern | Key Insight |
|---|---|---|
| LC 98 (Validate BST) | DFS with range | Pass min/max bounds down |
| LC 102 (Level Order) | BFS | `queue.size()` to separate levels |
| LC 105 (Construct from Pre+In) | Recursive build | HashMap for inorder index lookup |
| LC 124 (Max Path Sum) | DFS return + global answer | Return single branch, track full path as side effect |
| LC 230 (Kth Smallest in BST) | Iterative inorder | Stop after k pops |
| LC 235 (LCA in BST) | BST property | Go left/right until split |
| LC 236 (LCA in BT) | Recursive DFS | Both sides non-null = LCA |
| LC 297 (Serialize/Deserialize) | Preorder + null markers | Queue for deserialization |
| LC 543 (Diameter) | DFS return + global answer | Same trick as LC 124 |
| LC 1650 (LCA with Parent) | Two-pointer intersection | Same trick as LC 160 |

### Common Pitfalls
- **Confusing return value vs answer** — for diameter/max-path-sum, the recursive return serves the parent, the answer is tracked separately
- **BST validation with `int` bounds** — `node.val` can be `Integer.MIN_VALUE`, so use `long` for bounds
- **Build tree: left vs right first** — preorder → process left first. Postorder → process right first (reverse consumption)
- **Forgetting null check** — always handle `node == null` as base case
- **Modifying tree during traversal** — e.g., flattening to linked list (LC 114) — save `node.right` before overwriting it

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
- **Count connected components** (LC 323) — BFS/DFS also works
- **Dynamic connectivity** — edges added one by one, need to answer queries as you go

### When Union-Find is the Best or Only Choice

**1. Process edges incrementally and answer per-edge** (LC 684, LC 1319)

BFS/DFS would need to rebuild the graph each time. Union-Find processes each edge in near O(1).

```java
// LC 684 — Redundant Connection: return the LAST edge that creates a cycle
// Union-Find: try to union each edge; the first one that fails (returns false) = cycle
UnionFind uf = new UnionFind(n + 1);
for (int[] edge : edges) {
    if (!uf.union(edge[0], edge[1])) return edge;  // already connected → redundant
}

// LC 1319 — Number of Operations to Make Network Connected
// Need at least n-1 edges. If enough, answer is just components - 1.
if (edges.length < n - 1) return -1;
UnionFind uf = new UnionFind(n);
for (int[] edge : edges) uf.union(edge[0], edge[1]);
return uf.components - 1;
```

**2. Merge groups by shared attribute** (LC 721, LC 952)

When elements belong to multiple groups and you need transitive merging — "A shares email with B, B shares with C, so A/B/C are one group." BFS/DFS requires building a graph first; Union-Find merges directly.

```java
// LC 721 — Accounts Merge: group accounts that share any email
UnionFind uf = new UnionFind(accounts.size());
Map<String, Integer> emailToId = new HashMap<>();

for (int i = 0; i < accounts.size(); i++) {
    for (int j = 1; j < accounts.get(i).size(); j++) {
        String email = accounts.get(i).get(j);
        if (emailToId.containsKey(email)) {
            uf.union(i, emailToId.get(email));  // merge accounts
        } else {
            emailToId.put(email, i);
        }
    }
}

// collect emails by root
Map<Integer, TreeSet<String>> groups = new HashMap<>();
for (var entry : emailToId.entrySet()) {
    int root = uf.find(entry.getValue());
    groups.computeIfAbsent(root, k -> new TreeSet<>()).add(entry.getKey());
}
```

**3. Weighted Union-Find** (LC 399 — Evaluate Division)

`a / b = 2.0` means edge a→b with weight 2.0. To answer `a / c`, need the ratio along the path. BFS/DFS works but traverses the graph per query. Weighted Union-Find answers in near O(1) — store the ratio from each node to its parent, and update ratios during path compression.

```java
// Weighted Union-Find: parent map + weight-to-parent map
Map<String, String> parent = new HashMap<>();
Map<String, Double> weight = new HashMap<>();  // weight[x] = x / parent[x]

String find(String x) {
    if (!parent.get(x).equals(x)) {
        String root = find(parent.get(x));
        weight.put(x, weight.get(x) * weight.get(parent.get(x)));  // compress: x/root = x/parent * parent/root
        parent.put(x, root);
    }
    return parent.get(x);
}

void union(String a, String b, double val) {  // a / b = val
    parent.putIfAbsent(a, a); weight.putIfAbsent(a, 1.0);
    parent.putIfAbsent(b, b); weight.putIfAbsent(b, 1.0);
    String ra = find(a), rb = find(b);
    if (ra.equals(rb)) return;
    parent.put(ra, rb);
    // ra/rb = (a/b) * (b/rb) / (a/ra) = val * weight[b] / weight[a]
    weight.put(ra, val * weight.get(b) / weight.get(a));
}

double query(String a, String b) {
    if (!parent.containsKey(a) || !parent.containsKey(b)) return -1.0;
    String ra = find(a), rb = find(b);
    if (!ra.equals(rb)) return -1.0;  // not connected
    return weight.get(a) / weight.get(b);  // a/root ÷ b/root = a/b
}
```

**Key insight**: after `find(x)` with path compression, `weight[x]` = `x / root`. So `a / b` = `weight[a] / weight[b]` when they share the same root. The tricky part is updating `weight` during `union` — the formula `val * weight[b] / weight[a]` connects the two roots correctly.

**4. Dynamic graph with "is connected?" queries** (LC 547, LC 1101)

When edges are added over time and you need to check connectivity between arbitrary nodes. BFS/DFS is O(n) per query; Union-Find is near O(1).

```java
// LC 1101 — Earliest Moment When Everyone Becomes Friends
// Sort events by time, union each pair, return time when components == 1
Arrays.sort(logs, (a, b) -> a[0] - b[0]);
UnionFind uf = new UnionFind(n);
for (int[] log : logs) {
    uf.union(log[1], log[2]);
    if (uf.components == 1) return log[0];
}
return -1;
```

**4. MST — Kruskal's algorithm** (LC 1135, LC 1584)

Sort edges by weight, greedily add if it connects two components. Union-Find is the standard cycle check here.

```java
// LC 1584 — Min Cost to Connect All Points (Kruskal's)
// Build all edges, sort by weight, add via union-find
Arrays.sort(edges, (a, b) -> a[2] - b[2]);
UnionFind uf = new UnionFind(n);
int cost = 0, edgesUsed = 0;
for (int[] edge : edges) {
    if (uf.union(edge[0], edge[1])) {
        cost += edge[2];
        if (++edgesUsed == n - 1) break;
    }
}
```

### Union-Find vs BFS/DFS Decision

| Scenario | Union-Find | BFS/DFS |
|---|---|---|
| Static graph, find all components | Either works | Simpler |
| Edges added one by one, need per-edge answer | **Union-Find** | Rebuild graph each time |
| "Is X connected to Y?" after each add | **Union-Find** — near O(1) | O(n) per query |
| Merge groups by shared attribute | **Union-Find** | Need to build graph first |
| MST (Kruskal's) | **Union-Find** | N/A |
| Need to traverse/explore paths | N/A | **BFS/DFS** |

### String-Keyed Union-Find
For problems where nodes are strings (emails, words), use `Map<String, String> parent` instead of `int[]`.

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

### Map Utility Methods (Java 8+)

Methods that eliminate boilerplate in interview code. Work on `HashMap`, `TreeMap`, etc.

| Method | Signature | Use Case |
|---|---|---|
| `getOrDefault(k, def)` | `V` | Frequency counting: `map.getOrDefault(c, 0) + 1` |
| `putIfAbsent(k, v)` | `V` (existing or null) | Set default only if key missing |
| `computeIfAbsent(k, k -> v)` | `V` | Build adjacency lists / group by key |
| `compute(k, (k, v) -> newV)` | `V` | Read-modify-write in one call |
| `merge(k, v, (old, new) -> r)` | `V` | Cleanest frequency counting |
| `replaceAll((k, v) -> newV)` | `void` | Transform all values in-place |
| `forEach((k, v) -> ...)` | `void` | Iterate without entrySet boilerplate |

**Common interview patterns**:

```java
// Frequency map — three equivalent ways
map.put(c, map.getOrDefault(c, 0) + 1);          // most common
map.merge(c, 1, Integer::sum);                     // cleanest

// Build adjacency list — no more null checks
Map<Integer, List<Integer>> graph = new HashMap<>();
graph.computeIfAbsent(u, k -> new ArrayList<>()).add(v);
// vs the old way:
// if (!graph.containsKey(u)) graph.put(u, new ArrayList<>());
// graph.get(u).add(v);

// Group anagrams (LC 49) — one-liner grouping
Map<String, List<String>> groups = new HashMap<>();
for (String s : strs) {
    char[] key = s.toCharArray();
    Arrays.sort(key);
    groups.computeIfAbsent(new String(key), k -> new ArrayList<>()).add(s);
}
```

**`merge` vs `compute` vs `computeIfAbsent`**:
- `computeIfAbsent` — only runs if key is **absent**. Perfect for lazy initialization (lists, maps)
- `compute` — always runs, receives current value (or null). For read-modify-write
- `merge` — if absent, inserts value directly; if present, applies remapping function. Ideal for counters

---

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
