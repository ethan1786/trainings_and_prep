# Java Reference — Data Structures, Concurrency & Pitfalls

> Quick-reference for Java-specific knowledge in staff+ SWE interviews.

---

## Table of Contents

1. [Common Java Pitfalls](#common-java-pitfalls)
2. [Data Structures Reference](#data-structures-reference)
   - Map utility methods, TreeMap, ArrayDeque, PriorityQueue, Trie
3. [Java Concurrency](#java-concurrency)
   - synchronized, ReentrantLock, Semaphore, CyclicBarrier
   - volatile, Future/CompletableFuture, concurrent collections, deadlock

---

## Common Java Pitfalls

Pre-flight checklist for interview coding. Review before each practice session until automatic.

### Equality & Comparison

| Trap | Wrong | Right | Why |
|---|---|---|---|
| String comparison | `s1 == s2` | `s1.equals(s2)` | `==` compares references; only works on interned literals |
| Integer comparison (boxed) | `a != b` in comparator | `Integer.compare(a, b)` or `a.equals(b)` | Integer cache only covers -128 to 127; beyond that `==`/`!=` compares references |
| Null-safe equality | `maybeNull.equals("x")` | `"x".equals(maybeNull)` or `Objects.equals(a, b)` | Put known non-null on the left to avoid NPE |

### Comparators

```java
// WRONG — integer overflow for large values
(a, b) -> a - b

// RIGHT
(a, b) -> Integer.compare(a, b)
// or
Comparator.comparingInt(x -> x)
```

`a - b` overflows when `a` and `b` have different signs and large magnitudes. `Integer.compare` is always safe.

### Autoboxing / Unboxing

```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);

// WRONG — may NPE if key not found (unboxing null → NPE)
int val = map.get("missing");

// RIGHT
int val = map.getOrDefault("missing", 0);
// or
Integer val = map.get("missing");
if (val != null) { ... }
```

Any time you assign a `Map.get()` result to a primitive `int`/`long`/`double`, you risk NPE if the key is absent.

### Collections

| Trap | What Happens | Fix |
|---|---|---|
| `Arrays.asList(arr)` on primitives | Returns `List<int[]>` (one element!) | Use `IntStream.of(arr).boxed().toList()` |
| `List.of()` / `Collections.unmodifiableList()` | Immutable — `add()`/`set()` throws | Copy: `new ArrayList<>(List.of(...))` |
| `list.remove(0)` vs `list.remove(Integer.valueOf(0))` | First removes by index, second by value | Be explicit about which overload |
| Modifying collection during iteration | `ConcurrentModificationException` | Use `Iterator.remove()` or collect-then-remove |
| `PriorityQueue` iterator | NOT sorted | Only `peek()`/`poll()` gives min |
| `HashMap` key mutation | Key becomes unreachable if hashCode changes | Use immutable keys (String, Integer) |

### Strings

```java
// WRONG — O(n²) string concatenation in a loop
String s = "";
for (...) s += item;

// RIGHT
StringBuilder sb = new StringBuilder();
for (...) sb.append(item);
```

```java
// substring gotcha — returns empty for equal indices
"abc".substring(1, 1)  // "" (not an error)

// charAt vs codePointAt — for ASCII interviews, charAt is fine
// but be aware it exists for emoji/unicode questions
```

### Array & Index

| Trap | What Happens | Fix |
|---|---|---|
| `new int[n]` default values | All zeros (not -1, not MIN_VALUE) | `Arrays.fill(arr, -1)` if you need a sentinel |
| `int mid = (lo + hi) / 2` | Integer overflow for large lo + hi | `int mid = lo + (hi - lo) / 2` |
| Forgetting `Arrays.sort` mutates | Original array is modified | Clone first if you need the original |
| `int[] copy = arr` | Copies reference, not values | `arr.clone()` or `Arrays.copyOf(arr, arr.length)` |

### Numeric

| Trap | What Happens | Fix |
|---|---|---|
| Integer division truncation | `7 / 2 == 3`, `(3 + 4) / 2.0 == 3.5` | Cast to `double` or use `2.0` |
| `Integer.MIN_VALUE` negation | `-Integer.MIN_VALUE == Integer.MIN_VALUE` (overflow) | Use `long` for absolute values |
| `Math.abs(Integer.MIN_VALUE)` | Returns `Integer.MIN_VALUE` (negative!) | Same — cast to `long` first |
| Modulo with negatives | `(-3) % 5 == -3` in Java | `((x % k) + k) % k` for always-positive |

### Generics & Types

```java
// WRONG — can't create generic arrays
T[] arr = new T[n];

// RIGHT — use ArrayList or cast Object[]
List<T> list = new ArrayList<>();
// or (ugly but works for interview):
T[] arr = (T[]) new Object[n];
```

```java
// WRONG — comparing wrapper types with ==
Integer a = 200, b = 200;
a == b  // false! (outside Integer cache range)

// RIGHT
a.equals(b)  // true
```

### Method Gotchas

| Method | Gotcha |
|---|---|
| `String.split(".")` | `.` is regex — splits everywhere. Use `split("\\.")` |
| `Collections.sort()` | Stable sort (TimSort). Fine for interviews |
| `Arrays.sort(int[])` | Dual-pivot quicksort. `Arrays.sort(Integer[])` uses TimSort |
| `Math.max(a, b)` | Only two args — chain for three: `Math.max(a, Math.max(b, c))` |
| `queue.poll()` | Returns null if empty (no exception). `queue.remove()` throws |
| `stack.pop()` on ArrayDeque | Throws if empty. Check `isEmpty()` first |

### Constructor / Initialization

| Trap | What Happens | Fix |
|---|---|---|
| Accessing field before init | NPE if field is an object (null by default) | Initialize in constructor or at declaration |
| `new PriorityQueue<>(comparator)` | Default capacity 11, resizes automatically | Fine for interviews — don't worry about initial capacity |
| `HashMap` initial capacity | Rehashes at 0.75 load factor | Pre-size if you know the count: `new HashMap<>(n * 4 / 3 + 1)` |

### Interview-Specific

| Situation | Rule |
|---|---|
| Multi-level OOD problems | After finishing each level, scan all existing methods for correctness against the new state |
| Sorted structure for tiebreaking | Specify comparator explicitly — don't assume natural ordering handles ties |
| Return type `List<String>` | `.toList()` returns immutable in Java 16+. Use `.collect(Collectors.toList())` if caller might modify |
| Stream `.sorted()` on `Map.Entry` | Need full type: `Map.Entry.<String, Integer>comparingByValue(...)` |

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

### Data Structure Ordering Traps

**The #1 mistake: assuming iteration order equals sorted order.**

| Structure | `peek()`/`poll()` sorted? | Iterator/for-each sorted? | Gotcha |
|---|---|---|---|
| `PriorityQueue` | Yes (min) | **NO** | Internal array is a heap, not sorted. Iterating gives arbitrary order |
| `TreeMap` / `TreeSet` | Yes (min/max via first/last) | **Yes** | Iterator walks the red-black tree in order |
| `HashMap` / `HashSet` | N/A | **No guarantee** | Could be insertion order, could be anything |
| `LinkedHashMap` | N/A | **Yes — insertion order** | Useful when you need both O(1) lookup and deterministic iteration |
| `ArrayDeque` | N/A | **Yes — insertion order** | FIFO if used as queue, LIFO if used as stack |

**When you need sorted traversal:**

```java
// WRONG — heap order, not sorted
PriorityQueue<Integer> pq = new PriorityQueue<>(list);
for (int val : pq) { ... }  // arbitrary order!

// RIGHT — option 1: destructive (drains the heap)
while (!pq.isEmpty()) process(pq.poll());  // sorted

// RIGHT — option 2: sort a list (non-destructive)
List<Integer> sorted = new ArrayList<>(collection);
Collections.sort(sorted);
for (int val : sorted) { ... }

// RIGHT — option 3: use TreeSet if you need sorted + unique
TreeSet<Integer> ts = new TreeSet<>(collection);
for (int val : ts) { ... }  // sorted
```

**Choosing the right structure for "give me items in order":**

| Need | Best Choice | Why Not PQ? |
|---|---|---|
| Process items min-first (one by one) | `PriorityQueue` | This is PQ's sweet spot |
| Return sorted list / iterate in order | `ArrayList` + `sort()` | PQ iterator is not sorted |
| Maintain sorted set with adds/removes | `TreeSet` | PQ `remove(obj)` is O(n) |
| Sorted + need `floor`/`ceiling` queries | `TreeMap` / `TreeSet` | PQ has no neighbor queries |
| Top K from a stream | `PriorityQueue` (size K) | This is PQ's other sweet spot |

**HashMap iteration — don't rely on order:**
```java
// WRONG — assuming HashMap gives you insertion or sorted order
Map<String, Integer> map = new HashMap<>();
map.put("b", 2); map.put("a", 1); map.put("c", 3);
for (var entry : map.entrySet()) { ... }  // could be any order

// If you need insertion order: LinkedHashMap
// If you need sorted order: TreeMap
```

**HashSet and `equals()`/`hashCode()` contract:**
```java
// If you override equals(), you MUST override hashCode()
// Otherwise: set.contains(obj) may return false even when an "equal" object is in the set
// Rule: equal objects must have equal hash codes
```

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
| `PriorityBlockingQueue` | Thread-safe unbounded min-heap with blocking `take()` | Concurrent priority scheduling (e.g., scheduled payments) |
| `ConcurrentSkipListSet` | Thread-safe sorted set (skip list). O(log n) add/remove/contains | Concurrent sorted unique elements. O(log n) removal by value (vs PQ's O(n)) |
| `ConcurrentSkipListMap` | Thread-safe sorted map (skip list). O(log n) all ops | Concurrent `TreeMap` replacement — `firstKey`, `floorKey`, etc. |

**Choosing a concurrent sorted/priority structure**:

| Need | Use | Why |
|---|---|---|
| Thread-safe min-heap (peek/poll min) | `PriorityBlockingQueue` | Direct concurrent replacement for `PriorityQueue` |
| Thread-safe sorted set + O(log n) removal by value | `ConcurrentSkipListSet` | PQ's `remove(obj)` is O(n); skip list is O(log n) |
| Thread-safe sorted map with range queries | `ConcurrentSkipListMap` | Concurrent `TreeMap` — supports `floorKey`, `subMap`, etc. |

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
