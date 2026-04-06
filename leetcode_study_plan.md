# LeetCode Study Plan for Staff/Principal SWE Interviews

**Target companies:** Airbnb, Circle, Coinbase, Datadog, Figma, Netflix, OpenAI, Pinterest, Stripe
**Difficulty focus:** Medium (primary), select Hard (frequently asked)
**Time estimate:** ~4 weeks at 2–3 problems/day (~55 problems total)
**Lighter coverage:** Two pointers, strings, arrays, trees (already practiced)
**Heavier coverage:** Graphs, DP (core patterns only), intervals, heaps, concurrency

---

## Priority of Topics (by interview frequency at target companies)

1. **Hash Maps / Design** — very high (all companies)
2. **Graphs (BFS/DFS/Topo Sort/Union Find)** — very high (Airbnb, Pinterest, Coinbase, OpenAI)
3. **Intervals / Greedy** — high (Airbnb, Pinterest, Stripe, Netflix)
4. **Heaps / Priority Queues** — high (Pinterest, Netflix, Datadog)
5. **Sliding Window** — high (all companies)
6. **Binary Search** — medium-high (Datadog, Stripe, Figma)
7. **DP** — medium (focus on classic patterns)
8. **Backtracking** — medium (Airbnb, Figma)
9. **Stacks (Monotonic)** — medium (Pinterest, Datadog)
10. **Concurrency** — low-medium (OpenAI, Netflix)

---

## Week 1: Foundations Refresh + Hash Maps + Sliding Window

### Hash Maps / Frequency Counting

- [ ] 49. Group Anagrams (Medium) — Airbnb, Stripe, Coinbase
- [ ] 560. Subarray Sum Equals K (Medium) — Coinbase, Datadog
- [ ] 146. LRU Cache (Medium) — Airbnb, Netflix, Stripe, Circle
- [ ] 380. Insert Delete GetRandom O(1) (Medium) — Circle, Figma, Netflix
- [ ] 460. LFU Cache (Hard) — Circle, OpenAI, Airbnb

### Sliding Window

- [ ] 3. Longest Substring Without Repeating Characters (Medium) — Airbnb, Stripe, Netflix
- [ ] 76. Minimum Window Substring (Hard) — Airbnb, Stripe, Datadog
- [ ] 239. Sliding Window Maximum (Hard) — Pinterest, Datadog
- [ ] 424. Longest Repeating Character Replacement (Medium) — Airbnb, Figma — variable window + constraint
- [ ] 567. Permutation in String (Medium) — Airbnb, Coinbase — fixed window + frequency match
- [ ] 438. Find All Anagrams in a String (Medium) — Airbnb, Figma — fixed window variant of 567
- [ ] 1004. Max Consecutive Ones III (Medium) — Datadog, Netflix — variable window + flip budget
- [ ] 209. Minimum Size Subarray Sum (Medium) — Stripe, Coinbase — variable window + sum target
- [ ] 30. Substring with Concatenation of All Words (Hard) — Airbnb, Stripe — same pattern as 76 (window + frequency match)
- [ ] 727. Minimum Window Subsequence (Hard) — Airbnb, Pinterest — harder variant of 76 (Premium)
- [ ] 159. Longest Substring with At Most Two Distinct Characters (Medium) — Airbnb, Netflix — same shrink logic as 76 (Premium)
- [ ] 739. Daily Temperatures (Medium) — Datadog, Pinterest — monotonic stack (same core idea as 239)
- [ ] 1438. Longest Continuous Subarray With Absolute Diff ≤ Limit (Medium) — Pinterest, Datadog — monotonic deque, same pattern as 239
- [ ] 862. Shortest Subarray with Sum at Least K (Hard) — Stripe, Coinbase — monotonic deque on prefix sums

### Prefix Sum

- [ ] 525. Contiguous Array (Medium) — Stripe, Coinbase — prefix sum + HashMap (count variant)
- [ ] 523. Continuous Subarray Sum (Medium) — Coinbase, Circle — prefix sum + modulo + HashMap
- [ ] 974. Subarray Sums Divisible by K (Medium) — Stripe, Datadog — prefix sum + modulo counting
- [ ] 304. Range Sum Query 2D (Medium) — Datadog, Figma — 2D prefix sum
- [ ] 238. Product of Array Except Self (Medium) — Airbnb, Stripe, Coinbase — prefix/suffix product (same idea)

### Two Pointers / Arrays / Strings (light refresh)

- [ ] 15. 3Sum (Medium) — Airbnb, Coinbase
- [ ] 42. Trapping Rain Water (Hard) — Airbnb, Datadog, Pinterest
- [ ] 271. Encode and Decode Strings (Medium) — Airbnb, Stripe (Premium)

**Week 1 total: 27 problems**

---

## Week 2: Graphs + Topological Sort + Union Find

### BFS / DFS

- [ ] 200. Number of Islands (Medium) — Airbnb, Datadog, OpenAI, Figma
- [ ] 133. Clone Graph (Medium) — Airbnb, Coinbase
- [ ] 127. Word Ladder (Hard) — Airbnb, Figma, Circle
- [ ] 994. Rotting Oranges (Medium) — Pinterest, Coinbase
- [ ] 417. Pacific Atlantic Water Flow (Medium) — Airbnb, Pinterest

### Topological Sort

- [ ] 207. Course Schedule (Medium) — Airbnb, OpenAI, Figma
- [ ] 210. Course Schedule II (Medium) — Airbnb, Datadog, Circle
- [ ] 269. Alien Dictionary (Hard) — Airbnb, Pinterest (Premium)

### Union Find

- [ ] 323. Number of Connected Components (Medium) — Airbnb, Coinbase (Premium)
- [ ] 684. Redundant Connection (Medium) — Pinterest, Coinbase
- [ ] 721. Accounts Merge (Medium) — Airbnb, Pinterest
- [ ] 399. Evaluate Division (Medium) — Airbnb, Coinbase — weighted Union-Find or BFS on graph

### Trees (light refresh)

- [ ] 236. Lowest Common Ancestor of a Binary Tree (Medium) — Airbnb, Netflix, OpenAI, Figma
- [ ] 297. Serialize and Deserialize Binary Tree (Hard) — Airbnb, Netflix, Circle, OpenAI
- [ ] 102. Binary Tree Level Order Traversal (Medium) — Figma, Netflix

### Design Data Structures

- [ ] 208. Implement Trie (Medium) — Airbnb, Stripe, Circle — prefix tree fundamentals (warmup for 588/1166)
- [ ] 212. Word Search II (Hard) — Airbnb, Figma — trie + DFS backtracking
- [ ] 355. Design Twitter (Medium) — Airbnb, Circle — heap + hash map + linked list
- [ ] 981. Time Based Key-Value Store (Medium) — Datadog, Stripe, Circle, OpenAI — hash map + binary search
- [ ] 1396. Design Underground System (Medium) — Stripe, Datadog — hash map bookkeeping
- [ ] 362. Design Hit Counter (Medium) — Datadog, Stripe, Pinterest, Circle — queue or circular array (Premium)
- [ ] 588. Design In-Memory File System (Hard) — Datadog, Stripe, Airbnb — trie of directories (Premium)
- [ ] 716. Max Stack (Hard) — Netflix, Pinterest — TreeMap + doubly linked list (Premium)
- [ ] 1166. Design File System (Medium) — Airbnb, Stripe — hash map / trie (Premium)
- [ ] 895. Maximum Frequency Stack (Hard) — Netflix, Coinbase — hash map + stack per frequency

**Week 2 total: 25 problems**

---

## Week 3: DP (Core Patterns) + Intervals + Greedy

### DP — Focus on Recognizable Patterns

DP appears ~15-20% of the time. Don't over-invest — learn to recognize the 5 core
patterns and set up the recurrence. That's sufficient for staff+ level.

**1D DP (sequence/decision):**

- [ ] 198. House Robber (Medium) — Airbnb, Coinbase — simplest DP warmup
- [ ] 139. Word Break (Medium) — Airbnb, Stripe, Netflix
- [ ] 322. Coin Change (Medium) — Coinbase, Stripe, Figma
- [ ] 91. Decode Ways (Medium) — Airbnb, Figma
- [ ] 300. Longest Increasing Subsequence (Medium) — Pinterest, Datadog — classic 1D DP + binary search optimization
- [ ] 152. Maximum Product Subarray (Medium) — Airbnb, Coinbase — track min and max simultaneously

**2D DP (grid/string comparison):**

- [ ] 62. Unique Paths (Medium) — Figma, Coinbase
- [ ] 1143. Longest Common Subsequence (Medium) — Coinbase, Netflix
- [ ] 72. Edit Distance (Medium) — Airbnb, Stripe, OpenAI

**Knapsack / Subset DP:**

- [ ] 416. Partition Equal Subset Sum (Medium) — Coinbase, Netflix
- [ ] 518. Coin Change II (Medium) — Stripe, Coinbase

### Intervals

- [ ] 56. Merge Intervals (Medium) — Airbnb, Stripe, Datadog, Figma
- [ ] 57. Insert Interval (Medium) — Airbnb, Stripe, Pinterest — builds on 56
- [ ] 253. Meeting Rooms II (Medium) — Airbnb, Pinterest (Premium)
- [ ] 435. Non-overlapping Intervals (Medium) — Airbnb, Netflix — greedy interval scheduling
- [ ] 1235. Maximum Profit in Job Scheduling (Hard) — Airbnb, Pinterest, Netflix
- [ ] 759. Employee Free Time (Hard) — Pinterest, Airbnb — intervals + heap

### Greedy

- [ ] 621. Task Scheduler (Medium) — Airbnb, Netflix
- [ ] 134. Gas Station (Medium) — Coinbase, Stripe

**Week 3 total: 19 problems**

---

## Week 4: Heaps + Stacks + Binary Search + Backtracking + Concurrency

### Heaps / Priority Queues

- [ ] 295. Find Median from Data Stream (Hard) — Airbnb, Netflix, Datadog, Circle
- [ ] 347. Top K Frequent Elements (Medium) — Coinbase, Datadog
- [ ] 23. Merge k Sorted Lists (Hard) — Airbnb, Datadog, Circle
- [ ] 973. K Closest Points to Origin (Medium) — Airbnb, Pinterest
- [ ] 215. Kth Largest Element in an Array (Medium) — Airbnb, Datadog — quickselect or heap

### Linked List

- [ ] 206. Reverse Linked List (Easy) — Airbnb, Coinbase — fundamental, know iterative + recursive
- [ ] 25. Reverse Nodes in k-Group (Hard) — Airbnb, Netflix — builds on 206
- [ ] 141. Linked List Cycle (Easy) — Coinbase, Figma — fast/slow pointer
- [ ] 142. Linked List Cycle II (Medium) — Pinterest, Netflix — find cycle start (Floyd's algorithm)

### Monotonic Stack / Stack Parsing

- [ ] 84. Largest Rectangle in Histogram (Hard) — Pinterest, Datadog
- [ ] 739. Daily Temperatures (Medium) — Datadog, Pinterest
- [ ] 224. Basic Calculator (Hard) — Pinterest, Airbnb, Stripe — stack-based expression parsing
- [ ] 227. Basic Calculator II (Medium) — Airbnb, Figma — stack + operator precedence
- [ ] 394. Decode String (Medium) — Datadog, Figma, Stripe — stack-based string parsing

### Matrix

- [ ] 48. Rotate Image (Medium) — Airbnb, Figma — transpose + reverse
- [ ] 54. Spiral Matrix (Medium) — Airbnb, Netflix — boundary shrinking

### Binary Search

- [ ] 33. Search in Rotated Sorted Array (Medium) — Figma, Stripe, Datadog
- [ ] 528. Random Pick with Weight (Medium) — Airbnb, Stripe — prefix sum + binary search
- [ ] 4. Median of Two Sorted Arrays (Hard) — Datadog, Pinterest

### Backtracking

- [ ] 46. Permutations (Medium) — Airbnb, Figma — backtracking fundamental
- [ ] 79. Word Search (Medium) — Airbnb, Figma
- [ ] 51. N-Queens (Hard) — Figma, Coinbase
- [ ] 17. Letter Combinations of a Phone Number (Medium) — Airbnb, Netflix

### Bit Manipulation

- [ ] 191. Number of 1 Bits (Easy) — Coinbase, Datadog — Hamming weight, n & (n-1) trick
- [ ] 338. Counting Bits (Easy) — Coinbase, Figma — DP on bits

### Concurrency (relevant for backend/platform roles)

- [ ] 1188. Design Bounded Blocking Queue (Medium) — OpenAI, Netflix (Premium)
- [ ] 1117. Building H2O (Medium) — OpenAI, Netflix (Premium)

**Week 4 total: 27 problems**

---

## Bonus: Company-Specific Must-Dos

Do these before a specific company's interview or if you have extra time.

### Airbnb Classics

- [ ] 68. Text Justification (Hard) — Airbnb's most famous question
- [ ] 336. Palindrome Pairs (Hard) — frequently reported
- [ ] 787. Cheapest Flights Within K Stops (Medium) — graph + DP

### Pinterest Classics

- [ ] 772. Basic Calculator III (Hard) — full expression evaluation
- [ ] 277. Find the Celebrity (Medium) — elimination pattern
- [ ] 632. Smallest Range Covering K Lists (Hard) — heap + sliding window

### Datadog / Figma

- [ ] 588. Design In-Memory File System (Hard) — trie of directories (also Airbnb, Stripe)
- [ ] 394. Decode String (Medium) — stack-based string parsing (also in Week 4)

### OpenAI

- [ ] 1116. Print Zero Even Odd (Medium) — concurrency + semaphores
- [ ] 284. Peeking Iterator (Medium) — iterator design pattern

---

## Minor Patterns (Skim in Non-Coding Time)

One-trick patterns — know the technique and you can solve them instantly. No deep practice needed.

### Quick Wins (5 min each — just know the trick)

- [ ] 169. Majority Element (Easy) — **Boyer-Moore Voting**: cancel different elements, survivor is majority. O(1) space.
- [ ] 53. Maximum Subarray (Medium) — **Kadane's**: `maxHere = max(num, maxHere + num)`. Same idea as LC 152.
- [ ] 75. Sort Colors (Medium) — **Dutch National Flag**: 3-way partition with `low/mid/high` pointers, single pass.
- [ ] 41. First Missing Positive (Hard) — **In-place array marking**: use index as hash, sign-flip to mark visited. O(1) space.
- [ ] 876. Middle of the Linked List (Easy) — **Fast/slow pointer**: slow moves 1, fast moves 2, slow ends at middle.
- [ ] 382. Linked List Random Node (Medium) — **Reservoir Sampling**: keep item with probability `1/i` while streaming.
- [ ] 164. Maximum Gap (Medium) — **Bucket Sort**: when value range bounded, O(n) sort via buckets.

### Know the Concept (10 min each — read the approach once)

- [ ] 211. Design Add and Search Words (Medium) — **Trie + wildcard DFS**: branch at `.` to explore all children.
- [ ] 31. Next Permutation (Medium) — **Next permutation algorithm**: find dip → find swap → swap → reverse. Memorize the 4 steps.
- [ ] 528. Random Pick with Weight (Medium) — already in plan — **Prefix sum + binary search** for weighted random.

### Reference Only (don't solve — just know they exist)

| Technique | What It Does | When You'd Use It |
|---|---|---|
| **Segment Tree / BIT** | Range update + range query O(log n) | "Update index AND query range sum" — very rare |
| **KMP / Rabin-Karp** | String pattern matching O(n) | "Find pattern in text" — almost never asked |
| **Manacher's** | Longest palindromic substring O(n) | Expand-around-center O(n²) is always sufficient |
| **A\* Search** | Heuristic shortest path | Game dev pathfinding, not SWE interviews |
| **Suffix Array** | All suffixes sorted | Advanced string problems — never asked |
| **Heavy-Light Decomp** | Tree path queries | Competitive programming only |

---

## Study Tips

1. **Time yourself** — 25 min for Medium, 35 min for Hard. If stuck, read solution and re-implement from memory next day.
2. **Focus on patterns** — after each problem, write one sentence about the pattern used.
3. **Explain out loud** — at staff+ level, communication matters as much as the solution.
4. **Don't over-index on Hard** — a clean, well-communicated Medium beats a messy Hard.
5. **Review weekly** — re-solve 2-3 problems from earlier weeks without notes.

---

## Review Exams

Timed mock exams to review all patterns after completing the study plan.
**Rules**: 25 min per Medium, 35 min per Hard. No notes. Write solution from scratch. Explain out loud as you code.

### Day 1

| # | Problem | Time |
|---|---------|------|
| 1 | 76. Minimum Window Substring | 35 min |
| 2 | 721. Accounts Merge | 25 min |
| 3 | 295. Find Median from Data Stream | 25 min |

- [ ] Completed — Score: ___/3

### Day 2

| # | Problem | Time |
|---|---------|------|
| 1 | 269. Alien Dictionary | 35 min |
| 2 | 146. LRU Cache | 25 min |
| 3 | 416. Partition Equal Subset Sum | 25 min |

- [ ] Completed — Score: ___/3

### Day 3

| # | Problem | Time |
|---|---------|------|
| 1 | 394. Decode String | 25 min |
| 2 | 399. Evaluate Division | 25 min |
| 3 | 33. Search in Rotated Sorted Array | 25 min |

- [ ] Completed — Score: ___/3

### Day 4

| # | Problem | Time |
|---|---------|------|
| 1 | 72. Edit Distance | 25 min |
| 2 | 25. Reverse Nodes in k-Group | 35 min |
| 3 | 994. Rotting Oranges | 25 min |

- [ ] Completed — Score: ___/3

### Day 5

| # | Problem | Time |
|---|---------|------|
| 1 | 1235. Maximum Profit in Job Scheduling | 35 min |
| 2 | 208. Implement Trie | 25 min |
| 3 | 142. Linked List Cycle II | 25 min |

- [ ] Completed — Score: ___/3

### Day 6

| # | Problem | Time |
|---|---------|------|
| 1 | 127. Word Ladder | 35 min |
| 2 | 56. Merge Intervals | 25 min |
| 3 | 759. Employee Free Time | 25 min |

- [ ] Completed — Score: ___/3

### Day 7

| # | Problem | Time |
|---|---------|------|
| 1 | 42. Trapping Rain Water | 35 min |
| 2 | 139. Word Break | 25 min |
| 3 | 23. Merge k Sorted Lists | 35 min |

- [ ] Completed — Score: ___/3

### Day 8

| # | Problem | Time |
|---|---------|------|
| 1 | 224. Basic Calculator | 35 min |
| 2 | 253. Meeting Rooms II | 25 min |
| 3 | 300. Longest Increasing Subsequence | 25 min |

- [ ] Completed — Score: ___/3

### Day 9

| # | Problem | Time |
|---|---------|------|
| 1 | 51. N-Queens | 35 min |
| 2 | 152. Maximum Product Subarray | 25 min |
| 3 | 236. Lowest Common Ancestor | 25 min |

- [ ] Completed — Score: ___/3

### Day 10

| # | Problem | Time |
|---|---------|------|
| 1 | 4. Median of Two Sorted Arrays | 35 min |
| 2 | 862. Shortest Subarray with Sum at Least K | 35 min |
| 3 | 54. Spiral Matrix | 25 min |

- [ ] Completed — Score: ___/3

### Exam Scoring Guide

| Score | Action |
|-------|--------|
| 3/3 | Solid — move on |
| 2/3 | Re-study the missed pattern, retry in 2 days |
| 0-1/3 | Review cheat sheet sections, redo original problems first |

### Answer Key (don't peek until done!)

<details>

**Day 1**: Sliding window → Union-Find → Two heaps
**Day 2**: Topological sort → Design (HashMap + DLL) → Knapsack DP
**Day 3**: Stack-based parsing → Weighted graph BFS → Binary search
**Day 4**: 2D DP → Linked list reversal → Multi-source BFS
**Day 5**: DP + binary search → Trie → Floyd's cycle detection
**Day 6**: BFS shortest path → Sort + merge intervals → Intervals + heap
**Day 7**: Two pointers → 1D DP → Heap merge
**Day 8**: Stack-based parsing → Sweep line / heap → 1D DP + binary search opt
**Day 9**: Backtracking → DP (track min/max) → Tree recursion
**Day 10**: Binary search on two arrays → Monotonic deque + prefix sum → Matrix boundary

</details>

---

## Progress Tracker

| Week | Topic | Done | Total |
|------|-------|------|-------|
| 1 | Hash Maps + Sliding Window + Prefix Sum + Arrays | 27/27 | 27 |
| 2 | Graphs + Topo Sort + Union Find + Trees + Design | /25 | 25 |
| 3 | DP + Intervals + Greedy | /19 | 19 |
| 4 | Heaps + Stacks + LinkedList + Binary Search + Backtracking + More | /27 | 27 |
| Bonus | Company-Specific | /8 | 8 |
| **Total** | | **/106** | **106** |
