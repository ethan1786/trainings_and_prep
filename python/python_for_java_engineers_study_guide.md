
# Java → Python: A Principal Engineer's Study Guide

*For interviewing Python candidates and starting to build agentic eval systems, SDKs, and internal-tool APIs at CarGurus.*

This guide has two jobs. First, retool your Java mindset so you can **interview Python candidates credibly** — knowing the fundamentals, the idioms, the "tells" of a strong Pythonista, and how comprehensions actually work. Second, get you productive **writing production Python on CarGurus' actual stack**, culminating in full worked answers to the three agentic-eval design questions you'll be asked (and asking).

Everything here is grounded in the CarGurus AI team's Python Standards — Python 3.13+ (prefer 3.14), `uv` for dependencies, FastAPI, HTTPX, Pydantic, Ruff, Pyright, SQLAlchemy, and pytest. The company is standardizing on Python specifically for LLM workflows and agents, with Discover V2 replatforming onto LangChain/LangGraph and asyncio.

---

## Part 0 — A 3-Week Ramp Plan

You already know how to engineer software. You are not learning to program; you are learning a different runtime model, a different idiom set, and a different ecosystem. Budget accordingly.

**Week 1 — Language & mindset (Parts 1–3).** Read the mindset shift table, then write throwaway code: rewrite three small Java utilities you know well as idiomatic Python. Force yourself to use comprehensions, `enumerate`, `zip`, dataclasses, and f-strings. Set up `uv`, Ruff, and Pyright locally so you feel the toolchain.

**Week 2 — Interviewing (Part 4) + the CarGurus stack (Part 5).** Work through the interview rubrics and pick 2–3 questions you'd actually ask. Clone the [`python-fastapi-service-template`](https://code.cargurus.com/cargurus-eng/python-fastapi-service-template) and the [listings-comparison eval harness](https://code.cargurus.com/cargurus-eng/listings-comparison/blob/main/src/test/python/README.md) and read them end-to-end.

**Week 3 — Applied design (Part 6).** Build a tiny version of the eval SDK from Part 6 as a Jupyter notebook, then a package. This is the fastest way to internalize async, Pydantic, and trace modeling at once.

A useful internal on-ramp: FUEL hosts LinkedIn Learning's [Python Quick Start](https://cargurus.360learning.com/course/play/65f01ccbeab372e0e63d7357) and [Complete Guide to Python Fundamentals for MLOps](https://cargurus.360learning.com/course/play/66f7ab7e7e8e860eef8aca73), the latter covering APIs, SDKs, pandas/NumPy — directly relevant to your eval work.

---

## Part 1 — The Java → Python Mindset Shift

The syntax is the easy part. The mental adjustments below are what separate someone who "writes Java in Python" from someone who writes Python.

| Concept | Java | Python | What changes for you |
|---|---|---|---|
| Typing | Static, compiled, enforced | Dynamic at runtime; **type hints are optional annotations** checked by tools (Pyright), not the interpreter | Types are documentation + tooling, not a compiler gate. CarGurus requires hints on all params/returns in production code. |
| Everything is... | Primitives + objects; `int` ≠ `Integer` | **Everything is an object**, including functions, classes, and modules | Functions are first-class values you pass around. No autoboxing distinction. |
| Null | `null` + `Optional<T>` | `None`, checked with `is None` | `Optional[X]` from `typing` is a hint meaning `X | None`, not a wrapper you `.get()`. |
| Collections | `List`/`Map`/`Set` interfaces + impls | Built-in `list`, `dict`, `set`, `tuple` as language literals | You rarely pick an implementation; you pick a *shape*. `dict` is ordered since 3.7. |
| Iteration | Index loops, `Iterator` | `for x in iterable`; **comprehensions**; generators | Index loops are a code smell. See Part 3. |
| Concurrency | Threads, `ExecutorService`, real parallelism | `asyncio` event loop (cooperative, single-thread) + threads/processes; **GIL** limits CPU parallelism | Async is for **I/O-bound** work (LLM/API calls) — exactly the agent/eval workload. |
| Errors | Checked + unchecked exceptions | All exceptions unchecked; **EAFP** ("easier to ask forgiveness than permission") | `try/except` is idiomatic control flow, not just failure handling. |
| Build/deps | Maven/Gradle, `pom.xml` | **`uv`** with `pyproject.toml` + committed `uv.lock`; never `requirements.txt` | One tool for venv, install, run, lock. |
| Interfaces | `interface`, `implements` | **Duck typing** + `Protocol` (structural typing); ABCs when you need it | "If it walks like a duck…" — you assert capability by use, or declare a `Protocol`. |
| Data holders | POJOs, Lombok, records | `@dataclass`, `NamedTuple`, and **Pydantic** models for validated/serialized data | Pydantic ≈ "Jackson + Bean Validation + records" in one. |
| Style | `camelCase`, braces | `snake_case`, **indentation is syntax**, PEP 8, enforced by Ruff | Whitespace matters. Let the formatter win every style argument. |
| Access control | `private`/`protected`/`public` | Convention: `_private` prefix; no true enforcement | "We're all adults here." No compiler-enforced encapsulation. |
| Overloading | Method overloading by signature | No overloading; use **default args, `*args`, `**kwargs`, keyword-only args** | One function, flexible signature. |

The single biggest reframe: **Python trusts you and optimizes for reading and iteration speed, not compile-time guarantees.** The AI team chose it precisely because LLM development is exploratory trial-and-error where Java's rigidity and boilerplate create friction.

---

## Part 1.5 — Execution Model: JVM vs CPython

A common misconception is "Java is compiled, Python is interpreted." The truth is **both compile to bytecode and run on a virtual machine** — the real differences are *when* compilation happens, *how far* it goes toward native code, and *how much the runtime optimizes*.

### Does Python compile? Yes.

When you run a `.py` file, the standard implementation (CPython) does:

```
your_code.py  →  [compile at import time]  →  bytecode (.pyc)  →  [Python VM interprets it]  →  execution
```

The compile step happens automatically at import/run time and is cached in `__pycache__/*.pyc`. The bytecode then runs on the **Python VM** — a big interpreter loop executing one instruction at a time. You can inspect it directly with `import dis; dis.dis(my_func)`. So Python is **compiled *and* interpreted**, same as Java in spirit; the difference is the last mile.

### The key contrast: JIT and closeness to the metal

| | Java / JVM | Python / CPython |
|---|---|---|
| Compile step | Ahead of time: `javac` → `.class` bytecode | At import time: source → `.pyc` bytecode |
| Runs on | JVM | Python VM (CPython interpreter) |
| Bytecode → native | **JIT** (HotSpot) profiles hot paths, compiles them to optimized machine code at runtime | **No JIT by default** — bytecode is re-interpreted every time (the big one) |
| Result | Long-running apps get *very* fast | Interpretation overhead makes pure-Python compute much slower |

That JIT gap is the single biggest reason CPython is slower than the JVM for CPU-bound work: the JVM watches hot methods, compiles them to native, and does inlining/escape analysis; CPython just interprets bytecode over and over.

### There is no JVM in Python's world

**CPython** (written in C) is the reference implementation and what "Python" almost always means. Alternatives exist — **PyPy** (has a JIT, much faster for pure Python), Jython (runs on the real JVM), GraalPy — but CPython is the default. "Python is slow" really means "CPython interprets bytecode without a JIT."

### Memory management / GC

The JVM gives you a sophisticated **tracing garbage collector**. CPython does something simpler:

* **Reference counting is primary** — every object tracks how many references point to it; when the count hits zero the object is freed **immediately** (deterministic, no GC pause). This is why `with` / context managers reliably release resources the instant the block ends.
* **A cyclic garbage collector** runs on top to catch reference *cycles* that refcounting alone can't free (A → B → A). It's generational and tracing, but only for cycles.
* **The GIL (Global Interpreter Lock)** exists largely to make reference counting thread-safe cheaply. Its consequence: only one thread executes Python bytecode at a time, so threads give concurrency but **not CPU parallelism** — hence async (for I/O) and multiprocessing (for CPU) are the tools you reach for.

### What Python does instead of a JIT: drop into C

Since the interpreter is the bottleneck, the ecosystem's answer is **"don't do heavy work in pure Python."** The hot libraries — NumPy, pandas, Pydantic v2's Rust core, ML frameworks — are compiled native code with thin Python bindings. **Most Python applications are a thin orchestration layer**: pure-Python code declares objects, calls into optimized libraries/methods, and assembles the response shape, while the crunching happens in C/Rust. This is why Python dominates ML despite being "slow" — the math isn't actually running in Python.

CPython is also improving on its own: **3.11** shipped a specializing adaptive interpreter (large speedups, no JIT), and **3.13** added an experimental JIT and an experimental free-threaded (no-GIL) build — both early, but the direction is clear.

### Why this matters for your work

Eval/agent workloads are **I/O-bound** — waiting on LLM APIs and internal services, not burning CPU. In that regime CPython's interpreter slowness is irrelevant; wall-clock time is network latency, and `asyncio` keeps thousands of calls in flight on one thread. That's why the AI team could pick Python for agents without worrying about JVM-class execution speed, and why the GIL isn't a bottleneck here. You'd only feel it on CPU-heavy scoring (e.g., local embeddings), where you offload to a C-backed library or `multiprocessing`.

---

## Part 2 — Core Fundamentals You Must Know Cold

### 2.1 The data model & "everything is an object"

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

# Functions are objects: assign, pass, store
fn = greet
handlers: dict[str, callable] = {"greet": greet}
print(fn("Yifei"))            # Hello, Yifei
print(handlers["greet"]("CG")) # Hello, CG
```

`is` compares identity (like Java `==` on references); `==` compares value (like Java `.equals()`). Use `is` only for `None`, `True`, `False`.

### 2.2 Truthiness

Empty containers, `0`, `""`, and `None` are all falsy. This drives idiomatic code:

```python
items: list[str] = []
if not items:          # idiomatic; NOT "if len(items) == 0"
    print("empty")
```

### 2.3 Functions: the flexible signature

```python
def run_eval(
    dataset: str,
    *,                        # everything after is keyword-only
    parallelism: int = 8,
    tags: list[str] | None = None,
) -> None:
    tags = tags or []        # None-coalescing idiom
    ...

run_eval("golden_set", parallelism=16, tags=["nightly"])
```

**Interview-critical gotcha — mutable default arguments:**

```python
def bad(items: list = []):   # ⚠️ the list is created ONCE at def time
    items.append(1)
    return items

bad(); bad()  # returns [1, 1] — shared state bug!

def good(items: list | None = None):
    items = items if items is not None else []
    ...
```

A strong candidate flags this instantly. It's the Python equivalent of a static field surprise in Java.

### 2.4 Data classes vs. Pydantic (know when to use which)

```python
from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass(frozen=True)      # like a Java record: pure in-memory value object
class Point:
    x: float
    y: float

class EvalConfig(BaseModel): # Pydantic: validates + (de)serializes JSON at boundaries
    dataset: str
    parallelism: int = Field(default=8, ge=1, le=64)
    tags: list[str] = []
```

Rule of thumb, matching CarGurus standards: **Pydantic at every trust boundary** (API request/response, config, LLM output parsing), plain `@dataclass` for internal value objects.

### 2.5 Typing you'll actually use

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar("T")

class Scorer(Protocol):                 # structural interface — no "implements"
    def score(self, output: str) -> float: ...

def average(scores: list[float]) -> float:
    return sum(scores) / len(scores) if scores else 0.0
```

`Protocol` is how Pythonistas express "interface" without inheritance. Modern syntax uses builtin generics (`list[int]`, `dict[str, int]`) and `X | None` instead of `Optional[X]`. Pyright enforces all of this in the build.

### 2.6 Context managers (Python's try-with-resources)

```python
with open("data.jsonl") as f:      # auto-closes, even on exception
    for line in f:
        ...

# async version for network resources
async with httpx.AsyncClient() as client:
    resp = await client.get(url)
```

### 2.7 Generators & lazy evaluation

```python
def read_traces(path: str):
    with open(path) as f:
        for line in f:            # yields one at a time — constant memory
            yield Trace.model_validate_json(line)

for trace in read_traces("big_run.jsonl"):   # streams, never loads all
    process(trace)
```

Generators (`yield`) are lazy sequences. Critical for processing large eval runs without loading everything into memory.

### 2.8 Decorators (cross-cutting concerns, like Java annotations + AOP)

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter()-start:.3f}s")
    return wrapper

@timed
def evaluate(): ...
```

Decorators are how FastAPI routes, pytest fixtures, and retry logic are expressed. Understand that `@timed` is just `evaluate = timed(evaluate)`.

### 2.9 Errors: EAFP over LBYL

```python
# Pythonic (EAFP): try it, handle failure
try:
    value = config["parallelism"]
except KeyError:
    value = 8

# vs. the Java-ish LBYL habit
value = config["parallelism"] if "parallelism" in config else 8
```

Both work; the first is idiomatic when the happy path dominates.

---

## Part 2.5 — Must-Know Data Model & Fundamentals (Interview Cheat Sheet)

This is the Python equivalent of the Java checklist you'd know cold (`ArrayList` vs `ArrayDeque`, `Stack` vs `Queue`, iterator-modify-in-place vs loop, `Integer.equals` vs `==`). Know these by heart — both to answer and to grade.

### 2.5.1 The core built-in containers

| Type | Mutable? | Ordered? | Java analog | Use when |
|---|---|---|---|---|
| `list` | Yes | Yes (insertion) | `ArrayList` | Default sequence; append/pop-from-end O(1) |
| `tuple` | **No** | Yes | immutable array / record | Fixed-size record; hashable → usable as dict key |
| `dict` | Yes | Yes (insertion, since 3.7) | `LinkedHashMap` | Key→value; O(1) average lookup |
| `set` | Yes | No | `HashSet` | Membership tests, dedup; O(1) average |
| `frozenset` | **No** | No | immutable `Set` | Hashable set (dict key / set element) |

Key mental shift from Java: **you rarely pick an *implementation*** (there's no `ArrayList` vs `LinkedList` decision). You pick a *shape* — sequence, mapping, or set — and CPython's one highly optimized C implementation backs each.

### 2.5.2 Stacks and queues (your `Stack` vs `Queue` question)

Python has **no dedicated `Stack` or `Queue` class** for algorithm work. Instead:

* **Stack (LIFO):** just use a `list` — `lst.append(x)` / `lst.pop()` are both O(1).
* **Queue (FIFO):** use `collections.deque` — `dq.append(x)` / `dq.popleft()` are both O(1). **Never use `list.pop(0)`** — it's O(n) because every element shifts. This is a classic interview gotcha.
* **Double-ended:** `deque` does both ends in O(1); it's the `ArrayDeque` equivalent.
* `queue.Queue` exists but is for *thread-safe* producer/consumer pipelines, not algorithms — don't reach for it in a coding round.

```python
from collections import deque
stack = []; stack.append(1); stack.pop()          # LIFO, O(1)
q = deque(); q.append(1); q.popleft()             # FIFO, O(1) — use for BFS
```

### 2.5.3 The `collections` "batteries" you must know

* `defaultdict(list)` / `defaultdict(int)` — auto-initializes missing keys; the idiomatic grouping/counting tool.
* `Counter(iterable)` — frequency map; `.most_common(k)` for top-K. A `dict` subclass.
* `deque` — the O(1)-both-ends queue/stack above.
* `namedtuple` / `typing.NamedTuple` — lightweight immutable record (lighter than a dataclass).

### 2.5.4 `heapq` and `bisect` (the "know the real cost" pair)

* `heapq` — a **min-heap** built on a plain list. `heappush`/`heappop` are O(log n); `heapify` is O(n). For a max-heap, push negated values. This is your `PriorityQueue`.
* `bisect` — binary search on a **sorted** list. `bisect_left` is O(log n) to *find* the index, but `insort` is O(n) overall because inserting into a list shifts elements. Knowing that insertion cost is the senior tell.

### 2.5.5 Mutability, identity, and equality (your `Integer.equals` vs `==`)

* `==` compares **value** (calls `__eq__`); `is` compares **identity** (same object in memory). Use `is` only for `None`, `True`, `False`.
* **Immutable:** `int`, `float`, `str`, `bytes`, `tuple`, `frozenset`, `bool`. **Mutable:** `list`, `dict`, `set`, most custom objects.
* **Hashability = immutability, roughly.** Only hashable objects can be dict keys or set members. A `tuple` of immutables is hashable; a `list` is not. If you define `__eq__` on a class, you must also define `__hash__` or instances become unhashable.
* **Integer caching gotcha:** small ints (−5 to 256) are cached, so `a is b` may be `True` for `256` but `False` for `257`. Never rely on `is` for numbers — this is the direct analog of the `Integer.equals` vs `==` trap you already know.

### 2.5.6 Reference semantics & copying (the sharp edges)

* **Assignment never copies** — `b = a` binds a second name to the *same* object. Mutating through `b` is visible through `a`.
* **Shallow vs deep copy:** `a.copy()` / `list(a)` / `a[:]` copy the outer container but share nested objects; `copy.deepcopy(a)` recurses. Java's clone-vs-deep-copy intuition transfers directly.
* **Mutable default arguments** (`def f(x=[])`) — the default is created once at definition time and shared across calls. Covered in 2.3; it's the single most-asked Python gotcha.

### 2.5.7 Iterators vs iterables vs generators (your iterator-modify point)

* An **iterable** produces an **iterator** via `iter()`; the iterator yields items via `next()` until `StopIteration`. `for` does this for you.
* **Modifying a collection while iterating it is a bug** — unlike Java, there's no fail-fast `ConcurrentModificationException`; you get silently skipped elements or a `RuntimeError` for dicts. The idiom is to **iterate a copy** (`for x in list(items):`) or **build a new collection** via comprehension. This is the Python answer to your "iterator can modify in place vs loop cannot" concept: here, *neither* should mutate the underlying container mid-iteration.
* **Generators** (`yield`) are lazy iterators — constant memory, single-pass. Once exhausted they're done. Covered in 2.7.

### 2.5.8 Sorting (know the API cold)

* `sorted(iterable)` returns a **new** list; `list.sort()` sorts **in place** and returns `None` (forgetting this and writing `x = lst.sort()` is a common bug).
* Both take `key=` (a function) and `reverse=`. Python's sort is **stable** (Timsort), O(n log n) — same guarantee as Java's `Collections.sort`.
* There's **no `Comparator`/`compareTo`** — you pass a `key` function (e.g., `key=lambda r: (r.score, r.name)` for multi-key sort). Legacy `cmp` functions are gone; wrap with `functools.cmp_to_key` only if forced.

### 2.5.9 Big-O cheat sheet (state these without hesitation)

| Operation | list | dict / set | deque |
|---|---|---|---|
| Index / key lookup | O(1) | O(1) avg | O(1) ends only |
| Append / add | O(1) amortized | O(1) avg | O(1) both ends |
| Insert / pop at front | **O(n)** | — | **O(1)** |
| Membership (`x in`) | **O(n)** | **O(1) avg** | O(n) |
| Search unsorted | O(n) | O(1) | O(n) |

The most common interview mistake is doing `x in a_list` inside a loop (O(n²)) when a `set` makes it O(n). Reward candidates who convert to a `set` for membership.

### 2.5.10 Strings (immutable, like Java)

* Strings are **immutable** — every "modification" makes a new string. Building a string in a loop with `+=` is O(n²); use `"".join(parts)` instead (the `StringBuilder` equivalent).
* f-strings (`f"{x:.2f}"`) are the modern formatting standard. Rich slicing (`s[::-1]` to reverse) and methods (`.split`, `.strip`, `.startswith`) replace most manual char work.

---

## Part 2.7 — Object-Oriented Python (Class Design Fundamentals)

Python is fully object-oriented, but the conventions differ sharply from Java. The biggest reframe: **Python favors composition, duck typing, and lightweight data classes over deep inheritance hierarchies and getter/setter boilerplate.** This is the section to know cold for a class-design interview question.

### 2.7.1 Anatomy of a class

```python
class EvalRun:
    # class attribute — shared by ALL instances (like Java `static` field)
    default_timeout: float = 30.0

    def __init__(self, run_id: str, cases: list[str]) -> None:
        # instance attributes — per object; assigned on `self`
        self.run_id = run_id
        self.cases = cases
        self._cursor = 0            # "_" = internal by convention (not enforced)

    def next_case(self) -> str | None:      # instance method — explicit `self`
        if self._cursor >= len(self.cases):
            return None
        case = self.cases[self._cursor]
        self._cursor += 1
        return case
```

Key differences from Java:

* **`self` is explicit** — every instance method takes `self` as its first parameter (the Java `this`, but never implicit). Forgetting it is the #1 beginner error.
* **`__init__` is a constructor, not the constructor** — the object already exists when `__init__` runs (real construction is `__new__`, rarely overridden). You *initialize* here, you don't *allocate*.
* **No `new` keyword** — you instantiate with `EvalRun("r1", [...])`, calling the class directly.
* **No field declarations** — attributes spring into existence when assigned on `self`. There's no "declare all fields at the top" requirement (though type hints in `__init__` help).
* **Class vs instance attributes** — a value assigned in the class body is shared (`static`); one assigned on `self` is per-instance. A classic trap: a **mutable class attribute** (`tags: list = []` at class level) is shared across all instances, same bug as a mutable default argument.

### 2.7.2 The method trio: instance / class / static

| Decorator | First arg | Java analog | Use for |
|---|---|---|---|
| (none) | `self` | instance method | Normal behavior on an object |
| `@classmethod` | `cls` | `static` factory returning an instance | Alternative constructors (`from_json`, `from_file`) |
| `@staticmethod` | none | plain `static` util | Namespaced helper that needs no state |

```python
class EvalRun:
    @classmethod
    def from_jsonl(cls, path: str) -> "EvalRun":     # factory — the Pythonic named constructor
        cases = [line.strip() for line in open(path)]
        return cls(run_id=path, cases=cases)          # `cls` supports subclassing

    @staticmethod
    def is_valid_id(run_id: str) -> bool:
        return run_id.isalnum()
```

Python has **no method overloading** — you can't define two `__init__`s. Instead use `@classmethod` factories (`from_jsonl`, `from_dict`) or default/keyword arguments. This is a frequent Java-carryover question.

### 2.7.3 `@property` — the getter/setter you've been missing

**Do not write `get_x()` / `set_x()` in Python.** Access attributes directly. If you later need computed or validated access, convert to a `@property` *without changing any calling code* — this is why Python has no getter/setter boilerplate.

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:              # read: t.celsius (no parens!)
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None: # write: t.celsius = 20
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:           # computed, read-only
        return self._celsius * 9 / 5 + 32

t = Temperature(25)
t.celsius = 30          # calls the setter — validation runs
print(t.fahrenheit)     # 86.0 — looks like a field, computed on access
```

The lesson for a Java engineer: **start with a plain public attribute; promote to `@property` only when you need logic.** Adding getters "just in case" is an anti-pattern here.

### 2.7.4 Inheritance, `super()`, and MRO

```python
class Scorer:
    def __init__(self, name: str) -> None:
        self.name = name
    def score(self, output: str) -> float:
        raise NotImplementedError

class ExactMatch(Scorer):
    def __init__(self, name: str, target: str) -> None:
        super().__init__(name)               # call parent __init__ (no explicit `this`)
        self.target = target
    def score(self, output: str) -> float:   # override — no @Override annotation
        return 1.0 if output == self.target else 0.0
```

* **No `@Override`** — overriding is implicit; a typo silently creates a *new* method (Pyright/linters catch some of this).
* **`super()`** takes no args in modern Python and cooperates with **multiple inheritance** via the **MRO** (Method Resolution Order, C3 linearization). Python *allows* multiple inheritance — unlike Java — which is why `super()` follows the MRO chain, not just "the parent."
* **`isinstance(obj, Scorer)`** / **`issubclass`** for runtime type checks. But idiomatic Python leans on duck typing / `Protocol` instead of `isinstance` walls.

### 2.7.5 Composition and Protocols over inheritance

The single most important senior signal: **prefer composition and structural typing over inheritance.** In Java you reach for `interface` + `implements`; in Python you usually reach for a `Protocol` (structural, no declaration needed) or just duck typing.

```python
from typing import Protocol

class Scorer(Protocol):                      # structural interface — implementers need NOT subclass
    def score(self, output: str) -> float: ...

class KeywordScorer:                         # note: does NOT inherit Scorer
    def __init__(self, keyword: str) -> None:
        self.keyword = keyword
    def score(self, output: str) -> float:   # satisfies the Protocol by shape alone
        return 1.0 if self.keyword in output else 0.0

def run(scorer: Scorer, out: str) -> float:  # accepts anything with a matching .score()
    return scorer.score(out)
```

* **`Protocol`** = structural typing ("if it has `.score()`, it *is* a Scorer"), checked by Pyright, zero runtime coupling. This is what the eval SDK in Part 6 uses.
* **ABC (`abc.ABMeta`)** = nominal typing when you *want* to force explicit subclassing and share implementation:

```python
from abc import ABC, abstractmethod

class BaseScorer(ABC):
    @abstractmethod
    def score(self, output: str) -> float: ...   # subclass MUST implement or can't instantiate
    def describe(self) -> str:                    # shared concrete behavior
        return f"{type(self).__name__} scorer"
```

**Interview rule of thumb:** use a `Protocol` for a pluggable interface (users bring their own types), an ABC when you own the hierarchy and want shared code + enforced contract, and plain composition (hold a collaborator as an attribute) as the default over subclassing for reuse.

### 2.7.6 Dunder methods — making your class behave like a built-in

"Dunder" (double-underscore) methods are how a class hooks into language operators and built-in functions. This is Python's answer to `equals`/`hashCode`/`toString`/`Comparable`/`Iterable` — and a favorite senior probe (from the earlier `len()` → `__len__` discussion).

| Dunder | Enables | Java analog |
|---|---|---|
| `__init__` | construction/init | constructor |
| `__repr__` | debug string (`repr(x)`, REPL) | — (always add this) |
| `__str__` | user string (`str(x)`, `print`) | `toString()` |
| `__eq__` | `==` | `equals()` |
| `__hash__` | use as dict key / set member | `hashCode()` |
| `__lt__`, `__gt__`, ... | `<`, `>`, sorting | `Comparable`/`compareTo` |
| `__len__` | `len(x)` | `size()` |
| `__iter__`, `__next__` | `for x in obj` | `Iterable`/`Iterator` |
| `__getitem__`, `__setitem__` | `obj[k]` | array/`Map` access |
| `__contains__` | `x in obj` | `contains()` |
| `__enter__`, `__exit__` | `with obj:` | try-with-resources |
| `__call__` | `obj()` | `Runnable`/functional |

```python
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.major, self.minor = major, minor
    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor})"
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and (self.major, self.minor) == (other.major, other.minor)
    def __hash__(self) -> int:                 # REQUIRED if you define __eq__ and want hashability
        return hash((self.major, self.minor))
    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor) < (other.major, other.minor)
```

**Critical trap (the `equals`/`hashCode` contract, Python edition):** if you define `__eq__` but not `__hash__`, Python sets `__hash__` to `None` and your object becomes **unhashable** — it can't be a dict key or set member. Always define both together (or use a frozen dataclass, which does it for you).

### 2.7.7 Let the framework write it: dataclasses, `slots`, enums

Most of the boilerplate above is auto-generated for you:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)          # frozen = immutable; slots = memory-efficient
class Point:
    x: float
    y: float
    tags: list[str] = field(default_factory=list)   # correct mutable default
```

`@dataclass` auto-generates `__init__`, `__repr__`, `__eq__`, and (with `frozen=True`) `__hash__` — this is the Java **record**/Lombok equivalent. Use it for value objects; use **Pydantic** `BaseModel` when you also need validation and JSON (de)serialization at a boundary. `slots=True` (or `__slots__`) trades the per-instance `__dict__` for a fixed attribute layout — less memory and faster access, at the cost of dynamic attributes.

```python
from enum import Enum

class Status(str, Enum):        # subclassing str makes it JSON-friendly
    OK = "ok"
    ERROR = "error"
```

### 2.7.8 Encapsulation reality check

Python has **no true `private`**. Conventions instead:

* `name` — public.
* `_name` — "internal, don't touch" (convention only; fully accessible).
* `__name` (two leading underscores) — **name mangling**: rewritten to `_ClassName__name` to avoid *accidental* subclass collisions. It's not security, just collision-avoidance. Use sparingly.

The cultural norm — *"we're all adults here"* — means you design clear public APIs and trust callers, rather than relying on the compiler to enforce access. For an interviewer, the signal is a clean, minimal public surface and `_` on genuine internals, not `__` everywhere.

### 2.7.9 What to probe as an interviewer

* "You've written `get_score()`/`set_score()` — is that idiomatic?" (Strong: no, use a plain attribute, promote to `@property` if logic is needed.)
* "How would you offer two ways to construct this object?" (Strong: `@classmethod` factories, since there's no overloading.)
* "You defined `__eq__` — anything else you must do?" (Strong: `__hash__`, or explain the unhashable consequence.)
* "Inheritance or composition here?" (Strong: defaults to composition / `Protocol`; justifies inheritance only for genuine is-a + shared implementation.)
* "`Protocol` vs ABC?" (Strong: structural/pluggable vs nominal/owned-hierarchy tradeoff.)
* "How do you make this immutable?" (Strong: `@dataclass(frozen=True)` or a `NamedTuple`.)

---

## Part 3 — Comprehensions (The Thing You Asked About)

Comprehensions are Python's signature idiom and the fastest way to spot fluency. They replace the `for`-loop-append pattern with a single readable expression.

### 3.1 The four forms

```python
nums = [1, 2, 3, 4, 5]

# List comprehension
squares = [n * n for n in nums]                    # [1, 4, 9, 16, 25]

# With filter
evens = [n for n in nums if n % 2 == 0]            # [2, 4]

# Dict comprehension
lookup = {n: n * n for n in nums}                  # {1: 1, 2: 4, ...}

# Set comprehension
distinct = {n % 3 for n in nums}                   # {0, 1, 2}

# Generator expression (lazy — note parentheses)
total = sum(n * n for n in nums)                   # streams, no temp list
```

### 3.2 Java → comprehension translation

```java
// Java Stream
List<String> names = users.stream()
    .filter(u -> u.isActive())
    .map(User::getName)
    .collect(Collectors.toList());
```

```python
# Python comprehension — the direct equivalent
names = [u.name for u in users if u.is_active]
```

```python
# Grouping (Java Collectors.groupingBy) — use defaultdict or itertools.groupby
from collections import defaultdict
by_status: dict[str, list[Run]] = defaultdict(list)
for r in runs:
    by_status[r.status].append(r)
```

### 3.3 Idioms that pair with comprehensions

```python
for i, item in enumerate(items):        # index + value, no C-style loop
    ...

for name, score in zip(names, scores):  # parallel iteration
    ...

pairs = {name: score for name, score in zip(names, scores)}
```

### 3.4 The taste line (what to probe in interviews)

Comprehensions should stay **readable and one level of logic deep**. Nested, multi-clause comprehensions are a smell:

```python
# ⚠️ too clever — reject in review
result = [f(x) for row in matrix for x in row if g(x) and h(x)]

# ✓ a loop is clearer here
result = []
for row in matrix:
    for x in row:
        if g(x) and h(x):
            result.append(f(x))
```

A senior candidate knows comprehensions are for clarity, not showing off, and will refactor to a loop when logic gets deep.

---

## Part 4 — The Interviewer's Toolkit

CarGurus interviews assess **Programming Fundamentals** (algorithms, data structures, class/component design, data abstraction, object/array manipulation, Big O, concurrency, recursion) and **Frameworks & Languages** as distinct focus attributes, calibrated by level (IC2 needs guidance, IC3 mostly independent, IC4 fully independent with tradeoff analysis). Use the [Eng Technical Interview Questions Inventory](https://docs.google.com/spreadsheets/d/11OO4jVdJXTfm_zZxjuKJqPHpj-Sj7y4Z0e8opIUUlo0) for the shared question bank, and complete the required [Ask Better, Hire Better](https://app.socialtalent.com/my-learning/episode/663be2298a9070860909aeec/663be24c25e0f2f2fe13b9e2/664ba6e068d3d72cd900503e) SocialTalent training if you haven't.

### 4.1 What separates a strong Python candidate

**Green flags:**
* Reaches for comprehensions, `enumerate`, `zip`, dict/set idioms naturally.
* Uses type hints and knows they're tooling-enforced, not runtime.
* Knows the mutable-default-argument trap and why `is None` matters.
* Explains the **GIL** correctly: threads don't give CPU parallelism, but `asyncio` and multiprocessing address different bottlenecks; async shines for I/O-bound LLM/API work.
* Uses Pydantic/dataclasses for data modeling rather than raw dicts everywhere.
* Reaches for `pytest` (not `unittest`), knows fixtures.
* Mentions `uv`, Ruff, Pyright, or virtual environments unprompted — signals modern, professional Python.

**Red flags:**
* C-style `for i in range(len(x))` index loops everywhere.
* Bare `except:` that swallows all errors.
* Mutating a list while iterating it.
* Treating type hints as runtime-enforced ("Python will reject a str here").
* Never using context managers for files/connections.
* Confidently wrong on the GIL (e.g., "threads make CPU work faster").

### 4.2 A language-fundamentals mini-exercise (10 min)

Ask them to implement `summarize_runs`:

> Given a list of eval-run dicts like `[{"model": "gpt-4o", "passed": True, "latency_ms": 820}, ...]`, return a dict mapping each model to its pass rate and average latency.

A strong answer looks like:

```python
from collections import defaultdict
from statistics import mean

def summarize_runs(runs: list[dict]) -> dict[str, dict[str, float]]:
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        by_model[r["model"]].append(r)
    return {
        model: {
            "pass_rate": mean(1.0 if r["passed"] else 0.0 for r in rs),
            "avg_latency_ms": mean(r["latency_ms"] for r in rs),
        }
        for model, rs in by_model.items()
    }
```

**Probe:** Why `defaultdict`? Why a generator expression inside `mean`? What happens with an empty input? Would you validate the input shape (Pydantic) at a real boundary? How would you test this with `pytest`?

### 4.3 Behavioral / design prompts that map to CDM focus attributes

* *System analysis:* "A Python eval service is slow. Walk me through diagnosis." (Looks for: profiling, async vs. blocking I/O, N+1 API calls, connection pooling — your own wheelhouse.)
* *Concurrency:* "You need to run 5,000 LLM evaluations. How do you parallelize?" (Looks for: async + bounded concurrency via semaphore, not naive threads; awareness of rate limits.)
* *Design:* "Model the data for storing agent execution traces." (See Part 6.2 for the reference answer.)

### 4.4 Calibrating by level

| Level | Expectation |
|---|---|
| IC2 | Working solution with some hints; solid data-structure choices; basic tests. |
| IC3 | Mostly independent; clean idiomatic Python; explains tradeoffs; comprehensive tests. |
| IC4+ | Independent and fast; discusses performance, scalability, design patterns, fault tolerance; async/concurrency fluency. |

---

## Part 5 — Using Python at Work: The CarGurus Stack

The AI team has already made the hard tooling decisions. Start from templates and follow the standards rather than re-deriving them.

| Concern | CarGurus standard | Java analog |
|---|---|---|
| Python version | 3.13 minimum, prefer 3.14 | JDK version |
| Dependencies | `uv` + `pyproject.toml`, commit `uv.lock`, no `requirements.txt` | Maven + `pom.xml` |
| Web framework | FastAPI (not Django/Flask) | Spring Boot |
| HTTP client | HTTPX, async-capable (not `requests`) | WebClient / RestTemplate |
| Validation/serialization | Pydantic | Jackson + Bean Validation |
| Format & lint | Ruff | Checkstyle + Spotless |
| Type checking | Pyright (not MyPy) | `javac` |
| ORM / migrations | SQLAlchemy + Alembic | Hibernate + Flyway |
| Testing | pytest (not `unittest`) | JUnit + Mockito |
| Layout | `src/` package layout for services | Maven standard dir layout |
| Agent orchestration | LangChain / LangGraph on asyncio (Discover V2) | Custom / LangGraph4J |
| Observability | App logs → Observe, Prometheus, Sentry, OpenTelemetry → Honeycomb (via `python-common`) | Your existing metrics/alerting work |

Two internal references worth cloning and reading:
* [`python-fastapi-service-template`](https://code.cargurus.com/cargurus-eng/python-fastapi-service-template) — service skeleton, config, auth, observability, testing.
* [listings-comparison eval harness](https://code.cargurus.com/cargurus-eng/listings-comparison/blob/main/src/test/python/README.md) — a real CarGurus eval system using the OpenAI Evals API, `uv`, `pytest`, and Pydantic models generated from the Java service schema.

Your existing strengths in latency optimization, connection-pool metrics, circuit breakers, and Prometheus alerting transfer directly — you'll just express them through asyncio semaphores, HTTPX client limits, and the `python-common` observability library instead of Spring.

---

## Part 5.5 — Concurrency Deep Dive: threading, asyncio & the Java Mental Model

This is the section written for you specifically. You already understand concurrency at the level that matters — thread pools as the server bottleneck, starvation, pool tuning, and resilience patterns (circuit breaker, bulkhead). Python's models are different in mechanism but the *problems* and *patterns* are identical. The goal here is to re-map your instincts, not rebuild them.

### 5.5.1 The three models, and the one rule that decides

| Model | Parallel CPU? | Concurrency mechanism | Java analog | Use for |
|---|---|---|---|---|
| `threading` | **No** (GIL) | OS threads, preemptive | Platform threads + pool | Blocking I/O with sync libraries |
| `asyncio` | **No** (single thread) | Coroutines, cooperative | Virtual threads / Netty event loop | I/O-bound with async libraries (LLM, HTTPX) |
| `multiprocessing` | **Yes** | Separate interpreters | Multiple JVMs | CPU-bound work |

The decision rule: **CPU-bound → processes; I/O-bound → asyncio (if the libraries are async) or threads (if they're blocking).** The GIL is why this table looks nothing like Java's — in Java you reach for threads for *both* CPU and I/O parallelism; in CPython threads only ever buy you I/O concurrency because only one thread runs Python bytecode at a time.

One nuance that surprises Java engineers: **threads *do* help for blocking I/O in Python**, because CPython releases the GIL during blocking syscalls (socket reads, disk, `time.sleep`) and inside many C extensions. So a `ThreadPoolExecutor` of 50 threads all waiting on network sockets genuinely overlaps their waits — the GIL only serializes the tiny bytecode slices between syscalls.

### 5.5.2 The asyncio event loop — what it actually is

Mechanically, asyncio is **a single-threaded event loop over an OS selector (`epoll`/`kqueue`)** — the same architecture as Node.js or Netty's event loop, not a thread pool. Understanding the pieces removes all the mystery:

* **Coroutine** — calling an `async def` function does **not** run it; it returns a *coroutine object*, like a paused computation. This is the #1 beginner bug (see below). It runs only when awaited or scheduled.
* **`await`** — a cooperative yield point. It says "suspend me here, hand control back to the loop, wake me when this awaitable is done." Between `await` points your code runs uninterrupted — there is **no preemption**.
* **Task** — `asyncio.create_task(coro)` wraps a coroutine and schedules it on the loop to run *concurrently*. This is how you get overlap; a bare `await coro` just runs it inline.
* **Future** — a low-level awaitable placeholder for a result (Task is a subclass). You rarely create these directly; they're the plumbing under `gather`, locks, etc.
* **The loop** — runs ready callbacks until they hit an `await`, asks the selector which sockets are ready, wakes the corresponding tasks, repeats. `asyncio.run(main())` creates the loop, runs your top coroutine to completion, and tears it down.

```python
async def fetch(x): ...

# WRONG — creates a coroutine object and throws it away; nothing runs.
fetch(1)                              # RuntimeWarning: coroutine never awaited

# Runs it, but SEQUENTIALLY (each await blocks the next)
a = await fetch(1)
b = await fetch(2)

# CONCURRENT — schedule both as tasks, then await
t1 = asyncio.create_task(fetch(1))
t2 = asyncio.create_task(fetch(2))
a, b = await t1, await t2

# CONCURRENT, idiomatic — gather schedules all and waits
a, b = await asyncio.gather(fetch(1), fetch(2))
```

**The cardinal sin: blocking the loop.** Because it's one thread with no preemption, a single blocking call freezes *every* concurrent task — the async equivalent of holding a global lock. A synchronous `time.sleep(5)`, `requests.get(...)`, a big JSON parse, or a tight CPU loop inside a coroutine stalls the whole service.

```python
async def handler():
    time.sleep(5)                     # freezes ALL tasks for 5s
    await asyncio.sleep(5)            # yields to the loop; others run
    data = requests.get(url)          # blocking HTTP — freezes the loop
    data = await client.get(url)      # HTTPX async
    result = heavy_cpu(data)          # CPU work blocks the loop
    result = await asyncio.to_thread(heavy_cpu, data)  # offload to a thread
```

`asyncio.to_thread(fn, ...)` is your escape hatch: it runs a blocking function on asyncio's default `ThreadPoolExecutor` and gives you an awaitable, letting you bridge sync libraries into async code without freezing the loop. For CPU-bound work, offload to a `ProcessPoolExecutor` via `loop.run_in_executor` instead.

### 5.5.3 The `ThreadPoolExecutor` — your Java pool, mostly intact

Everything you know about thread pools transfers, with the GIL caveat. `concurrent.futures` is the near-direct `ExecutorService` analog:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=32) as pool:      # bounded pool
    futures = {pool.submit(call_api, u): u for u in urls}
    for fut in as_completed(futures):                 # completion order
        try:
            result = fut.result(timeout=30)           # re-raises worker exceptions here
        except TimeoutError:
            ...
```

**Thread starvation and pool tuning are exactly the same discipline.** An unbounded or undersized pool that fills with slow/blocked tasks starves everything behind it — identical to your Java experience. Sizing heuristics carry over too: for I/O-bound work you oversize relative to cores (`workers ≈ target_concurrency` bounded by downstream capacity); for CPU-bound work threads are pointless (GIL) so you size a *process* pool near core count. The one genuinely new failure mode: a CPU-heavy task submitted to a thread pool doesn't just occupy its worker, it also contends for the GIL and slows *every other thread's* bytecode — so mixing CPU work into an I/O thread pool is worse in Python than in Java.

Key API mapping:

| Java | Python | Notes |
|---|---|---|
| `ExecutorService` | `ThreadPoolExecutor` / `ProcessPoolExecutor` | Context-manage it (`with`) for clean shutdown |
| `Future.get()` | `future.result(timeout=)` | Blocks; re-raises the worker's exception |
| `CompletableFuture` chaining | `add_done_callback`, or just use asyncio | asyncio is cleaner for composition |
| `invokeAll` | `pool.map(fn, iterable)` | Preserves input order |
| `ExecutorCompletionService` | `as_completed(futures)` | Yields as they finish |
| Core/max/queue tuning | `max_workers` (+ your own bounded queue) | No separate core/max; one fixed size |

### 5.5.4 Resilience patterns: circuit breaker & bulkhead in Python

Here's where your Java resilience toolkit maps over — with the important caveat that **Python has no Resilience4j/Hystrix in the standard library**, so you either pull a library or hand-roll (both are common and interview-worthy).

**Bulkhead** is the most natural pattern in asyncio: a bulkhead is just **a `Semaphore` per downstream dependency**. Isolating each dependency's concurrency budget prevents one slow dependency from consuming all your capacity — exactly the bulkhead intent.

```python
class Bulkheads:
    """One concurrency budget per downstream — failures/slowness stay isolated."""
    def __init__(self):
        self._limits = {
            "llm":       asyncio.Semaphore(20),   # LLM provider budget
            "inventory": asyncio.Semaphore(50),   # internal service budget
            "db":        asyncio.Semaphore(10),
        }
    async def call(self, dep: str, coro):
        async with self._limits[dep]:             # blocks only that dependency's callers
            return await coro
```

If a dependency hangs, only its 20/50/10 permits get tied up; callers of the *other* dependencies sail through. The threaded equivalent is a **separate `ThreadPoolExecutor` per dependency** rather than one shared pool — same isolation principle, which is precisely why one-pool-per-dependency is the classic bulkhead implementation.

**Circuit breaker** — the state machine (CLOSED → OPEN → HALF_OPEN) is identical to what you know. A compact async hand-roll:

```python
import time, asyncio

class CircuitOpen(Exception): ...

class CircuitBreaker:
    def __init__(self, *, fail_threshold=5, reset_after=30.0):
        self._fail_threshold = fail_threshold
        self._reset_after = reset_after
        self._failures = 0
        self._opened_at = 0.0
        self._state = "CLOSED"
        self._lock = asyncio.Lock()

    async def call(self, coro):
        async with self._lock:
            if self._state == "OPEN":
                if time.monotonic() - self._opened_at >= self._reset_after:
                    self._state = "HALF_OPEN"        # allow one trial call
                else:
                    raise CircuitOpen("circuit is open; failing fast")
        try:
            result = await coro
        except Exception:
            await self._on_failure()
            raise
        else:
            await self._on_success()
            return result

    async def _on_failure(self):
        async with self._lock:
            self._failures += 1
            if self._failures >= self._fail_threshold or self._state == "HALF_OPEN":
                self._state = "OPEN"
                self._opened_at = time.monotonic()

    async def _on_success(self):
        async with self._lock:
            self._failures = 0
            self._state = "CLOSED"
```

In production you'd usually reach for a library — `pybreaker` (sync + async), `aiobreaker`, or `purgatory` — rather than hand-roll, but knowing the state machine cold is the senior signal. Combined with `asyncio.timeout()` (fail fast on slow calls) and retries-with-backoff, these are the same three legs — timeout, retry, circuit-break — you already deploy in Java, just expressed with async primitives. This is exactly the transfer noted in Part 5: your circuit-breaker and connection-pool instincts carry over, expressed through semaphores and HTTPX client limits.

### 5.5.5 Virtual threads vs asyncio — the mental bridge you're looking for

This is the comparison that will click hardest for you, because Java's Project Loom virtual threads and Python's asyncio are **two different answers to the same problem**: "how do I run 100k concurrent I/O operations without 100k expensive OS threads?"

Both avoid the "thread-per-request pool is the bottleneck" trap you described. But they differ on the axis that matters most day-to-day — **function coloring**:

| Dimension | Java virtual threads (Loom) | Python asyncio |
|---|---|---|
| Unit | Virtual thread (M:N onto carrier threads) | Coroutine on one event-loop thread |
| Scheduling | JVM mounts/unmounts vthreads on carriers | Cooperative; yields only at `await` |
| **Function coloring** | **None** — blocking code just works; `Thread.sleep` transparently unmounts | **Colored** — `async`/`await` is viral; sync and async worlds don't mix freely |
| Blocking a call | Cheap — vthread unmounts, carrier runs others | Catastrophic if truly blocking — freezes the loop |
| Parallel CPU | Yes (real threads underneath, no GIL) | No (single thread + GIL) |
| Existing sync code | Runs unchanged, now scalable | Must be rewritten to `async`, or offloaded via `to_thread` |
| Mental model | "Threads, but cheap" | "One thread, cooperative multitasking" |

The headline difference: **Loom makes blocking cheap and invisible, so your existing imperative, blocking code scales for free.** Python makes concurrency *explicit and cooperative* — you must mark suspension points with `await`, and the "colored function" problem is real: an `async def` can only be awaited from async context, so introducing async into a sync codebase tends to propagate upward. Loom deliberately eliminates coloring; asyncio deliberately embraces it (explicit yield points make races easier to reason about, since your code can't be preempted mid-critical-section).

Two practical consequences for you:

1. **Don't look for a Loom equivalent in CPython — there isn't a mainstream one.** The closest is `gevent`/greenlets (monkeypatches the stdlib to make blocking calls yield transparently, giving Loom-like invisibility), but the ecosystem standardized on explicit `asyncio` instead. If you want "cheap threads that block transparently," that's `gevent`; if you want the modern, supported, LangGraph-aligned path, that's `asyncio`.
2. **The cooperative model is a feature for correctness.** Because nothing preempts you between `await` points, whole classes of data races that plague Java thread pools simply can't occur on a single event loop — you only need to reason about interleavings at `await` boundaries. That's why asyncio code often needs *fewer* locks than the equivalent threaded code.

### 5.5.6 Cancellation, timeouts & structured concurrency

Loom and modern asyncio both converged on **structured concurrency**. In Python (3.11+):

```python
# Timeout that actually cancels the work (not just stops waiting)
async def fetch_bounded(url):
    async with asyncio.timeout(5):          # raises TimeoutError, cancels the coro
        return await client.get(url)

# TaskGroup — all tasks awaited together; if one fails, siblings are cancelled
async def run_batch(cases):
    results = []
    async with asyncio.TaskGroup() as tg:   # replaces bare gather for structured lifetimes
        for c in cases:
            tg.create_task(process(c, results))
    return results                          # only reached if all succeeded
```

Cancellation is cooperative too: cancelling a task injects `asyncio.CancelledError` at its next `await`. Always let it propagate (don't swallow it in a bare `except:`) and use `try/finally` or `async with` for cleanup — the direct analog of responding to Java's `Thread.interrupt()`. `TaskGroup` gives you the "all-or-nothing, no leaked tasks" guarantee that a raw `gather` does not.

### 5.5.7 The one-paragraph summary for interviews

*Python has three concurrency models divided by the GIL: `multiprocessing` for CPU parallelism, and `threading`/`asyncio` for I/O concurrency. `asyncio` is a single-threaded cooperative event loop over an OS selector — like Netty or Node — where coroutines yield at explicit `await` points, so it scales to huge I/O fan-out with no thread-pool starvation, but a single blocking or CPU-bound call freezes everything. Threads still help for blocking I/O because CPython releases the GIL during syscalls, but never for CPU work. Resilience patterns map directly: bulkheads are per-dependency semaphores (or per-dependency pools), circuit breakers are the same CLOSED/OPEN/HALF_OPEN state machine, and timeouts/retries use asyncio primitives. Compared to Java virtual threads, asyncio trades Loom's transparent-blocking model for explicit function coloring — more ceremony, but cooperative scheduling that eliminates most data races.*

---

## Part 5.6 — The asyncio Debugging Playbook

Async bugs don't throw stack traces the way a Java `NullPointerException` does — they manifest as *silence*: latency that shouldn't exist, tasks that vanish, exceptions that never surface. Coming from Java, the instinct is to attach a debugger and read the thread dump. In asyncio the equivalent skill is **"who is holding the event loop, and what did I forget to await."**

### 5.6.1 The #1 production bug: a blocked event loop

The entire model rests on one rule — coroutines must yield control at every I/O point via `await`. A single synchronous blocking call freezes *all* concurrency on that thread, because there is only one thread. Your 5,000 in-flight LLM calls all stall behind one bad line.

The usual culprits, all of which look innocent:

```python
import time, requests

async def handle(case):
    time.sleep(0.5)               # ❌ freezes the loop for 500ms — use await asyncio.sleep
    data = requests.get(url)      # ❌ blocking HTTP — use httpx.AsyncClient
    rows = cursor.execute(sql)    # ❌ blocking DB driver — use an async driver
    embedding = model.encode(x)   # ❌ CPU-bound — offload with asyncio.to_thread / a process
```

**Symptom to recognize:** throughput that doesn't improve when you raise concurrency, and p99 latency that scales linearly with load even though the work is I/O. That's the async equivalent of Java **thread starvation**, except you can't fix it by growing a pool — there is no pool, just the loop. The fix is to make the call non-blocking or push it off the loop:

```python
result = await asyncio.to_thread(blocking_fn, arg)   # runs in the default thread pool
```

### 5.6.2 Turn on debug mode — it finds blocked loops for you

asyncio ships a debug mode that logs any callback or coroutine step that hogs the loop for more than 100ms (tunable), warns on coroutines that were never awaited, and on tasks destroyed while pending.

```python
import asyncio
asyncio.run(main(), debug=True)          # simplest
# or: PYTHONASYNCIODEBUG=1 python app.py
# or, on a running loop:
loop.set_debug(True)
loop.slow_callback_duration = 0.05       # flag callbacks slower than 50ms
```

With debug on, a blocking call produces: `Executing <Task ...> took 0.512 seconds` — pointing you straight at the offending coroutine. This is your first move whenever async latency looks wrong.

### 5.6.3 The "forgotten await" and "orphaned task" traps

```python
result = agent.run(case)          # ❌ returns a coroutine object, not the result
result = await agent.run(case)    # ✓
```

A forgotten `await` doesn't error — the coroutine is created and silently never runs. Debug mode catches it (`coroutine '...' was never awaited`); Pyright/Ruff also flag it, which is one more reason the CarGurus type-checking standard earns its keep.

**Orphaned fire-and-forget tasks** are subtler and bite in production:

```python
asyncio.create_task(log_metrics(result))   # ⚠️ no reference kept
```

The loop keeps only *weak* references to tasks, so a task with no strong reference can be garbage-collected mid-flight and simply disappear — no error, no completion. Always keep a reference (or use a `TaskGroup`, which owns its children):

```python
_background: set[asyncio.Task] = set()
def spawn(coro):
    t = asyncio.create_task(coro)
    _background.add(t)
    t.add_done_callback(_background.discard)   # let it be collected once truly done
```

### 5.6.4 Exceptions that never surface

An exception inside a task stays *inside* that task until you `await` it or read `.result()`. Fire-and-forget tasks that raise will log `Task exception was never retrieved` only when garbage-collected — often long after, or never. Two defenses:

```python
# 1) gather with return_exceptions=True — collect failures as data
results = await asyncio.gather(*coros, return_exceptions=True)
for r in results:
    if isinstance(r, Exception):
        handle(r)

# 2) TaskGroup (3.11+) — first failure cancels siblings and re-raises as ExceptionGroup
try:
    async with asyncio.TaskGroup() as tg:
        for c in cases:
            tg.create_task(run(c))
except* ValueError as eg:          # note except* — matches inside the ExceptionGroup
    for exc in eg.exceptions:
        report(exc)
```

`ExceptionGroup` + `except*` is the structured-concurrency error model — the analog of aggregating exceptions from a batch of Java `Future`s, but the language handles the fan-in.

### 5.6.5 Introspecting a live loop (the "thread dump" equivalent)

When something hangs, enumerate the tasks and see where each is parked:

```python
for t in asyncio.all_tasks():
    print(t.get_name(), t.get_coro().__qualname__)
    t.print_stack()          # shows where this task is currently awaiting
```

Name your tasks so this output is readable — the async equivalent of naming your threads:

```python
asyncio.create_task(run(case), name=f"eval-{case.id}")
```

Deeper tooling, in order of reach:
* **`aiomonitor`** — attach a REPL to a running loop in production and list/inspect tasks live (the closest thing to jstack for asyncio).
* **`faulthandler`** — dump all stacks on a signal or timeout for a truly wedged process.
* **`aiodebug` / event-loop-lag metrics** — export loop lag as a Prometheus gauge; rising lag is your leading indicator of a blocked loop, and slots directly into the observability work you already do.

### 5.6.6 Debugging checklist

| Symptom | Likely cause | First check |
|---|---|---|
| Latency doesn't drop as concurrency rises | Blocked loop (sync call in coroutine) | Debug mode "took N seconds" warnings |
| Coroutine "did nothing" | Missing `await` | Debug mode / Pyright "never awaited" |
| Task vanished with no result | Orphaned task GC'd | Are you holding a reference / using TaskGroup? |
| Error disappeared | Unretrieved task exception | `return_exceptions=True` or TaskGroup |
| Whole batch dies on one failure | Bare `gather` propagating first error | `return_exceptions=True` |
| Hang with no CPU use | Deadlock / awaiting something never set | `all_tasks()` + `print_stack()` |
| Intermittent RuntimeError about event loop | Loop reused across threads, or `asyncio.run` nested | One loop per thread; `get_running_loop()` |

The mental model to keep: **in Java you debug threads (dumps, pool metrics, contention); in asyncio you debug the single loop (what's blocking it, what you forgot to await, and which tasks are orphaned).**

---

## Part 5.7 — Pydantic & Data Modeling Depth

Pydantic is the other pillar of your eval work and a CarGurus standard — it's how you validate and (de)serialize at every trust boundary (API bodies, config, LLM output). The one-line frame for a Java engineer: **Pydantic ≈ Jackson + Bean Validation + Lombok records in one, but validation runs at construction time, and v2's core is compiled Rust — so it's fast enough to sit in the hot path.**

### 5.7.1 The mental model

A `BaseModel` subclass declares fields with type hints; instantiating it **parses, coerces, and validates** the input, raising `ValidationError` on failure. Unlike your Part 1 lesson that "type hints are just annotations Pyright checks," Pydantic **actually enforces the types at runtime** — it's the one place in Python where a type hint has teeth.

```python
from pydantic import BaseModel, Field, field_validator, ValidationError

class EvalConfig(BaseModel):
    dataset: str
    parallelism: int = Field(default=8, ge=1, le=64)     # constraint like @Min/@Max
    tags: list[str] = Field(default_factory=list)         # never a mutable default!
    threshold: float = 0.7

    @field_validator("dataset")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("dataset must not be blank")
        return v

cfg = EvalConfig(dataset="golden", parallelism="16")   # "16" str → coerced to int 16
EvalConfig(dataset="x", parallelism=999)               # raises ValidationError (le=64)
```

Note `default_factory=list` — Pydantic protects you from the mutable-default trap, but get in the habit anyway.

### 5.7.2 Coercion vs strict mode (a common gotcha)

By default Pydantic is **lax**: it coerces `"16"` → `16`, `1` → `True`, etc. — convenient for HTTP query params, dangerous for LLM output you want to trust exactly. Use strict typing where correctness matters:

```python
from pydantic import StrictInt, StrictBool
class Score(BaseModel):
    value: float
    passed: StrictBool        # rejects 1/0/"true"; must be a real bool
    model_config = {"strict": True}   # or make the whole model strict
```

### 5.7.3 Validators: field-level and model-level

```python
from pydantic import model_validator

class CaseResult(BaseModel):
    case_id: str
    latency_ms: float
    error: str | None = None
    passed: bool

    @model_validator(mode="after")
    def check_consistency(self):
        if self.error and self.passed:          # cross-field invariant
            raise ValueError("a failed case cannot also be passed")
        return self
```

`mode="before"` validators see raw input (good for normalizing/reshaping messy LLM JSON before typing); `mode="after"` validators see the fully-typed model (good for cross-field invariants). This is your `@AssertTrue`/custom-validator layer, but colocated with the model.

### 5.7.4 Serialization, aliases, and computed fields

```python
from pydantic import computed_field, ConfigDict

class Span(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    span_id: str = Field(alias="spanId")          # accept camelCase JSON, use snake_case in Python
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @computed_field                                # serialized like a field, computed on the fly
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

s = Span.model_validate_json('{"spanId": "abc", "prompt_tokens": 10}')
s.model_dump()                       # {'span_id': 'abc', ..., 'total_tokens': 10}
s.model_dump(by_alias=True)          # {'spanId': 'abc', ...}  ← for the wire
s.model_dump_json(exclude_none=True) # JSON string, drop null fields
```

Key methods (the Jackson `ObjectMapper` equivalents): `model_validate(dict)`, `model_validate_json(str)`, `model_dump()` (→ dict), `model_dump_json()` (→ str). Aliases with `populate_by_name=True` let you speak camelCase on the wire (matching the Java services you interoperate with) and snake_case in Python — exactly what the listings-comparison harness does when generating models from the Java schema.

### 5.7.5 Discriminated (tagged) unions — the trace-modeling power tool

This is the feature that makes agent event/trace modeling clean. A discriminated union lets Pydantic pick the right subtype from a tag field in O(1), instead of trying each — perfect for a heterogeneous stream of trace spans:

```python
from typing import Literal, Annotated, Union
from pydantic import Field, TypeAdapter

class LLMSpan(BaseModel):
    kind: Literal["llm"]
    model: str
    prompt_tokens: int

class ToolSpan(BaseModel):
    kind: Literal["tool"]
    tool_name: str
    args: dict

Span = Annotated[Union[LLMSpan, ToolSpan], Field(discriminator="kind")]

adapter = TypeAdapter(list[Span])
spans = adapter.validate_json(raw_jsonl_array)   # each row → correct class by "kind"
```

This directly upgrades the trace model from Part 6.2 — instead of one `Span` with an `attributes` grab-bag, you get typed, validated variants with a fast discriminator. A strong senior candidate reaches for this when asked to model heterogeneous events.

### 5.7.6 Config via pydantic-settings (12-factor config)

For SDK/service config, `pydantic-settings` reads and validates from environment variables — the typed, validated replacement for scattered `os.getenv` calls (think Spring `@ConfigurationProperties`):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str                    # required — fails fast at startup if missing
    eval_concurrency: int = 16
    model_config = {"env_prefix": "EVAL_"} # reads EVAL_OPENAI_API_KEY, EVAL_EVAL_CONCURRENCY

settings = Settings()                       # validates the environment on construction
```

### 5.7.7 Choosing the right modeling tool

| Tool | Validation? | Use when | Java analog |
|---|---|---|---|
| **Pydantic `BaseModel`** | Yes (runtime) | Trust boundaries: API I/O, config, LLM/JSON parsing | Jackson + Bean Validation |
| **`@dataclass`** | No (hints only) | Internal value objects you fully control | record / POJO |
| **`NamedTuple`** | No | Tiny immutable tuples with named fields, hashable keys | small immutable record |
| **`TypedDict`** | No (static only) | Typing an existing plain-dict shape without wrapping it | `Map` with a known shape |

Rule of thumb, matching the CarGurus standard: **Pydantic at every boundary, `@dataclass` inside.** Don't pay Pydantic's validation cost on hot internal objects that never touch untrusted input; don't skip it on anything crossing a trust boundary.

### 5.7.8 Performance & the Rust core

Pydantic v2's validation core (`pydantic-core`) is compiled Rust — this is the Part 1.5 "drop into C/Rust for the hot path" principle in action, and it's why Pydantic is fast enough to validate every request and every LLM response without becoming the bottleneck. Two practical notes: `model_validate(data)` is the fast path for parsing known-good dicts; and for validating a large list against a schema, build one `TypeAdapter(list[Model])` and reuse it rather than constructing models in a Python loop.

### 5.7.9 Interviewer probes

* *"When would you use a dataclass vs Pydantic vs a plain dict?"* — Strong answer names the trust-boundary rule and the runtime-validation cost tradeoff, not just "Pydantic is nicer."
* *"How would you model a stream of heterogeneous agent events?"* — Look for discriminated unions / tagged variants, not one god-object with optional fields everywhere.
* *"Your LLM returns JSON that sometimes has extra or missing fields. How do you handle it?"* — Look for `extra="forbid"` vs `"ignore"`, `before` validators to normalize, and defaults/`Optional` for missing fields.
* *"Where does validation run, and what does that cost?"* — Strong answer knows it's at construction, that v2 is Rust-backed, and that you reuse `TypeAdapter` for bulk.

The takeaway to anchor: **Pydantic is where Python's optional type hints become enforced contracts — use it as the validated shell around your system, keep the interior in cheap dataclasses, and lean on discriminated unions for the heterogeneous event/trace data at the heart of eval work.**

---

## Part 6 — The Three Design Questions: Full Worked Answers

These are the questions you'll both answer and ask. Each includes a model answer with runnable code and a rubric for grading candidates.

### 6.1 "Design an SDK for evaluating agent behavior across multiple runs"

**Framing.** An eval SDK's job is to take a **dataset** of cases, run an **agent (or system under test)** against each case (often multiple times to measure non-determinism), apply one or more **scorers**, and aggregate **results** across runs — with concurrency, retries, and observability built in. Design it as a library (package layout, per CarGurus standards) with clean extension points.

**Core API design principles:**
* Pydantic models at all data boundaries for validation + serialization.
* Scorers are a `Protocol` — users plug in their own without inheritance.
* Async-first for I/O-bound LLM calls, with bounded concurrency.
* "Multiple runs" is a first-class concept: run each case `n` times to measure variance/flakiness.

```python
# eval_sdk/models.py
from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any, Protocol

class EvalCase(BaseModel):
    id: str
    inputs: dict[str, Any]
    expected: dict[str, Any] | None = None
    metadata: dict[str, Any] = {}

class AgentOutput(BaseModel):
    text: str
    tool_calls: list[dict[str, Any]] = []
    raw: dict[str, Any] = {}

class Score(BaseModel):
    name: str
    value: float                       # normalize to 0.0–1.0 by convention
    passed: bool
    detail: str | None = None

class CaseResult(BaseModel):
    case_id: str
    run_index: int                     # which of the N repeats
    output: AgentOutput | None = None
    scores: list[Score] = []
    latency_ms: float = 0.0
    error: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Agent(Protocol):                  # what a user plugs in as the system-under-test
    async def run(self, case: EvalCase) -> AgentOutput: ...

class Scorer(Protocol):                 # structural interface — no subclassing required
    name: str
    async def score(self, case: EvalCase, output: AgentOutput) -> Score: ...
```

```python
# eval_sdk/runner.py
import asyncio, time
from collections.abc import Sequence
from .models import Agent, Scorer, EvalCase, CaseResult

class EvalRunner:
    def __init__(
        self,
        agent: Agent,
        scorers: Sequence[Scorer],
        *,
        runs_per_case: int = 1,        # repeat each case to measure non-determinism
        concurrency: int = 8,          # bound in-flight LLM calls
    ) -> None:
        self._agent = agent
        self._scorers = scorers
        self._runs_per_case = runs_per_case
        self._sem = asyncio.Semaphore(concurrency)

    async def _run_once(self, case: EvalCase, run_index: int) -> CaseResult:
        async with self._sem:          # backpressure: never exceed `concurrency`
            start = time.perf_counter()
            try:
                output = await self._agent.run(case)
                scores = await asyncio.gather(
                    *(s.score(case, output) for s in self._scorers)
                )
                return CaseResult(
                    case_id=case.id, run_index=run_index, output=output,
                    scores=list(scores),
                    latency_ms=(time.perf_counter() - start) * 1000,
                )
            except Exception as e:      # isolate failures — one bad case never sinks the run
                return CaseResult(
                    case_id=case.id, run_index=run_index, error=repr(e),
                    latency_ms=(time.perf_counter() - start) * 1000,
                )

    async def evaluate(self, dataset: Sequence[EvalCase]) -> list[CaseResult]:
        tasks = [
            self._run_once(case, i)
            for case in dataset
            for i in range(self._runs_per_case)
        ]
        return await asyncio.gather(*tasks)
```

```python
# eval_sdk/report.py — aggregation across runs
from collections import defaultdict
from statistics import mean, pstdev
from .models import CaseResult

def summarize(results: list[CaseResult]) -> dict:
    by_scorer: dict[str, list[float]] = defaultdict(list)
    for r in results:
        for s in r.scores:
            by_scorer[s.name].append(s.value)

    # per-case consistency across repeated runs (non-determinism signal)
    by_case: dict[str, list[float]] = defaultdict(list)
    for r in results:
        agg = mean(s.value for s in r.scores) if r.scores else 0.0
        by_case[r.case_id].append(agg)

    return {
        "n_results": len(results),
        "error_rate": mean(1.0 if r.error else 0.0 for r in results) if results else 0.0,
        "p50_latency_ms": sorted(r.latency_ms for r in results)[len(results)//2] if results else 0.0,
        "scorers": {
            name: {"mean": mean(vals), "min": min(vals), "max": max(vals)}
            for name, vals in by_scorer.items()
        },
        "flakiness": {                 # stdev>0 means the agent gave inconsistent scores
            cid: pstdev(vals) for cid, vals in by_case.items() if len(vals) > 1
        },
    }
```

```python
# usage — reads like the public API a teammate would consume
runner = EvalRunner(agent=my_agent, scorers=[ExactMatch(), LLMJudge()],
                    runs_per_case=5, concurrency=16)
results = await runner.evaluate(dataset)
print(summarize(results))
```

**Design points to call out (and to look for in candidates):**
* **Extensibility via `Protocol`:** anyone can add a scorer or swap the agent without touching the runner — no inheritance required.
* **Bounded concurrency** with a semaphore respects provider rate limits — the async equivalent of a connection pool / circuit breaker, squarely in your observability wheelhouse.
* **Failure isolation:** exceptions become data (`error` field), so one bad case never aborts a 5,000-case run.
* **"Multiple runs" is first-class:** `runs_per_case` + the flakiness metric directly answer "across multiple runs."
* **Boundaries validated** by Pydantic; results are trivially serializable to JSON/JSONL for storage and dashboards.
* **Production alignment:** wrap `evaluate()` in a FastAPI endpoint, use HTTPX inside the agent, publish Prometheus metrics via `python-common`. A managed alternative used at CarGurus is the OpenAI Evals API, as in the listings-comparison harness.

**Rubric.** *Strong (IC4):* clean Protocol-based extension points, async with backpressure, failure isolation, multi-run/variance handling, testability, mentions observability and rate limits. *Solid (IC3):* working async runner, Pydantic models, aggregation, some extensibility. *Junior (IC2):* sequential runner, dicts instead of models, but correct scoring/aggregation logic.

---

### 6.2 "How would you model agent execution traces for analysis?"

**Framing.** An agent execution isn't one call — it's a **tree/DAG of spans**: the top-level run, LLM calls, tool invocations, retriever lookups, and sub-agent branches. To analyze it (latency breakdowns, token cost, failure attribution, tool-usage patterns), model it as **hierarchical spans with a shared trace ID**, which also maps cleanly onto OpenTelemetry → Honeycomb, the CarGurus tracing standard.

```python
# traces/model.py
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any
import uuid

class SpanKind(str, Enum):
    AGENT = "agent"          # a reasoning step / agent turn
    LLM = "llm"              # a model call
    TOOL = "tool"            # a tool / function call
    RETRIEVER = "retriever"  # RAG lookup
    ROUTER = "router"        # intent classification / routing decision

class SpanStatus(str, Enum):
    OK = "ok"
    ERROR = "error"

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    @property
    def total(self) -> int:
        return self.prompt_tokens + self.completion_tokens

class Span(BaseModel):
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    parent_id: str | None = None          # None => root span
    trace_id: str                          # ties every span in one execution together
    name: str
    kind: SpanKind
    status: SpanStatus = SpanStatus.OK
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime | None = None
    inputs: dict[str, Any] = {}
    outputs: dict[str, Any] = {}
    tokens: TokenUsage | None = None
    error: str | None = None
    attributes: dict[str, Any] = {}       # model name, temperature, tool args, etc.

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000

class Trace(BaseModel):
    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    case_id: str | None = None            # links a trace back to an eval case
    spans: list[Span] = []                # flat list; tree rebuilt via parent_id

    def add(self, span: Span) -> None:
        self.spans.append(span)

    def children(self, parent_id: str | None) -> list[Span]:
        return [s for s in self.spans if s.parent_id == parent_id]

    def root(self) -> Span | None:
        roots = self.children(None)
        return roots[0] if roots else None
```

**Why a flat list with `parent_id` rather than nested objects?** It serializes to one JSONL row per span (append-friendly, queryable, streamable), reconstructs into a tree on demand, and matches how tracing backends store data. This is a classic design-tradeoff talking point.

```python
# traces/analysis.py — the "for analysis" part
from collections import defaultdict
from .model import Trace, SpanKind

def latency_by_kind(trace: Trace) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for s in trace.spans:
        totals[s.kind.value] += s.duration_ms
    return dict(totals)

def total_tokens(trace: Trace) -> int:
    return sum(s.tokens.total for s in trace.spans if s.tokens)

def tool_call_counts(trace: Trace) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for s in trace.spans:
        if s.kind is SpanKind.TOOL:
            counts[s.name] += 1
    return dict(counts)

def critical_path_ms(trace: Trace) -> float:
    """Longest root-to-leaf duration — where the wall-clock time actually goes."""
    def longest(span_id: str | None) -> float:
        kids = trace.children(span_id)
        here = next((s.duration_ms for s in trace.spans if s.span_id == span_id), 0.0)
        return here + (max((longest(k.span_id) for k in kids), default=0.0))
    root = trace.root()
    return longest(root.span_id) if root else 0.0

def failures(trace: Trace) -> list[tuple[str, str]]:
    return [(s.name, s.error or "") for s in trace.spans if s.status.value == "error"]
```

**Design points to call out:**
* **Hierarchy via `trace_id` + `parent_id`** captures the full agent DAG (LLM → tool → sub-agent) — essential for LangGraph's multi-agent, parallel-branch execution model that Discover V2 targets.
* **Rich per-span attributes** (tokens, model, tool args) enable cost analysis, latency attribution, and tool-usage mining.
* **`case_id` links traces to eval cases**, so the SDK in 6.1 and the trace model here compose: each `CaseResult` can carry a `Trace`.
* **Standards alignment:** this is deliberately shaped like OpenTelemetry spans, so it exports to Honeycomb with minimal glue, and to LangSmith if using LangChain tooling.
* **Critical-path analysis** is exactly the latency-root-cause work you already do — here it's finding the longest path through the span tree instead of profiling a Java call stack.

**Rubric.** *Strong:* hierarchical spans with IDs, rich attributes (tokens/cost/status), flat-storage-vs-tree tradeoff articulated, ties to OTel/observability and to eval cases, thinks about querying at scale. *Solid:* parent/child span model with timing and status. *Junior:* a flat list of "steps" with timestamps but no hierarchy or cost/analysis dimension.

---

### 6.3 "How do you handle async execution in evaluation workflows?"

**Framing.** Eval workloads are **I/O-bound** — dominated by LLM API calls and internal service calls, not CPU. This is the sweet spot for Python's `asyncio`: a single-threaded cooperative event loop that keeps thousands of calls in flight without threads. The GIL is not a bottleneck here because you're waiting on the network, not burning CPU — the same reasoning behind Discover V2 choosing asyncio + LangGraph's native async node execution to avoid "the blocking-thread bottleneck."

**The core building blocks:**

```python
import asyncio
import httpx   # async-capable HTTP client — the CarGurus standard, not `requests`
```

**1. Bounded concurrency with a semaphore (the #1 pattern):**

```python
async def run_all(cases: list[EvalCase], agent, *, limit: int = 16) -> list[CaseResult]:
    sem = asyncio.Semaphore(limit)          # never more than `limit` in flight
    async def guarded(case):
        async with sem:
            return await agent.run(case)
    return await asyncio.gather(*(guarded(c) for c in cases))
```

Unbounded `gather` over 5,000 cases would fire 5,000 simultaneous requests and get you rate-limited or OOM'd. The semaphore is your concurrency governor — the async analog of a bounded thread pool or connection pool.

**2. Timeouts and cancellation:**

```python
async def with_timeout(coro, seconds: float):
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        return CaseResult(case_id="?", run_index=0, error="timeout")
```

**3. Retries with backoff for flaky provider calls:**

```python
async def call_with_retry(client: httpx.AsyncClient, url: str, *, retries: int = 3):
    for attempt in range(retries):
        try:
            resp = await client.post(url, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPError, httpx.TimeoutException):
            if attempt == retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)   # exponential backoff
```

**4. Shared async client (connection pooling — your wheelhouse):**

```python
async def evaluate_dataset(cases: list[EvalCase]) -> list[dict]:
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits) as client:   # one pooled client, reused
        sem = asyncio.Semaphore(16)
        async def one(case):
            async with sem:
                return await call_with_retry(client, "/agent/run")
        return await asyncio.gather(*(one(c) for c in cases), return_exceptions=True)
```

**5. Processing results as they finish (`as_completed`) for streaming progress:**

```python
async def stream_results(coros):
    for fut in asyncio.as_completed(coros):
        result = await fut
        yield result                     # e.g. update a progress bar / write JSONL incrementally
```

**Critical gotchas to raise (and to grade candidates on):**
* **Never call blocking code directly in async** — a synchronous `time.sleep()`, `requests.get()`, or heavy CPU work freezes the entire event loop. Use `await asyncio.sleep()`, HTTPX async, and offload CPU/blocking work with `asyncio.to_thread(...)`.
* **`return_exceptions=True`** in `gather` so one failure doesn't cancel the batch (failure isolation, echoing 6.1).
* **The GIL** means asyncio gives you concurrency, not CPU parallelism — correct for I/O-bound evals; for CPU-bound scoring (e.g., local embedding models), use `multiprocessing` or `to_thread`.
* **Structured concurrency** (Python 3.11+ `asyncio.TaskGroup`) is the modern alternative to bare `gather` with cleaner cancellation semantics — a nice signal of current knowledge.

```python
# Modern structured-concurrency form (3.11+)
async def evaluate(cases, agent):
    results: list[CaseResult] = []
    async with asyncio.TaskGroup() as tg:      # all tasks awaited; failures propagate cleanly
        for c in cases:
            tg.create_task(_run_and_collect(c, agent, results))
    return results
```

**Rubric.** *Strong (IC4):* correctly identifies I/O-bound → asyncio, bounded concurrency via semaphore, timeouts/retries/backoff, shared pooled client, failure isolation, GIL nuance, and blocking-in-async pitfalls; may mention TaskGroup. *Solid (IC3):* uses `async`/`await` + `gather`, understands non-blocking I/O, adds basic concurrency limits. *Junior (IC2):* knows `async`/`await` syntax and `gather` but misses concurrency bounding, blocking pitfalls, or the GIL reasoning.

---

## Quick Reference: Java Habits to Unlearn

* Stop writing `for (int i = 0; i < n; i++)` — use `for x in xs`, `enumerate`, `zip`, comprehensions.
* Stop reaching for getters/setters and inheritance — use dataclasses/Pydantic and `Protocol`.
* Stop treating type hints as a compiler gate — they're for Pyright and readers.
* Stop using threads for I/O concurrency — use `asyncio` with a semaphore.
* Stop managing dependencies by hand — `uv` + committed `uv.lock`.
* Stop using `requests` — use HTTPX (async-capable).
* Let Ruff win every formatting argument; let Pyright catch type mistakes in CI.


---

## Sources

- [Python Standards for Production Services](https://cargurus.atlassian.net/wiki/spaces/AI/pages/5080514717)
- [Python Enablement Project](https://cargurus.atlassian.net/wiki/spaces/AI/pages/5098143770)
- [Discover V2 Motivation and Milestones](https://cargurus.atlassian.net/wiki/spaces/SD/pages/6090916063)
- [Python Standards for Production Services](https://cargurus.atlassian.net/wiki/spaces/AI/pages/5080514717)
- [Listings Comparison Quality Evaluation](https://code.cargurus.com/cargurus-eng/listings-comparison/blob/main/src/test/python/README.md)
- [Python Quick Start](https://cargurus.360learning.com/course/play/65f01ccbeab372e0e63d7357)
- [Complete Guide to Python Fundamentals for MLOps](https://cargurus.360learning.com/course/play/66f7ab7e7e8e860eef8aca73)
- [DEC-1656 VDP Consumer AI Chatbot Backend](https://cargurus.atlassian.net/wiki/spaces/DEC/pages/5514166294)
- [Software Development Engineering - Domain Expertise Interview Question Guide](https://cargurus.atlassian.net/wiki/spaces/TA/pages/3871211586)
- [Eng Technical Interview Questions Inventory](https://docs.google.com/spreadsheets/d/11OO4jVdJXTfm_zZxjuKJqPHpj-Sj7y4Z0e8opIUUlo0)
- [Exploring SocialTalent](https://cargurus.atlassian.net/wiki/spaces/PT/pages/4158423404)
- [Eng Technical Interview Questions Inventory](https://docs.google.com/spreadsheets/d/11OO4jVdJXTfm_zZxjuKJqPHpj-Sj7y4Z0e8opIUUlo0)
- [Why Python?](https://cargurus.atlassian.net/wiki/spaces/AI/pages/5414846565)
