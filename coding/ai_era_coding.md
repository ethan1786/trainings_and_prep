# Coding Interviews in the AI Era — Derivation & AI Skills

> Companion to `patterns.md` (pattern mechanics) and `lc_quickref.md` (recognition).
> This doc is about what the AI era actually scores: **deriving** the approach from the problem's properties, and **directing/validating** AI output. Raw recall is now the anti-signal — Coinbase's blog says it verbatim: "The signal we got was preparation, not capability."

---

## 1. Why "I remember the pattern" fails

The interviewer's "how do you know it's a XXX pattern?" is not a trivia check. It's testing whether you can **derive** the algorithm from the problem's properties. Recall without derivation has three failure modes:

1. **You can't defend the choice** — when pushed, there's nothing between "I've seen this before" and silence.
2. **You can't adapt** — the real interview twist changes one constraint, and the memorized pattern breaks silently.
3. **It's now the anti-signal** — with AI available, recall is table stakes. The scored skill is judgment: knowing *which* pattern fits *this* problem and *why*.

**The fix:** convert every memorized pattern into a derivation chain. Property → mechanism → pattern. After that, "how do you know?" has a real answer, and the AI era makes this conversion *more* valuable, because the derivation chain is exactly what you feed the AI and exactly what you use to check its output.

---

## 2. The derivation framework

Every algorithm exists to exploit a specific property of the problem. The four-part answer script for "how did you know to use X?":

1. **Name the property, not the pattern** — "the problem gives us X" (never "this is a Y problem")
2. **Map property → mechanism** — "the only thing that exploits X efficiently is Y"
3. **Negative reasoning** — "I ruled out Z because it doesn't use X"
4. **Boundary** — "and I know Y breaks if W changes, so I'd check for that"

### Worked derivations — the core patterns

| Pattern | Property that forces it | Mechanism (why it works) | Why alternatives fail | What breaks it |
|---|---|---|---|---|
| **Topological sort** | Elements have "must come before" dependencies; question asks for an order respecting them | Dependencies = directed edges. In-degree zero = no unmet dependencies = safe next. Cycle ⇒ no order exists — so "can we order" and "find an order" are the *same computation* | BFS/DFS find reachability, not "before" constraints; sorting needs a *total* order, dependencies give only a *partial* one | Weighted edges (→ shortest path instead); undirected edges (ordering question disappears) |
| **Sliding window** | Contiguous subarray/substring, constraint checkable incrementally | For a fixed right end, valid left positions form one contiguous range — so one shrinking window covers all O(n²) candidates | Two pointers need sortedness/monotonicity; prefix+hash answers sums but not "contains all of X" | **Negative numbers** (shrinking no longer monotonically improves the sum) — switch to atMost-trick or prefix+hash |
| **Binary search** | Answer is a threshold over a monotone space: smallest X such that f(X) works, and f is monotone | Monotonicity ⇒ each probe halves the space; O(n)-time verification becomes O(log n) probes | Linear scan = O(n) verifications; greedy needs a proof of local optimality, binary search doesn't | f non-monotone (rotated arrays: only *one half* is sorted — search where monotonicity survives) |
| **DP** | Optimal substructure + overlapping subproblems: the best answer at a state decomposes into best answers of smaller states | Define state → recurrence → fill in topological order; memoization makes each state computed once | Greedy commits to a local choice without proof; backtracking re-explores states exponentially; divide-and-conquer needs disjoint subproblems | **Cycles in the state graph** (no topological order to fill) — then it's shortest-path/DP on DAG only |
| **Greedy vs DP test** | — | — | The one-sentence test: can you prove the locally-best choice never hurts the global answer? Yes ⇒ greedy. No ⇒ DP | If a single counterexample exists, greedy silently fails |
| **Heap (top-K)** | Only the K best/worst are needed — not the full order | A size-K heap stores the K best seen; each new item compares against only the Kth best: O(n log k) | Sorting computes a total order you never use: O(n log n) | Need the full order or range queries on rank |
| **Two pointers (sorted)** | Sorted input ⇒ moving pointers changes the target value monotonically | Each comparison eliminates one position; both pointers move only forward ⇒ O(n) | Hash map works unsorted but costs O(n) space; binary search per element = O(n log n) | Unsorted input (sort first, or use hash map); non-monotone target function |
| **Monotonic stack** | Each element needs its nearest greater/smaller element on a side | While stack-top < current, current IS its next-greater — answer and pop. Stack stays sorted because answered elements leave | Brute force is O(n²); sorting loses positional order entirely | Need *any* greater, not nearest (sorted scan suffices); multiple dimensions |
| **Union-Find** | Dynamic connectivity/grouping queries while edges arrive incrementally | Path compression + rank ⇒ near-O(1) amortized find; groups merge transitively without rebuilding | BFS/DFS re-scan the graph per query (O(n) each); sets of sets need manual merging | Static one-shot queries (plain BFS/DFS is simpler); need to enumerate paths (traversal, not connectivity) |
| **Backtracking** | Need ALL valid configurations (not count/min/max) | State space is a tree; generate-and-prune visits each candidate once | DP only counts/optimizes — it collapses configurations; greedy returns one | Only the count matters ⇒ DP (overlapping states collapse) |

### Worked example — the NVIDIA moment (topological sort)

> "I didn't go looking for a pattern name. The problem says course A must come before course B — that's a **partial order over dependencies**. Any question about honoring dependencies in an ordering is topological sorting, because the edges *are* the constraints. And notice the equivalence: if a cycle exists, no ordering exists — which is why 'can this be done' and 'in what order' are literally the same computation. So in-degree peeling: at every step, take a node with no unmet dependencies — that's always safe, and it's the only thing that's always safe. I'd worry about this only if the edges gained weights or the graph became undirected."

That answer is: property (partial order) → mechanism (edges = constraints, cycle ⇔ no order) → negative reasoning (only in-degree-zero nodes are always safe) → boundary (weights/undirected). Same story, derivable, adaptable.

---

## 3. How to drill derivation instead of recall

The drill formats change. LC is still used — but as pattern-*speed maintenance*, not as the primary skill. Three drills:

**D1 · Derivation drill (10 min, any solved problem).** Pick a solved problem. Write the four-part derivation chain — *before* looking at the code. Property → mechanism → negative reasoning → boundary. If you can't write step 2 (the mechanism), that pattern is memorized, not understood — re-derive it from first principles once.

**D2 · Constraint-twist drill (weekly).** Take a solved problem, change one constraint (sorted → unsorted; positive → negatives allowed; k fixed → k variable; find one → count all). Say what breaks, what replaces it. This is the "adapt" muscle interviewers test with follow-ups.

**D3 · The interview sentence.** Before writing code, state the property aloud: *"The problem gives me X, which means Y is the right tool — here's why Z doesn't work."* One sentence, every timed solve. That sentence is the scored signal.

**LC's remaining role:** daily 1 problem for syntax/speed maintenance (the re-warm). But the *deliverable* of each solve is now the derivation chain, not the green checkmark.

---

## 4. AI-assisted rounds — the skills actually being scored

From Coinbase's AI-era blog + your own override data, the scored skills are: **directing** (spec-first prompting), **validating** (the review loop), and **guarding** (knowing where human judgment goes).

### 4a. Spec-first prompting (you do the derivation, AI does implementation)

The prompt pattern that replaces "solve this problem":

1. **State the property you identified** ("the input is a partial order over dependencies")
2. **Name the mechanism and why** ("topological sorting via in-degree peeling, because only in-degree-zero nodes are always safe")
3. **Give acceptance criteria** (correctness cases + complexity bound)
4. **Ask for the code, then separately for edge-case tests** (tests are the best delegation)

You never ask the AI to *choose the approach* on the scored part — that's the judgment being tested. AI chooses for scaffolding, parsing, syntax, test generation.

### 4b. The validation loop

After AI output, run the loop out loud:

1. **Trace the examples through the code** — does the mechanism actually implement the property?
2. **Delegate edge-case generation** — "generate tests for X, Y, Z" (negatives, empties, duplicates, boundaries)
3. **Check invariants** — what must remain true after each operation? (dual-structure sync, monotonic stack order, heap size k)
4. **State complexity** — and check the implementation matches the claimed bound.

### 4c. Reviewing AI code — your failure-mode checklist

Your override log gives the real recurring AI failure modes. Use as a review checklist:

| Failure mode | Review question |
|---|---|
| Scope creep / invented work | Does this change anything the task didn't ask for? |
| Unverified platform assumptions | Does it assume a capability that must be checked? |
| Shortcut missing edge cases | Which case did the shortcut drop? |
| Overstated risk/certainty | Is that claim measured or asserted? |
| Inferred-from-code instead of runtime | Does it read production *state* from code? |

### 4d. Guardrails — what you hand-write vs. delegate

| Hand-write (the signal) | Delegate (the leverage) |
|---|---|
| The core algorithm + derivation chain | Edge-case test generation |
| The data-structure choice + why | Scaffolding, fixtures, input parsing |
| The invariant checks | API/syntax recall |
| The review verdict | Repo navigation |

**The delegation narration** (say it out loud — it's the judgment being scored):
> *"I'll write the core logic myself since that's where the thinking is — once the shape settles, I'll have the agent generate edge-case tests and we'll run them together."*

### 4e. Drill for AI-assisted rounds

**D4 · AI-critique drill (30 min).** Feed a problem to an AI tool. Review its solution against the 4c checklist. Find at least two real issues (bug, missed edge case, wrong assumption). State what you'd change and why. This is literally the new interview format — repo-based, AI-generated code, your judgment.

**D5 · Repo-based timed drill (45 min, from round3_plan E).** Box a real work ticket to 45 minutes with AI enabled. Narrate every delegation decision. The day job with a clock and speaking added.

---

## 5. The one-paragraph position (for "how do you code with AI now?")

> "The pattern I work in: I identify the property of the problem — that's the judgment part AI can't do — then the AI implements against that spec, and I spend my time validating: edge cases, invariants, review against known failure modes. The scarce skill isn't typing code, it's knowing what to build, what the failure modes are, and when the output is wrong. My overrides are where that judgment lives — I keep a log of them."
