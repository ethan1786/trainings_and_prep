# Coding Round (60 min, CoderPad)

**Language:** Java (confirm with recruiter)
**AI:** Allowed via CoderPad's built-in ChatGPT — for syntax/library help only, not solving the problem
**Format:** Backend only, live with interviewer

---

## What They're Evaluating

From the interview doc: "problem-solving skills, logical thinking, core coding fundamentals and some basic language-specific fluency."

They explicitly say: "Feel free to be scrappy in the interview & call out how you would do it in production."

Translation: Get it working first, then discuss production-quality improvements verbally.

---

## Strategy

### The Coinbase OA Lesson: START SIMPLE

1. **Clarify** (2-3 min) — ask about input/output, edge cases, constraints
2. **Approach** (3-5 min) — talk through your plan before coding. Pseudocode or verbal.
3. **Implement simplest working version** (15-20 min) — get something that passes the basic case
4. **Test manually** (5 min) — walk through an example
5. **Optimize if time** (10-15 min) — improve complexity, handle edge cases
6. **Discuss production concerns** (5 min) — error handling, concurrency, testing

### Do NOT:
- Jump straight into coding without talking
- Build an overengineered solution from the start
- Spend more than 30 seconds stuck without talking — narrate your thinking

---

## Common Backend Coding Patterns

Since Cherry is a fintech BNPL company, likely problem domains:

**Data processing:**
- Parse/transform financial records
- Aggregate transactions by user/date/category
- Implement a simple ledger or balance tracker

**API-adjacent logic:**
- Validate and process payment requests
- Implement rate limiting or quota logic
- State machine (loan application lifecycle)

**Classic DS&A (still possible):**
- HashMap problems (frequency, grouping, lookup)
- String processing
- Graph/tree traversal
- Sorting with custom comparators

---

## Java-Specific Things to Review

- `HashMap`, `LinkedHashMap`, `TreeMap` — when to use each
- `Stream` API — filter, map, collect, groupingBy
- `Comparator` — chaining, reverseOrder, thenComparing
- `Optional` — basic usage
- String manipulation — `split`, `substring`, `contains`, `toLowerCase`
- `Collections.sort` vs `list.sort` with custom comparators

---

## Using AI During the Interview

**Good uses:**
- "What's the Java method to parse a date string?" — syntax lookup
- "How do I create a PriorityQueue with a custom comparator?" — library usage

**Bad uses:**
- Pasting the entire problem and asking for a solution
- Having AI generate your algorithm

**When to use it:** Only when you know WHAT you want to do but forgot HOW Java does it. If you're stuck on the approach itself, talk to the interviewer instead.

---

## Post-Solution Talking Points

After your solution works, volunteer these:

- "In production, I'd add input validation here..."
- "This is O(n log n) — if we needed better, we could..."
- "I'd add unit tests for these edge cases: empty input, single element, duplicates..."
- "For concurrency, this would need..."

This is what they mean by "call out how you would do it in production."
