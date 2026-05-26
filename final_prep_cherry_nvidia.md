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
