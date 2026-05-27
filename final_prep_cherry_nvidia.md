# Final Interview Prep — Cherry + NVIDIA

> Last prep round. Cherry Wed May 27 (3 rounds), NVIDIA Thu-Fri May 29-30 (4 rounds).

---

## Coding — Fresh LC Medium List

### Cherry-relevant (fintech/BNPL domain — CRUD, state machines, financial logic)

| LC # | Problem | Why Cherry | Pattern |
|---|---|---|---|
| 146 | LRU Cache | Design problem, HashMap + LinkedList sync | Dual data structure |
| 380 | Insert Delete GetRandom O(1) | Multiple data structures in sync | HashMap + Array |
| 981 | Time Based Key-Value Store | Versioned lookups, binary search | TreeMap / binary search |
| 1166 | Design File System | Trie-based CRUD, path parsing | HashMap of HashMaps |
| 362 | Design Hit Counter | Sliding window, rate limiting | Queue or circular buffer |
| 155 | Min Stack | Stack with O(1) min | Dual stack |
| 49 | Group Anagrams | HashMap grouping | Sort + HashMap |
| 56 | Merge Intervals | Interval logic (time windows, loan terms) | Sort + merge |
| 138 | Copy List with Random Pointer | Deep copy complex structures | HashMap clone |
| 341 | Flatten Nested List Iterator | Iterator design, recursion vs stack | Stack-based iterator |

### NVIDIA-relevant (Java-heavy, distributed systems, high-performance)

| LC # | Problem | Why NVIDIA | Pattern |
|---|---|---|---|
| 1114 | Print in Order | Java concurrency, thread coordination | CountDownLatch / Semaphore |
| 1115 | Print FooBar Alternately | Thread synchronization | Semaphore |
| 1188 | Design Bounded Blocking Queue | Producer-consumer, concurrency | ReentrantLock + Condition |
| 232 | Implement Queue using Stacks | Data structure internals | Amortized O(1) |
| 225 | Implement Stack using Queues | Data structure internals | Queue rotation |
| 146 | LRU Cache | Classic design, O(1) everything | HashMap + DLL |
| 460 | LFU Cache | Frequency tracking, multiple maps in sync | HashMap + LinkedHashSet |
| 353 | Design Snake Game | State management, deque | Deque + HashSet |
| 622 | Design Circular Queue | Ring buffer (like window aggregation) | Array + pointers |
| 355 | Design Twitter | Multi-entity, timeline merge, follow/unfollow | HashMap + PriorityQueue |

### Quick warm-up (do 1-2 tonight, 15 min each)

| LC # | Problem | Time | Pattern |
|---|---|---|---|
| 20 | Valid Parentheses | 5 min | Stack |
| 242 | Valid Anagram | 5 min | HashMap count |
| 15 | 3Sum | 10 min | Sort + two pointers |
| 200 | Number of Islands | 10 min | BFS/DFS grid |

---

## System Design — Cherry-Relevant Topics

### Most likely: Payment/Loan Processing System

> "Design the backend for a BNPL system where patients apply for healthcare financing."

**Your mental model applies directly:**
- Product reqs: patient applies → credit check → approve/deny → provider paid → patient pays monthly
- State machine: APPLIED → APPROVED → ACTIVE → COMPLETED / DEFAULTED
- Payment: disbursement to provider, monthly collections from patient
- Failure modes: credit check timeout, payment failure, default handling

**Key components:**
```
Patient App → API → Loan Service → Credit Check Provider (async)
                       ↓
                  Payment Service → Payment Provider
                       ↓
                  Notification Service (Kafka)
                       ↓
                  Provider Portal (dealer equivalent)
```

**Cherry-specific angles:**
- Healthcare compliance (HIPAA — patient data is sensitive)
- Provider gets paid upfront (Cherry takes the risk)
- Patient payment schedule (installments)
- What if patient misses a payment? Grace period? Late fee? Collections?

---

### Backup: Multi-Tenant Provider Portal

> "Design a system where multiple healthcare providers (clinics, dentists) each have their own dashboard showing their patients' loan statuses."

**Key design points:**
- Multi-tenancy: one system, many providers, data isolation
- Row-level security (provider can only see their patients)
- Real-time status updates (patient paid → provider sees it)
- Reporting/analytics per provider

---

### Backup: Notification/Communication System

> "Design a system that sends patients payment reminders via email, SMS, and push notifications."

**Key design points:**
- Multiple channels (email, SMS, push)
- Scheduling (send 3 days before due date)
- Template management
- Delivery tracking + retry on failure
- Unsubscribe/preferences

---

## System Design — NVIDIA-Relevant Topics

### Context: NGC (NVIDIA GPU Cloud)

NGC is NVIDIA's catalog/registry platform — users browse, pull, and deploy GPU-optimized containers, pre-trained models, and SDKs. Think "Docker Hub for GPU software." Not fleet management or DGX hardware.

### Most likely: Content Registry / Catalog Platform

> "Design a system where users browse, search, and download GPU-optimized containers and models from a catalog."

**Key components:**
```
User → API Gateway → Catalog Service → Postgres (metadata)
                          ↓
                    Search Service (Elasticsearch)
                          ↓
                    Artifact Storage (S3 / container registry)
                          ↓
                    Access Control (entitlements, licensing)
```

**Key design points:**
- Catalog CRUD (publish, version, deprecate artifacts)
- Search/discovery (by framework, GPU type, use case)
- Download/pull (presigned URLs for large artifacts, rate limiting)
- Access control (free tier, enterprise licenses, per-org entitlements)
- Versioning + immutability (published artifacts don't change)
- Usage metrics (download counts, popular items)

---

### Backup: Model Registry / Artifact Storage

> "Design a system to store and serve ML model files (GBs each) with versioning."

You already did this at NVIDIA! Key points:
- Metadata in Postgres (model name, version, owner, metrics)
- Binary files in S3 (presigned URLs for upload/download)
- Versioning (immutable once published)
- Access control per model/team

---

### Backup: Telemetry / Metrics Pipeline

> "Design a system that ingests GPU telemetry (temperature, utilization, errors) from thousands of machines and serves dashboards."

**Same pattern as Coinbase Explore:**
- Ingest: agents on each machine push metrics
- Process: aggregate per time window
- Store: time-series DB (InfluxDB or TimescaleDB)
- Serve: Grafana dashboards + alerting
- Scale: thousands of machines × metrics per second

---

## Java Concurrency Quick Reference (NVIDIA)

```java
// CompletableFuture — fan out + fan in
List<CompletableFuture<Result>> futures = ids.stream()
    .map(id -> CompletableFuture.supplyAsync(() -> process(id), pool))
    .toList();
CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

// ReentrantLock — when you need tryLock or multiple conditions
ReentrantLock lock = new ReentrantLock();
lock.lock();
try { /* critical section */ }
finally { lock.unlock(); }

// ConcurrentHashMap — thread-safe map
map.computeIfAbsent(key, k -> new ArrayList<>()).add(value);
map.merge(key, 1, Integer::sum); // atomic increment

// Semaphore — bounded concurrency
Semaphore sem = new Semaphore(10); // max 10 concurrent
sem.acquire();
try { /* do work */ }
finally { sem.release(); }

// BlockingQueue — producer-consumer
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);
queue.put(task);    // blocks if full
queue.take();       // blocks if empty
```

**Key points to mention if asked:**
- "I use CompletableFuture for parallel fan-out to downstream services"
- "Per-service connection pools (HikariCP) with bulkhead isolation"
- "ConcurrentHashMap for shared state that's read-heavy, write-occasional"
- "Avoid synchronized — use ReentrantLock when I need tryLock or timeout"

---

## Concurrency Patterns — Web API Examples

### LC 1114 — Three Solutions (Print in Order)

```java
// Solution 1: Lock + Condition + state variable
// - signalAll() wakes all CURRENTLY waiting threads
// - The boolean persists, so NEW threads arriving later check the boolean
//   and skip the await() entirely (while loop condition is false)
// - await() releases the lock, so other threads can acquire it
class Foo {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition cond = lock.newCondition();
    private int step = 1;  // shared state — safe because only accessed under lock

    void first(Runnable r) throws InterruptedException {
        lock.lock();
        try {
            r.run();
            step = 2;
            cond.signalAll(); // wake all currently waiting threads
        } finally {
            lock.unlock();
        }
    }

    void second(Runnable r) throws InterruptedException {
        lock.lock();
        try {
            while (step != 2) cond.await(); // releases lock, waits, re-acquires on wake
            r.run();
            step = 3;
            cond.signalAll();
        } finally {
            lock.unlock();
        }
    }

    void third(Runnable r) throws InterruptedException {
        lock.lock();
        try {
            while (step != 3) cond.await();
            r.run();
        } finally {
            lock.unlock();
        }
    }
}

// Solution 2: Semaphore (simplest for ordering)
// - Permits persist — if first() runs before second() starts, the permit is already there
// - acquire() returns immediately if permit available, blocks if 0
class Foo {
    private final Semaphore sem2 = new Semaphore(0);
    private final Semaphore sem3 = new Semaphore(0);

    void first(Runnable r) throws InterruptedException {
        r.run();
        sem2.release();  // +1 permit for second()
    }

    void second(Runnable r) throws InterruptedException {
        sem2.acquire(); // blocks until first() releases
        r.run();
        sem3.release();  // +1 permit for third()
    }

    void third(Runnable r) throws InterruptedException {
        sem3.acquire(); // blocks until second() releases
        r.run();
    }
}

// Solution 3: CountDownLatch (one-shot, can't reuse)
// - count stays at 0 after countDown — late arrivals pass through immediately
class Foo {
    private final CountDownLatch latch1 = new CountDownLatch(1);
    private final CountDownLatch latch2 = new CountDownLatch(1);

    void first(Runnable r) throws InterruptedException {
        r.run();
        latch1.countDown();
    }

    void second(Runnable r) throws InterruptedException {
        latch1.await(); // blocks until count = 0
        r.run();
        latch2.countDown();
    }

    void third(Runnable r) throws InterruptedException {
        latch2.await();
        r.run();
    }
}
```

**Why `while` + state variable in the Lock solution?**
1. **Spurious wakeups:** `await()` can return without `signal()` (JVM spec). While loop re-checks.
2. **Late arrivals:** If step2 thread arrives AFTER step1 signaled, signal is lost. The boolean persists and step2 sees `step == 2`, skips `await()` entirely.
3. **Thread safety:** The boolean is safe because it's only read/written while holding the lock.

**Comparison:**

| Solution | Handles late arrival? | Handles spurious wakeup? | Reusable? | Complexity |
|---|---|---|---|---|
| Lock + Condition | Yes (boolean persists) | Yes (while loop) | Yes | Most |
| Semaphore | Yes (permits persist) | N/A (no spurious) | Yes | Least |
| CountDownLatch | Yes (count stays 0) | N/A (no spurious) | No (one-shot) | Least |

---

### Scenario 1: Lock + Conditions (Web API — ordering, no count limit)

Use when: step 2 must wait for step 1's result (data dependency). No limit on how many times step 2 can be called after.

```java
class OrderedApiService {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition step1Done = lock.newCondition();
    private final Condition step2Done = lock.newCondition();
    private boolean step1Completed = false;
    private boolean step2Completed = false;

    void apiStep1() {
        lock.lock();
        try {
            doStep1Work();
            step1Completed = true;
            step1Done.signalAll();
        } finally {
            lock.unlock();
        }
    }

    void apiStep2() throws InterruptedException {
        lock.lock();
        try {
            while (!step1Completed) step1Done.await();
            doStep2Work();
            step2Completed = true;
            step2Done.signalAll();
        } finally {
            lock.unlock();
        }
    }

    void apiStep3() throws InterruptedException {
        lock.lock();
        try {
            while (!step2Completed) step2Done.await();
            doStep3Work();
        } finally {
            lock.unlock();
        }
    }
}
```

### Scenario 2: Semaphore (count-bounded — step2 count ≤ step1 count)

Use when: each step 1 completion allows one step 2 to proceed. Like "can't capture more payments than authorized."

```java
class PaymentService {
    private final Semaphore capturePermits = new Semaphore(0);

    // Each auth releases one capture permit
    void authorize(PaymentRequest req) {
        doAuth(req);
        capturePermits.release(); // +1 permit
    }

    // Each capture consumes one permit — blocks if no auths available
    void capture(PaymentRequest req) throws InterruptedException {
        capturePermits.acquire(); // blocks if 0 permits (no uncaptured auths)
        doCapture(req);
    }

    // Optional: check without blocking
    boolean canCapture() {
        return capturePermits.availablePermits() > 0;
    }
}
```

### When to use which:

| Pattern | Guards | Blocks until | Real-world example |
|---|---|---|---|
| Lock + Condition | **State** ("is step 1 done?") | Condition becomes true | Fee/tax API waits for trade-in result |
| Semaphore | **Count** ("how many permits available?") | Permit available | Can't capture more payments than authorized |
| CountDownLatch | **One-time gate** ("did N things finish?") | Count reaches 0 | Wait for all providers to respond |

> "If it's count-bounded (can't capture more than authorized) → Semaphore. If it's a data dependency (step 2 needs step 1's output) → Lock + Condition. If it's one-time initialization → CountDownLatch."

---

## Reminders

**Cherry:**
- "Start simple, iterate" — they'll add requirements mid-session
- Be scrappy in coding, talk about production verbally
- No outside resources for SD — internalize the mental model
- App Design = your domain interview muscle (data model + API + state machine)

**NVIDIA:**
- Old school Java shop — depth on concurrency, connection pools, JVM
- "Walk me through a system" — API Mod technical layer
- No standard format — conversational, follow their lead
- Lead with technical depth, not leadership stories
