# Design Knowledge Base — Patterns + Deep Tools

A working reference. Each entry answers: what problem it solves, how it works, when it fits, when it doesn't — and where it shows up in practice at CarGurus.

Conventions used below:
- **In practice (CG):** a concrete internal example illustrating the generic pattern.
- **Correction:** a claim that is commonly stated but wrong or overstated, and the accurate version.

---

## Contents

- [Part 1: Pattern Recognition (with context)](#part-1-pattern-recognition-with-context)
  - [Caching](#caching)
  - [Message Queue / Async Processing](#message-queue-async-processing)
  - [Sharding / Partitioning](#sharding-partitioning)
  - [CQRS (Command Query Responsibility Segregation)](#cqrs-command-query-responsibility-segregation)
  - [Event Sourcing](#event-sourcing)
  - [Fan-out (Push vs Pull)](#fan-out-push-vs-pull)
  - [Saga Pattern (Distributed Transactions)](#saga-pattern-distributed-transactions)
  - [Circuit Breaker](#circuit-breaker)
  - [Rate Limiting and Load Shedding](#rate-limiting-and-load-shedding)
  - [Consistent Hashing](#consistent-hashing)
  - [Tiered Storage (Hot/Warm/Cold)](#tiered-storage-hotwarmcold)
  - [Lease-Based Execution and Leader Election (Exactly-One in Distributed Systems)](#lease-based-execution-and-leader-election-exactly-one-in-distributed-systems)
  - [Change Data Capture (CDC)](#change-data-capture-cdc)
- [Part 2: Deep Dives (mechanisms worth reasoning about)](#part-2-deep-dives-mechanisms-worth-reasoning-about)
  - [2.1 Streaming and Connection Models](#21-streaming-and-connection-models)
    - [Choosing a transport: the decision is direction and timing, not payload size](#choosing-a-transport-the-decision-is-direction-and-timing-not-payload-size)
    - [Why streaming at all — it's latency-to-first-byte, not size](#why-streaming-at-all-its-latency-to-first-byte-not-size)
    - [SSE wire format — the whole protocol](#sse-wire-format-the-whole-protocol)
    - [Why SSE over WebSocket for turn-based chat](#why-sse-over-websocket-for-turn-based-chat)
    - [Correction — connection capacity is not a protocol property](#correction-connection-capacity-is-not-a-protocol-property)
    - [High-frequency binary: why WebSocket, precisely](#high-frequency-binary-why-websocket-precisely)
    - [The three-way connection taxonomy (the thing that collides numerically)](#the-three-way-connection-taxonomy-the-thing-that-collides-numerically)
    - [Proxied streaming pipelines and layer placement](#proxied-streaming-pipelines-and-layer-placement)
  - [2.2 API Composition and Ownership](#22-api-composition-and-ownership)
    - [The three transports, and what each actually optimizes](#the-three-transports-and-what-each-actually-optimizes)
    - [Where GraphQL's performance actually comes from](#where-graphqls-performance-actually-comes-from)
    - [DataLoader: batching vs dedup, and where the real win is](#dataloader-batching-vs-dedup-and-where-the-real-win-is)
    - [Keeping the subgraph graph shallow, and @provides](#keeping-the-subgraph-graph-shallow-and-provides)
    - [The placement rule: whose logic, not logic-vs-data](#the-placement-rule-whose-logic-not-logic-vs-data)
    - [The threshold question: when is federation worth it at all?](#the-threshold-question-when-is-federation-worth-it-at-all)
  - [2.3 Derived-Store Materialization](#23-derived-store-materialization)
    - [The layered truth model](#the-layered-truth-model)
    - [Build-from-source vs dump-a-replica](#build-from-source-vs-dump-a-replica)
    - [Snapshot anatomy and cadence](#snapshot-anatomy-and-cadence)
    - [Correction — snapshots don't re-base the fleet](#correction-snapshots-dont-re-base-the-fleet)
    - [Recovery patterns](#recovery-patterns)
    - [Ingestion sources and the two-path pattern](#ingestion-sources-and-the-two-path-pattern)
    - [Correction — "the ingestor is one process" is a real limitation, not a design ideal](#correction-the-ingestor-is-one-process-is-a-real-limitation-not-a-design-ideal)
    - [Materialization vs stream processing](#materialization-vs-stream-processing)
- [Part 3: Deep Tool Knowledge](#part-3-deep-tool-knowledge)
  - [PostgreSQL / MySQL (Relational)](#postgresql-mysql-relational)
  - [Redis / Valkey](#redis-valkey)
  - [MongoDB / DynamoDB (Document / NoSQL)](#mongodb-dynamodb-document-nosql)
  - [Kafka](#kafka)
  - [Elasticsearch / OpenSearch](#elasticsearch-opensearch)
  - [GraphQL Federation](#graphql-federation)
  - [gRPC](#grpc)
  - [WebSocket and SSE](#websocket-and-sse)
  - [S3 / Object Storage](#s3-object-storage)
  - [ZooKeeper / etcd / Consul (Coordination)](#zookeeper-etcd-consul-coordination)
  - [CDN (Content Delivery Network)](#cdn-content-delivery-network)
  - [Flink / Stream Processing](#flink-stream-processing)
- [Part 4: Constraint → Solution Mapping (Quick Reference)](#part-4-constraint-solution-mapping-quick-reference)
- [Part 5: Tradeoff Pairs (One-Liners)](#part-5-tradeoff-pairs-one-liners)
- [Part 6: Recurring Meta-Principles](#part-6-recurring-meta-principles)
- [Part 7: Corrections Index](#part-7-corrections-index)

---


## Part 1: Pattern Recognition (with context)

---

### Caching

**Problem it solves:** Reads are too frequent or too expensive for the source to handle on every request.

**How it works:**
- Store computed/fetched results in a faster layer (memory)
- On read: check cache first → if hit, return immediately → if miss, fetch from source, populate cache
- Invalidate or expire entries to avoid serving stale data

#### The layer map — each layer caches a different thing

| Layer | Typical cache | Scope | Main benefit |
|---|---|---|---|
| Client | Browser cache | One user | Eliminates the request entirely |
| Edge | CDN / HTTP cache | Global/regional | Never reaches the application |
| Service L1 | Caffeine, in-memory map | One process/pod | Fastest lookup, no serde |
| Service L2 | Redis / Valkey | Shared across pods | Shared view, lower source load |
| ORM L1 | Hibernate persistence context | One session/transaction | Identity map within a unit of work |
| ORM L2 | Hibernate second-level cache | Across sessions/pods (if enabled) | Entity reuse across requests |
| DB engine | InnoDB buffer pool, WiredTiger cache | DB node | Avoids disk reads |
| Plan/query | Prepared statements, query plans | Driver/DB/search node | Avoids re-parsing/re-planning |

**Correction — "DB caches are usually not enabled" is two claims, and only one is true.**
Database **engine** caches (InnoDB buffer pool, WiredTiger cache) are fundamental and always on; disabling them would make the DB unusable. What teams commonly disable is the **ORM second-level / query cache**, because invalidation is hard, data can change outside the app, contents duplicate per pod, and the engine already caches pages and indexes.
**In practice (CG):** Several Spring services (Service Provider V2 and multiple cg-main services) explicitly set Hibernate second-level cache and query cache to `false`. Hibernate L1 (session-scoped) is different and useful — it prevents duplicate entity loads inside one transaction.

#### Read/write strategies

| Strategy | Best fit | Important caveat |
|---|---|---|
| **Cache-aside (lazy)** | Most read-heavy business data. The default. | App owns misses and invalidation |
| **Read-through** | Standardized cache library/platform | Semantics are still cache-aside underneath |
| **Write-through** | Data that must be cached immediately after write | Cache + DB writes are **not atomic** |
| **Write-around** | Write-heavy, rarely re-read data | Write DB, invalidate cache; avoids cache pollution |
| **Write-behind / write-back** | Counters, telemetry, batch aggregates | Needs a **durable** queue/log; volatile Redis alone is unsafe |
| **Refresh-ahead** | Very hot, relatively stable data | Refresh before expiry so users never see a miss |

**Correction — write-through is not "strong consistency."** If the cache write succeeds and the DB write fails, the cache holds data the source never accepted. For durable business data, **write DB → invalidate cache** is safer than synchronously updating both.

**Write-behind is only safe with a durable log:**
```text
application → cache → durable queue/log → database
```
Appropriate for telemetry and counters. Inappropriate for payments, orders, or core business facts.

#### Invalidation / freshness strategies

| Strategy | Best fit | Main risk |
|---|---|---|
| **TTL** | Bounded staleness, simplest | Stale until expiry |
| **Event-driven invalidation** | Fresh shared data | Missed, duplicated, delayed, out-of-order events |
| **Versioned keys** | Immutable artifacts, static assets | Old versions need GC/lifecycle |
| **ETag / conditional GET** | HTTP/CDN caches | Still costs a validation round-trip |
| **Manual purge** | Rare operational changes | Human process, doesn't scale |
| **Stale-while-revalidate** | Latency/availability priority | Deliberately serves stale for a bounded window |

**TTL should be a backstop, not the only correctness mechanism.** The robust combination is `event-driven invalidation + long TTL safety net` — if an invalidation is missed, the entry still eventually expires.

**Event-driven invalidation needs an outbox, not a fire-and-forget publish:**
```text
DB transaction → durable outbox event → invalidation consumer → evict/refresh
```
Publishing from app code after commit loses the event if the publish fails. Events should carry a version or timestamp so consumers can discard out-of-order invalidations.

**Versioned keys** replace overwriting with immutability plus a pointer:
```text
listing:123      → v42     (pointer)
listing:123:v41  → payload (old)
listing:123:v42  → payload (current)
```
Ideal for object-storage artifacts, search indices, config bundles, and content-hashed assets. Does not remove the need for cleanup.

#### Additions worth knowing

- **Request coalescing (singleflight):** on a miss storm, one request fetches and the rest wait — `100 concurrent misses → 1 source call + 99 waiters`. The primary defense against cache stampede.
- **Negative caching:** cache "not found" briefly (short TTL) so invalid IDs don't hammer the source.
- **Cache warming:** preload hot/reference data before taking traffic; rate-limit it or you create a startup thundering herd.
- **Two-level caching:** `L1 local → L2 shared → source`. L1 is fastest but per-pod; L2 is shared but adds a hop. Invalidation and memory duplication get harder.
- **Admission and eviction policy:** max object size, max entries, LRU/LFU, minimum access frequency before admission. A large, rarely-reused object makes a cache *slower*.

#### Dangers

- **Cache stampede:** hot key expires, concurrent misses hit the source. Fix: coalescing, early refresh, TTL jitter.
- **Cold-start spike:** deploy or cache flush sends all traffic to the source.
- **Cache outage → fallback load:** the failure mode people forget.
  **In practice (CG):** the Dealer Reviews runbook treats the cache circuit breaker opening as dangerous precisely because all requests then fall through to MongoDB — roughly 2–5× latency and potential Mongo pool saturation.
- **Oversized entries in a shared cache:** a CG finance-transaction cache was moved from Redis to Caffeine because the payload exceeded ~500 KB and Redis operations took ~10s, causing connection-pool exhaustion. The accepted tradeoff was one copy per pod plus a DB hit on first request after startup. "Distributed cache is always better" is false.
- **Key correctness bugs:** a key missing tenant/user/locale/permission/filter dimensions leaks one user's result to another.

**In practice (CG) — the three-tier pattern:** the finance-transaction service documents Caffeine (local, microsecond), ElastiCache Redis (shared, cache-aside), and Kafka-synchronized in-memory maps (fast local reads with explicit propagation). Not redundant — three different problems.

**In practice (CG) — cache is not persistence:** internal guidance treats Redis data as **ephemeral** (fsync ~1s, no journal backup, no restore process). Anything durable goes to MySQL/Mongo. Dealer Reviews follows the canonical shape: ElastiCache-Valkey cache, MongoDB durable store, circuit breaker falling back to Mongo.

#### Where caching applies, by data class

| Data class | Approach |
|---|---|
| Public static assets | Content-hashed/versioned keys, long CDN TTL, immutable, lifecycle cleanup |
| Durable transactional data | Cache-aside, DB is truth, event invalidation after commit, TTL backstop, coalescing |
| Stable reference data | Local + optional shared cache, refresh-ahead, longer TTL |
| Derived/search data | Versioned snapshots/indices, incremental events, rebuild-from-source recovery, alias switch (this is a materialized view, not just a cache) |
| Telemetry / counters | Write-behind, batching, durable log, eventual persistence |
| Personalized / volatile | Short TTL or no cache; keys must include every dimension |

#### Correction — where "free" caching actually lives

- Free HTTP/CDN caching exists **only at the client edge**, keyed on a cacheable `GET`. Internal east-west (service→service) hops have **no edge**, so switching an internal call from one routing path to another never "recovers free caching."
- A GraphQL client edge forfeits it too: everything is `POST /graphql`, which HTTP caches can't key on.
- **Caching and call-routing are orthogonal axes.** If a hot, static, high-repeat entity needs caching, cache it **at/in front of the owning service** — then you keep batching/dedup/fail-open/observability *and* get cross-request caching.
- SSR relocates the client edge: with a server-rendered front end, the cacheable boundary becomes browser↔SSR-server, and whether free caching survives is a **config** question (loader/document cache headers + CDN), not a paradigm limitation.

#### Validation checklist before adding any cache

1. Source of truth — which system is authoritative?
2. Allowed staleness — seconds, minutes, never?
3. Read-after-write — must the writer see its own write?
4. Failure behavior — can the request fall back to the source, and can the source take it?
5. Invalidation guarantee — what prevents missed invalidations?
6. Stampede protection — what happens when thousands miss at once?
7. Key correctness — tenant, locale, permissions, filters, version all in the key?
8. Size and eviction — what happens when it fills?
9. Warmup — does deploy create a source spike?
10. Observability — hit rate, miss latency, evictions, stale serves, refresh failures, fallback load.
11. Recovery — can it be rebuilt safely from the source?
12. Security — can one tenant read another's cached result?

**Fits when:** Read-heavy (10:1+), staleness tolerable, hot set is a small subset.
**Doesn't fit when:** Real-time consistency required (payments, inventory), writes ≈ reads, or the working set doesn't fit.

**One-liner:** A cache is not free performance — it is a second, potentially stale copy whose value must exceed the cost of maintaining, invalidating, warming, monitoring, and recovering it.

---

### Message Queue / Async Processing

**Problem it solves:** Decouple producer from consumer, absorb traffic spikes, handle work that doesn't need an immediate response.

**How it works:**
- Producer writes a message to a queue
- Consumer pulls messages and processes them independently
- Queue acts as a buffer between the two

**Two flavors:**
- **Work queue (SQS, RabbitMQ):** message consumed once, then deleted.
- **Event stream (Kafka):** messages retained with offsets. Multiple consumer groups read independently. Replay possible.

**Key patterns:**
- Fan-out: one event → multiple consumers (Kafka consumer groups)
- Dead letter queue: failed messages diverted for investigation
- Backpressure: monitor lag and scale consumers

**Fits when:** Bursty traffic, non-critical-path work, independent scaling/deployment.

**Doesn't fit when:** Sustained write volume permanently exceeds processing capacity, caller needs synchronous confirmation, or immediate consistency is required.

**Key insight:** Queues absorb SPIKES, not SUSTAINED overload. If producer rate permanently exceeds consumer rate, the queue grows forever.

**In practice (CG):** most "stream processing" is plain Kafka consumers reacting per-event — LDS Writer, LSDI, SPDI, IMV, CGSP incremental ingestion. Change events say *what changed*; the consumer re-fetches truth. See Part 2.3 and the Flink entry for why that choice removes the need for a stream-processing framework.

---

### Sharding / Partitioning

**Problem it solves:** A single node can't handle write throughput, connection count, or data volume.

**Strategies:**
- **Hash-based:** `hash(key) % N` — even distribution, painful resharding
- **Range-based:** range queries work, hotspots if uneven
- **Consistent hashing:** minimizes redistribution when membership changes

**Choosing a key:** query pattern determines the key. Good key = even distribution + queries stay within one shard. Bad key = scatter-gather.

**Triggers:** write QPS beyond single-node capacity, data volume where indexes no longer fit in RAM, connection pool exhaustion.

#### Partitioning for ordering vs throughput (Kafka-shaped, but general)

- Order is guaranteed **within** a partition only, never across a topic.
- **Global order for the whole topic** → 1 partition (gives up parallelism).
- **Per-entity order + scale** → multiple partitions keyed by a stable entity id. This is the usual sweet spot.
- **Max throughput, order irrelevant** → default distribution.
- Keyed partitioning creates the **hot-key/skew** problem. Four remedies: accept the skew (ordering matters more), raise total partition count so the rest of the keyspace spreads, shard the hot key (`entityId#0..N`, relaxes strict per-entity order), or isolate the hot workload into its own topic/path.
- Key→partition mapping is stable only relative to the **current** partition count; increasing partitions re-maps future writes.

**Sizing rule:** `partitions ≈ maximum useful consumers`, with modest headroom — not "current pod count," and not "as many as possible."
- Fewer partitions than consumers → idle consumers.
- Far more partitions than needed → broker metadata, coordination, and metrics-cardinality overhead.
**In practice (CG):** internal guidance offers "partitions = consumers" as a conservative default; a 300-partition topic was flagged as over-provisioned and a contributor to Prometheus/metadata pain; and a lag incident was root-caused as a mismatch between 6 partitions and only 3 active consumer pods ([consumer-lead postmortem](https://cargurus.atlassian.net/wiki/spaces/DEV/pages/4342383057)). Separately, one team's request to add partitions was declined because the real bottleneck was a downstream REST API, not Kafka parallelism.

**Correction — "one consumer with two partitions processes them in parallel" is not guaranteed.** Kafka gives partition-level assignment; whether one consumer instance processes its partitions concurrently is a client/framework choice. Parallelism normally comes from **more consumer instances**.

**Fits when:** vertical scaling and read replicas are exhausted, and a clear access pattern exists.
**Doesn't fit when:** frequent cross-partition joins, small data, or a single node with replicas suffices.

---

### CQRS (Command Query Responsibility Segregation)

**Problem it solves:** Read and write patterns are fundamentally different — different shapes, frequencies, performance needs.

**How it works:** separate the write model (normalized, correctness-optimized) from the read model (denormalized, query-optimized); async events propagate changes.

**In practice (CG):** MySQL is the transactional write model for listings; LDS is a read-optimized denormalized document per listing in MongoDB, fed by a synchronizer and consumed via GraphQL. Explicitly read-only — MySQL remains the only place for listing writes.

**Fits when:** reads need denormalized views, writes need strict normalization, read:write ratio is high.
**Doesn't fit when:** read and write shapes are the same, the system is small, or stale reads are unacceptable.

**Tradeoff:** eventual consistency between models. Decide explicitly whether "user sees slightly stale data" is acceptable.

---

### Event Sourcing

**Problem it solves:** Complete audit trail, replay/reconstruct state, temporal queries.

**How it works:** store every state change as an immutable event; current state = replay from the beginning or a snapshot; never mutate or delete events.

**Benefits:** full audit trail, rebuild state at any point in time, replay with new logic, natural fit for event-driven architectures.

**Costs:** snapshots needed for performance, event schema evolution is hard, eventually consistent reads.

**Depth-of-lock-in note:** event sourcing is the deepest commitment in this document, because the **source of truth becomes the append-only log** — state is *derived* by replay. Backing out means reconstructing what "correct" means. Compare: CQRS reshapes the data model; a transport/contract choice like gRPC only reshapes service edges and is reversible per-edge. Weight adoption bars accordingly.

**Fits when:** financial/compliance domains, "how did we get here" matters, undo/replay needed.
**Doesn't fit when:** simple CRUD, no audit requirement, state is simple and rarely disputed.

---

### Fan-out (Push vs Pull)

| Approach | How | Pro | Con |
|---|---|---|---|
| **Push (fan-out on write)** | Write to all recipients' feeds on event | Fast reads (pre-built) | Expensive for high-follower accounts, wasted on inactive users |
| **Pull (fan-out on read)** | Query and merge sources at read time | No wasted writes | Slow reads, high read-time compute |
| **Hybrid** | Push for normal, pull for celebrities | Best of both | Implementation complexity |

**The celebrity problem:** 10M followers → 10M writes per post. Don't push for celebrities; merge at read time.

**Key decision:** what is the follower distribution?

---

### Saga Pattern (Distributed Transactions)

**Problem it solves:** A business operation spans services/databases and needs atomicity (all succeed or all compensate).

**How it works:** a sequence of local transactions, each with a compensating action; on failure, compensate in reverse.

**Two coordination modes:**
- **Choreography:** services react to events. Decoupled, but overall progress is hard to track.
- **Orchestration:** a central coordinator directs steps. Easier to reason about, coordinator is a dependency.

**Alternatives:** 2PC (locks across phases, coordinator SPOF), TC/C (application-level, parallel, more complex).

**Related correction:** a **federated GraphQL mutation has no distributed transaction** — the router cannot give atomicity or rollback across subgraphs. That's a strong reason to keep writes on the owning service (REST or a service-local transaction) rather than composing writes in a graph.

**Fits when:** services can't share a database, operations are compensatable, eventual consistency is acceptable.
**Doesn't fit when:** a single DB transaction is possible, compensation is impossible (sent email), or real-time consistency is required.

---

### Circuit Breaker

**Problem it solves:** A failing dependency causes cascading failure — requests pile up on timeouts, pools exhaust, the system degrades.

**Three states:** Closed (flowing, tracking failures) → Open (short-circuit immediately, return fallback) → Half-open (probe one request; success closes, failure reopens).

**Key parameters:** failure threshold, cooldown, fallback.

**In practice (CG):** the federated router runs native circuit breakers globally and per-subgraph, with **fail-open timeouts** (3s default, 15s for the large-batch subgraph) that null just the affected field and return the rest. Retries are deliberately **disabled** to avoid retry storms; rate limiting is available but not enabled (client-side instead). Dealer Reviews puts a breaker in front of its cache and falls back to MongoDB.

**Design lesson from the fallback side:** always ask what the fallback path costs. A breaker that dumps cache traffic onto the primary datastore trades one outage for another.

**Doesn't fit when:** the dependency is mandatory with no meaningful fallback.

---

### Rate Limiting and Load Shedding

**Problem it solves:** Protect a service from overload (DDoS, misbehaving clients, thundering herd) — and protect a **scarce downstream** from your own traffic.

**Algorithms:** token bucket (bursts, most common), sliding window counter (accurate, low memory), leaky bucket (smooth output).

**Implementation:** Redis + Lua for atomic check-and-increment; key = `rate:{identifier}:{window}`. Granularity: user, IP, API key, endpoint, global — often multi-tier.

**Admission control / load shedding is the sibling pattern:** when the constrained resource is *your own* capacity or a costly upstream, cap concurrency and reject early rather than queueing forever.
**In practice (CG):** the AI streaming server caps concurrent streams per worker and returns 503 past the limit, with client-side 503 handling. That cap protects LLM concurrency and per-stream memory — it is a deliberate throttle, **not** a protocol limit (see Part 2.1).

---

### Consistent Hashing

**Problem it solves:** Distribute data across nodes so adding/removing a node doesn't reshuffle everything.

**How it works:** hash nodes and keys onto a ring; a key maps to the first node clockwise; adding a node only affects keys between it and its predecessor; virtual nodes (100–200 per physical) even out distribution.

**Used in:** Cassandra, DynamoDB partitioning, CDN edge mapping, distributed caches.

**Doesn't solve:** the hot **key** problem. That needs key replication, key sharding, or local caching.

---

### Tiered Storage (Hot/Warm/Cold)

**Problem it solves:** Data grows unbounded but most queries touch recent data.

**Tiers:** hot (memory/SSD) → warm (primary DB/cheaper SSD) → cold (object storage/archive), with lifecycle policies moving data by age or access.

**Fits when:** strong temporal locality, long retention requirements, cost matters.

**Operational note:** lifecycle policies are also a **cost-leak defense** — expiring old versions/snapshots and aborting incomplete multipart uploads are the two most commonly forgotten rules (see the S3 entry).

---

### Lease-Based Execution and Leader Election (Exactly-One in Distributed Systems)

**Problem it solves:** Some work must be done by **exactly one** instance at a time, but you still want N replicas for availability. Leader election gives you singleton semantics *with* automatic failover.

**How it works (lock + session):**
1. Every replica creates a **session** with a TTL and heartbeats to renew it
2. All replicas race to **atomically acquire** a lock on one key; exactly one wins
3. Winner runs the singleton work; losers watch and wait
4. If the leader dies and stops heartbeating, the session expires, the lock auto-releases, watchers re-race

**Why "any healthy node, first-to-acquire" is the right design, not laziness:**
- Replicas are **interchangeable** — there is no "best" leader, so selection criteria would add complexity for nothing
- **Symmetry** means zero config: every node runs the same loop, replicas can be added/removed freely
- **Failover is automatic and fast** because leadership *is* lock ownership tied to liveness
- The acquire is **atomic**, so the thundering herd on release resolves safely — exactly one winner regardless of who

**Tuning tension:** short TTL = fast failover but false-positive risk on a blip; long TTL = stable but slow failover. A partitioned leader may believe it still leads for up to its TTL, so **singleton work should be idempotent or fenced** rather than assuming perfect exclusivity.

**Database-lease variant:**
```sql
UPDATE jobs SET status='RUNNING', worker_id=me, lease_expires=now()+5min
WHERE job_id=X AND status='QUEUED'
-- 0 rows = another worker got it; 1 row = I hold the lease
```

**In practice (CG):** a `leader-election` library over Consul sessions + KV locks gates the singleton-shaped services — the search dataset ingestor (its cron only runs on the leader), LDS Writer, SPDI, and IMV. Two hard-won lessons: (1) the client **must** re-initialize its session on coordinator errors, because a Consul blip once left a service unable to recover until restart; (2) the coordination store deserves **P1 dependency** status — a quiet coordinator is a hard dependency of a loud revenue service.

---

### Change Data Capture (CDC)

**Problem it solves:** Keep derived stores (search index, cache, analytics) in sync with the source without dual-write inconsistency.

**How it works:** read the DB transaction log (binlog/WAL), stream changes via Kafka, consumers update their own stores.

**Why not dual-write:** if the second write fails you have divergence. CDC guarantees: if it's committed, it will reach downstream.

**Tools:** Debezium, AWS DMS, pg_logical.

#### Two event shapes — and why the second one matters more than it looks

| Shape | Event carries | Consumer must | Consequence |
|---|---|---|---|
| **Full-payload event** | The new state | Apply the payload | Consumer accumulates state; ordering and completeness are load-bearing |
| **Invalidate-then-refetch** | Only "id X changed" | Re-query the source for current truth | Consumer stays **stateless**; naturally self-correcting |

The refetch shape is quietly powerful: because the consumer never reconstructs state by folding the stream, it needs no windowing, no large keyed state, and no exactly-once operator machinery. **That design choice is a large part of why a stream-processing framework isn't needed** (see the Flink entry).

Its costs: an extra read against the source per change, and freshness bounded by refetch latency.

**In practice (CG):** the listing pipeline is `MySQL → (synchronizer) → LDS/Mongo → Kafka → search nodes`, and CGSP's ingestor listens to Kafka/SQS change topics and **re-fetches only the changed documents**. Deletes/closures propagate as upstream state changes, with full rebuilds as the completeness backstop.

**Fits when:** syncing to multiple stores, needing guaranteed primary→derived consistency, needing a change stream.

---

## Part 2: Deep Dives (mechanisms worth reasoning about)

Three areas where the generic pattern language above isn't enough, and the mechanism has to be understood directly.

---

### 2.1 Streaming and Connection Models

#### Choosing a transport: the decision is direction and timing, not payload size

| Requirement | Transport |
|---|---|
| Known refresh interval, client-driven | HTTP polling (with `ETag` / `If-None-Match` / deltas) |
| Server must push the moment data changes, one direction | SSE |
| Client must send **while** the server is streaming, on one channel | WebSocket |
| High-frequency binary, dynamic subscriptions, multiplexed interactive streams | WebSocket |

**The dividing rule:** SSE is sufficient whenever the two directions are **temporally separated** (request, then stream). WebSocket earns its cost only when you need **simultaneous** bidirectional traffic on a single connection.

#### Why streaming at all — it's latency-to-first-byte, not size

A chat reply is only a few KB. The reason a plain response won't do is that the content is **produced incrementally over 5–30 seconds**. A blocking response means a blank spinner for the whole generation, then a dump; streaming paints the first tokens in ~1–4s.

Two secondary reasons a single long response is worse: it risks **proxy/LB idle timeouts** with nothing on the wire (heartbeat chunks keep SSE demonstrably alive), and it forfeits **progressive typed events** (see below).

The general trigger: **is this payload slow to produce and revealed progressively?** If it's complete-at-once (a lookup, cached data, a templated welcome message), stream nothing.

#### SSE wire format — the whole protocol

An HTTP response with `Content-Type: text/event-stream` that stays open. Four field names and a blank-line delimiter:

```text
event: text-delta
data: {"content":"The "}

event: text-delta
data: {"content":"Honda "}

event: metadata
data: {"suggestions":["Compare trims"]}

```

- `data:` — payload (the only required field)
- `event:` — names the message **type**; absent means the default `message` event
- `id:` — message id, remembered by the browser for reconnect
- `retry:` — reconnect delay hint
- **A blank line (`\n\n`) terminates one message** — this is the "dispatch now" signal

No framing headers, no length prefixes, no binary. That simplicity is exactly why SSE traverses ordinary HTTP proxies and CDNs (buffering must be off) while WebSocket needs upgrade-aware infrastructure.

One typed stream can therefore express a whole protocol — incremental text, a title, final metadata, an error, and a mid-stream replacement — all as different `event:` labels on the same connection.

#### Why SSE over WebSocket for turn-based chat

The decisive advantages:
- **Stateless / scales horizontally** — SSE is a plain HTTP response, so any node can serve a reconnect provided history lives in a shared store. WebSocket is stateful and wants sticky sessions or a broker to survive deploys.
- **Traverses existing infra** — any HTTP proxy/CDN/firewall.
- **Standard auth, free reconnect, built-in event typing** — `EventSource` auto-reconnects; WebSocket needs custom auth/CSRF, manual reconnect, and a hand-rolled envelope.

Human-in-the-loop does **not** require bidirectionality: the agent's clarifying question streams as a complete response, the stream closes, and the user's answer is a new POST. Because full history is replayed, the agent "remembers" it was mid-clarification.

Revisit WebSocket only for **binary** (voice/audio) or **true low-latency bidirectional control** (interrupt mid-generation) — and then as a small side-channel, not a wholesale migration.

**Note on POST-SSE:** native `EventSource` is GET-only. Carrying a prompt body requires a POST that returns SSE (e.g. the `fetch-event-source` polyfill). The wire format is identical; only the client read differs.

#### Correction — connection capacity is not a protocol property

**Wrong:** "WebSocket holds ~5k connections, SSE holds ~50."

Both are one long-lived TCP connection with near-identical per-connection cost. Capacity is bounded by **file descriptors, per-connection memory, and event-loop/thread capacity** — a tuned server holds tens of thousands of either. If anything SSE is marginally *lighter* per idle connection (no frame decoding, no ping/pong machinery).

- A low per-app stream limit is an **application throttle protecting a scarce downstream** (LLM concurrency, per-stream memory), not an SSE ceiling.
- The one genuine SSE-specific limit is client-side: **~6 connections per domain on HTTP/1.1**, so multiple tabs can starve each other. **HTTP/2 multiplexing removes it.**
- WebSocket's real differentiators are *what flows over* the connection — bidirectionality, lower per-message overhead, binary frames — not *how many* connections.

**HTTP/2 Server Push is not an alternative.** It was deprecated in browsers and does not let a server arbitrarily push application updates.

#### High-frequency binary: why WebSocket, precisely

Not because it's inherently lower-latency — latency is dominated by distance, processing, buffering, and congestion. It's because:
- **binary frames are native**; SSE is UTF-8 text, so binary needs base64 (larger) or a custom text encoding
- Protobuf/CBOR are smaller and far cheaper to parse than JSON
- lightweight framing after handshake
- bidirectional control for dynamic subscribe/unsubscribe, acks, commands

For genuinely ultra-low-latency market data, even WebSocket may not suffice — QUIC/WebTransport or specialized transports enter the picture.

#### The three-way connection taxonomy (the thing that collides numerically)

Different resources, wildly different hold times. Identical numbers mean opposite things.

| Concept | What it caps | Hold time | Scarcity |
|---|---|---|---|
| **Stream slot** (SSE/WebSocket) | End-to-end things happening at once | Full generation, 5–30s | High — fills fast |
| **HTTP/TCP transport capacity** | Sockets the box can hold | Same, but bounded by FD/memory | Tens of thousands |
| **DB pool connection** | Simultaneously **in-flight DB operations** | ~5–10ms per operation | Low — one pool serves hundreds of streams |

A 20-second stream holds **one** stream slot for its whole life while borrowing a DB connection **6–8 separate times** for milliseconds each. That's why the same number (say 50) fills instantly as stream slots but comfortably serves hundreds of concurrent streams as a DB pool.

**Why the DB pool stays open at all:** connection pooling is a universal driver-level practice to amortize the **TCP + TLS + auth (SCRAM) + topology handshake** — easily 10–100ms of setup versus a 5–10ms query. `minPoolSize` keeps warm sockets ready; `maxPoolSize` caps concurrent in-flight operations. It has nothing to do with streaming.

**How a pool nevertheless gets exhausted** (the counter-intuitive part): a connection is held for the **full operation latency**, not the CPU time. A single-threaded event loop can hold **hundreds of concurrent in-flight awaits**, each pinning a connection until it resolves. So `outstanding ops ≈ arrival_rate × op_latency` (Little's Law). Three amplifiers: concurrency × latency, **latency spikes** (maintenance/failover holds each connection longer), and **abandoned work**.

**Pool math worth remembering:** `connections = pods × workers × clients_per_worker × poolSize`. A dev environment at 19 × 3 × 2 × 5 produced ~570 idle connections (observed ~985 per node with bursting); reducing `minPoolSize` to 1 cut idle to 114. Separate clients (e.g. storage vs vector) each get **their own** pool.

**Runtime asymmetry:** on a thread-per-request runtime (JVM/Tomcat), a non-stream read lands on its own thread with its own connection, so stream work can't starve it. On a single-event-loop runtime, stream flushes and reads compete for the **same per-worker pool on the same loop** — so a flush burst can queue a read.

**Zombie streams:**without client-disconnect detection, a stream keeps generating and flushing after the client is gone, inflating concurrency for no user benefit. The fix is to abort on close (`res.on('close', () => abortController.abort())`).

#### Proxied streaming pipelines and layer placement

A two-hop proxied SSE pipeline (`browser → BFF → generation service → LLM`) has an important consequence: **each active stream pins two long-lived connections**, doubling the held-connection count.

The layering rule that matters:

| Layer | Owns | Does **not** own |
|---|---|---|
| Generation service | Token generation, intent routing, **safety enforcement** | Client-specific display shape |
| BFF | Transport, SSE framing, **display hydration** | Safety, generation, routing |

**Mid-stream guardrails** are the payoff of streaming: an output processor inspects accumulated text per chunk (regex, ~1–5ms, no extra model call) and on a violation calls `abort()` — which stops the **LLM generation**, not the connection. The middleware then emits a single `guardrail-replace` event, and the client overwrites the text it was building. **Abort the generation, not the connection; swap the event type, don't tear down the stream.**

Two refinements worth stealing:
- **Severity-gated abort.** High-severity categories abort immediately; low-severity ones defer to finish-time, because partial text false-positives (a half-streamed refusal reads like a violation). The earlier you abort, the less leaks — but the more you risk killing a good response.
- **Enforcement belongs next to generation, not in the BFF.** Put it in the processor and *every* client (web, mobile, internal tools) inherits it; put it in one BFF and only that path is protected.

**IDs-only + downstream hydration.** The model emits **validated ids**, not display payloads; the presentation layer hydrates them fresh. This buys four things at once: data can't be mutated or hallucinated by the model, display data is **fresh at render time** rather than frozen at reasoning time, token cost stays low, and the generation output stays **client-agnostic** so web and mobile can render differently.

Counter-argument worth knowing (and its answer): passing the reasoning-time snapshot through would make text and card consistent — but it makes *both* stale, relocates the fetch to the wrong owner, and couples generation to one client's display shape. Fresh hydration's failure mode (missing card) is safer than stale-but-confident numbers. The residual text-vs-card mismatch is handled by convention: **numbers live in the card, not in prose.**

---

### 2.2 API Composition and Ownership

#### The three transports, and what each actually optimizes

| Axis | REST | GraphQL Federation | gRPC |
|---|---|---|---|
| Mental model | Manipulate resources with HTTP verbs | Typed composition across domains | Call a typed remote **method** |
| Round trips / over-fetch | Client orchestrates | Solves it (one query, fan-out, exact fields) | Doesn't — you call each method |
| Wire serialization cost | JSON | JSON (unchanged) | Solves it (protobuf + HTTP/2) |
| Typed contract | Bolted on (OpenAPI) | Yes (SDL) | Yes (`.proto` IDL + codegen) |
| Writes | Native | `mutation` (no cross-subgraph atomicity) | Unary RPC |
| Streaming | SSE/WebSocket alongside | `subscription` (browser-facing, one direction) | Four call types incl. **bidirectional** |
| Cross-domain composition | Manual | Native | Not a feature |

**Correction — three common misconceptions:**
1. **GraphQL is not a data store.** It's an API contract + execution/composition layer in front of real datastores. A federated router splits one query, fans out to owning subgraphs, and stitches results.
2. **GraphQL is not read-only.** `query` / `mutation` / `subscription` are all first-class. Keeping writes on REST is an *adoption choice* justified by the lack of cross-subgraph atomicity — not a protocol limitation.
3. **"gRPC is for performance, GraphQL isn't"** is the wrong framing. They optimize **different axes**: GraphQL attacks round-trips and over-fetch; gRPC attacks wire serialization and connection multiplexing. That's why they *overlap* — both are typed, contract-first ways to invoke backend capability — and why the overlap is total except at the raw-wire and true-bidi-streaming corners.

**gRPC is not "REST with a better connection."** The persistent HTTP/2 connection is one of four pillars: HTTP/2 multiplexing, **protobuf binary serialization**, **IDL + generated stubs**, and **four call types** (unary, server-streaming, client-streaming, bidirectional). Only unary maps onto a REST request.

**What an RPC framework provides:** IDL + codegen, client stubs / server skeletons, serialization, transport and connection management, and cross-cutting concerns (deadlines, cancellation, retries, load balancing, discovery, auth, interceptors). Examples: gRPC, Thrift, Dubbo, Finagle.

**When RPC is preferred:** internal east-west traffic, high-volume latency-sensitive hot paths, strict evolving contracts across many teams/languages, **true bidirectional streaming**, polyglot environments needing consistent semantics.

**When it isn't:** public/browser-facing APIs, needing HTTP caching/CDN/human-readable payloads, fundamentally asynchronous work (that's messaging), and cross-domain read composition (federation already owns that lane).

**Operational gotcha:** gRPC pins long-lived HTTP/2 connections, which defeats naive L4 round-robin — you need L7-aware balancing or client-side LB. Also: deadline propagation must be threaded through call chains.

#### Where GraphQL's performance actually comes from

Ranked by how much it matters:

1. **Round-trip consolidation (largest).** One client request instead of N sequential ones. The win scales with per-round-trip latency — large for a distant browser, **near-zero for backend hops on a fast internal network**.
2. **Parallel fan-out at the router (modest).** Real, but only a win over a *naive* serial client, and it evaporates when the query has a dependency chain.
3. **DataLoader batching / dedup — damage control that becomes the main win.** See below.
4. **Over-fetch elimination.** Matters mostly for bandwidth-constrained clients.

**And on the other side of the ledger — it forfeits free HTTP/CDN caching**, because everything is `POST /graphql`.

**Correction — the router's caches optimize the router, not your data.**
- **Query plan / normalization cache** — skips parse/validate/plan on repeat operations. Saves **router CPU**; the backend fetches still happen every time.
- **Persisted queries (APQ)** — shrinks request payload, can restore some GET-cacheability. Not a data cache.
- **Response/entity caching** — the thing people mean, and the hard one: federated responses are often personalized and composed from subgraphs with different freshness, and **cross-subgraph invalidation is genuinely hard**.
- **DataLoader batching** — per-request only, caches nothing across requests.

**In practice (CG):** router guidance tells consumers to treat it as **non-caching by default**; entity/sub-entity caching is an enterprise-tier feature that the self-hosted OSS path deliberately deferred (a plugin spike closed without shipping it). Measured router overhead is ~4ms, and multi-service queries can be faster purely from **parallel planning**, not caching. If you want data cached, cache the **owning service**.

**The trade, stated honestly:** round-trip consolidation helps **cold** requests; caching helps **repeat** requests. So:
- **read-heavy, high-repeat, low-fan-out** (same popular object fetched a million times) → REST + CDN wins decisively
- **personalized, low-repeat, high-fan-out** (a logged-in user's tailored screen from many domains) → federation wins
That **repeat-rate × fan-out** interaction is the whole story, and it's why a mixed architecture is correct rather than indecisive.

#### DataLoader: batching vs dedup, and where the real win is

Two distinct behaviors:
- **Batching:** 30 entities → 30 distinct ids → one call instead of 30. Saves round-trips/overhead.
- **Dedup (coalescing):** 30 entities → only 8 **unique** ids → the downstream fetch is for **8**, not 30. Reduces actual work and payload.

Dedup is the bigger deal wherever **fan-in is high** (many listings share few dealers/service providers). The win scales with `N_references / M_unique_entities`, and the savings land on the *downstream service's* QPS and datastore load — not just the caller's latency.

**Mechanism.** Not cross-request batching. It batches the N **field-resolutions inside one query**:
1. resolving the field for item #1 calls `loader.load(id)`, which **queues the key and returns a promise** without calling anything
2. same for #2…#N; the loader **dedupes by key**
3. at dispatch, the batch function fires **once** with the unique keys and resolves all pending promises

**Dispatch timing differs by runtime:**
- **Node/graphql-js:** relies on the event loop — all `load()` calls happen in one tick, dispatch on the next microtask.
- **graphql-java / DGS:** no tick to lean on, so it does explicit **level-tracking** — an instrumentation counts expected field fetches at the current query level and calls `dispatchAll()` once they've queued. Deliberate bookkeeping, not thread scheduling.

**The Spring transaction question dissolves:** (1) the DataLoader is **request-scoped** — a fresh instance per GraphQL execution, mandatory so the dedup cache can't leak across requests; (2) there is **no distributed DB transaction** — the batch function makes a *remote read* to another service that isn't enrolled in your local `@Transactional` boundary. It's read composition, not a distributed write. `@BatchMapping` receives the whole `List<T>` so you can't accidentally write the N+1 version.

**In federation, dedup happens at two layers:** the router collects entity references across the result and sends **one `_entities` query** with an array of `{__typename, id}` representations; the owning subgraph's **entity resolver** then batches the actual data fetch with its own DataLoader. Whether the *router* dedupes identical representations is implementation-specific — but even if it passes all N, the subgraph's loader collapses them, so the fan-in win survives either way.

**Bound:** all of this is **per-request**. The same hot entity requested by two separate requests a second apart is fetched twice. Cross-request repeat load is a **cache-tier** job, not a DataLoader job.

#### Keeping the subgraph graph shallow, and `@provides`

Reference-resolution should be **flat**: a subgraph resolves its own domain and returns foreign entities as **keys**; the router does one hydration phase for all of them. Four things depend on flatness:
1. **Cross-query dedup** — all references to an entity type must flow through the same hydration layer, or you split one deduped fan-in into independent siloed ones
2. **Parallelism and timeout budget** — a nested call inside a subgraph is invisible to the router's per-field deadline
3. **Fail-open granularity** — the router can null just the failed field; a nested failure fails the whole parent field
4. **Single ownership** — otherwise every referencing service reimplements how to call, auth to, and shape a domain it doesn't own

**When a reference is the wrong tool: dependent keys.** If the foreign id is only knowable *after* another subgraph call plus business logic, a resolvable reference doesn't batch — it adds a **third sequential hop**. In that case keep it a plain scalar id and let the consumer hydrate in a second query. Conditional, business-logic-gated references are also awkward to model type-safely.

**`@provides` is a declaration, not a fetch.** It promises the router "these fields are already present in my response — don't hydrate them," typically paired with `@key(fields: "id", resolvable: false)`.
- **Worthwhile only when the subgraph already holds the data** as part of its own job → zero extra calls, and the consumer saves a round-trip.
- **If satisfying it requires an extra fetch, don't** — you've relocated a hop into a place with no router timeout/circuit-breaker coverage and no cross-subgraph batching.
- **Subgraphs never call back into the router.** Resolution flows strictly downward. Re-entrancy is cyclic, wastes plan/validate work for a known id, doubles router QPS, and complicates auth/trace propagation. If a subgraph must fetch, it calls the **owning service directly**.

#### The placement rule: whose logic, not logic-vs-data

"Logic is logic, data is data" is too clean — taken literally it exiles legitimate **derived domain attributes** from their own domain, leaving them homeless in an orchestration layer. The correct axis is **ownership**:

| Kind of logic | Correct home |
|---|---|
| Domain-semantic derivation over **one domain's own data** (a computed flag, a tier, a computed fee) | That domain's service/subgraph — computed or not, a domain owns its facts *and* their derivations |
| **Cross-domain composition** (join several domains into a page shape) | A service that owns that composition. Never a domain subgraph |
| **Presentation / page logic** (which banner, which layout, A/B wiring) | The app / presentation layer |

Corollaries worth keeping:
- **"Everyone already calls it" is gravity, not architecture.** Marginal cost is a legitimate tiebreaker *between* correct homes; it can never *make* a home correct. Otherwise the busiest junction accretes all logic and becomes a distributed monolith with a single critical-path chokepoint.
- **Single-source-of-truth is a code-organization goal with three solutions** — a shared library, one owning service everyone calls, or a subgraph. Same-language pure logic: a **library** is far cheaper. Cross-language consumers: **call the owning service** rather than each reimplementing. Only pick a subgraph when the field is a domain fact and that domain is already in the graph.
- **A composition/orchestration service is defined by what it owns, not by the fact that it fans out.** "Orchestrator" names a mechanism; identity is ownership.

#### The threshold question: when is federation worth it at all?

GraphQL solves a **client × service fan-out** problem, not a raw-throughput problem. Without a composition layer, every client re-implements the same fan-out, stitching, and error handling.

**You need it when the cost of N clients each composing M fragmented services exceeds the cost of running a federation platform.** Below that threshold it's a liability: the router becomes critical-path infrastructure, you take on schema composition, resolver-waterfall latency, and a new observability surface — to solve a problem you don't have.

The strongest argument isn't even latency — it's **decoupling frontend iteration from backend deploys**. So the real tell is organizational: **how often does a UI change require a backend change today?** If endpoints are stable and UI changes rarely need new shapes, even that argument evaporates.

And a depth caveat that is also an **organizational signal**: a subgraph tree that *wants* to be deep usually means the domain boundaries are drawn wrong. When you hit the depth wall, the first question is "should this even be three subgraphs?" — not "how do I optimize the resolver."

**Lock-in framing:** REST, federation, RPC, CQRS, event sourcing, and standardizing on Kafka are all platforms with exit costs. There is no commitment-free option at this layer — only *choosing which lock-in matches the dominant workload*. Weight by blast radius: event sourcing reaches the definition of truth (highest bar), federation reaches client contracts + router, gRPC reaches service edges and is **reversible per-edge** (lowest of the three).

---

### 2.3 Derived-Store Materialization

How a search index or read-optimized store is built, kept fresh, and recovered.

#### The layered truth model

```text
MySQL (transactional source of truth)
  → derived document store (denormalized read model)
    → Kafka change events
      → search index / cache (derived, bounded-staleness)
```

**Every downstream store is a derivative.** Truth lives upstream; the job of the system is to keep staleness **bounded and recoverable** — never to mistake a derivative for the source.

**In practice (CG):** MySQL is the only place for listing writes; LDS is an explicitly read-only denormalized Mongo store fed by a synchronizer; search consumes LDS-derived Kafka updates. A given field's "source of truth for ingestion" (LDS) is not the same as the "source of truth for writes" (MySQL) — keep those distinct.

#### Build-from-source vs dump-a-replica

The instinct "just snapshot a running node's index" is mechanically simpler and architecturally wrong. Six reasons:

1. **A node's index is a cache of a computation, not data** — it's baseline load plus hours of incremental application, including any missed messages, mis-applied updates, or partial corruption. Dumping it backs up a copy of a copy, with the drift baked in.
2. **Which node?** N nodes applying a change stream independently are at slightly different offsets and are **not** byte-identical. Dumping one blesses its particular state as canonical.
3. **No clean resume point.** Recovery needs the snapshot paired with the exact **change-log offset** it corresponds to. A live index has no crisp marker (mid-application, per-segment), so you can't safely replay from it without risking missed or double-applied changes.
4. **Physical coupling.** A node dump is tied to the on-disk/segment format and version. Uploading the **logical dataset (JSON) *and* the physical index** means the index can always be rebuilt if the format moves.
5. **It preserves the single-fetch property.** The reason the ingestor exists is so the source is queried **once, centrally** instead of once per node. "Nodes dump themselves" recreates the fan-out or is circular.
6. **Completeness.** Only a fresh total query against the source guarantees the snapshot is the complete, correct current set (including deletions/closures).

**In practice (CG):** legacy search once had 21 nodes each querying for the same ~4.5M listings, adding ~10 minutes per deploy. Extracting a dedicated ingestor that fetches once and publishes an artifact removed both problems.

#### Snapshot anatomy and cadence

- **Who:** a **separate service**, and within it a **single leader-elected instance** (see Lease-Based Execution). Not the primary node, not every node.
- **How often:** cron, a few times a day (e.g. `0 0 7,12,17 * * *`), plus a manual trigger. The cadence is deliberately conservative because **each full generation is a full dump that pressures the source** — the mitigation for staleness is widening the lookback window, not adding runs.
- **Chunking:** producer/consumer with a bounded queue — parallel per-group source queries push batches; upload workers drain them. **Logical batching** (e.g. 50 groups per object) avoids a swarm of tiny objects. The physical index is closed, zipped, and uploaded as **one archive at the end**, followed by a metadata file written **last as the completion marker**.
- **Versioning:** timestamped path prefixes (`.../<region>/<yy-MM-dd_HH:mm:ss>/...`), never overwritten, each carrying its **change-log offset** so a booting node knows where to resume.
- **TTL:** freshness comes from generating a newer version and pointing at the latest — old-version expiry is a **lifecycle-policy** concern and a common cost leak if unset.

#### Correction — snapshots don't re-base the fleet

A new snapshot landing does **not** trigger fleet recreation. A node adopts a snapshot only when it **starts** (deploy, restart, bounce, scale-up, pod replacement). A long-running pod keeps its on-disk index and stays current purely by **continuous change-stream consumption**.

So the division of labor is:

| Mechanism | Role |
|---|---|
| **Live change-stream consumption** | The *primary* freshness mechanism, running continuously on every node |
| **Periodic from-source snapshot** | *Bootstrap and recovery* — fast startup, plus a known-good baseline + offset so a booting node replays only a short tail |

Consequently, a periodic from-source rebuild corrects accumulated corruption or missed messages **only for nodes that restart**. That's exactly why the standard mitigation for a stale or corrupted node is **bounce it** — a targeted re-base on the latest clean snapshot plus replay.

**One-liner:** nodes hold a derivative (baseline + X hours of changes) that by construction is not a source of truth; drift is an accepted, bounded tradeoff; the from-source snapshot exists to reset it with an authoritative, resumable baseline.

#### Recovery patterns

| Pattern | Mechanism | Guarantee |
|---|---|---|
| **New-version build + alias swap** | Build into a new index version, then atomically repoint a stable alias | Safe cutover, easy rollback, background rebuild |
| **Snapshot + offset replay** | Load artifact at offset X, replay the change log from X | Bounded, resumable catch-up |
| **Watermark checkpoint** | Store progress in durable object storage; advance **only after** successful upserts; upsert by id (idempotent) | Failed runs simply re-read from the old watermark |
| **Rebuild-from-source as backstop** | Periodic total refresh | Catches deletions and completeness gaps incrementals can miss |

Deletes are the classic asymmetry: incremental change feeds often can't express "this no longer exists" reliably, so **full rebuilds are the completeness mechanism** for deletions/closures.

#### Ingestion sources and the two-path pattern

A mature ingestion platform usually needs two source paths, because the fetch shapes differ fundamentally:

| Path | Source | Read mechanism |
|---|---|---|
| **API/graph path** | Operational data already exposed as a service/subgraph | Paged queries, thin denormalized documents |
| **Analytical path** | Warehouse tables not exposed operationally | Table-format reads (Iceberg/Glue/Spark) writing directly to the index |

Design discipline that keeps the API path affordable: **keep the index document lean** — index only what's needed for filtering, sorting, and aggregation, and fetch rich display fields *after* search from the owning services. Also page/group the rebuild rather than issuing one giant query, and schedule rebuilds on cron rather than continuously.

**Text search config note:** dataset config chooses which fields are text and how they're mapped; the **analyzer attached to the field** does the actual tokenization. Common shape: an analyzed root text field plus a `.keyword` subfield for exact match and aggregation. Prefer explicit mappings over dynamic defaults.

**Sharding note:** shards/replicas should be **per-dataset tunable**, not one hardcoded value for every dataset.

#### Correction — "the ingestor is one process" is a real limitation, not a design ideal

Synchronous rebuild in a single leader pod means a wedged rebuild can stall with no recovery. The maturing direction is to **distribute rebuild work across pods via a queue** while keeping the *fetch-once* property. Worth knowing when reasoning about a platform's recovery story.

#### Materialization vs stream processing

The refetch-shaped CDC pattern keeps consumers **stateless**, which is why plain consumers suffice and a stream-processing framework isn't needed. The two triggers are independent:

- **Capability trigger (the real one):** you need fault-tolerant **state across events** — windowing, stream-stream joins within a time bound, pattern detection over sequences, large continuously-updated keyed state, or exactly-once stateful aggregates.
- **Cost trigger:** volume high enough to justify operating a stateful cluster.

Either alone can make plain consumers correct; both together make it obvious. Escalate by operational weight: **plain consumer → warehouse ELT (minutes of latency is fine) → Kafka Streams/ksqlDB (stateful, no cluster) → Flink (heavy state, CEP, batch+stream, multi-source), preferably managed.**

**In practice (CG):** analytical stream work is deferred to the warehouse via ELT (land raw in object storage, transform at rest); real-time freshness comes from invalidate-then-refetch. Flink appears only as a *future* idea for real-time index updates — the threshold hasn't been crossed.

---

## Part 3: Deep Tool Knowledge

For each tool: WHY it works the way it does, WHEN it's right, WHEN it breaks.

---

### PostgreSQL / MySQL (Relational)

**What it is:** Relational database with ACID transactions, rich SQL, and constraints.

**RIGHT choice when:** transactions across tables, complex queries (joins, CTEs, window functions), strong consistency, clear relationships and schema, DB-level constraints.

**WRONG choice when:** write throughput exceeds a single node and you can't shard cleanly; schema genuinely unknown/rapidly changing; simple KV lookup at extreme scale; document-shaped data with no cross-document queries.

**Alternatives:** DynamoDB/Cassandra (rich queries → horizontal write scaling), MongoDB (ACID → flexible schema), Redis (durability → sub-ms latency).

**Failure modes:**
- Connection exhaustion — fix with pooling (PgBouncer, HikariCP)
- Vacuum lag / MVCC bloat — tune autovacuum
- Lock contention from long transactions — keep transactions short, consider optimistic locking
- Replication lag serving stale reads — route critical reads to primary
- Index bloat — every index taxes every write

**Capacity reference:** single node ~5K writes/sec, ~50K indexed reads/sec; comfortable to ~2–5TB before ops (backup, vacuum, restore) hurt; ~500–1000 connections with pooling.

**Deciding question:** Need ACID or complex joins? → relational. Simple lookups at massive scale? → look elsewhere.

**In practice (CG):** relational remains the durable source of truth for core business data; new services get their own isolated schema. Analytics goes to the warehouse — never operational queries against it (orders-of-magnitude higher latency).

---

### Redis / Valkey

**What it is:** In-memory data structure store. Sub-millisecond latency. Rich structures beyond KV.

**RIGHT choice when:** sub-ms hot-path reads, data fits in memory (or eviction is acceptable), rich structures (sorted sets, HyperLogLog, streams, pub/sub), cache in front of a database, session storage, rate-limit counters, simple distributed locks, shared state across instances.

**WRONG choice when:** data must be durable; source of truth for financial data; data doesn't fit and eviction is unacceptable; complex queries; **or a single service where an in-memory cache is simpler with no network hop**.

**Correction — Redis is not a persistence layer.** Treat it as **ephemeral**: typical config fsyncs ~once per second (not per write), journals may not be backed up, and there may be **no restore process** for corruption. Anything durable belongs in a real database. Recommended uses: session/form/cached ephemeral state.

**Valkey vs Redis:** Valkey is a **Redis-compatible engine**, not a different technology. Clients stay in the Redis ecosystem (e.g. Redisson `RMap`/`RMapCache`); the engine/infra moves to managed ElastiCache-Valkey, which is meaningfully cheaper per GB with a much lower idle-cost floor. When people say "Redis" colloquially, check whether they mean the **client/API** or the **engine**.

**Failure modes:**
- Memory exhaustion → eviction or OOM. Set `maxmemory` + policy, monitor.
- Single-threaded blocking — never `KEYS` in production; use `SCAN`.
- Split-brain on partition — quorum config, Sentinel.
- Thundering herd on restart (cold cache) — warm before taking traffic, stagger TTLs.
- Replication lag — don't read replicas on consistency-critical paths.
- **Large values are a trap** — a >500KB payload can turn a ~1ms op into seconds and exhaust the connection pool. Cap object size; move oversized entries to a local cache.

**Capacity reference:** 100K–500K ops/sec per node; ~0.5–1ms per op; memory is what you buy.

**Deciding question:** Multiple instances need shared fast state? → Redis/Valkey. Single instance hot path? → in-memory. Can't lose it? → not Redis.

---

### MongoDB / DynamoDB (Document / NoSQL)

**What they are:** Schema-flexible stores optimized for known access patterns and horizontal scaling.

**RIGHT choice when:** naturally document-shaped data (nested objects/arrays, no cross-document joins), access patterns known at design time (mandatory for DynamoDB), horizontal write scaling, frequently evolving schema, single-digit-ms latency at scale.

**WRONG choice when:** multi-document transactions are central, complex ad-hoc joins/aggregations, access patterns unknown or frequently changing, highly relational data.

#### Three distinct usage patterns (don't collapse them into "persistent cache")

| Pattern | Role | Note |
|---|---|---|
| **Derived / denormalized read store** | ETL from the relational source into one document per entity, read-only, fronted by an API | Looks cache-like, but chosen for **durability and fast recovery**, not speed |
| **Primary datastore for a document-shaped domain** | System of record for that domain | e.g. reviews with nested categories, scores, votes — forced into flat tables and joins by an ORM |
| **Operational/agent state** | Conversation history, working memory, observability spans | Durable operational state, often high write volume |

The real cache tier sits **in front** of Mongo (Redis/Valkey), which is where the "fast but ephemeral, size-limited" tradeoff actually lives.

#### Correction — bulk operations are recommended, not discouraged

Two different axes get conflated:

| Concept | Preference | Why |
|---|---|---|
| Multi-document ACID transaction | **Avoid / design around** | Embed related data so single-document atomicity suffices |
| Single-doc update-in-place | **Prefer** over delete+insert | Faster, uses padding |
| **Bulk write (batched ops)** | **Strongly prefer** for volume | One command, many independent atomic ops → large CPU/IO savings |
| Per-record loop of `save()` | **Anti-pattern** | Explodes op count and CPU |

So a relational habit of batching 30–50 rows per read/update **translates directly** via `bulkWrite`/`BulkOperations`. A bulk write is *not* a long transaction — each op is still an independent atomic single-document write.
**In practice (CG):** replacing a per-record `foreach Save()` (millions of ops/day) with `BulkPersist(batchSize: 500)` was projected to cut CPU 40–50% and DB operations ~99%; another migration replaced 2000 individual find+write calls per batch with one unordered bulk upsert.

#### Optimization checklist

- **Document design:** field names repeat in every document — use terse names, omit null/empty fields, stay well under the document size limit, avoid unbounded arrays.
- **Indexing:** index only proven hot queries; every index taxes writes. More than ~4 indexes on a collection is a design smell. Prefer high-cardinality leading fields and compound/covered indexes for the hottest queries. Create indexes manually across environments **before** deploying code — many threads creating the same index concurrently can take a cluster down.
- **Write pressure:** strip large payloads before write; use TTL indexes for retention; drop unused indexes. One CG investigation combined TTL/retention, bulk writes, index cleanup, and compound indexes to move a cluster from 92% → ~72% CPU and defer a costly tier upgrade.
- **Pooling:** see the pool math in Part 2.1. Non-prod and prod need different `min/maxPoolSize`; each client gets its own pool.
- **Platform standards:** Terraform-provisioned, standard cluster families per environment, **autoscaling disabled** to avoid runaway cost, periodic non-prod refresh via snapshot/restore.

**Engine-cache note:** WiredTiger's cache (like InnoDB's buffer pool) is fundamental and always on — distinct from the optional ORM second-level cache that is often disabled.

**Cost note:** the "MongoDB by default" answer is worth re-checking periodically — a managed dedicated-tier floor per cluster is misaligned with a fleet of low-traffic/non-prod clusters, which is why a cheaper compatible engine may become the default for new workloads with the managed option kept as a justified exception.

**Deciding question:** Document-shaped with known access patterns? → document store. Joins, transactions, ad-hoc queries? → relational.

---

### Kafka

**What it is:** Distributed event streaming platform. Append-only partitioned log with configurable retention.

**RIGHT choice when:** replay for recovery/reprocessing, multiple independent consumers of the same data, ordering within a partition, high-throughput event streaming, decoupling with retention, CDC pipelines / event sourcing / lake ingestion.

**WRONG choice when:** single consumer + simple low-volume work queue; need per-message routing/filtering (RabbitMQ); need request-reply; need neither replay nor multiple consumers (SQS is simpler); sub-ms latency required (Kafka batches by design).

**Alternatives:** SQS (managed, simple, no replay), RabbitMQ (routing, per-message ack, lower per-message latency), Redis Streams (lightweight), direct HTTP (simplest, coupled).

**How partitions actually work:**
- A topic is split into partitions, each an **independently ordered log** — order holds within a partition, never across the topic
- The **producer** picks the partition: default distribution, hash of a **key**, or a custom partitioner
- In a consumer group, **each partition is assigned to exactly one consumer at a time**; a consumer death triggers rebalance
- Throughput scales with partitions: N partitions support up to N-way parallel consumption
- **Replication factor** is what provides fault tolerance — partitions give parallelism, replicas give availability

**Sizing and skew:** see Sharding / Partitioning in Part 1 for the full sizing rule, hot-key remedies, and the consumer-count-mismatch failure.

**Failure modes:**
- Unbounded consumer lag — scale consumers, or fix the real bottleneck (often downstream, not Kafka)
- Rebalancing storms from unstable group membership — increase session timeout, stabilize membership
- Offset management bugs — commit before processing loses messages, after processing duplicates; use at-least-once + idempotent consumers
- Broker disk full — monitor, set time/size retention
- Uneven partition load from a hot key
- **Too many partitions/consumer groups** — metadata and metrics-cardinality overhead; excessive consumer-group churn has caused real monitoring and cluster pain

**Producer tuning for volume:** `batch.size`, `linger.ms`, `compression.type`.

**Topic creation note:** in non-prod, auto-created topics get **defaults** (e.g. 3 partitions / 3 replicas) — not traffic-driven autoscaling. Partition count can be **increased but never decreased**, so size it intentionally.

**Capacity reference:** 100K–500K msgs/sec per broker; 5–50ms end-to-end.

**Correction — the ZooKeeper dependency is going away.** Kafka historically used ZooKeeper for broker membership, topic config, and partition metadata; **KRaft** folds consensus inside Kafka itself. Kafka 4.0 removes ZooKeeper support, which means an old client library that can't do KRaft becomes the thing pinning your Kafka version. Greenfield clusters already run KRaft with no ZooKeeper.

**Deciding question:** Need replay OR multiple independent consumers? → Kafka. Simple fire-and-forget queue? → SQS. Routing/filtering? → RabbitMQ.

---

### Elasticsearch / OpenSearch

**What it is:** Distributed search and analytics engine built on Apache Lucene. Inverted index for full-text search.

**RIGHT choice when:** full-text search (fuzzy matching, relevance scoring, tokenization), complex aggregations on semi-structured data, flexible multi-field queries, log analytics, near-real-time index (seconds, not ms).

**WRONG choice when:** source of truth (**always pair with a primary store**), simple exact-match lookups, high write throughput with strong consistency, small datasets, transactions or relational integrity.

**Cluster model:** cluster → indices → **primary shards** (+ replicas) → documents. Text fields get an **inverted index** built by an analyzer (tokenize, term→doc postings, optional positions for phrase queries); numeric/date/geo fields get range-optimized structures. Queries fan out to relevant shards in parallel and merge.

**Correction — "slow to write, slow to index" is the wrong mental model for how it's maintained.** You don't write to it directly from the transactional DB on every change. The sustainable pattern is:
```text
relational source → derived read store → change events → search index
```
with a **dedicated ingestor** doing full rebuilds plus incremental updates. See Part 2.3 for the full materialization, snapshot, and recovery model.

**Failure modes:**
- Split brain on partition → index corruption. Proper discovery/quorum settings.
- GC pauses on large heaps → node appears dead → rebalancing storm. Keep heap ≤ ~32GB.
- **Shard explosion** — too many small shards, per-shard overhead. Target ~20–50GB per shard, and make shard/replica counts **per-dataset tunable** rather than one hardcoded default.
- **Mapping explosion** — dynamic mapping creating unbounded fields. Use explicit/strict mappings and cap total fields.
- Stale reads after write until segment refresh (default ~1s). Explicit refresh costs performance.
- **Unbounded index versions** — timestamped indices need automatic cleanup, or they accumulate.

**Alternatives:** relational full-text search (simpler ops, weaker relevance tuning), managed search products (typo-tolerance and speed, expensive at scale), lighter engines for smaller scale. OpenSearch is functionally an Elasticsearch fork.

**Platform pattern worth stealing:** make search a **self-service platform** rather than one bespoke service — per-dataset config (source query, searchable/filter/sort fields, rebuild schedule, change topics), timestamped indices with **alias-based atomic cutover**, automatic old-index cleanup, and a standard query interface. That turns one product's search service into infrastructure many teams can use, and separates platform concerns from product-specific business logic.

**Deciding question:** Do users type free-text and expect relevant fuzzy results? → search engine. Exact match on known fields? → database index.

---

### GraphQL Federation

**What it is:** An API contract + composition layer. A router takes one query, splits it across owning subgraphs, and stitches results. **Not a datastore.**

**RIGHT choice when:** many clients with different data needs, data fragmented across many services, cross-domain **read** composition for client/browser-facing surfaces, and you want frontend iteration decoupled from backend deploys.

**WRONG choice when:** one or few clients with stable endpoints; data isn't fragmented; backend-to-backend low-latency single-domain hops; **and when the goal is caching** (it forfeits free HTTP/CDN caching).

**Operational profile:** ~4ms router overhead; parallel query planning can make multi-service queries faster than serial client calls; treat it as **non-caching by default**; fail-open per-field timeouts and per-subgraph circuit breakers; retries usually disabled to avoid storms.

**Key mechanisms and their limits:** DataLoader dedup (per-request only), `@provides` (a declaration, only free if the data is already held), flat reference resolution, no cross-subgraph mutation atomicity. Full treatment in Part 2.2.

**Biggest operational risk:** the router becomes a **single point of failure on the critical path** for all composed traffic. Budget for that explicitly.

**Deciding question:** Are we past the client × service fan-out threshold on *this* surface? Client-facing and fragmented → yes. Internal, single-domain, latency-critical → no.

---

### gRPC

**What it is:** A contract-first RPC framework: typed remote **methods**, protobuf binary payloads, HTTP/2 multiplexed transport, four call types including bidirectional streaming.

**RIGHT choice when:** internal service-to-service (east-west), strong contracts across teams/languages via `.proto` + codegen, measured serialization- or connection-bound hot paths, **true bidirectional streaming**, polyglot clients needing consistent timeout/retry/auth semantics.

**WRONG choice when:** public/browser-facing APIs (needs gRPC-Web), simple CRUD where REST is clear enough, you need HTTP caching/CDN or human-readable payloads for debugging, the interaction is fundamentally asynchronous (use messaging), or cross-domain read composition (federation owns that).

**Failure modes:**
- Broken proto compatibility — never reuse field numbers; only add optional fields
- **L4 load balancer misconfiguration** — long-lived HTTP/2 connections pin to one backend; use L7 (Envoy) or client-side LB
- Missing deadline propagation across A→B→C chains
- Opaque payloads without protobuf-aware tooling

**Adoption discipline:** it overlaps heavily with federation (both are typed contract layers), so adopting it broadly alongside federation fragments the contract story into two schema/codegen toolchains. The non-redundant zones are **wire-level performance on a proven-hot internal hop** and **true bidirectional streaming**. Adopt **per-edge and benchmark-driven**, never as a blanket mandate — its lock-in is at the service edge and therefore reversible per-edge.

**Note:** gRPC often already exists in the infrastructure layer (metrics backends, OTLP collectors, cloud client libraries) even where it's absent from application service-to-service traffic. "We don't have gRPC" usually means "not between our own services."

**Deciding question:** Internal, typed, measured-hot or genuinely bidirectional? → gRPC. External, browser, or cross-domain composition? → REST/GraphQL.

---

### WebSocket and SSE

**What they are:** WebSocket is a persistent bidirectional channel over TCP (HTTP-upgraded). SSE is a persistent one-directional server→client stream over plain HTTP.

**Choose SSE when:** server→client push only, text/JSON, standard HTTP infrastructure, and the client's sends are temporally separated (request, then stream). You get stateless horizontal scaling, proxy/CDN traversal, standard auth, free auto-reconnect, and typed events.

**Choose WebSocket when:** the client must send **while** the server streams on one channel — dynamic subscribe/unsubscribe, acks/commands, presence/typing, interrupt-mid-generation — or you need **binary frames** or very high message rates.

**Choose polling when:** the refresh interval is known (dashboards on a 5s tick). Use deltas + `ETag`/`If-None-Match`.

**Correction — connection capacity is not a protocol difference.** Both are one long-lived TCP connection with near-identical per-connection cost; ceilings come from FDs, memory, and event-loop capacity, plus any application throttle. SSE's only genuine disadvantage is the **~6-connections-per-domain browser cap on HTTP/1.1**, which HTTP/2 multiplexing removes. **HTTP/2 Server Push is deprecated and not an alternative.**

**Operational concerns:**
- WebSocket servers are **stateful** — client↔server affinity means sticky sessions or a connection registry, and deploys break connections
- SSE is stateless *provided* conversation/session state lives in a shared store
- Both need buffering disabled and idle timeouts understood; heartbeats keep connections demonstrably alive
- A **proxied** stream pins two connections per active stream
- Watch for **zombie streams** — always wire client-disconnect to cancellation

**Scaling a streaming tier:** the right long-term shape is **route isolation** — put streaming routes on their own pods/target group (or a dedicated streaming BFF), because streaming is I/O-bound, long-lived, and **connection-count-scaled** while page-serving is CPU-bound, millisecond, and **RPS-scaled**. Two different resource profiles in one autoscaling group is the problem.

Sequence the fixes by cost: **per-pod concurrency limiter (503 early) → observability (an `active_streams` gauge) → autoscaling on a dual trigger (CPU for SSR + active-stream count for streaming) → route isolation.** Note that naive CPU or RPS signals are **blind to held-open streams** — ~99% idle streams keep CPU flat, so the first visible symptom of exhaustion is OOM or connection refusal. You must instrument the stream count explicitly.

**Deciding question:** Known interval → poll. Server-driven one-way → SSE. Simultaneous two-way, binary, or high-rate → WebSocket.

---

### S3 / Object Storage

**What it is:** Effectively infinite, highly durable blob storage. Store anything; retrieve by key.

**RIGHT choice when:** files/images/video/backups/logs/data lake, effectively infinite capacity, very high durability, write-once-read-many, and you don't need to query *inside* the objects.

**WRONG choice when:** low-latency random access on a hot path, querying/filtering/joining within objects, atomic partial updates (objects are immutable — replace entirely), small structured data that belongs in a database.

**The governance insight worth internalizing:** object storage is often the **one durable store a browser-facing leaf app is permitted to own**, precisely because of what it *lacks*. It stores files behind URLs, **enforces no schema**, and has **no complex querying or transactional capability** — so it "significantly reduces the risk of coupling between systems." A shared relational schema is a distributed-monolith risk; a shared bucket is just files. **Its limitations are the feature.**

**Three canonical roles:**

| Role | Pattern | Example |
|---|---|---|
| **Build-once artifact store** | Central process builds an artifact; consumers boot from it | Search dataset + zipped index that nodes bootstrap from (serves deploys *and* recovery) |
| **Durable checkpoint** | Watermark/offset advanced only after success; idempotent replay | Incremental-ingestion watermark; table-format warehouse storage |
| **Firehose landing buffer** | Producer lands raw; a loader moves it onward | Model input/output capture → loader → warehouse (minutes of latency) |

All three exploit the same property: big immutable things some other system reads or replays later.

**Transfer mechanics — two upload modes, and the size boundary is the whole game:**

| Object size | Approach | Why |
|---|---|---|
| < ~100 MB | Single `PutObject` | One round-trip is fine |
| ~100 MB – 5 GB | Multipart (parallel parts) | Parallelism + **per-part retry** |
| > 5 GB | Multipart **mandatory** | Single-PUT hard limit is 5 GB |
| Millions of tiny objects | **Aggregate first** | Per-request overhead dominates |

Multipart exists for **reliability and throughput**, not just capacity: parallel parts saturate bandwidth, a failed part retries alone rather than restarting a multi-GB upload, and interrupted uploads can resume (5 MB minimum part, up to 10,000 parts, 5 TB max object).

**Best practice: use the high-level transfer manager, not raw put/get.** Node `@aws-sdk/lib-storage`, Java `S3TransferManager`, boto3 `upload_file`, and the CLI all switch to multipart automatically above a configurable threshold (commonly ~8 MB) and manage part-splitting, concurrency, and retries. Hand-tune `partSize`/concurrency only for specific throughput or memory constraints.

**Don't conflate two kinds of "chunking":** *logical batching* (how many records per object — an application choice, to avoid a swarm of tiny objects) versus *transfer chunking* (how one object's bytes move — an SDK choice based on size).

**Read side:** `GetObject` streams the whole object; transfer managers parallelize large downloads via **ranged GETs**. **Range GETs** are also a first-class tool on their own — read a footer/index, resume a download, or let a columnar/table format read only the needed column chunks without pulling the whole file.

**Two gotchas that cost real money:**
1. **Abort incomplete multipart uploads** — orphaned parts are billed but invisible as normal objects. Add a lifecycle rule.
2. **Expire old versions/snapshots** — a thrice-daily snapshot bucket with no lifecycle rule grows forever.

**Security posture:** private buckets, no public objects — serve public reads through a **CDN/static domain** in front, which is also how you get *real* HTTP/CDN caching for assets. Access via IAM roles and **role assumption** rather than shared keys; provision via a canonical Terraform module (encrypted, versioned, access-controlled, with retention policies).

**Commonly underused capabilities worth knowing:**
- **Presigned URLs** — time-limited GET/PUT without credentials; the idiomatic way to let a client upload/download directly instead of proxying bytes through your app
- **Event notifications** (→ SNS/SQS/Lambda/EventBridge) — the event-driven alternative to polling a bucket
- **Intelligent-Tiering** — near-free cost win on artifact/capture buckets
- **Versioning** — config/artifact rollback
- **Cross-region replication** — a real DR question for a multi-region footprint

**Correctly unused for most shops:** Transfer Acceleration (co-located producers), Requester Pays, S3 Select (superseded by table formats + warehouse), Object Lambda, MRAP, Object Lock (unless compliance demands WORM).

**Deciding question:** Is it a blob? → object storage. Structured data I need to query? → database.

---

### ZooKeeper / etcd / Consul (Coordination)

**What they are:** Distributed coordination stores. A **small** replicated key-value store plus a **consensus protocol**, providing the primitives that are hard in a distributed system: leader election, membership/discovery, config with change notification, and distributed locks.

**The shared core:** a replicated log where a **majority (quorum)** must agree before a write commits. ZooKeeper uses **ZAB**; etcd and Consul use **Raft**. Clusters are almost always **3 or 5** nodes — 3 tolerates 1 failure, 5 tolerates 2; even numbers cost more for no extra tolerance. Consequence: **writes are expensive** (a round-trip to a majority), so these are for rarely-changing metadata, never bulk data.

**The two primitives that make them more than a tiny database:**
- **Watches** — subscribe to a key and be *notified* on change instead of polling
- **Ephemeral state tied to a session/lease** — if the client stops heartbeating, its keys **automatically disappear**. This is what makes leader election and liveness detection work (see Lease-Based Execution in Part 1).

**RIGHT choice when:** leader election, distributed config, service discovery, consensus-backed locks, cluster membership.
**WRONG choice when:** storing more than a few MB, high-throughput reads/writes, application data, or when a database advisory lock suffices.

| | ZooKeeper | etcd | Consul |
|---|---|---|---|
| Consensus | ZAB | Raft | Raft |
| Data model | Hierarchical znodes | Flat KV with prefixes | KV **+ service catalog** |
| Interface | Custom binary client libs | gRPC / HTTP | HTTP / **DNS** |
| Ephemeral primitive | Ephemeral znodes + sessions | Leases | Sessions with TTL |
| Sweet spot | Legacy big-data coordination | **Kubernetes' state store**; cloud-native config | Service discovery + health + multi-DC + mesh |

**Correction — three widespread misconceptions:**

1. **"Distributed systems always use ZooKeeper."** True for the ~2010–2018 big-data generation, now actively reversing. Kafka is moving to **KRaft**; other systems have replaced ZooKeeper with embedded Raft equivalents. ZooKeeper is being **displaced, not deprecated** — it still runs huge legacy fleets and is actively maintained; new systems just stop choosing it.

2. **"ZooKeeper is a single point of failure."** A ZooKeeper *ensemble* is explicitly fault-tolerant — same quorum model as etcd/Consul. The real objections are **operational weight** (a separate distributed system to deploy, tune, patch, and reason about) and **shared-fate coupling** (an external hard dependency whose degradation impairs every system leaning on it). That's the argument for absorbing consensus, not a fragility claim.

3. **"etcd is only for Kubernetes, and we don't use it."** etcd is general-purpose, and if you run Kubernetes you use it **constantly and invisibly** — every pod, service, secret, configmap, and deployment lives in etcd, and every autoscaling decision reads and writes it. Also: gRPC-native is why it's *pleasant to integrate*, not why Kubernetes chose it (simplicity + strong consistency + watches). The category of "needs an **external** coordinator" is shrinking as embedded Raft spreads, but within that category etcd dominates — and it's simultaneously among the most-deployed coordination stores anywhere.

**Also worth separating:** Consul is not only a mesh tool. Its four pillars are discovery, health checking, **KV**, and multi-datacenter federation — and the KV + sessions half is what powers application **leader election**, often the heaviest internal use.

**Failure modes:**
- **Session expiry / lost session** — a coordinator blip can leave a client unable to recover without a restart. The client **must** re-initialize its session on coordinator errors.
- Transient dual-leader behavior during a partition — consensus prevents divergence, but understand the TTL window and make singleton work idempotent or fenced.
- Storage misuse — these are not databases.
- **Forgotten criticality** — a quiet coordination store is a hard dependency of loud, revenue-critical services. Mark it P1 and alert on it.

**Deciding question:** Need distributed coordination (leader election, locks, config, discovery)? → a coordination store, sized 3–5 nodes. Storing application data? → a database.

**Industry trend:** toward **self-contained consensus** — absorb the coordinator (KRaft and friends) rather than depend on an external one. Fewer moving parts, fewer hidden coupling surfaces.

---

### CDN (Content Delivery Network)

**What it is:** Globally distributed cache of content served from edge locations near users.

**RIGHT choice when:** static content for a global audience, latency reduction for distributed users, offloading origin traffic, semi-static cacheable API responses.

**WRONG choice when:** highly personalized per-request content (cache-key explosion, low hit rate), content changing every request, single-region users, or strong consistency requirements.

**Pull vs push:** pull fetches from origin on miss (simpler, first request is cold); push preloads proactively (good for predictable large content).

**Invalidation options:** TTL (accept staleness), purge API (explicit), **versioned URLs** (`/static/app.v42.js` — never invalidate, just deploy a new name). Versioned URLs are the lowest-risk choice.

**Why this matters beyond assets:** the CDN/client edge is the **only place free HTTP caching lives**. Internal service-to-service hops have no edge, and a `POST`-based API edge forfeits it. So if a hot, static, high-repeat resource needs caching, the two real levers are **CDN at the client edge** and an **explicit cache tier at the owning service** — nothing in between recovers it for free.

**Deciding question:** Static/semi-static AND multi-region? → CDN. Dynamic, personalized, single-region? → origin.

---

### Flink / Stream Processing

**What it is:** Distributed stream processing framework for unbounded data with fault-tolerant state.

**The one thing it is fundamentally for:** computing a result that depends on **many events**, **continuously**, at **low latency**, where intermediate state **survives failure exactly-once**. Remove any one of those four and something simpler wins.

**Capability triggers (the real "why"):**
1. **Windowed aggregation** — running counts/sums/rates over a bounded slice of an unbounded stream; requires recoverable buffered state
2. **Stream-to-stream joins** within a time bound — must hold both sides' recent events in recoverable state
3. **Complex event processing** — ordered pattern detection ("A then B but not C within T"), requires per-key partial-match state
4. **Large continuously-updated keyed state** — millions of keys, needs a spillable checkpointed backend (RocksDB), not a HashMap
5. **Exactly-once stateful pipelines** where state and output must be atomically consistent with input offsets

**Situational triggers (the "when"):** latency requirement is seconds not minutes (which disqualifies warehouse ELT); the same computation is reused by many consumers (compute once centrally); **reprocessing/replay** through updated logic matters (savepoints, unified batch+stream); state outgrows a single process.

**Key concepts:** tumbling/sliding/session windows; **watermarks** (event-time progress, when a window is complete); late-event handling (side output or update); **checkpointing** for exactly-once recovery; state backends.

**When NOT to jump, and what to use instead:**

| Situation | Right tool |
|---|---|
| Per-event stateless transform | Plain Kafka consumer |
| CDC "id changed → refetch truth" | Consumer + refetch (**this shape avoids needing stream state at all**) |
| Analytics tolerating minutes of latency | Warehouse ELT (land raw, transform at rest) |
| Modest stateful streaming inside Kafka | **Kafka Streams / ksqlDB** — windowing, joins, fault-tolerant state as a *library*, no cluster |
| Heavy state, CEP, big scale, batch+stream, multi-source | Flink — preferably **managed** to shed ops cost |

**The escalation ladder (climb only as far as the workload forces):** plain consumer → warehouse ELT → Kafka Streams/ksqlDB → Flink.

**Two independent triggers, and why keeping them separate matters:** if **volume** grows but the pattern stays per-event and stateless, you still don't need Flink — scale consumers horizontally. If a **windowing/join/pattern requirement** appears even at *small* volume, low volume no longer saves you. Capability is the real trigger; volume is only the cost trigger.

**Deciding question:** Do I need fault-tolerant state **across** events, computed continuously at low latency with exactly-once correctness? → stream processor. Simple per-event transform? → consumer. Batch analytics? → warehouse.

---

## Part 4: Constraint → Solution Mapping (Quick Reference)

| Constraint | Pattern | Tool options |
|---|---|---|
| High read volume | Cache | In-memory → Redis/Valkey → CDN (layered) |
| High write burst (async OK) | Queue/buffer | Kafka (replay) vs SQS (simple) |
| High write burst (sync required) | Scale write path | Shard, batch+flush, back-pressure (429) |
| Slow processing | Async job | Message queue + worker pool |
| Read/write contention | Separation | Read replica, CQRS, materialized views |
| Data growing unbounded | Tiering | Hot/warm/cold, TTL, archive to object storage |
| External service unreliable | Resilience | Circuit breaker + timeout + fail-open + fallback |
| Multiple services need same data | Shared state | Redis, event-driven invalidation, CDC |
| Need audit trail | Append-only log | Event table, Kafka topic, event sourcing |
| Caller needs durability guarantee | Sync persist | Must hit the durable store before 200 |
| Caller only needs acceptance | Fast-ack + async | Accept into fast store, 200, persist async, reconcile |
| Business operation spans services | Distributed transaction | Saga (simple) or TC/C (parallel) |
| Global users, static content | Edge delivery | CDN + versioned URLs |
| Need unique time-sortable IDs | Distributed ID gen | Snowflake-style (64-bit, no coordination) |
| Need full-text search | Search index | Elasticsearch/OpenSearch (secondary, never source of truth) |
| Need coordination / leader election | Consensus service | ZooKeeper / etcd / Consul (3–5 nodes) |
| **Known refresh interval, client-driven** | Polling | HTTP + `ETag`/deltas |
| **Server must push immediately, one direction** | Streaming | SSE (stateless, proxy-friendly) |
| **Simultaneous two-way / binary / high-rate** | Bidirectional channel | WebSocket (stateful — plan sticky sessions) |
| **Content slow to produce, revealed progressively** | Stream it | SSE with typed events |
| **N clients each composing M fragmented services** | Composition layer | GraphQL Federation (shallow graph) |
| **Same entity referenced many times in one request** | Intra-request dedup | DataLoader batch loader |
| **Same entity re-requested across requests** | Cache the owner | Redis/Valkey **at the owning service** |
| **Proven-hot internal M2M hop (benchmarked)** | Binary RPC | gRPC (per-edge, L7 LB required) |
| **True bidirectional server-to-server streaming** | RPC streaming | gRPC bidi |
| **Derived store must survive restart/redeploy fast** | Artifact bootstrap | Object storage snapshot + change-log offset |
| **Derived store index must swap safely** | Versioned index + alias | Build new version → atomic alias repoint |
| **Incremental ingestion must be replay-safe** | Durable watermark | Advance only after successful idempotent upsert |
| **Incrementals can't express deletion** | Completeness backstop | Periodic full rebuild from source |
| **Streaming workload starves page-serving pods** | Route isolation | Separate target group / streaming BFF |
| **Autoscaler blind to held-open connections** | Custom metric | `active_streams` gauge + dual trigger (CPU + streams) |
| **Long-held connections exhaust a scarce upstream** | Load shedding | Per-pod concurrency cap, 503 early, client handling |
| **Handshake cost dominates short queries** | Connection pooling | Driver pool with tuned `min`/`maxPoolSize` |
| **Need state across events (windows/joins/patterns)** | Stream processing | Kafka Streams (no cluster) → Flink (heavy state) |
| **Analytics tolerating minutes of latency** | ELT | Land raw in object storage → warehouse transform |
| **Exactly one instance must run a job** | Leader election | Session + KV lock (Consul/etcd/ZK), TTL heartbeat |
| **Large file transfer must be reliable** | Multipart upload | SDK transfer manager (parallel parts, per-part retry) |
| **Swarm of tiny objects** | Logical batching | Aggregate records into right-sized objects |
| **Client needs direct upload/download** | Presigned URL | Time-limited URL, no proxying bytes through the app |
| **Orphaned cost in object storage** | Lifecycle rules | Expire old versions + abort incomplete multipart |

---

## Part 5: Tradeoff Pairs (One-Liners)

| Decision | A | B | The deciding question |
|---|---|---|---|
| Relational vs document | ACID, joins, constraints | Flexible schema, horizontal scale | Need transactions or joins? → relational |
| Redis vs in-memory cache | Shared across instances | Zero latency, no serde | Multiple instances need the same view? → Redis |
| Kafka vs SQS | Replay, ordering, multi-consumer | Managed, simple, cheap | Need replay or multiple consumers? → Kafka |
| REST vs gRPC | Human-readable, browser-compatible | Binary, typed, streaming | External API? → REST. Internal + hot? → gRPC |
| Sync vs async | Simple, immediate consistency | Decoupled, absorbs burst | User waiting? → Sync |
| Push vs pull fan-out | Fast reads (pre-built) | No wasted writes | Most users low-follower? → Push, hybrid for celebrities |
| Strong vs eventual consistency | Correct, higher latency | Fast, stale possible | Money/inventory? → Strong |
| Monolith vs microservice | Simple ops, fast iteration | Independent scale and ownership | Early stage? → Monolith |
| Optimistic vs pessimistic locking | No lock held, conflict on write | Lock held, blocks others | Low conflict? → Optimistic |
| **SSE vs WebSocket** | Stateless, proxy-friendly, one-way | Bidirectional, binary, high-rate | Client sends *while* server streams? → WebSocket |
| **Polling vs streaming** | Simple, cacheable, client-driven | Immediate, server-driven | Is the interval known? → Poll |
| **REST+CDN vs federation** | Free edge caching on repeats | Composition on cold, fragmented reads | High repeat + low fan-out? → REST+CDN |
| **Batching vs dedup** | Fewer round-trips | Less downstream **work** | Is fan-in high (many refs → few entities)? → dedup is the real win |
| **Entity reference vs `@provides`** | Router batches and hydrates | Fields returned inline, zero hydration | Does the subgraph already hold the data? → `@provides` |
| **Reference vs scalar id** | Router-hydrated, batched | Consumer hydrates in a second query | Is the key **dependent** on a prior call? → scalar id |
| **Shared library vs owning service** | Cheapest for same-language pure logic | Works across languages | Are consumers polyglot? → owning service |
| **Fewer vs more partitions** | Less metadata/coordination overhead | Headroom for consumer scale-up | Size to *max useful consumers*, not current pods |
| **Global order vs throughput** | 1 partition, fully serialized | N partitions keyed by entity | Need per-entity order only? → key by entity |
| **Build-from-source vs dump a node** | Authoritative, resumable, format-independent | Mechanically simpler | Is the node a derivative? → always build from source |
| **Snapshot cadence vs source load** | Fresher baseline | Less pressure on the source | Widen the lookback window before adding runs |
| **Multi-doc transaction vs bulk write** | Cross-document atomicity | Throughput, one command many atomic ops | Can the document embed it? → bulk write |
| **Write-through vs write+invalidate** | Cache warm immediately | No cache/DB divergence on partial failure | Durable business data? → write DB, invalidate |
| **TTL vs event invalidation** | Simple, bounded staleness | Fresher, more moving parts | Use **both**: events with a long TTL backstop |
| **Local L1 vs shared L2** | Microsecond, no hop | One consistent view | Is the object large or hot-and-immutable? → local |
| **Consensus store vs embedded Raft** | Reusable across systems | No external dependency to operate | Building the system itself? → embed |
| **Stream processor vs consumer** | State across events | Simplicity | Do you need windows/joins/patterns? → processor |

---

## Part 6: Recurring Meta-Principles

The reasoning that generalizes beyond any single tool.

**1. Truth lives upstream; everything downstream is a bounded-staleness derivative.**
The job of a system is to keep that staleness **bounded and recoverable** — never to promote a derivative into the source. Applies to search indices, caches, read models, and node-local state alike. Corollary: never seed a backup from a replica, because one node's drift becomes everyone's starting point.

**2. Logic belongs with whoever owns the data it derives from.**
Domain-semantic derivations belong in their domain (computed or not). Cross-domain composition belongs to a service that owns that composition. Presentation belongs to the app. The anti-pattern is a shared concern owned in the wrong place — and it wears different costumes at different zoom levels (a monolith, a bespoke orchestrator, a catch-all subgraph, a deep subgraph re-resolving someone else's entity).

**3. Convenience is a tiebreaker, never a justification.**
"It's already wired up" can legitimately choose *between* correct homes; it can never *make* a home correct. Otherwise the busiest junction accretes all logic and becomes a distributed monolith with a single critical-path chokepoint.

**4. Identify the real bottleneck before adding capacity.**
More partitions don't help if the constraint is a downstream API. More replicas don't help if the pool is exhausted by latency. Every scaling lever should follow a measurement, not an intuition.

**5. Distinguish the capability trigger from the cost trigger.**
Volume tells you *when* something becomes expensive; capability tells you *whether* the simpler tool can do the job at all. Adopt heavy platforms only when a capability is genuinely required (state across events, true bidi streaming, cross-domain composition) — then climb the operational-weight ladder only as far as forced.

**6. Every platform has an exit cost — choose which lock-in fits the dominant workload.**
There is no commitment-free option at the architecture layer. Weight by blast radius and reversibility: event sourcing reaches the definition of truth, a composition platform reaches client contracts, a transport choice reaches service edges and is reversible per-edge.

**7. Consequences are not justifications.**
Decomposition is justified by **boundary and independence** (independent deploy, scale, failure domain); the resilience and observability wins are **dividends the boundary pays**, because those controls only become expressible once the concern has its own home. Mistaking the dividend for the reason leads to decomposing the next thing "for speed" — and decomposition usually makes a single request *slower*.

**8. Ask what the failure path costs, not just the happy path.**
A circuit breaker that dumps cache traffic onto the primary datastore. A load shedder that 503s the user. A fail-open timeout that returns a null field. Every resilience mechanism relocates load rather than deleting it — know where it lands.

**9. Symmetry and interchangeability are features.**
Leader election works precisely *because* nodes are interchangeable: zero config, automatic failover, race-safety for free. Optimizing *which* node wins would solve a problem that doesn't exist at the cost of the simplicity that makes it reliable.

**10. Prefer designs that keep the workload simple enough that heavy tooling never becomes necessary.**
Invalidate-then-refetch keeps consumers stateless, which is why a stream processor isn't needed. Keeping numbers in a hydrated card rather than generated prose is why a text/data mismatch stays rare. The best architectural move is often the one that removes the need for a later one.

---

## Part 7: Corrections Index

Claims that are commonly stated and wrong or overstated. Each is expanded in place above.

| Common claim | The accurate version |
|---|---|
| "WebSocket holds far more concurrent connections than SSE" | Near-identical per-connection cost; capacity is FDs/memory/event-loop plus app throttles. SSE's only real limit is the ~6-per-domain HTTP/1.1 browser cap, removed by HTTP/2 |
| "A low stream cap is an SSE limitation" | It's an application throttle protecting a scarce upstream (LLM concurrency, per-stream memory) |
| "HTTP/2 push can replace SSE" | Deprecated in browsers; not an alternative |
| "Streaming is needed because the payload is large" | It's needed because the payload is **slow to produce and revealed progressively** |
| "DB caches are usually disabled" | Engine caches (buffer pool, WiredTiger) are always on; the *ORM second-level/query* cache is what's often disabled |
| "Write-through gives strong consistency" | Cache and DB writes aren't atomic; prefer write-DB-then-invalidate |
| "Redis is a persistence layer" | Treat as ephemeral: ~1s fsync, journals may not be backed up, restore may not exist |
| "A distributed cache is always better than local" | A >500KB value can turn ~1ms into seconds and exhaust the pool; local was the fix |
| "Going direct instead of via the router restores free caching" | Free edge caching lives only at the **client edge**; internal hops never had it. Caching and routing are orthogonal axes |
| "The router's caching improves data performance" | Plan/normalization cache saves **router CPU**; entity/response caching is the hard, often-unbuilt part |
| "MongoDB prefers many small ops, so avoid bulk" | Conflates multi-doc **transactions** (avoid) with **bulk writes** (strongly preferred) |
| "Elasticsearch is slow to write, so keep it in sync directly" | Maintain it as a derived store: relational → read model → change events → index, with a dedicated ingestor |
| "Elasticsearch/OpenSearch can be the source of truth" | Always pair with a primary store; rebuild-from-source is the recovery model |
| "Snapshot the running index — simpler than rebuilding" | A node index is a derivative with baked-in drift, no crisp resume offset, and physical format coupling |
| "A new snapshot re-bases the fleet" | Nodes adopt a snapshot only on **startup**; continuous change consumption is the freshness mechanism |
| "One consumer with two partitions processes them in parallel" | Not guaranteed by Kafka; parallelism comes from more consumer **instances** |
| "partitions = consumers is the rule" | Conservative default; size to **max useful consumers** with headroom, and avoid over-partitioning overhead |
| "GraphQL is a data store / read-only / can't do writes" | It's a contract + composition layer; `mutation` and `subscription` are first-class. Writes stay on REST because federation has **no cross-subgraph atomicity** |
| "gRPC is REST over a better connection" | Four pillars: HTTP/2 multiplexing, protobuf, IDL+codegen, four call types incl. bidirectional |
| "gRPC is about performance, GraphQL isn't" | Different axes: GraphQL attacks round-trips/over-fetch, gRPC attacks wire serialization |
| "@provides means the subgraph fetches the entity" | It's a **declaration** that fields are already present (`resolvable: false`); only free if the data is already held |
| "A subgraph can call back into the router" | Resolution flows strictly downward; if a subgraph must fetch, it calls the owning service directly |
| "Logic is logic, data is data" | Too clean — it exiles legitimate derived domain attributes. The axis is **whose** logic |
| "Distributed systems always use ZooKeeper" | Being displaced (KRaft and equivalents); still maintained and widely deployed, just not chosen for new systems |
| "ZooKeeper is a single point of failure" | The ensemble is quorum-fault-tolerant; the real costs are operational weight and shared-fate coupling |
| "etcd is only for Kubernetes, and we don't use it" | If you run Kubernetes, you use it constantly and invisibly — it stores all cluster state |
| "Consul is a service mesh tool" | Four pillars: discovery, health, **KV**, multi-DC. KV+sessions powers leader election, often the heaviest use |
| "Decomposition was justified by performance" | Justified by boundary/independence; resilience and observability are dividends the boundary pays |
| "Chunked upload means the SDK split the file" | Distinguish **logical batching** (records per object) from **transfer chunking** (bytes per part) |
