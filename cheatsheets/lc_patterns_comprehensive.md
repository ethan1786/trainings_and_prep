# LC Patterns — Comprehensive Quick Reference

> Skim for pattern recognition. Don't memorize — just refresh "oh right, that's the approach."

---

## Quick Reference — "What pattern is this?"

| Signal in problem | Pattern |
|---|---|
| "Substring" or "subarray" with constraint | Sliding window |
| "All pairs" or "sorted input" | Two pointers |
| "Nested structure" or "matching brackets" | Stack |
| "Top K" or "Kth largest" | Heap |
| "Shortest path" or "level by level" | BFS |
| "All paths" or "combinations" | DFS / backtracking |
| "Dependencies" or "ordering" | Topological sort |
| "Overlapping intervals" | Sort + sweep |
| "Lookup/grouping" | HashMap |
| "Sorted + search" | Binary search |
| "Optimal substructure" | DP |

---

## String Parsing

| LC # | Problem | Key Insight |
|---|---|---|
| 71 | Simplify Path | Split by "/", use stack, skip "." and "..", pop for ".." |
| 468 | Validate IP Address | Split by "." or ":", validate each segment's range and format |
| 8 | String to Integer | Handle: whitespace, sign, overflow (check before multiply), stop at non-digit |
| 394 | Decode String | Stack of (string, count). When "]" → pop and repeat. Nested = recursive stack. |
| 227 | Basic Calculator II | Stack for values. Process * / immediately, + - push to stack, sum at end. |
| 722 | Remove Comments | State machine: normal, in //, in /* */. Track across lines for block comments. |

---

## HashMap / Counting

| LC # | Problem | Key Insight |
|---|---|---|
| 1 | Two Sum | Map value → index. Check complement exists before inserting. |
| 49 | Group Anagrams | Sort each string as key → group by sorted key. |
| 347 | Top K Frequent | Count frequency map → bucket sort by frequency (index = freq, value = list of nums). O(N). |
| 560 | Subarray Sum = K | Prefix sum + map. map[prefixSum] = count. At each index: check map[prefixSum - k]. |
| 128 | Longest Consecutive | HashSet. For each num, if num-1 NOT in set → it's a sequence start. Count up from there. |
| 380 | Insert Delete GetRandom O(1) | HashMap (val→index) + ArrayList. Swap with last before remove. |

---

## Stack

| LC # | Problem | Key Insight |
|---|---|---|
| 20 | Valid Parentheses | Push open brackets. Pop and compare on close. Stack empty at end = valid. |
| 155 | Min Stack | Two stacks: main + min. Push to min only when ≤ current min. |
| 739 | Daily Temperatures | Monotonic decreasing stack of indices. Pop when current > stack top. |
| 84 | Largest Rectangle in Histogram | Monotonic increasing stack. On pop: width = current_i - stack.peek() - 1. |
| 150 | Evaluate RPN | Push numbers. On operator: pop two, compute, push result. |

---

## Sliding Window

| LC # | Problem | Key Insight |
|---|---|---|
| 3 | Longest Substring Without Repeating | HashSet + left pointer. When duplicate found, shrink left until removed. |
| 76 | Minimum Window Substring | HashMap for target counts. Expand right until valid, shrink left to minimize. Track "formed" count. |
| 424 | Longest Repeating Character Replacement | Window where (window_size - max_freq_char) ≤ k. Shrink left when violated. |
| 239 | Sliding Window Maximum | Monotonic decreasing deque of indices. Remove from front if outside window. |
| 567 | Permutation in String | Fixed-size window = s1.length(). Compare character frequency maps. |

**Template:**
```
left = 0
for right in range:
    add arr[right] to window
    while window invalid:
        remove arr[left], left++
    update answer
```

---

## Two Pointers

| LC # | Problem | Key Insight |
|---|---|---|
| 15 | 3Sum | Sort. Fix one, two pointers on rest. Skip duplicates. |
| 11 | Container With Most Water | Start at both ends. Move the shorter side inward. |
| 42 | Trapping Rain Water | Two pointers + track leftMax, rightMax. Water = min(leftMax, rightMax) - height. |
| 125 | Valid Palindrome | Two pointers inward, skip non-alphanumeric. |
| 167 | Two Sum II (sorted) | Left + right. Too small → left++. Too big → right--. |

---

## Intervals

| LC # | Problem | Key Insight |
|---|---|---|
| 56 | Merge Intervals | Sort by start. If current.start ≤ prev.end → merge (extend prev.end). |
| 57 | Insert Interval | Add all before, merge overlapping, add all after. |
| 253 | Meeting Rooms II | Sort start times. Min-heap of end times. Heap size = rooms needed. |
| 435 | Non-overlapping Intervals | Sort by end. Greedily keep earliest-ending. Count removed. |

---

## Graph / BFS / DFS

| LC # | Problem | Key Insight |
|---|---|---|
| 200 | Number of Islands | DFS/BFS from each '1'. Mark visited. Count components. |
| 207 | Course Schedule | Topological sort. In-degree map. BFS from in-degree 0. If processed ≠ total → cycle. |
| 994 | Rotting Oranges | Multi-source BFS. All rotten in queue initially. Level = minutes. |
| 133 | Clone Graph | BFS/DFS + HashMap(original → clone). |
| 210 | Course Schedule II | Same as 207 but collect processing order. |

**Topological sort template:**
```
compute in-degree for all nodes
queue = all nodes with in-degree 0
while queue:
    node = poll
    for each neighbor:
        in-degree[neighbor]--
        if 0: add to queue
```

---

## Binary Search

| LC # | Problem | Key Insight |
|---|---|---|
| 33 | Search in Rotated Array | Find which half is sorted. If target in sorted half → go there. |
| 34 | Find First/Last Position | Two binary searches: leftmost and rightmost. |
| 153 | Find Min in Rotated | If mid > right → min in right half. |
| 981 | Time Based KV Store | HashMap + binary search on timestamp list. |

**Template:**
```
lo = 0, hi = n-1
while lo <= hi:
    mid = lo + (hi - lo) / 2
    if condition: hi = mid - 1
    else: lo = mid + 1
```

---

## Heap / Priority Queue

| LC # | Problem | Key Insight |
|---|---|---|
| 347 | Top K Frequent | Min-heap size K. Or bucket sort O(N). |
| 253 | Meeting Rooms II | Min-heap of end times = occupied rooms. |
| 295 | Find Median from Stream | Max-heap (left) + min-heap (right). Balance sizes. |
| 23 | Merge K Sorted Lists | Min-heap of K heads. Poll smallest, add next. |
| 215 | Kth Largest | Min-heap size K. Top = answer. |

---

## Tree / Recursion

| LC # | Problem | Key Insight |
|---|---|---|
| 104 | Max Depth | 1 + max(left, right). Base: null → 0. |
| 226 | Invert Binary Tree | Swap left/right recursively. |
| 236 | LCA | If root == p or q → return root. Both sides non-null → root is LCA. |
| 98 | Validate BST | Pass min/max bounds down recursively. |
| 102 | Level Order | BFS with queue. Level size = queue.size() at start of each level. |

---

## Dynamic Programming

| LC # | Problem | Key Insight |
|---|---|---|
| 70 | Climbing Stairs | dp[i] = dp[i-1] + dp[i-2]. Fibonacci. |
| 322 | Coin Change | dp[amount] = min(dp[amount - coin] + 1) for each coin. |
| 139 | Word Break | dp[i] = true if dp[j] && s[j:i] in dict. |
| 300 | LIS | dp[i] = max(dp[j] + 1) where nums[j] < nums[i]. Or patience sort O(N log N). |
| 53 | Max Subarray | dp[i] = max(nums[i], dp[i-1] + nums[i]). Kadane's. |

---

## Design / OOD

| LC # | Problem | Key Insight |
|---|---|---|
| 146 | LRU Cache | LinkedHashMap(accessOrder=true) + removeEldestEntry. Or HashMap + DLL. |
| 460 | LFU Cache | HashMap(key→node) + HashMap(freq→LinkedHashSet) + minFreq. |
| 355 | Design Twitter | HashMap per user (followees + tweets). GetFeed = merge K sorted (heap). |
| 362 | Design Hit Counter | Queue of timestamps. Or circular array [300]. |
| 1166 | Design File System | HashMap<path, value>. On create: check parent path exists. |
