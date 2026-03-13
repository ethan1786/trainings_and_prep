# LeetCode Study Plan for Staff/Principal SWE Interviews

**Target companies:** Airbnb, Netflix, Nvidia, Stripe, Coinbase, Snowflake, Uber, Anthropic, OpenAI
**Difficulty focus:** Medium (primary), select Hard (frequently asked)
**Time estimate:** ~4 weeks at 2–3 problems/day (~55 problems total)
**Lighter coverage:** Two pointers, strings, arrays, trees (already practiced)
**Heavier coverage:** Graphs, DP (core patterns only), intervals, heaps, concurrency

---

## Priority of Topics (by interview frequency at target companies)

1. **Hash Maps / Design** — very high (all companies)
2. **Graphs (BFS/DFS/Topo Sort/Union Find)** — very high (Uber, Airbnb, Nvidia)
3. **Intervals / Greedy** — high (Airbnb, Uber, Stripe)
4. **Heaps / Priority Queues** — high (Uber, Netflix, Nvidia)
5. **Sliding Window** — high (all companies)
6. **Binary Search** — medium-high (Uber, Nvidia, Stripe)
7. **DP** — medium (~15-20% of coding rounds; focus on classic patterns)
8. **Backtracking** — medium (Uber, Airbnb)
9. **Stacks (Monotonic)** — medium (Uber, Nvidia)
10. **Concurrency** — low-medium (backend/platform roles at Uber, Netflix)

---

## Week 1: Foundations Refresh + Hash Maps + Sliding Window

### Hash Maps / Frequency Counting

- [x] 49. Group Anagrams (Medium) — Uber, Airbnb, Stripe
- [x] 560. Subarray Sum Equals K (Medium) — Uber, Coinbase
- [x] 146. LRU Cache (Medium) — Airbnb, Netflix, Uber, Stripe, Nvidia
- [x] 380. Insert Delete GetRandom O(1) (Medium) — Uber, Netflix
- [x] 460. LFU Cache (Hard) — Uber, Airbnb

### Sliding Window

- [x] 3. Longest Substring Without Repeating Characters (Medium) — Uber, Airbnb, Stripe, Netflix
- [x] 76. Minimum Window Substring (Hard) — Airbnb, Uber, Stripe
- [x] 239. Sliding Window Maximum (Hard) — Nvidia, Uber
- [x] 424. Longest Repeating Character Replacement (Medium) — Uber, Airbnb — variable window + constraint
- [x] 567. Permutation in String (Medium) — Uber, Airbnb — fixed window + frequency match
- [x] 438. Find All Anagrams in a String (Medium) — Uber, Airbnb — fixed window variant of 567
- [x] 1004. Max Consecutive Ones III (Medium) — Uber, Nvidia — variable window + flip budget
- [x] 209. Minimum Size Subarray Sum (Medium) — Uber, Stripe — variable window + sum target
- [x] 30. Substring with Concatenation of All Words (Hard) — Uber, Airbnb — same pattern as 76 (window + frequency match)
- [x] 727. Minimum Window Subsequence (Hard) — Airbnb, Uber — harder variant of 76 (Premium)
- [x] 159. Longest Substring with At Most Two Distinct Characters (Medium) — Uber, Airbnb — same shrink logic as 76 (Premium)
- [x] 739. Daily Temperatures (Medium) — Uber, Nvidia — monotonic stack (same core idea as 239)
- [x] 1438. Longest Continuous Subarray With Absolute Diff ≤ Limit (Medium) — Uber, Nvidia — monotonic deque, same pattern as 239
- [x] 862. Shortest Subarray with Sum at Least K (Hard) — Uber, Stripe — monotonic deque on prefix sums

### Prefix Sum

- [x] 525. Contiguous Array (Medium) — Uber, Stripe — prefix sum + HashMap (count variant)
- [x] 523. Continuous Subarray Sum (Medium) — Uber, Coinbase — prefix sum + modulo + HashMap
- [x] 974. Subarray Sums Divisible by K (Medium) — Uber, Stripe — prefix sum + modulo counting
- [x] 304. Range Sum Query 2D (Medium) — Uber, Nvidia — 2D prefix sum
- [x] 238. Product of Array Except Self (Medium) — Uber, Airbnb, Stripe — prefix/suffix product (same idea)

### Two Pointers / Arrays / Strings (light refresh)

- [x] 15. 3Sum (Medium) — Uber, Airbnb
- [x] 42. Trapping Rain Water (Hard) — Uber, Airbnb, Nvidia
- [x] 271. Encode and Decode Strings (Medium) — Airbnb, Stripe (Premium)

**Week 1 total: 27 problems**

---

## Week 2: Graphs + Topological Sort + Union Find

### BFS / DFS

- [x] 200. Number of Islands (Medium) — Uber, Airbnb, Nvidia
- [x] 133. Clone Graph (Medium) — Uber, Airbnb
- [x] 127. Word Ladder (Hard) — Airbnb, Uber
- [x] 994. Rotting Oranges (Medium) — Uber, Nvidia
- [x] 417. Pacific Atlantic Water Flow (Medium) — Uber

### Topological Sort

- [x] 207. Course Schedule (Medium) — Uber, Airbnb, Stripe
- [x] 210. Course Schedule II (Medium) — Uber, Airbnb
- [x] 269. Alien Dictionary (Hard) — Airbnb, Uber (Premium)

### Union Find

- [x] 323. Number of Connected Components (Medium) — Uber, Airbnb (Premium)
- [x] 684. Redundant Connection (Medium) — Uber
- [x] 721. Accounts Merge (Medium) — Uber, Airbnb
- [x] 399. Evaluate Division (Medium) — Uber, Airbnb — weighted Union-Find or BFS on graph

### Trees (light refresh)

- [x] 236. Lowest Common Ancestor of a Binary Tree (Medium) — Uber, Airbnb, Netflix
- [x] 297. Serialize and Deserialize Binary Tree (Hard) — Uber, Airbnb, Netflix

### Design Data Structures

- [x] 208. Implement Trie (Medium) — Uber, Airbnb, Stripe — prefix tree fundamentals (warmup for 588/1166)
- [x] 212. Word Search II (Hard) — Uber, Airbnb — trie + DFS backtracking
- [x] 355. Design Twitter (Medium) — Uber, Airbnb — heap + hash map + linked list
- [x] 981. Time Based Key-Value Store (Medium) — Uber, Stripe, Netflix — hash map + binary search
- [x] 1396. Design Underground System (Medium) — Uber, Stripe — hash map bookkeeping
- [x] 362. Design Hit Counter (Medium) — Uber, Stripe, Netflix — queue or circular array (Premium)
- [x] 588. Design In-Memory File System (Hard) — Stripe — trie of directories (Premium)
- [x] 716. Max Stack (Hard) — Uber, Netflix — TreeMap + doubly linked list (Premium)
- [x] 1166. Design File System (Medium) — Airbnb, Stripe — hash map / trie (Premium)
- [x] 895. Maximum Frequency Stack (Hard) — Uber, Netflix — hash map + stack per frequency

**Week 2 total: 24 problems**

---

## Week 3: DP (Core Patterns) + Intervals + Greedy

### DP — Focus on Recognizable Patterns

DP appears ~15-20% of the time. Don't over-invest — learn to recognize the 5 core
patterns and set up the recurrence. That's sufficient for staff+ level.

**1D DP (sequence/decision):**

- [ ] 198. House Robber (Medium) — Uber, Airbnb — simplest DP warmup
- [ ] 139. Word Break (Medium) — Uber, Airbnb, Stripe
- [ ] 322. Coin Change (Medium) — Uber, Coinbase, Stripe
- [ ] 91. Decode Ways (Medium) — Uber, Airbnb
- [ ] 300. Longest Increasing Subsequence (Medium) — Uber, Nvidia — classic 1D DP + binary search optimization
- [ ] 152. Maximum Product Subarray (Medium) — Uber, Airbnb — track min and max simultaneously

**2D DP (grid/string comparison):**

- [ ] 62. Unique Paths (Medium) — Uber, Nvidia
- [ ] 1143. Longest Common Subsequence (Medium) — Uber, Coinbase
- [ ] 72. Edit Distance (Medium) — Uber, Airbnb, Stripe

**Knapsack / Subset DP:**

- [ ] 416. Partition Equal Subset Sum (Medium) — Uber, Coinbase
- [ ] 518. Coin Change II (Medium) — Stripe, Coinbase

### Intervals

- [ ] 56. Merge Intervals (Medium) — Uber, Airbnb, Stripe, Netflix
- [ ] 57. Insert Interval (Medium) — Uber, Airbnb, Stripe — builds on 56
- [ ] 253. Meeting Rooms II (Medium) — Uber, Airbnb (Premium)
- [ ] 435. Non-overlapping Intervals (Medium) — Uber, Airbnb — greedy interval scheduling
- [ ] 1235. Maximum Profit in Job Scheduling (Hard) — Uber, Airbnb, Nvidia

### Greedy

- [ ] 621. Task Scheduler (Medium) — Uber, Airbnb
- [ ] 134. Gas Station (Medium) — Uber

**Week 3 total: 18 problems**

---

## Week 4: Heaps + Stacks + Binary Search + Backtracking + Concurrency

### Heaps / Priority Queues

- [ ] 295. Find Median from Data Stream (Hard) — Uber, Airbnb, Netflix
- [ ] 347. Top K Frequent Elements (Medium) — Uber, Coinbase
- [ ] 23. Merge k Sorted Lists (Hard) — Uber, Airbnb, Nvidia
- [ ] 973. K Closest Points to Origin (Medium) — Uber, Airbnb
- [ ] 215. Kth Largest Element in an Array (Medium) — Uber, Airbnb — quickselect or heap

### Linked List

- [ ] 206. Reverse Linked List (Easy) — Uber, Airbnb — fundamental, know iterative + recursive
- [ ] 25. Reverse Nodes in k-Group (Hard) — Uber, Airbnb — builds on 206
- [ ] 141. Linked List Cycle (Easy) — Uber, Nvidia — fast/slow pointer
- [ ] 142. Linked List Cycle II (Medium) — Uber — find cycle start (Floyd's algorithm)

### Monotonic Stack / Stack Parsing

- [ ] 84. Largest Rectangle in Histogram (Hard) — Uber, Nvidia
- [ ] 739. Daily Temperatures (Medium) — Uber
- [ ] 224. Basic Calculator (Hard) — Uber, Airbnb, Stripe — stack-based expression parsing
- [ ] 227. Basic Calculator II (Medium) — Uber, Airbnb — stack + operator precedence

### Matrix

- [ ] 48. Rotate Image (Medium) — Uber, Airbnb — transpose + reverse
- [ ] 54. Spiral Matrix (Medium) — Uber, Airbnb — boundary shrinking

### Binary Search

- [ ] 33. Search in Rotated Sorted Array (Medium) — Uber, Airbnb, Nvidia
- [ ] 528. Random Pick with Weight (Medium) — Uber, Airbnb — prefix sum + binary search
- [ ] 4. Median of Two Sorted Arrays (Hard) — Uber, Nvidia

### Backtracking

- [ ] 46. Permutations (Medium) — Uber, Airbnb — backtracking fundamental
- [ ] 79. Word Search (Medium) — Uber, Airbnb
- [ ] 51. N-Queens (Hard) — Uber, Nvidia
- [ ] 17. Letter Combinations of a Phone Number (Medium) — Uber, Airbnb

### Bit Manipulation

- [ ] 191. Number of 1 Bits (Easy) — Uber, Nvidia — Hamming weight, n & (n-1) trick
- [ ] 338. Counting Bits (Easy) — Uber — DP on bits

### Concurrency (relevant for backend/platform roles)

- [ ] 1188. Design Bounded Blocking Queue (Medium) — Uber, Netflix (Premium)
- [ ] 1117. Building H2O (Medium) — Uber (Premium)

**Week 4 total: 26 problems**

---

## Bonus: Company-Specific Must-Dos

Do these before a specific company's interview or if you have extra time.

### Airbnb Classics

- [ ] 68. Text Justification (Hard) — Airbnb's most famous question
- [ ] 336. Palindrome Pairs (Hard) — frequently reported
- [ ] 787. Cheapest Flights Within K Stops (Medium) — graph + DP

### Stripe Classics

- [ ] 843. Guess the Word (Hard) — interactive problem

### Uber Classics

- [ ] 815. Bus Routes (Hard) — BFS on graph

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

### Exam 1 — Foundations (Hash Map, Sliding Window, Prefix Sum, Two Pointers)

| # | Problem | Pattern | Time |
|---|---------|---------|------|
| 1 | 76. Minimum Window Substring | Variable sliding window + frequency | 35 min |
| 2 | 560. Subarray Sum Equals K | Prefix sum + HashMap | 25 min |
| 3 | 146. LRU Cache | Design: HashMap + doubly linked list | 25 min |
| 4 | 42. Trapping Rain Water | Two pointers / monotonic stack | 35 min |
| 5 | 862. Shortest Subarray with Sum at Least K | Monotonic deque + prefix sum | 35 min |

- [ ] Completed — Score: ___/5

### Exam 2 — Graphs (BFS/DFS, Topo Sort, Union Find)

| # | Problem | Pattern | Time |
|---|---------|---------|------|
| 1 | 127. Word Ladder | BFS shortest path + neighbor generation | 35 min |
| 2 | 269. Alien Dictionary | Build graph + topological sort (Kahn's) | 35 min |
| 3 | 721. Accounts Merge | Union-Find (string keys, merge groups) | 25 min |
| 4 | 994. Rotting Oranges | Multi-source BFS | 25 min |
| 5 | 399. Evaluate Division | Weighted graph BFS or weighted Union-Find | 25 min |

- [ ] Completed — Score: ___/5

### Exam 3 — DP + Intervals + Greedy

| # | Problem | Pattern | Time |
|---|---------|---------|------|
| 1 | 139. Word Break | 1D DP | 25 min |
| 2 | 72. Edit Distance | 2D DP (string comparison) | 25 min |
| 3 | 416. Partition Equal Subset Sum | Knapsack DP | 25 min |
| 4 | 56. Merge Intervals | Sort + merge | 25 min |
| 5 | 1235. Maximum Profit in Job Scheduling | DP + binary search | 35 min |

- [ ] Completed — Score: ___/5

### Exam 4 — Heaps, Stacks, Binary Search, Backtracking

| # | Problem | Pattern | Time |
|---|---------|---------|------|
| 1 | 295. Find Median from Data Stream | Two heaps | 25 min |
| 2 | 84. Largest Rectangle in Histogram | Monotonic stack | 35 min |
| 3 | 33. Search in Rotated Sorted Array | Modified binary search | 25 min |
| 4 | 23. Merge k Sorted Lists | Heap merge | 35 min |
| 5 | 51. N-Queens | Backtracking + constraint pruning | 35 min |

- [ ] Completed — Score: ___/5

### Exam 5 — Design + Trees + Mixed

| # | Problem | Pattern | Time |
|---|---------|---------|------|
| 1 | 208. Implement Trie | Trie | 25 min |
| 2 | 236. Lowest Common Ancestor | Tree recursion (return value as signal) | 25 min |
| 3 | 895. Maximum Frequency Stack | HashMap + stack per frequency | 25 min |
| 4 | 300. Longest Increasing Subsequence | 1D DP + binary search optimization | 25 min |
| 5 | 253. Meeting Rooms II | Sweep line / heap | 25 min |

- [ ] Completed — Score: ___/5

### Exam 6 — Linked List + Stack Parsing + Matrix + Bits

| # | Problem | Pattern | Time |
|---|---------|---------|------|
| 1 | 25. Reverse Nodes in k-Group | Linked list reversal in chunks | 35 min |
| 2 | 224. Basic Calculator | Stack-based expression parsing | 35 min |
| 3 | 54. Spiral Matrix | Boundary shrinking traversal | 25 min |
| 4 | 142. Linked List Cycle II | Floyd's cycle detection | 25 min |
| 5 | 152. Maximum Product Subarray | DP — track min/max | 25 min |

- [ ] Completed — Score: ___/5

### Exam Scoring Guide

| Score | Action |
|-------|--------|
| 5/5 | Move on — these patterns are solid |
| 3-4/5 | Re-study missed patterns, retry those problems in 2 days |
| 0-2/5 | Review the cheat sheet section, redo the original problems first |

---

## Progress Tracker

| Week | Topic | Done | Total |
|------|-------|------|-------|
| 1 | Hash Maps + Sliding Window + Prefix Sum + Arrays | 27/27 | 27 |
| 2 | Graphs + Topo Sort + Union Find + Trees + Design | 24/24 | 24 |
| 3 | DP + Intervals + Greedy | /18 | 18 |
| 4 | Heaps + Stacks + LinkedList + Binary Search + Backtracking + More | /26 | 26 |
| Bonus | Company-Specific | /5 | 5 |
| **Total** | | **/100** | **100** |
