# Python Interview Prep

> For Staff/Senior roles requiring Python (NVIDIA, AI/ML infra, data platforms)
> Coming from 13 years of Java — building Python fluency for interviews

---

## Current State

**Experience:**
- Side projects: options-ai (353 tests, async workflows, Pydantic, production-style), GenAI evaluation platform
- Work: MCP server (Python backend for agent orchestration)
- Gap: Haven't written Python line-by-line in interview style recently

**Goal:**
Get interview-ready in Python for Senior-level coding + system design rounds in 2-3 weeks.

---

## Learning Plan

### Week 1-2: LC Easy/Medium (Rebuild Muscle Memory)

Focus: Core data structures + common patterns, BY HAND (no AI assist)

| Topic | Focus | Resources |
|---|---|---|
| Data Structures | `dict`, `list`, `set`, `deque`, `heapq` | LC Easy: Two Sum, Valid Anagram, etc. |
| List comprehensions | `[x for x in items if condition]` | Practice converting loops → comprehensions |
| String manipulation | `split()`, `join()`, slicing `s[::-1]` | LC: Reverse String, Valid Palindrome |
| Two pointers / Sliding window | Same algorithm, Python syntax | LC: Container With Most Water, Longest Substring |

**Goal:** 2-3 problems/day. Stop translating from Java — think in Python.

---

### Week 3-4: Python Idioms + System Design in Python

| Topic | What to Learn | Resources |
|---|---|---|
| **Effective Python** | When dict vs list vs set, comprehensions, generators | Book: "Effective Python" by Brett Slatkin |
| **Typing** | Type hints, `typing.Dict`, `typing.List`, `Optional` | Python docs + existing code review |
| **Pydantic** | Data validation, models, schemas | options-ai uses this — review your own code |
| **Async/await** | `asyncio`, `async def`, `await`, event loops | You already use this in options-ai |
| **SDK design in Python** | API design, classes, modules, `__init__.py` | Review MCP server structure |

**Practice:** 
- Redo one module from options-ai BY HAND (no looking)
- Design: "Design an evaluation SDK for AI agents" (just interfaces, not full impl)

---

## Python vs Java Quick Reference

| Concept | Java | Python |
|---|---|---|
| Array length | `arr.length` | `len(arr)` |
| Loop | `for (int i=0; i<n; i++)` | `for i in range(n):` |
| HashMap | `Map<K,V> map = new HashMap<>()` | `map = {}` or `from collections import defaultdict` |
| Set | `Set<T> set = new HashSet<>()` | `set()` or `{1, 2, 3}` |
| List slice | `Arrays.copyOfRange(arr, i, j)` | `arr[i:j]` |
| String reverse | `new StringBuilder(s).reverse()` | `s[::-1]` |
| Max heap | `PriorityQueue<>(Collections.reverseOrder())` | `import heapq; heapq.nlargest(...)` |
| Sorting with lambda | `list.sort(Comparator.comparing(...))` | `arr.sort(key=lambda x: x[1])` |

---

## Python Interview Prep Checklist

### Core Language (Must Know)

- [ ] Dict operations: `get()`, `setdefault()`, `defaultdict`, iteration
- [ ] List: slicing `[start:end]`, comprehensions, `append()`, `pop()`
- [ ] Set: `add()`, `discard()`, set operations (`|`, `&`, `-`)
- [ ] String: `split()`, `join()`, slicing, `strip()`, `replace()`
- [ ] `range()`, `enumerate()`, `zip()`
- [ ] List/dict/set comprehensions
- [ ] Lambda functions
- [ ] `collections`: `Counter`, `defaultdict`, `deque`
- [ ] `heapq`: `heappush()`, `heappop()`, `nlargest()`, `nsmallest()`

### Intermediate (Good to Know)

- [ ] Type hints: `def func(x: int) -> str:`
- [ ] `dataclasses` or Pydantic models
- [ ] Generators and `yield`
- [ ] Context managers (`with` statement)
- [ ] Exception handling (`try/except/finally`)
- [ ] File I/O: `open()`, `read()`, `write()`, `with open(...) as f:`
- [ ] `itertools`: `combinations`, `permutations`, `groupby`
- [ ] `functools`: `lru_cache`, `reduce`

### Async (For System Design)

- [ ] `async def`, `await`
- [ ] `asyncio.gather()`, `asyncio.create_task()`
- [ ] When to use async vs sync

### System Design in Python

- [ ] Class design: `__init__`, `@property`, `@staticmethod`, `@classmethod`
- [ ] Module structure: `__init__.py`, imports
- [ ] Typing for APIs: `typing.Protocol`, `TypeVar`, `Generic`
- [ ] Pydantic for validation and schemas
- [ ] FastAPI or Flask basics (if web service design comes up)

---

## Practice Projects (Rebuild from Scratch)

To prove fluency, rebuild small modules from your existing Python projects BY HAND:

1. **Decision engine core** (from GenAI project)
   - Input: context dict
   - Output: decision with confidence score
   - Practice: class design, typing, validation

2. **Signal accumulator** (from options-ai)
   - Input: price + news events
   - Output: flip proposal
   - Practice: state management, async updates

3. **Evaluation harness** (from GenAI project)
   - Input: test cases
   - Output: metrics (accuracy, latency)
   - Practice: async execution, result aggregation

---

## LeetCode Patterns to Focus On (Python-specific)

| Pattern | Why it matters in Python | Example problems |
|---|---|---|
| Hash table (dict) | Python dicts are fast, use them everywhere | Two Sum, Group Anagrams |
| List slicing | Unique to Python, very common | Reverse String, Rotate Array |
| Set operations | Python sets are elegant for deduplication | Intersection of Two Arrays |
| Comprehensions | Pythonic way to transform data | Filter/Map/Reduce patterns |
| Two pointers | Same as Java, just cleaner syntax | Container With Most Water |
| Sliding window | Same as Java, cleaner with slicing | Longest Substring Without Repeating |
| Heap (heapq) | Different API than Java PriorityQueue | Top K Frequent Elements |
| Graph (dict of lists) | Python's dict makes adjacency lists natural | Number of Islands, Course Schedule |

---

## Interview Framing (How to Talk About Python Experience)

**Honest framing:**

> "My background is 13 years in Java, building distributed systems and platform infrastructure. Over the past year, my work has shifted to agentic AI systems in Python — I've built agent orchestration infrastructure (MCP server), evaluation platforms with multi-provider LLM support, and autonomous systems with 350+ tests. I'm fluent in Python for the work I'm doing now, and I bring deep systems thinking from 13 years of production engineering. I'm currently building interview fluency — the muscle memory for writing Python from scratch at speed."

**What NOT to say:**
- "I'm learning Python" (sounds junior)
- "Claude wrote most of my Python code" (even if true — focus on what YOU designed and reviewed)
- "I'm worried I'll mix up Java and Python" (keep fears internal)

**What TO emphasize:**
- Architecture: "I designed the decision tree, the evaluation harness, the SDK interfaces"
- Production quality: "350+ tests, async workflows, Pydantic validation, runs in production"
- Systems thinking: "The algorithms are language-agnostic — I've been doing distributed systems for 13 years"

---

## Files in This Folder

| File | What's Inside | When to Use |
|---|---|---|
| **`python_playbook.md`** | Python reference: data structures (dict/set/deque/heapq), concurrency (threading/asyncio/GIL), common pitfalls (mutable defaults, identity vs equality, integer division) | Quick reference during interviews or when writing Python code |
| **`python_for_java_engineers_study_guide.md`** | Java→Python mindset shift, 3-week ramp plan, CarGurus Python standards (FastAPI, Pydantic, asyncio), interviewing Python candidates, applied design for eval systems | Comprehensive learning guide — read Week 1-3 sections in order |
| **`python_leetcode_toolkit.md`** | Python companion to LC study plan: stdlib imports, per-topic toolkit (Counter/heapq/bisect/etc.), week-by-week notes, Python-specific gotchas | Use alongside LC practice — what tools to reach for per pattern |
| **`lc_patterns_python.md`** | LC pattern quick reference with Python idioms: string parsing, hash maps, sliding window, heaps, graphs, DP, etc. | Pattern recognition during LC — "what pattern is this?" → Python template |

---

## How to Use These Files

**If you have 2-3 weeks before an interview:**
1. Read `python_for_java_engineers_study_guide.md` Part 1-3 (mindset shift, execution model, idioms)
2. Start LC using `python_leetcode_toolkit.md` as your imports/toolkit reference
3. When stuck on a pattern, check `lc_patterns_python.md` for the template
4. Keep `python_playbook.md` open for quick lookups (heapq API, asyncio, pitfalls)

**If you're practicing LC right now:**
1. Start with the imports from `python_leetcode_toolkit.md`
2. Check `lc_patterns_python.md` for pattern→template mapping
3. Reference `python_playbook.md` when you hit a pitfall or forget a stdlib method

**If you're designing a system in Python:**
1. Review concurrency section in `python_playbook.md` (asyncio vs threading)
2. Read applied design sections in `python_for_java_engineers_study_guide.md` (SDK design, Pydantic, FastAPI)
3. Practice: design eval SDK interfaces, trace models, async execution

---

## Resources to Keep Adding

As you learn, add to this folder:
- Your own LC solutions with notes on idioms used
- Common mistakes you caught (Java habits that don't translate)
- Interview questions you practiced
- Real code examples: Pydantic models, async patterns, SDK interfaces

This folder is your Python learning journal. Update it as you go.

---

## Timeline

**Now → Week 2:** LC Easy/Medium in Python, 2-3 problems/day
**Week 3-4:** Python idioms, system design in Python, rebuild a module by hand
**By end of Week 4:** Interview-ready for Senior Python roles (NVIDIA, AI infra)

The goal isn't to become a Python expert. The goal is to pass a Senior Python interview. Those are different bars.

You have the concepts. Now build the syntax fluency.
