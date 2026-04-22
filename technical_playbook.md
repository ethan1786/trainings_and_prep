# Interview Playbook — Patterns, Data Structures & Tricks

> Quick-reference for staff+ level SWE interviews. Organized by **pattern** first, **data structure** second.

---

## Table of Contents

1. [Pattern Recognition Decision Tree](#pattern-recognition-decision-tree)
2. [Two Pointers](#two-pointers)
   - Templates (opposite, same-direction), LC 42 cross-ref
3. [Sliding Window](#sliding-window)
   - Variable longest/shortest, fixed window templates
   - LC 76 pattern (freq map + valid counter)
   - atMost(K) − atMost(K−1) trick (LC 992, 1248, 930)
   - atMost vs Prefix Sum + HashMap decision guide
   - Monotonic deque for window max/min (LC 239, 1438)
4. [Prefix Sum + HashMap](#prefix-sum--hashmap)
   - Count subarrays sum=K (LC 560), divisible by K (LC 523, 974)
   - Transform trick (LC 525)
5. [Binary Search](#binary-search)
   - Templates, rotated array (LC 33)
   - Median of two sorted arrays (LC 4)
6. [Intervals](#intervals)
   - Merge, insert, non-overlapping, sweep line, sort by start vs end
7. [Greedy](#greedy)
8. [Dynamic Programming](#dynamic-programming)
   - Five core patterns, top-down vs bottom-up
   - Knapsack: 0/1 (2D→1D), unbounded, combinations vs permutations
   - Non-obvious DP (LC 727), top-down → bottom-up conversion (LC 494)
9. [Backtracking](#backtracking)
   - Template, avoiding duplicates, backtracking vs DP decision
10. [Tree](#tree)
    - Traversals (recursive + iterative), DFS with return value
    - LCA (3 variants including node-not-exist LC 1644)
    - Build tree from traversals, serialize/deserialize
    - Leaf peeling / boundary inward (LC 310)
11. [Graph Algorithms](#graph-algorithms)
    - BFS template, Dijkstra, Bellman-Ford
    - MST (Kruskal's + Prim's), when to use which
12. [Union-Find](#union-find)
    - Array template, Map-based template (string/non-contiguous keys)
    - Incremental edges, merge by shared attribute, weighted UF (LC 399)
    - MST (Kruskal's), UF vs BFS/DFS decision table
13. [Topological Sort](#topological-sort)
    - Kahn's BFS, DFS post-order, lexicographic variant
14. [Linked List Tricks](#linked-list-tricks)
    - Core patterns (dummy head, fast/slow, reverse), cycle detection (LC 142)
15. [Stack Patterns](#stack-patterns)
    - Monotonic stack (next greater/smaller, LC 42)
16. [Recursive Descent / Calculator Pattern](#recursive-descent--calculator-pattern)
    - Recursion for nesting (LC 224, 394), stack for precedence (LC 227), both (LC 772)
17. [Heap / Priority Queue Patterns](#heap--priority-queue-patterns)
    - Top K, two heaps for median, merge K sorted
    - BFS + min-heap frontier for kth smallest (LC 378, 373, 786)
18. [Bit Manipulation](#bit-manipulation)
    - Essential tricks, key problems
19. [Matrix Tricks](#matrix-tricks)
    - Row/col sorted matrix: staircase walk (LC 240), binary search on value (LC 378), BFS frontier
    - Transpose vs rotation, spiral, 4-directional traversal
20. [Minor Patterns & One-Trick Techniques](#minor-patterns--one-trick-techniques)
    - Boyer-Moore voting, Kadane's, Dutch National Flag, reservoir sampling
    - Bucket sort, next permutation, Trie + wildcard DFS
21. **Java Reference** → moved to [java_reference.md](java_reference.md)
    - Common Java pitfalls, data structures, concurrency

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

When asked "count subarrays with **exactly** K [something]", a direct sliding window is hard — when you hit exactly K, the left pointer has a range of valid positions, not just one. Instead, decompose:

```
exact(K) = atMost(K) - atMost(K - 1)
```

**Why exact K is hard**: at a valid window `[left, right]` with exactly K distinct, left could potentially move right and still stay at K. You'd need a second pointer to find the range — messy.

**Why atMost K is easy**: every position from `left` to `right` is valid. No ambiguity — just `count += right - left + 1`.

```java
int atMost(int[] nums, int k) {
    Map<Integer, Integer> freq = new HashMap<>();
    int left = 0, count = 0;
    for (int right = 0; right < nums.length; right++) {
        freq.merge(nums[right], 1, Integer::sum);
        while (freq.size() > k && left <= right) {
            int d = nums[left++];
            if (freq.merge(d, -1, Integer::sum) == 0) freq.remove(d);
        }
        count += right - left + 1;  // all subarrays ending at right with ≤ k distinct
    }
    return count;
}
```

**Why `count += right - left + 1`**: every subarray `[left..right], [left+1..right], ..., [right..right]` is valid. This counts all of them. Subtraction removes subarrays with fewer than K, leaving exactly K.

**Problems that use this trick:**
| Problem | "Exactly K" of what |
|---|---|
| LC 992 | K distinct integers |
| LC 1248 | K odd numbers |
| LC 930 | sum equals K (binary array) |

### atMost(K) vs Prefix Sum + HashMap

Both solve "count subarrays with exactly K [something]" — different strengths:

| | Prefix Sum + HashMap | atMost(K) − atMost(K−1) |
|---|---|---|
| **Best for** | "Subarray sum == K" | "Exactly K distinct/odd/etc" |
| **Negative values** | Works | Breaks (window not monotonic) |
| **Space** | O(n) | O(k) |
| **Key idea** | `prefix[j] - prefix[i] == K` | Inclusion-exclusion on window counts |

**Rule of thumb**: if the problem says "sum", reach for prefix + HashMap. If it says "exactly K [countable property]", reach for atMost. LC 930 sits in the overlap (binary array: sum == count of 1s) — prefix + HashMap is simpler there.

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

### Trick: Median of Two Sorted Arrays (LC 4)

Binary search on the shorter array to find the correct partition. Split both arrays into left/right halves such that left half has `(m+n+1)/2` elements and everything in left ≤ everything in right.

```java
public double findMedianSortedArrays(int[] nums1, int[] nums2) {
    if (nums1.length > nums2.length) return findMedianSortedArrays(nums2, nums1);
    int m = nums1.length, n = nums2.length;
    int half = (m + n + 1) / 2;
    int left = 0, right = m;

    while (left <= right) {
        int pA = left + (right - left) / 2;  // partition in nums1
        int pB = half - pA;                   // partition in nums2 (determined)
        // sentinels handle boundary cases — no if/else needed
        int leftA  = (pA == 0) ? Integer.MIN_VALUE : nums1[pA - 1];
        int rightA = (pA == m) ? Integer.MAX_VALUE : nums1[pA];
        int leftB  = (pB == 0) ? Integer.MIN_VALUE : nums2[pB - 1];
        int rightB = (pB == n) ? Integer.MAX_VALUE : nums2[pB];

        if (leftA <= rightB && leftB <= rightA) {          // valid partition
            if ((m + n) % 2 == 0)
                return (Math.max(leftA, leftB) + Math.min(rightA, rightB)) / 2d;
            else
                return Math.max(leftA, leftB);
        } else if (leftB > rightA) {
            left = pA + 1;   // pA too small
        } else {
            right = pA - 1;  // pA too big
        }
    }
    return 0d;
}
```

**Key ideas:**
- **Search on shorter array** — ensures `pB = half - pA` is always non-negative
- **`(m+n+1)/2`** — the `+1` biases left half to have the extra element when total is odd, so median = `max(leftA, leftB)`
- **Sentinel values** (`MIN_VALUE`/`MAX_VALUE`) — cleanly handle boundary cases where one array contributes nothing to left or right half, avoiding if/else chains
- **Valid partition**: cross-check `leftA <= rightB` and `leftB <= rightA` — left elements of each array ≤ right elements of the other
- **`/ 2d` not `/ 2`** — integer division truncates; must use double

**Time: O(log(min(m, n)))**, Space: O(1).

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

The classic: given items with weight and value, maximize value without exceeding capacity. Each item used at most once.

```java
// 2D version (clearer to understand):
// dp[i][w] = max value using items 0..i-1 with capacity w
for (int i = 1; i <= n; i++)
    for (int w = 0; w <= capacity; w++) {
        dp[i][w] = dp[i-1][w];                          // skip item i
        if (w >= weight[i-1])
            dp[i][w] = Math.max(dp[i][w], dp[i-1][w - weight[i-1]] + value[i-1]); // take item i
    }

// 1D optimization — iterate RIGHT to LEFT so each item is used at most once:
for (int i = 0; i < n; i++)
    for (int w = capacity; w >= weight[i]; w--)  // RIGHT to LEFT
        dp[w] = Math.max(dp[w], dp[w - weight[i]] + value[i]);
```

**Why right to left**: if you go left to right, `dp[w - weight[i]]` may already include item `i` from this round, effectively using item `i` multiple times. Right to left ensures `dp[w - weight[i]]` is still from the previous round (without item `i`).

**0/1 knapsack variants:**

```java
// LC 416 (Partition Equal Subset Sum) — "can we reach target sum?"
// dp[j] = can we form sum j? (boolean knapsack)
boolean[] dp = new boolean[target + 1];
dp[0] = true;
for (int num : nums)
    for (int j = target; j >= num; j--)  // RIGHT to LEFT
        dp[j] = dp[j] || dp[j - num];

// LC 494 (Target Sum) — "how many ways to reach target?"
// dp[j] = number of ways to form sum j (counting knapsack)
int[] dp = new int[target + 1];
dp[0] = 1;
for (int num : nums)
    for (int j = target; j >= num; j--)  // RIGHT to LEFT
        dp[j] += dp[j - num];

// LC 474 (Ones and Zeroes) — 2D 0/1 knapsack with two constraints
// dp[i][j] = max items using at most i zeros and j ones
for (String s : strs) {
    int zeros = count0(s), ones = count1(s);
    for (int i = m; i >= zeros; i--)      // RIGHT to LEFT (both dimensions)
        for (int j = n; j >= ones; j--)
            dp[i][j] = Math.max(dp[i][j], dp[i - zeros][j - ones] + 1);
}
```

**4. Knapsack (unbounded)** — items reusable → iterate **left to right**

Same structure, but each item can be used unlimited times.

```java
// 1D — iterate LEFT to RIGHT so dp[w - weight[i]] includes item i from this round:
for (int i = 0; i < n; i++)
    for (int w = weight[i]; w <= capacity; w++)  // LEFT to RIGHT
        dp[w] = Math.max(dp[w], dp[w - weight[i]] + value[i]);
```

**Unbounded variants:**

```java
// LC 322 (Coin Change) — minimum coins to reach amount
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1);  // use amount+1 as "impossible" (avoids Integer.MAX_VALUE overflow)
dp[0] = 0;
for (int coin : coins)
    for (int j = coin; j <= amount; j++)  // LEFT to RIGHT
        dp[j] = Math.min(dp[j], dp[j - coin] + 1);

// LC 518 (Coin Change II) — count number of combinations
// Outer loop = coins, inner loop = amount → combinations (order doesn't matter)
int[] dp = new int[amount + 1];
dp[0] = 1;
for (int coin : coins)
    for (int j = coin; j <= amount; j++)
        dp[j] += dp[j - coin];

// LC 377 (Combination Sum IV) — count number of permutations
// Outer loop = amount, inner loop = coins → permutations (order matters)
int[] dp = new int[target + 1];
dp[0] = 1;
for (int j = 1; j <= target; j++)
    for (int num : nums)
        if (j >= num) dp[j] += dp[j - num];
```

**Combinations vs Permutations — loop order matters:**

| Goal | Outer Loop | Inner Loop | Why |
|---|---|---|---|
| Combinations (LC 518) | items | capacity | Each item considered once in order → {1,2} and {2,1} counted as same |
| Permutations (LC 377) | capacity | items | For each capacity, try all items → {1,2} and {2,1} counted separately |

### Knapsack Decision Guide

| Signal | Type | Direction | Example |
|---|---|---|---|
| Each item used once | 0/1 | Right to left | LC 416, 494, 474 |
| Items reusable | Unbounded | Left to right | LC 322, 518, 377 |
| "Can we reach X?" | Boolean | `dp[j] = dp[j] \|\| dp[j-w]` | LC 416 |
| "How many ways?" | Counting | `dp[j] += dp[j-w]` | LC 494, 518 |
| "Min/max to reach X?" | Optimization | `dp[j] = min/max(dp[j], dp[j-w] + v)` | LC 322 |
| Two constraints | 2D knapsack | Both dimensions R→L (0/1) | LC 474 |

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

### Top-Down → Bottom-Up Conversion

Mechanical steps to convert memoized recursion into iterative DP:

| Top-down | Bottom-up |
|---|---|
| State = recursive parameters | State = table dimensions |
| Base case = recursion termination | Base case = initial table values |
| Recurse on `index + 1` | Loop `index` from 0 to n |
| Memo map/array | DP table (array or map) |
| Return `memo[start state]` | Read `dp[target state]` |

**Example: LC 494 (Target Sum)** — choose +/- for each number, count ways to reach target.

```java
// Top-down: (index, currentSum) → count
// Bottom-up: push forward from base case

Map<Integer, Integer> dp = new HashMap<>();
dp.put(0, 1);  // base: sum=0 has 1 way before picking any number

for (int i = 0; i < nums.length; i++) {
    Map<Integer, Integer> next = new HashMap<>();
    for (var entry : dp.entrySet()) {
        int sum = entry.getKey(), count = entry.getValue();
        next.merge(sum + nums[i], count, Integer::sum);
        next.merge(sum - nums[i], count, Integer::sum);
    }
    dp = next;
}
return dp.getOrDefault(target, 0);
```

**When state space is sparse** (not all sums reachable), use `Map`. When dense (knapsack with small capacity), use array.

**Mental shift**: top-down asks "what do I need?" and pulls answers up. Bottom-up asks "what can I build?" and pushes answers forward.

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

### Backtracking vs DP: "Choose for Each Element" Problems

Problems like LC 494 (Target Sum) feel like permutations — for each element, choose +/-. But if you only care about the **count** (not all actual configurations), it's DP, not backtracking. The clue: overlapping subproblems (many paths reach the same `(index, sum)` state).

- **Need all configurations** → backtracking (generate each one)
- **Need count / min / max** → DP with memoization (states collapse)

Top-down memoized recursion is natural for these. See [Top-Down → Bottom-Up Conversion](#top-down--bottom-up-conversion) in the DP section for converting to iterative.

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

**LCA when nodes may not exist (LC 1644)** — can't return early on finding p or q. Must search the entire tree to confirm both exist.

```java
TreeNode ans = null;

boolean dfs(TreeNode root, TreeNode p, TreeNode q) {
    if (root == null) return false;
    boolean left = dfs(root.left, p, q);
    boolean right = dfs(root.right, p, q);
    boolean curr = (root == p || root == q);
    if ((left && right) || (curr && (left || right))) {
        ans = root;  // LCA found — won't be overwritten by ancestors
    }
    return left || right || curr;
}
```

**Key difference from LC 236**: return boolean (found p or q?) instead of the node. LCA is only set when both targets are confirmed — either on different sides (`left && right`), or current node is one target and the other is in a subtree (`curr && (left || right)`). If p or q doesn't exist, `ans` is never set.

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

### Pattern: Leaf Peeling (LC 310 — Minimum Height Trees)

Topological sort on an undirected tree — peel degree-1 nodes (leaves) layer by layer until 1-2 nodes remain. Those are the center of the tree.

```java
if (n == 1) return List.of(0);
Map<Integer, Set<Integer>> adj = new HashMap<>();
for (int[] e : edges) {
    adj.computeIfAbsent(e[0], k -> new HashSet<>()).add(e[1]);
    adj.computeIfAbsent(e[1], k -> new HashSet<>()).add(e[0]);
}
Deque<Integer> queue = new ArrayDeque<>();
for (var entry : adj.entrySet())
    if (entry.getValue().size() == 1) queue.offer(entry.getKey());

int remaining = n;
while (remaining > 2) {
    remaining -= queue.size();
    Deque<Integer> next = new ArrayDeque<>();
    while (!queue.isEmpty()) {
        int leaf = queue.poll();
        for (int neighbor : adj.get(leaf)) {
            adj.get(neighbor).remove(leaf);
            if (adj.get(neighbor).size() == 1) next.offer(neighbor);
        }
    }
    queue = next;
}
return new ArrayList<>(queue);
```

**Why it works**: minimum height tree roots are the center of the longest path. Peeling leaves inward finds the center — like finding the middle of a rope by burning from both ends.

**Same pattern applies to**:
- **Kahn's algorithm** (LC 207/210) — peel in-degree 0 nodes in directed graphs
- **LC 802 (Eventual Safe States)** — reverse edges, peel out-degree 0
- **LC 2603 (Collect Coins)** — peel leaves without coins first, then peel 2 more layers

**Key idea**: when you can't compute a property top-down (because root is unknown), work from the boundary inward.

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
| LC 310 (Min Height Trees) | Leaf peeling | Peel degree-1 nodes until ≤ 2 remain |
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

Shortest path from one source to all nodes. **Requires non-negative weights.** Greedy — always process the node with smallest known distance next.

```java
// LC 743 — Network Delay Time
int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]); // [dist, node]
pq.offer(new int[]{0, src});

while (!pq.isEmpty()) {
    int[] curr = pq.poll();
    int d = curr[0], u = curr[1];
    if (d > dist[u]) continue;  // stale entry — already found a shorter path
    for (int[] edge : graph.getOrDefault(u, List.of())) {
        int v = edge[0], w = edge[1];
        if (dist[u] + w < dist[v]) {
            dist[v] = dist[u] + w;
            pq.offer(new int[]{dist[v], v});
        }
    }
}
```

**Why the stale check**: Java's PQ doesn't support decrease-key. Instead, we add a new entry with the updated distance. Old entries with larger distances remain in the PQ — the `d > dist[u]` check skips them.

**Why negative weights break Dijkstra's**: Dijkstra assumes once a node is popped (smallest distance), its distance is final. With negative edges, a later path through a negative edge could produce a shorter distance — but we've already "finalized" the node.

**Dijkstra's variants in interviews:**

```java
// LC 787 — Cheapest Flights Within K Stops
// Modified: limit number of edges (stops). Can't use standard Dijkstra
// because we might skip a longer path that uses fewer stops.
// Use Bellman-Ford with K+1 rounds instead (see below).

// LC 1631 — Path With Minimum Effort
// Modified: edge weight = max absolute height difference along the path.
// Change relaxation: dist[v] = min(dist[v], max(dist[u], w))
// Still works with Dijkstra because "max" is monotonically non-decreasing.
```

### Bellman-Ford

Shortest path from one source. **Handles negative weights.** Relaxes all edges V-1 times. Slower than Dijkstra but more flexible.

```java
int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;
for (int i = 0; i < n - 1; i++)       // V-1 rounds
    for (int[] e : edges)               // relax all edges
        if (dist[e[0]] != Integer.MAX_VALUE && dist[e[0]] + e[2] < dist[e[1]])
            dist[e[1]] = dist[e[0]] + e[2];
```

**Why V-1 rounds**: in the worst case (a straight line graph), shortest path to the farthest node passes through V-1 edges. Each round guarantees at least one more node gets its correct distance.

**Two cases where Bellman-Ford is preferred over Dijkstra:**

**1. Negative edge weights** — Dijkstra breaks, Bellman-Ford handles correctly:
```java
// After V-1 rounds, run one more round to detect negative cycles:
for (int[] e : edges)
    if (dist[e[0]] != Integer.MAX_VALUE && dist[e[0]] + e[2] < dist[e[1]])
        return -1;  // negative cycle exists — distance can decrease infinitely
```

**2. Limited number of steps** (LC 787 — Cheapest Flights Within K Stops):
```java
// Only relax K+1 rounds instead of V-1. This gives shortest path using at most K+1 edges.
// IMPORTANT: copy dist array each round to prevent cascading relaxations within one round.
int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[src] = 0;

for (int i = 0; i <= k; i++) {          // K+1 rounds, not V-1
    int[] prev = dist.clone();           // snapshot — prevent chain relaxation
    for (int[] e : edges) {
        int u = e[0], v = e[1], w = e[2];
        if (prev[u] != Integer.MAX_VALUE && prev[u] + w < dist[v])
            dist[v] = prev[u] + w;       // use prev[], not dist[]
    }
}
return dist[dst] == Integer.MAX_VALUE ? -1 : dist[dst];
```

**Why `prev.clone()`**: without it, a chain A→B→C→D could all relax in one round, effectively using multiple edges in a single round. Cloning ensures each round adds at most one more edge to the path.

**Dijkstra vs Bellman-Ford:**

| | Dijkstra | Bellman-Ford |
|---|---|---|
| Time | O(E log V) | O(V × E) |
| Negative weights | Breaks silently | Handles correctly |
| Negative cycle detection | No | Yes (extra round) |
| Limited stops/edges | Hard to adapt | Just change number of rounds |
| Interview frequency | Higher (LC 743, 1631) | Lower (LC 787 is the main one) |

### Minimum Spanning Tree (MST)

MST = connect all nodes with minimum total edge weight. Two approaches:

**Kruskal's** — sort all edges, greedily add smallest that doesn't create a cycle. Union-Find checks connectivity.

```java
// LC 1584 — Min Cost to Connect All Points
// Step 1: build all edges (n² edges for complete graph)
List<int[]> edges = new ArrayList<>();
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        edges.add(new int[]{i, j, Math.abs(points[i][0]-points[j][0]) + Math.abs(points[i][1]-points[j][1])});

// Step 2: sort by weight, greedily union
edges.sort((a, b) -> a[2] - b[2]);
UnionFind uf = new UnionFind(n);
int total = 0, count = 0;
for (int[] e : edges) {
    if (uf.union(e[0], e[1])) {      // returns false if already connected
        total += e[2];
        if (++count == n - 1) break;  // MST has exactly n-1 edges
    }
}
```

**Why Union-Find**: when adding edge (u, v), you need to know if u and v are already connected (cycle check). `boolean[]` can't do this — it tracks "visited" not "connected." Union-Find tracks components, so `find(u) == find(v)` means they're already in the same tree.

**Prim's** — grow one tree from a starting node. Always add the cheapest edge from the tree to an unvisited node.

```java
// LC 1584 — Prim's (better for dense graphs, avoids building all edges upfront)
boolean[] inMST = new boolean[n];
// pq: [cost, node]
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
pq.offer(new int[]{0, 0});  // start from node 0
int total = 0, count = 0;

while (count < n) {
    int[] curr = pq.poll();
    if (inMST[curr[1]]) continue;  // already in tree
    inMST[curr[1]] = true;
    total += curr[0];
    count++;
    // add edges from new node to all unvisited nodes
    for (int j = 0; j < n; j++)
        if (!inMST[j])
            pq.offer(new int[]{Math.abs(points[curr[1]][0]-points[j][0]) + Math.abs(points[curr[1]][1]-points[j][1]), j});
}
```

**Why `boolean[]` works for Prim's but not Kruskal's**: Prim's grows a single connected tree — every added node connects to the existing tree. Kruskal's picks globally smallest edges, which can create disconnected fragments that need Union-Find to track.

**Kruskal's vs Prim's:**

| | Kruskal's | Prim's |
|---|---|---|
| Approach | Sort all edges, add greedily | Grow from one node |
| Data structure | Union-Find | PriorityQueue + boolean[] |
| Better for | Sparse graphs (fewer edges) | Dense graphs (many edges) |
| LC 1584 | O(n² log n²) — build + sort n² edges | O(n² log n) — avoids sorting all edges upfront |

For LC 1584 (complete graph with n² edges), Prim's is slightly better since it avoids building and sorting all edges upfront.

### When to Use Which
```
Shortest path?
├── Unweighted → BFS
├── Non-negative weights → Dijkstra's
└── Negative weights → Bellman-Ford

MST?
├── Edge list / sparse → Kruskal's (Union-Find)
└── Adjacency list / dense → Prim's (PQ + visited)
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

### Map-Based Union-Find (String or Non-Contiguous Keys)

When nodes are strings, or IDs aren't contiguous `0..n-1`, use `Map` instead of `int[]`. Nodes are lazily initialized on first access.

```java
class MapUnionFind<T> {
    Map<T, T> parent = new HashMap<>();
    Map<T, Integer> rank = new HashMap<>();
    int components = 0;

    T find(T x) {
        parent.putIfAbsent(x, x);       // lazy init
        rank.putIfAbsent(x, 0);
        if (!parent.get(x).equals(x)) {
            parent.put(x, find(parent.get(x)));  // path compression
        }
        return parent.get(x);
    }

    boolean union(T a, T b) {
        T ra = find(a), rb = find(b);
        if (ra.equals(rb)) return false;
        int rankA = rank.get(ra), rankB = rank.get(rb);
        if (rankA < rankB) parent.put(ra, rb);
        else if (rankA > rankB) parent.put(rb, ra);
        else { parent.put(rb, ra); rank.put(ra, rankA + 1); }
        components--;
        return true;
    }
}
```

**Key differences from array-based:**
- `==` becomes `.equals()` — critical for String comparison
- `putIfAbsent` for lazy init — no need to know all nodes upfront
- `components` tracking needs care — increment in `find` on first-seen, decrement in `union`

**When to use Map vs array:**
| Scenario | Use |
|---|---|
| Nodes are 0..n-1 integers | `int[]` — faster, simpler |
| Nodes are strings (LC 399, LC 721 emails) | `Map<String, String>` |
| Nodes are sparse/large integers | `Map<Integer, Integer>` |
| Nodes created dynamically (don't know all upfront) | `Map` with lazy init |

**LC 399 (Evaluate Division)** uses Map-based weighted UF — see template above. **LC 721 (Accounts Merge)** can go either way: map emails directly, or map email→accountIndex and use array-based UF on account indices (shown above).

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
| LC 895 (Max Frequency Stack) | HashMap + stack per frequency |

### Common Pitfalls
- **Forgetting elements remaining in the stack after the loop** — for "next greater element", leftover items have no next greater (set to -1 or default). For histogram, use a sentinel value (height 0) at the end to flush the stack
- **Pushing values vs indices** — push indices when you need position info (width calculation in histogram); push values when you only need comparison
- **Wrong monotonic direction** — decreasing stack for "next greater", increasing stack for "next smaller"

---

## Recursive Descent / Calculator Pattern

### Core Idea

Two orthogonal concerns: **recursion handles nesting** (`()`, `[]`), **stack handles operator precedence** (`*`/`/` before `+`/`-`). Use only what the problem needs.

### Recursion Only — No Precedence

When there's nesting but no operator precedence, recursion alone is enough. `(` or `[` triggers a recursive call, `)` or `]` returns.

**LC 224 (Basic Calculator)** — `+`, `-`, `()`:

```java
int i = 0;

int calc(String s) {
    int result = 0, num = 0, sign = 1;
    while (i < s.length()) {
        char c = s.charAt(i++);
        if (Character.isDigit(c)) num = num * 10 + (c - '0');
        else if (c == '(') num = calc(s);         // recurse — sub-expression becomes a number
        else if (c == ')') break;                  // return to caller
        else if (c == '+' || c == '-') {
            result += sign * num;
            num = 0;
            sign = (c == '+') ? 1 : -1;
        }
    }
    return result + sign * num;
}
```

**LC 394 (Decode String)** — `k[encoded_string]`, same recursive structure:

```java
int i = 0;

String decode(String s) {
    StringBuilder sb = new StringBuilder();
    int num = 0;
    while (i < s.length()) {
        char c = s.charAt(i++);
        if (Character.isDigit(c)) num = num * 10 + (c - '0');
        else if (c == '[') {
            String inner = decode(s);    // recurse — [...] becomes a string
            sb.append(inner.repeat(num));
            num = 0;
        }
        else if (c == ']') break;        // return to caller
        else sb.append(c);
    }
    return sb.toString();
}
```

**The pattern**: LC 224 and LC 394 are structurally identical — read tokens, recurse on open bracket, break on close bracket. The only difference is what you accumulate (numbers vs strings).

### Stack Only — Precedence, No Nesting

When there's operator precedence but no nesting, a stack is enough.

**LC 227 (Basic Calculator II)** — `+`, `-`, `*`, `/`, no `()`:

```java
public int calculate(String s) {
    Deque<Integer> stack = new ArrayDeque<>();
    int num = 0;
    char op = '+';
    for (int i = 0; i < s.length(); i++) {
        char c = s.charAt(i);
        if (Character.isDigit(c)) num = num * 10 + (c - '0');
        if ((!Character.isDigit(c) && c != ' ') || i == s.length() - 1) {
            switch (op) {
                case '+': stack.push(num); break;
                case '-': stack.push(-num); break;
                case '*': stack.push(stack.pop() * num); break;   // compute immediately
                case '/': stack.push(stack.pop() / num); break;   // compute immediately
            }
            num = 0;
            op = c;
        }
    }
    return stack.stream().mapToInt(Integer::intValue).sum();
}
```

**Why the stack gives precedence**: `*`/`/` pop and compute immediately. `+`/`-` just push — they're computed later when summing. This naturally makes `*`/`/` higher precedence.

### Recursion + Stack — Both Nesting and Precedence

**LC 772 (Basic Calculator III)** — `+`, `-`, `*`, `/`, `()`:

```java
int i = 0;  // global pointer — advances across recursive calls

int calc(String s) {
    Deque<Integer> stack = new ArrayDeque<>();
    int num = 0;
    char op = '+';

    while (i < s.length()) {
        char c = s.charAt(i++);
        if (Character.isDigit(c)) num = num * 10 + (c - '0');
        if (c == '(') num = calc(s);           // recurse — () becomes a number
        if (c == ')' || i == s.length() || (!Character.isDigit(c) && c != ' ')) {
            switch (op) {
                case '+': stack.push(num); break;
                case '-': stack.push(-num); break;
                case '*': stack.push(stack.pop() * num); break;
                case '/': stack.push(stack.pop() / num); break;
            }
            num = 0;
            op = c;
            if (c == ')') break;               // return to caller
        }
    }
    return stack.stream().mapToInt(Integer::intValue).sum();
}
```

**Why `i == s.length()`**: flushes the last number at the top-level call. For `"1+2*3"`, after reading `'3'`, `i` becomes `s.length()`. Without this check, the final digit never triggers the switch. Recursive calls never hit this — they always exit via `c == ')'`.

### Decision Guide

| Problem | Nesting | Precedence | Use |
|---|---|---|---|
| LC 224 (Basic Calculator) | `()` | No | Recursion only |
| LC 394 (Decode String) | `[]` | No | Recursion only (same structure as 224) |
| LC 227 (Basic Calculator II) | No | `*`/`/` vs `+`/`-` | Stack only |
| LC 772 (Basic Calculator III) | `()` | `*`/`/` vs `+`/`-` | Recursion + stack |

### Common Pitfalls
- **Not flushing the last number** — for recursion: `return result + sign * num`. For stack: the `i == s.length()` check
- **Global `i` pointer** — must be a class field, not a local variable, so recursive calls advance the same pointer
- **LC 394: forgetting to reset `num`** after processing `[` — the repeat count should reset to 0

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

**Kth smallest via BFS + min-heap (frontier expansion)** (LC 378, LC 373, LC 786):

Turn a structured space (sorted matrix, pair sums) into a graph problem. Start from the smallest element, expand neighbors, pop k times.

```java
// LC 378 — Kth Smallest in Sorted Matrix
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
boolean[][] visited = new boolean[n][n];
pq.offer(new int[]{matrix[0][0], 0, 0});
visited[0][0] = true;

while (--k > 0) {
    int[] curr = pq.poll();
    int r = curr[1], c = curr[2];
    if (r + 1 < n && !visited[r+1][c]) {  // expand down
        visited[r+1][c] = true;
        pq.offer(new int[]{matrix[r+1][c], r+1, c});
    }
    if (c + 1 < n && !visited[r][c+1]) {  // expand right
        visited[r][c+1] = true;
        pq.offer(new int[]{matrix[r][c+1], r, c+1});
    }
}
return pq.peek()[0];
```

**Why it works**: sorted rows + columns mean the next smallest must be a neighbor of something already popped. The heap holds the frontier — its min is always the global next smallest. O(k log n).

**When to use**: kth element from a structured/virtual matrix where you can't afford to materialize the whole thing. Same pattern applies to:
- **LC 373** (K Smallest Pairs) — `sum[i][j] = a[i] + b[j]`, expand `(i+1,j)` and `(i,j+1)`
- **LC 786** (Kth Smallest Prime Fraction) — sorted fractions as virtual matrix

**Two approaches to "kth smallest in sorted structure":**
| Approach | How | When |
|---|---|---|
| Min-heap + BFS frontier | Pop k times, expand neighbors | k is small relative to n² |
| Binary search on value | Count elements ≤ mid, O(n) per count | k is large, need O(n log(range)) |

### Key Problems
| Problem | Pattern |
|---|---|
| LC 215 (Kth Largest) | Max-heap of size k (evict smallest) |
| LC 347 (Top K Frequent) | Frequency map + min-heap |
| LC 295 (Find Median) | Two heaps (max + min) |
| LC 23 (Merge K Sorted) | Min-heap of heads |
| LC 253 (Meeting Rooms II) | Min-heap of end times |
| LC 378 (Kth Smallest in Matrix) | BFS + min-heap frontier / binary search on value |
| LC 373 (K Smallest Pairs) | BFS + min-heap frontier |

### PriorityQueue Gotchas
- `remove(obj)` is **O(n)** — prefer `TreeMap` when you need arbitrary removal
- Iterator is **NOT sorted** — only `peek()/poll()` gives min. To traverse in order, poll in a loop (destructive) or copy-then-poll.
- **Not stable** — equal-priority elements are NOT returned in insertion order. Add a sequence number to break ties:
  ```java
  int seq = 0;
  pq.add(new int[]{priority, seq++, value});
  // comparator: compare priority first, then seq
  ```
- Duplicates allowed (unlike TreeMap)
- **String sorting**: `compareTo` is lexicographic and case-sensitive (`"Banana" < "apple"`). For case-insensitive: `new PriorityQueue<>(String.CASE_INSENSITIVE_ORDER)`

### Sorted traversal — use the right structure
| Need | Use | Why |
|---|---|---|
| Repeated peek/poll of min/max | `PriorityQueue` | O(log n) offer/poll |
| Sorted iteration | `TreeSet` / `TreeMap` | Iterator is sorted |
| Both | `TreeMap` | Sorted + O(log n) min/max |

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

### Row/Column Sorted Matrix Patterns

When rows and columns are independently sorted (not fully sorted like LC 74), three techniques exploit this structure:

**1. Staircase Walk — search or count in O(m + n)** (LC 240, LC 378)

Start from **top-right** (or bottom-left). Left decreases value, down increases — each step eliminates a row or column.

```java
// LC 240 — Search a 2D Matrix II: find if target exists
public boolean searchMatrix(int[][] matrix, int target) {
    int row = 0, col = matrix[0].length - 1;  // start top-right
    while (row < matrix.length && col >= 0) {
        if (matrix[row][col] == target) return true;
        if (matrix[row][col] > target) col--;  // too big → eliminate column
        else row++;                              // too small → eliminate row
    }
    return false;
}

// Count elements <= target — O(n), used in LC 378 binary search approach
int countLessOrEqual(int[][] matrix, int target) {
    int count = 0, col = matrix.length - 1;
    for (int row = 0; row < matrix.length; row++) {
        while (col >= 0 && matrix[row][col] > target) col--;  // col never resets
        count += col + 1;
    }
    return count;
}
```

**Key insight**: `col` never increases across rows. If `matrix[row][col] > target`, then `matrix[row+1][col] > target` too (column sorted), so a column once passed never comes back. Total: O(m + n).

**2. Binary Search on Value — kth smallest in O(n × log(range))** (LC 378)

Binary search on the answer value, use staircase walk to count elements ≤ mid:

```java
int lo = matrix[0][0], hi = matrix[n-1][n-1];
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (countLessOrEqual(matrix, mid) < k) lo = mid + 1;
    else hi = mid;
}
return lo;  // converges to an actual matrix value
```

**Why `lo` is always a real value**: at the boundary, count jumps from `< k` to `≥ k` exactly at a value that exists in the matrix.

**3. BFS + Min-Heap Frontier — kth smallest in O(k log n)** (LC 378, LC 373)

Start from smallest `[0][0]`, expand right and down, pop k times. See Heap section for full template.

**When to use which:**
| Task | Technique | Time |
|---|---|---|
| Search for a value | Staircase walk | O(m + n) |
| Count elements ≤ value | Staircase walk | O(m + n) |
| Kth smallest (k is large) | Binary search on value + staircase count | O(n log(range)) |
| Kth smallest (k is small) | BFS + min-heap frontier | O(k log n) |

**Related — fully sorted matrix** (LC 74): each row starts after the previous row ends. Treat as a flat sorted array, binary search with `matrix[mid/cols][mid%cols]`. O(log(m×n)).

### Transpose vs Rotation

Transpose is a **reflection** along the main diagonal, not a rotation.

```
Original:       Transpose:       90° CW:          90° CCW:
1 2 3            1 4 7            7 4 1            3 6 9
4 5 6            2 5 8            8 5 2            2 5 8
7 8 9            3 6 9            9 6 3            1 4 7
```

| Transformation | Steps |
|---|---|
| **90° CW** | Transpose + reverse each row |
| **90° CCW** | Transpose + reverse each column |
| **180°** | Reverse each row + reverse each column |

### Rotate Image 90° CW (LC 48)
```java
// Step 1: Transpose (swap [i][j] with [j][i])
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        swap(matrix[i][j], matrix[j][i]);
// Step 2: Reverse each row
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

> **Java-specific reference** (data structures, concurrency, common pitfalls) has been moved to [java_reference.md](java_reference.md).
