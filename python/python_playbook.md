
# Python Reference — Data Structures, Concurrency & Pitfalls

> Quick-reference for Python-specific knowledge in staff+ SWE interviews. The Python counterpart to the Java playbook.

---

## Table of Contents

1. Common Python Pitfalls
2. Data Structures Reference (dict methods, sorted structures, deque, heapq, bisect, Trie)
3. Python Concurrency (threading, asyncio, multiprocessing, the GIL)

---

## Common Python Pitfalls

Pre-flight checklist for interview coding. Review before each practice session until automatic.

### Equality & Identity

| Trap | Wrong | Right | Why |
|---|---|---|---|
| Value vs identity | `x is 5` / `s is "a"` | `x == 5` / `s == "a"` | `is` compares identity; only use for `None`/`True`/`False` |
| Small-int caching | relying on `a is b` for ints | `a == b` | Ints −5..256 are cached, so `is` may be `True` there and `False` for `257` (the `Integer` cache analog) |
| Float equality | `0.1 + 0.2 == 0.3` | `math.isclose(a, b)` | Binary floating point — `0.1+0.2 == 0.30000000000000004` |
| None check | `if x == None` | `if x is None` | `None` is a singleton; `is` is correct and faster |

### Numbers (big differences from Java)

| Trap | Java behavior | Python behavior |
|---|---|---|
| Integer overflow | wraps at 32/64 bits | **No overflow — ints are arbitrary precision.** No `long`, no `(lo+hi)/2` overflow. Simplifies binary search. |
| Integer division | `7 / 2 == 3` | `7 / 2 == 3.5` (true division); use `7 // 2 == 3` for floor |
| Floor div with negatives | `-7 / 2 == -3` (truncates toward 0) | `-7 // 2 == -4` (**floors toward −∞**) — a common bug |
| Modulo with negatives | `-3 % 5 == -3` | `-3 % 5 == 2` (**already non-negative**) — no `((x%k)+k)%k` needed |
| Infinity sentinel | `Integer.MAX_VALUE` | `float("inf")` / `float("-inf")` — cleaner for min/max init |

### Mutable Defaults & Aliasing

```python
# WRONG — default list created ONCE at def time, shared across calls
def add(x, items=[]):
    items.append(x); return items
add(1); add(2)   # [1, 2] — shared state bug!

# RIGHT
def add(x, items=None):
    items = items if items is not None else []
    items.append(x); return items
```

```python
# 2D array init trap — the inner list is shared by reference
grid = [[0] * 3] * 3        # WRONG: all 3 rows are the SAME list
grid[0][0] = 1               # mutates every row → [[1,0,0],[1,0,0],[1,0,0]]

grid = [[0] * 3 for _ in range(3)]   # RIGHT: independent rows
```

```python
b = a                # NOT a copy — same object
b = a[:]             # shallow copy of a list
b = a.copy()         # shallow copy (list/dict/set)
import copy; b = copy.deepcopy(a)    # deep copy for nested structures
```

### Collections

| Trap | What Happens | Fix |
|---|---|---|
| `list.pop(0)` | **O(n)** — shifts all elements | Use `collections.deque` + `popleft()` (O(1)) |
| `x in a_list` in a loop | O(n) each → O(n²) | Convert to `set` for O(1) membership |
| Modifying list/dict while iterating | Skipped elements or `RuntimeError` (dict) | Iterate a copy `for x in list(d):` or build a new collection |
| `dict` ordering | Insertion-ordered (3.7+), **not sorted** | Sort explicitly, or use `sorted(d.items())` |
| `set`/`dict` ordering | sets have **no** order guarantee | Don't rely on iteration order of a `set` |
| `sorted` vs `.sort()` | `.sort()` returns `None` | `x = lst.sort()` is a bug; use `sorted(lst)` for a new list |

### Sorting

```python
# No Comparator/compareTo — pass a key function
data.sort(key=lambda r: (r.score, r.name))     # multi-key, ascending
data.sort(key=lambda r: r.score, reverse=True) # descending

# Sort by one field descending, another ascending — negate numeric key
data.sort(key=lambda r: (-r.score, r.name))

# Legacy cmp function (rarely needed):
from functools import cmp_to_key
data.sort(key=cmp_to_key(my_cmp))
```

Python's sort is **stable** Timsort, O(n log n) — same guarantee as Java's `Collections.sort`.

### Strings

```python
# WRONG — O(n²): strings are immutable, each += builds a new string
s = ""
for part in parts: s += part

# RIGHT — the StringBuilder equivalent
s = "".join(parts)
```

* `s.split(".")` — **not** regex (unlike Java); splits on literal `.`. Use `re.split(r"\.", s)` for regex.
* `s[::-1]` reverses; `s[a:b]` slices (empty if `a==b`, never errors on out-of-range).
* No `char` type — iterating a string yields 1-char strings; `ord(c)`/`chr(n)` convert to/from code points.

### Slicing & Indexing

| Idiom | Meaning |
|---|---|
| `a[-1]` | last element (negative indexing) |
| `a[a:b]` | out-of-range bounds are clamped, never throw |
| `a[::-1]` | reversed copy |
| `a[::2]` | every other element |
| `a[:] = [...]` | replace contents in place (keeps same object) |

### Recursion & Scope

* **Default recursion limit is 1000** — deep DFS on a large graph/tree can hit `RecursionError`. Either convert to an explicit stack or `import sys; sys.setrecursionlimit(10**6)` (interview: mention it).
* **Closures capture by reference (late binding):**

```python
# WRONG — all lambdas see the final i
fns = [lambda: i for i in range(3)]   # all return 2
# RIGHT — bind now via default arg
fns = [lambda i=i: i for i in range(3)]
```

* `nonlocal` to mutate an enclosing function's variable; `global` for module scope. A common backtracking pattern uses a `nonlocal` counter or a mutable container (`result = []`) closed over by the helper.

### Truthiness

Empty containers, `0`, `0.0`, `""`, and `None` are falsy. `if not items:` is the idiomatic empty check. Beware: `if x:` treats `0` and `""` as absent — use `if x is not None:` when `0`/`""` are valid values.

### Interview-Specific

| Situation | Rule |
|---|---|
| Need a sorted map/set | Python has **no built-in `TreeMap`/`TreeSet`** — see Data Structures below |
| Tuple as dict key | Works (tuples are hashable); great for `(row, col)` visited sets / memo keys |
| Memoization | `@functools.lru_cache(maxsize=None)` on a pure function — but confirm the interviewer wants it vs. hand-rolled |
| Multiple return values | Return a tuple; unpack with `a, b = f()` |
| Swapping | `a, b = b, a` — no temp variable |

---

## Data Structures Reference

### dict Utility Methods

| Method | Use Case |
|---|---|
| `d.get(k, default)` | Safe read; frequency: `d[c] = d.get(c, 0) + 1` |
| `d.setdefault(k, default)` | Return existing or insert default (lazy init) |
| `collections.defaultdict(list)` | Auto-init missing keys — build adjacency lists |
| `collections.Counter(iterable)` | Frequency map + `.most_common(k)` |
| `d.items()` / `.keys()` / `.values()` | Iterate views (live, no copy) |
| `d.pop(k, default)` | Remove + return, no `KeyError` if default given |
| `dict1 | dict2` (3.9+) | Merge dicts |

```python
from collections import defaultdict, Counter

# Frequency — three ways
freq = {}
freq[c] = freq.get(c, 0) + 1
freq = Counter(chars)               # cleanest; freq['a'] == count
freq = defaultdict(int); freq[c] += 1

# Adjacency list — no null checks
graph = defaultdict(list)
graph[u].append(v)

# Group anagrams (LC 49) — sorted string as key
groups = defaultdict(list)
for s in strs:
    groups["".join(sorted(s))].append(s)
```

`defaultdict` vs `setdefault` vs `Counter`: `defaultdict(factory)` auto-creates on *any* missing-key access; `setdefault(k, v)` inserts only if absent (works on a plain dict); `Counter` is a `dict` subclass specialized for counting with `.most_common()`, arithmetic (`c1 + c2`), and `most_common` top-K.

### The Missing TreeMap: sorted structures in Python

**Python's standard library has no balanced BST / `TreeMap` / `TreeSet`.** Options in an interview:

* **`bisect`** on a sorted `list` — O(log n) search, but **O(n) insert/delete** (list shift). Fine when inserts are rare or the list is built once then queried.
* **`sortedcontainers`** (`SortedList`, `SortedDict`, `SortedSet`) — third-party, O(log n) add/remove/lookup, has `bisect_left`, `irange`, `peekitem`. **Not in the stdlib**, so state the assumption: "I'd use `sortedcontainers.SortedList`, which most eval/prod environments have; if restricted to stdlib I'd use `bisect` on a list or a heap." Interviewers at Python shops generally accept it.
* **`heapq`** — if you only need repeated min/max extraction (not arbitrary ordered queries).

```python
import bisect
arr = [1, 3, 5, 7]
i = bisect.bisect_left(arr, 5)     # 2 — leftmost index where 5 fits (O(log n))
bisect.insort(arr, 4)              # insert keeping sorted order (O(n) due to shift)
# floor/ceiling:
#   ceiling(x) = arr[bisect_left(arr, x)]
#   floor(x)   = arr[bisect_right(arr, x) - 1]
```

### collections.deque

O(1) at both ends — the `ArrayDeque` equivalent. Use for **queue (BFS)** and **stack**.

```python
from collections import deque
q = deque([1, 2, 3])
q.append(4); q.appendleft(0)     # both O(1)
q.pop(); q.popleft()             # both O(1)
q = deque(maxlen=300)            # ring buffer — auto-evicts oldest (LC 362 Hit Counter)
```

Never use `list.pop(0)` for a queue — it's O(n).

### heapq (min-heap on a list)

Python's `PriorityQueue` equivalent. **Min-heap only** — negate for max-heap.

```python
import heapq
h = []
heapq.heappush(h, 5)             # O(log n)
smallest = heapq.heappop(h)      # O(log n)
smallest = h[0]                  # peek, O(1)
heapq.heapify(nums)              # O(n) in place

# Max-heap: push negatives
heapq.heappush(h, -x); largest = -heapq.heappop(h)

# Priority via tuple (sorts by first element, then second, ...)
heapq.heappush(h, (dist, node))
# Tie-break with an insertion counter to avoid comparing unorderable payloads:
heapq.heappush(h, (priority, next(counter), task))

# Top-K helpers
heapq.nlargest(k, nums)          # or nsmallest
heapq.nlargest(k, freq, key=freq.get)   # top-k keys by value
```

Gotchas: not sorted when iterated; `remove` is O(n) (no efficient decrease-key — push a new entry and lazily skip stale ones); tuples with equal first element will try to compare the second, so add a counter for non-orderable payloads.

### Trie (Prefix Tree)

Dict-based is the idiomatic Python form (no fixed 26-array needed):

```python
class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True
    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end
```

`is_end` is critical (without it "app" matches when only "apple" was inserted). Insert/search/prefix are O(L). Trie + DFS solves LC 212 (Word Search II); wildcard DFS branching at `.` solves LC 211.

### Data Structure Ordering Traps

| Structure | `[0]`/pop sorted? | Iteration sorted? | Note |
|---|---|---|---|
| `heapq` (list) | Yes (`h[0]` = min) | **No** | Heap array, not sorted |
| `dict` / `set` | N/A | dict = insertion; **set = none** | Never assume sorted |
| `collections.OrderedDict` | N/A | Insertion order | `move_to_end`, `popitem(last=)` — handy for LRU |
| `deque` | N/A | Insertion order | FIFO or LIFO by which end you use |
| `sortedcontainers.SortedList` | Yes | **Yes** | Third-party; the real `TreeSet` replacement |

### Quick Comparison

| | `bisect`+list / SortedList | `deque` | `heapq` |
|---|---|---|---|
| Order | Sorted | Insertion | Heap (min) |
| Min access | O(1) / O(log n) | O(1) ends | O(1) peek |
| Arbitrary remove | O(n) / O(log n) | O(n) | O(n) |
| Neighbor query | O(log n) via bisect | N/A | N/A |
| Best for | Sorted access + range | Stack / Queue / BFS | Pure min/max stream, top-K |

---

## Python Concurrency

Python has **three** concurrency models. Picking the right one is the interview signal.

| Model | Parallelism? | Best for | Module |
|---|---|---|---|
| **Threading** | No (GIL serializes bytecode) | I/O-bound with blocking libs | `threading`, `concurrent.futures.ThreadPoolExecutor` |
| **asyncio** | No (single thread, cooperative) | I/O-bound with async libs (LLM/API calls) | `asyncio` |
| **Multiprocessing** | **Yes** (separate interpreters) | CPU-bound work | `multiprocessing`, `ProcessPoolExecutor` |

**The GIL (Global Interpreter Lock):** only one thread executes Python bytecode at a time, so threads give **concurrency, not CPU parallelism**. For CPU-bound work use processes; for I/O-bound work use threads or asyncio. (Python 3.13 ships an experimental free-threaded no-GIL build, but assume the GIL in interviews.)

### threading primitives (map to the Java table)

| Python | Java analog | Notes |
|---|---|---|
| `threading.Lock` | `synchronized` / `ReentrantLock` | Basic mutual exclusion; use as `with lock:` |
| `threading.RLock` | reentrant lock | Same thread can re-acquire |
| `threading.Semaphore(n)` | `Semaphore` | `acquire`/`release`; `with sem:` |
| `threading.Condition` | `Condition` + wait/notify | `wait()` / `notify()` / `notify_all()` inside `with cond:` |
| `threading.Event` | latch-ish flag | `set()`/`wait()`/`clear()` — one flag many waiters |
| `threading.Barrier(n)` | `CyclicBarrier` | Reusable; all `n` wait then release together |
| `queue.Queue` | `BlockingQueue` | Thread-safe blocking `put`/`get` — don't roll your own |
| no `volatile` | `volatile` | The GIL makes single ops atomic-ish; use `Lock` for compound ops |

```python
import threading

lock = threading.Lock()
with lock:               # ALWAYS prefer context manager over lock.acquire()/release()
    critical_section()

# Condition — producer/consumer (use while, not if, for the predicate)
cond = threading.Condition()
def consume():
    with cond:
        while not queue:
            cond.wait()          # releases lock, suspends
        item = queue.popleft()
    return item
def produce(x):
    with cond:
        queue.append(x)
        cond.notify()            # wake one waiter
```

### concurrent.futures (the `ExecutorService` / `CompletableFuture` analog)

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as pool:   # threads: I/O-bound
    futures = [pool.submit(fetch, url) for url in urls]
    for fut in as_completed(futures):             # process as they finish
        result = fut.result()                     # re-raises exceptions here

with ProcessPoolExecutor() as pool:               # processes: CPU-bound
    results = list(pool.map(heavy_cpu_fn, inputs))
```

`Future.result(timeout=)` blocks (like Java `get`); `as_completed` yields in completion order; `pool.map` preserves input order.

### asyncio (the production model for LLM/eval work)

```python
import asyncio

# Bounded concurrency — the #1 pattern (async semaphore = connection pool)
async def run_all(items, limit=16):
    sem = asyncio.Semaphore(limit)
    async def guarded(x):
        async with sem:
            return await do_io(x)
    return await asyncio.gather(*(guarded(x) for x in items),
                                return_exceptions=True)   # isolate failures

# Structured concurrency (3.11+): cleaner cancellation than gather
async def main(items):
    async with asyncio.TaskGroup() as tg:
        for x in items:
            tg.create_task(do_io(x))

# asyncio also has Lock, Semaphore, Event, Queue — same names, awaitable versions
```

**Never call blocking code inside a coroutine** (`time.sleep`, `requests.get`, heavy CPU) — it freezes the event loop. Use `await asyncio.sleep(...)`, an async client (HTTPX), or offload with `await asyncio.to_thread(fn, ...)`.

### LC concurrency problems in Python

**LC 1188 — Bounded Blocking Queue** (two semaphores, cleanest):

```python
import threading
from collections import deque

class BoundedBlockingQueue:
    def __init__(self, capacity: int):
        self._q = deque()
        self._enq = threading.Semaphore(capacity)  # slots free (starts full)
        self._deq = threading.Semaphore(0)         # items available (starts empty)
        self._lock = threading.Lock()              # protects the deque only
    def enqueue(self, element: int) -> None:
        self._enq.acquire()                        # blocks if full
        with self._lock:
            self._q.append(element)
        self._deq.release()                        # signal: item available
    def dequeue(self) -> int:
        self._deq.acquire()                        # blocks if empty
        with self._lock:
            val = self._q.popleft()
        self._enq.release()                        # signal: slot free
        return val
    def size(self) -> int:
        return len(self._q)
```

**LC 1117 — Building H2O** (semaphores + barrier):

```python
import threading

class H2O:
    def __init__(self):
        self._h = threading.Semaphore(2)
        self._o = threading.Semaphore(1)
        self._barrier = threading.Barrier(3)       # 2H + 1O release together
    def hydrogen(self, releaseHydrogen) -> None:
        self._h.acquire()
        releaseHydrogen()
        self._barrier.wait()
        self._h.release()
    def oxygen(self, releaseOxygen) -> None:
        self._o.acquire()
        releaseOxygen()
        self._barrier.wait()
        self._o.release()
```

**LC 1116 — Print Zero Even Odd** (three semaphores gating turns): use `Semaphore(1)` for zero, `Semaphore(0)` for odd/even; each thread acquires its permit, prints, and releases the next — the canonical turn-passing pattern.

### Deadlock — four conditions (all must hold)

Mutual exclusion, hold-and-wait, no preemption, circular wait. **Prevention:** consistent lock ordering, or `lock.acquire(timeout=...)`. In Python specifically: always release via `with` so an exception can't leak a held lock, and keep critical sections tiny (no I/O while holding a lock).

### Common Pitfalls

* Using `if` instead of `while` for a `Condition` predicate — spurious wakeups.
* `threading` for CPU-bound work — the GIL means no speedup; use `multiprocessing`.
* Blocking calls inside `asyncio` coroutines — freezes the loop.
* Forgetting `return_exceptions=True` in `gather` — one failure cancels the whole batch.
* Rolling your own thread-safe queue instead of `queue.Queue` / `asyncio.Queue`.
* Assuming `+=` / `count++`-style ops are atomic — they're read-modify-write; guard with a `Lock`.
