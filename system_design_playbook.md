# System Design Playbook — Staff / Principal Level

> At staff+ level, interviewers evaluate **how you think**, not just what you draw. They want to see you drive ambiguity, articulate tradeoffs, anticipate failure modes, and make decisions that reflect real production experience.

---

## Table of Contents

1. [How Staff+ SD Interviews Differ](#how-staff-sd-interviews-differ)
2. [The Framework (30–45 min)](#the-framework)
3. [Requirements & Scoping](#1-requirements--scoping-5-min)
4. [API Design](#2-api-design-5-min)
5. [High-Level Architecture](#3-high-level-architecture-5-min)
6. [Data Model & Storage](#4-data-model--storage-5-min)
7. [Deep Dives & Tradeoffs](#5-deep-dives--tradeoffs-10-15-min)
8. [Operational Excellence](#6-operational-excellence-5-min)
9. [Building Blocks Catalog](#building-blocks-catalog)
10. [Communication Protocols](#communication-protocols)
11. [Scalability Patterns](#scalability-patterns)
12. [Replication & Partitioning](#replication--partitioning)
13. [Consistent Hashing](#consistent-hashing)
14. [Consistency & Coordination](#consistency--coordination)
15. [Messaging & Async Patterns](#messaging--async-patterns)
16. [Batch & Stream Processing](#batch--stream-processing)
17. [Caching Strategies](#caching-strategies)
18. [Storage Decision Guide](#storage-decision-guide)
19. [Encoding & Schema Evolution](#encoding--schema-evolution)
20. [Rate Limiting & Load Management](#rate-limiting--load-management)
21. [Observability & Reliability](#observability--reliability)
22. [Security Considerations](#security-considerations)
23. [Common System Design Problems](#common-system-design-problems)
24. [Numbers Every Engineer Should Know](#numbers-every-engineer-should-know)
25. [Staff+ Differentiators](#staff-differentiators)
26. [Recommended Resources](#recommended-resources)

---

## How Staff+ SD Interviews Differ

| Level | What They Evaluate |
|---|---|
| **Mid-level** | Can you produce a working design that handles the basic case? |
| **Senior** | Do you understand scalability, storage tradeoffs, and caching? |
| **Staff** | Can you **drive ambiguity**, identify the hardest subproblem, and make principled tradeoffs? |
| **Principal** | Can you reason about **organizational constraints**, multi-year evolution, and cross-system impact? |

### What Staff+ Candidates Must Demonstrate

1. **Own the conversation** — don't wait for hints. Proactively scope, propose, and course-correct.
2. **Tradeoff articulation** — never say "we'll use X." Say "we'll use X because [reason], the alternative Y would give us [benefit] but costs [downside], and for our requirements that tradeoff isn't worth it."
3. **Operational thinking** — how does this fail? How do we detect it? How do we recover? What does the on-call experience look like?
4. **Evolution & migration** — "this works for v1, and when we hit [scale], we'd migrate to [approach] by [strategy]."
5. **Org-aware design** — team boundaries, ownership, deploy independence, API contracts between teams.

---

## The Framework

```
┌─────────────────────────────────────────────────────┐
│  1. Requirements & Scoping              (5 min)     │
│  2. API Design                          (5 min)     │
│  3. High-Level Architecture             (5 min)     │
│  4. Data Model & Storage                (5 min)     │
│  5. Deep Dives & Tradeoffs             (10–15 min)  │
│  6. Operational Excellence              (5 min)     │
└─────────────────────────────────────────────────────┘
```

**Key principle**: Don't follow this rigidly. The interviewer may want to spend 20 min on deep dives. Be flexible, but make sure you cover requirements and a high-level diagram before diving deep.

---

## 1. Requirements & Scoping (5 min)

### Functional Requirements
Ask: "What are the **core use cases** we need to support?"

Prioritize ruthlessly. For a URL shortener:
- ✅ "Shorten a URL, redirect to original" — core
- ⚠️ "Custom aliases" — mention, defer
- ❌ "Analytics dashboard" — out of scope unless interviewer says otherwise

### Non-Functional Requirements
Always quantify. Don't say "high availability" — say "99.99% uptime."

| Dimension | Questions to Ask |
|---|---|
| **Scale** | How many users? QPS for reads vs writes? |
| **Latency** | P50/P99 targets? What's acceptable? |
| **Availability** | Can we tolerate brief downtime? What's the SLA? |
| **Consistency** | Strong or eventual? What happens on stale reads? |
| **Durability** | Can we lose data? What's the RPO? |
| **Data volume** | How much storage? Growth rate? Retention? |

### Back-of-Envelope Estimation

Always do this. Show you can reason about scale.

```
Example: Twitter-like feed
- 500M users, 200M DAU
- Avg user: 2 reads/min during active hours → 400M reads/min → ~7M QPS reads
- Avg user: 1 tweet/day → 200M writes/day → ~2.3K QPS writes
- Read-heavy: 3000:1 read/write ratio
- Each tweet: ~300 bytes text + metadata → 200M × 300B = 60GB/day new data
```

### Staff+ Move: Identify the Hard Problem
After scoping, explicitly state: "The hardest part of this system is ___. I want to spend most of our time there." This shows you can cut through noise.

---

## 2. API Design (5 min)

### REST Conventions

```
POST   /api/v1/messages          — create
GET    /api/v1/messages/{id}     — read one
GET    /api/v1/messages?user=X   — list/search
PUT    /api/v1/messages/{id}     — full update
PATCH  /api/v1/messages/{id}     — partial update
DELETE /api/v1/messages/{id}     — delete
```

### Pagination
```
GET /api/v1/feed?cursor=<opaque_token>&limit=20

Response:
{
  "data": [...],
  "next_cursor": "abc123",  // opaque, encodes position
  "has_more": true
}
```

**Cursor-based** (preferred for feeds/timelines):
- Stable under inserts/deletes
- Encode last seen ID or timestamp

**Offset-based** (`?page=3&limit=20`):
- Simple but breaks when data changes between pages

### API Design Principles (Staff+ Level)
- **Idempotency**: POST with client-generated idempotency key for writes
- **Versioning**: `/v1/` prefix or header-based
- **Rate limiting**: return `429` with `Retry-After` header
- **Bulk endpoints**: `POST /api/v1/messages/bulk` for batch operations
- **Field selection**: `?fields=id,title,author` to reduce payload

---

## 3. High-Level Architecture (5 min)

Draw a clear diagram. Label every component and data flow.

### Standard Web Architecture

```
Client → CDN → Load Balancer → API Gateway → Services → Database
                                    │
                                    ├── Cache (Redis/Memcached)
                                    ├── Message Queue (Kafka/SQS)
                                    ├── Object Storage (S3)
                                    └── Search (Elasticsearch)
```

### When to Split into Services

| Signal | Action |
|---|---|
| Different scaling needs (read-heavy vs write-heavy) | Separate read/write services |
| Different team ownership | Service boundary = team boundary |
| Different deployment cadence | Independent deployable |
| Different availability requirements | Isolate blast radius |

### Staff+ Move: Justify Every Box
Don't just draw boxes. For each component, state **why** it exists and what happens if you remove it. "We need this cache because our DB can't handle 7M QPS reads, and cache miss rate at 1% still means 70K QPS to DB which is manageable."

---

## 4. Data Model & Storage (5 min)

### Choosing a Database

```
Structured data + transactions + complex queries?
├── Yes → Relational (PostgreSQL, MySQL)
│
Flexible schema + high write throughput + horizontal scale?
├── Yes → Document store (MongoDB, DynamoDB)
│
High-throughput time-series or event data?
├── Yes → Column store (Cassandra, ClickHouse) or Time-series DB
│
Graph relationships (friends-of-friends, recommendations)?
├── Yes → Graph DB (Neo4j) or adjacency list in relational
│
Full-text search?
├── Yes → Elasticsearch / OpenSearch (secondary index, not source of truth)
│
Binary blobs / media?
└── Yes → Object storage (S3) + metadata in DB
```

### Schema Design Tips
- **Denormalize for read performance** — duplicate data is fine if it avoids expensive joins
- **Design for your access patterns** — especially in NoSQL. Think "what queries will I run?" first
- **Use composite keys** wisely — `(user_id, timestamp)` for time-ordered per-user data
- **Soft deletes** — `deleted_at` timestamp instead of hard delete for auditability

### Indexing Strategy
- Index columns used in `WHERE`, `JOIN`, `ORDER BY`
- Composite index: **leftmost prefix rule** — `INDEX(a, b, c)` supports queries on `(a)`, `(a, b)`, `(a, b, c)` but not `(b, c)`
- Covering index: include all selected columns to avoid table lookup
- **Don't over-index** — each index costs write performance and storage

---

## 5. Deep Dives & Tradeoffs (10–15 min)

This is where staff+ candidates differentiate. Pick the 1–2 hardest subproblems and go deep.

### How to Structure a Deep Dive

1. **State the problem clearly**: "The challenge is [X] because [Y]"
2. **Propose 2–3 approaches**: with pros/cons for each
3. **Make a decision**: "For our requirements, I'd choose [Z] because..."
4. **Acknowledge limitations**: "This breaks down when [edge case], and we'd handle that by..."

### Tradeoff Framework

| Dimension | Tension |
|---|---|
| **Consistency vs Availability** | CP vs AP (CAP theorem in practice) |
| **Latency vs Throughput** | Batching increases throughput, hurts latency |
| **Simplicity vs Scalability** | Monolith is simpler; microservices scale independently |
| **Cost vs Performance** | More replicas = faster reads but higher cost |
| **Freshness vs Load** | Real-time sync = more DB load than eventual consistency |

### Staff+ Move: Name the Tradeoff Before Being Asked
"I want to call out that this design prioritizes availability over consistency. If a user posts a message, followers might see it with up to 5 seconds delay. For a social feed that's acceptable, but if this were a payment system, we'd need strong consistency and I'd design it differently."

---

## 6. Operational Excellence (5 min)

Staff+ engineers are expected to think about **day 2 operations**, not just day 1 launch.

### Monitoring & Alerting
- **The Four Golden Signals** (Google SRE):
  - **Latency**: P50, P99, P99.9 — alert on P99 degradation
  - **Traffic**: QPS — detect unusual spikes or drops
  - **Errors**: 5xx rate, error ratio — alert when > threshold
  - **Saturation**: CPU, memory, disk, connection pool — alert before hitting limits

### Failure Modes & Mitigation

| Failure | Detection | Mitigation |
|---|---|---|
| **DB overload** | Connection pool exhaustion, latency spike | Read replicas, caching, circuit breaker |
| **Cascading failure** | Error rate spike across services | Circuit breaker, bulkhead isolation, fallbacks |
| **Hot partition** | Uneven load across shards | Better partition key, scatter-gather |
| **Data corruption** | Checksum mismatch, anomaly detection | Immutable audit log, point-in-time recovery |
| **Dependency failure** | Health check failure, timeout increase | Retry with backoff, fallback, graceful degradation |

### Deployment Strategy
- **Blue-green**: instant rollback, but 2x resources during deploy
- **Canary**: route 1–5% traffic to new version, watch metrics, gradually roll out
- **Feature flags**: decouple deploy from release; kill switch for new features

### Staff+ Move: The On-Call Test
"If I'm on call and this system pages me at 3 AM, what information do I need? I'd want dashboards showing [X], runbooks for [Y], and the ability to [Z] as an emergency lever."

---

## Building Blocks Catalog

Quick reference for the components you'll use repeatedly.

### Load Balancing

| Layer | Technology | Algorithm |
|---|---|---|
| **L4 (TCP)** | NLB, HAProxy | Round-robin, least connections |
| **L7 (HTTP)** | ALB, Nginx, Envoy | Path-based routing, weighted |
| **DNS** | Route 53, CloudFlare | Geographic, latency-based |
| **Client-side** | gRPC, service mesh | Consistent hashing, weighted round-robin |

**Consistent hashing**: minimizes redistribution when nodes join/leave. Use virtual nodes to improve balance.

### CDN (Content Delivery Network)
- Cache static assets at edge locations close to users
- **Pull-based**: CDN fetches from origin on cache miss (simpler, good for most cases)
- **Push-based**: You push content to CDN proactively (good for predictable, large content)
- Invalidation: TTL-based or explicit purge

### Service Mesh / API Gateway

| Component | Handles |
|---|---|
| **API Gateway** | Auth, rate limiting, request routing, protocol translation |
| **Service Mesh** (Istio, Linkerd) | mTLS, retries, circuit breaking, observability — sidecar pattern |

### Proxies & Reverse Proxies

| Type | Direction | Purpose |
|---|---|---|
| **Forward proxy** | Client → Proxy → Server | Client anonymity, corporate firewalls, caching |
| **Reverse proxy** | Client → Proxy → Backend servers | Load balancing, SSL termination, caching, compression |

**Load balancer vs reverse proxy**: A load balancer distributes across multiple servers. A reverse proxy can do that *plus* SSL termination, caching, compression, and request rewriting. In practice, ALB/Nginx serve as both.

---

## Communication Protocols

### Protocol Comparison

| Protocol | Transport | Format | Use Case |
|---|---|---|---|
| **REST** | HTTP | JSON | Public APIs, CRUD, browser clients |
| **gRPC** | HTTP/2 | Protobuf (binary) | Service-to-service, low latency, streaming |
| **GraphQL** | HTTP | JSON | Mobile clients, flexible queries, reduce over-fetching |
| **WebSocket** | TCP (upgraded HTTP) | Any | Real-time bidirectional (chat, live updates) |
| **Server-Sent Events** | HTTP | Text | Server → client one-way stream (notifications) |
| **UDP** | UDP | Any | Video streaming, gaming, DNS (loss-tolerant, low latency) |

### REST vs gRPC vs GraphQL

| Dimension | REST | gRPC | GraphQL |
|---|---|---|---|
| **Payload** | JSON (text, verbose) | Protobuf (binary, compact) | JSON (flexible shape) |
| **Performance** | Good | Excellent (2-10x smaller payloads) | Good |
| **Schema** | OpenAPI/Swagger (optional) | `.proto` files (required, strongly typed) | Schema (required, strongly typed) |
| **Streaming** | Not native (polling/SSE) | Native bidirectional streaming | Subscriptions (via WebSocket) |
| **Browser support** | Native | Needs gRPC-Web proxy | Native |
| **Best for** | Public APIs, simple CRUD | Internal microservices, high-throughput | Mobile/frontend with varied data needs |

### RPC vs REST Mental Model

| | REST | RPC (gRPC) |
|---|---|---|
| Style | Resource-oriented: `GET /users/123` | Action-oriented: `GetUser(id=123)` |
| Contract | Loose (HTTP verbs + URL conventions) | Strict (`.proto` IDL with code generation) |
| Versioning | URL path `/v1/` or headers | Package versioning in proto |

**Staff+ insight**: "For service-to-service communication within our platform, I'd use gRPC for performance and strong contracts. For public-facing APIs, REST for broad compatibility. For mobile clients needing flexible data, consider GraphQL to reduce round trips."

---

## Scalability Patterns

### Horizontal vs Vertical Scaling

| | Horizontal (Scale Out) | Vertical (Scale Up) |
|---|---|---|
| **How** | Add more machines | Bigger machine |
| **Limit** | Nearly unlimited | Hardware ceiling |
| **Complexity** | Need distributed systems design | Simple, just upgrade |
| **When** | Beyond single-machine limits | Before you need distribution |

**Staff+ insight**: Always start simple (vertical) and state when you'd switch to horizontal. "A single PostgreSQL instance handles 10K QPS reads easily. We'd only shard when we exceed [threshold]."

### Database Scaling

**Read replicas** → separate read and write traffic
```
Client → Write → Primary DB
Client → Read  → Read Replica 1, 2, 3
```
- Replication lag: reads may be stale by milliseconds to seconds
- Good for read-heavy workloads (most systems)

**Sharding** → distribute data across multiple databases
```
User ID % N → Shard N
```

| Sharding Strategy | Pros | Cons |
|---|---|---|
| **Hash-based** (`hash(key) % N`) | Even distribution | Resharding is painful |
| **Range-based** (`A-M → shard1`) | Range queries work | Hot spots if uneven |
| **Directory-based** | Flexible mapping | Lookup service is bottleneck |
| **Consistent hashing** | Minimal redistribution | More complex |

**Cross-shard queries are expensive** — design your shard key to keep related data together. If you need cross-shard joins, you probably need a different approach.

### Rebalancing Strategies (When Adding/Removing Shards)
- **Fixed number of partitions**: Create many more partitions than nodes (e.g., 1000 partitions on 10 nodes). When adding a node, move whole partitions — no re-hashing.
- **Dynamic partitioning**: Split a partition when it gets too large, merge when too small. (Used by HBase, DynamoDB.)
- **Consistent hashing**: See dedicated section below.

### CQRS (Command Query Responsibility Segregation)
Separate the write model from the read model:
```
Write → Command Service → Write DB (normalized)
                              ↓ (async event)
                        Read DB (denormalized, optimized for queries)
Read  → Query Service → Read DB
```
**When to use**: Read and write patterns are very different. Reads need denormalized views. Write throughput is high.

---

## Replication & Partitioning

### Replication Models (from DDIA)

| Model | How It Works | Pros | Cons |
|---|---|---|---|
| **Single-leader** | One primary accepts writes, replicates to followers | Simple, strong consistency possible | Leader is bottleneck & SPOF |
| **Multi-leader** | Multiple nodes accept writes, replicate to each other | Tolerates datacenter failure, lower write latency | Conflict resolution needed (LWW, CRDTs, custom) |
| **Leaderless** | Client writes to multiple replicas, reads from multiple | High availability, no failover needed | Quorum math, read repair, anti-entropy |

### Replication: Sync vs Async

| | Synchronous | Asynchronous |
|---|---|---|
| **Guarantee** | Follower confirmed before response | Leader responds immediately, follower catches up |
| **Latency** | Higher (wait for follower) | Lower |
| **Durability** | Stronger (data on ≥ 2 nodes) | Weaker (data loss if leader fails before replication) |
| **Common config** | Semi-synchronous: 1 sync follower + rest async | Fully async (most setups) |

### Replication Lag Problems

| Problem | Symptom | Solution |
|---|---|---|
| **Read-after-write** | User posts, refreshes, doesn't see their post | Read own writes from leader (session affinity) |
| **Monotonic reads** | User sees newer data, then older data on refresh | Always read from same replica per user |
| **Consistent prefix** | Causal order violated (answer appears before question) | Use causal ordering / version vectors |

### Leaderless Quorum

```
N = total replicas, W = write quorum, R = read quorum
Rule: W + R > N  →  guarantees overlap (at least one node has latest)

Common: N=3, W=2, R=2
Tuning:
  W=1, R=3  →  fast writes, slow reads (write-heavy)
  W=3, R=1  →  slow writes, fast reads (read-heavy)
```

**Sloppy quorum**: During network partition, writes go to any N reachable nodes (not necessarily the "home" replicas). Increases availability but weakens consistency. Requires **hinted handoff** to replay writes to correct nodes later.

### Partitioning with Secondary Indexes

| Approach | How | Pros | Cons |
|---|---|---|---|
| **Document-partitioned** (local index) | Each partition maintains its own secondary index | Writes update one partition | Reads must scatter-gather across all partitions |
| **Term-partitioned** (global index) | Secondary index itself is partitioned across nodes | Reads hit one partition | Writes may need to update multiple index partitions |

**Staff+ insight**: "For our search feature, I'd use a document-partitioned local index because write throughput matters more. The scatter-gather read cost is acceptable since search queries are less frequent than writes and we can parallelize them."

---

## Consistent Hashing

### The Problem
With `hash(key) % N`, adding or removing a node changes the mapping for almost all keys → massive data movement.

### How It Works
```
1. Hash both nodes and keys onto a ring (0 to 2^32)
2. Each key maps to the first node clockwise from its position
3. Adding a node only affects keys between the new node and its predecessor
4. Removing a node only affects keys that mapped to it → they shift to next node
```

### Virtual Nodes (Vnodes)
Each physical node gets multiple positions on the ring (e.g., 100-200 vnodes each).

**Why**: Without vnodes, data distribution is uneven (some nodes get more keys by luck of hash position). Vnodes spread the load evenly and make rebalancing smoother when nodes join/leave.

```
Physical Node A → vnode_A1, vnode_A2, ..., vnode_A150
Physical Node B → vnode_B1, vnode_B2, ..., vnode_B150
```

### Where It's Used
- **Cassandra, DynamoDB**: Partition data across nodes
- **CDN**: Map URLs to edge servers
- **Distributed cache**: Map keys to cache nodes (Memcached)
- **Load balancing**: Sticky sessions with consistent hashing

### When to Mention in Interviews
Consistent hashing comes up when:
- Designing a **distributed cache** or **distributed KV store**
- Asked "what happens when you add/remove a node?"
- Designing any system where you need **stable key → node mapping** with minimal disruption

---

## Consistency & Coordination

### CAP Theorem (Practical Version)

In a network partition, you must choose:
- **CP** (Consistency + Partition tolerance): refuse requests rather than return stale data. Example: ZooKeeper, etcd.
- **AP** (Availability + Partition tolerance): serve requests but may return stale data. Example: Cassandra, DynamoDB.

**In practice**, network partitions are rare. The real tradeoff is **consistency vs latency** (PACELC theorem):
- During **P**artition: choose **A**vailability or **C**onsistency
- **E**lse (normal operation): choose **L**atency or **C**onsistency

### Consistency Models

| Model | Guarantee | Example |
|---|---|---|
| **Strong (linearizable)** | Reads always see latest write | Single-node DB, Spanner |
| **Sequential** | All nodes see operations in same order | ZooKeeper |
| **Causal** | Causally related ops seen in order | Some Cassandra configs |
| **Eventual** | All replicas converge eventually | DynamoDB, Cassandra default |
| **Read-your-writes** | You see your own writes immediately | Session affinity |

### Distributed Consensus
- **Raft / Paxos**: Leader election, log replication. Used in etcd, CockroachDB.
- **Two-phase commit (2PC)**: Coordinator → prepare → commit. Blocking protocol, coordinator is SPOF.
- **Saga pattern**: Sequence of local transactions with compensating actions on failure. Better for microservices than 2PC.

### Distributed Locking
- **Redis SETNX + TTL**: Simple but not fully safe (clock skew, GC pauses)
- **Redlock**: Redis-based, uses quorum across N independent Redis nodes
- **ZooKeeper / etcd**: Stronger guarantees via consensus protocol
- **Advisory locks in DB**: Simple, uses existing infrastructure

**Staff+ insight**: "For this use case, I'd use an optimistic concurrency approach (version stamps) instead of distributed locks, because locks add latency and failure modes. Locks are only needed when the conflict rate is high and we can't tolerate any lost updates."

---

## Messaging & Async Patterns

### When to Go Async
- **Decouple producer from consumer** — different scaling, different failure domains
- **Smooth out traffic spikes** — queue absorbs burst, consumers process at steady rate
- **Work that doesn't need immediate response** — emails, notifications, analytics

### Message Queue vs Event Stream

| | Message Queue (SQS, RabbitMQ) | Event Stream (Kafka) |
|---|---|---|
| **Semantics** | Message consumed once, then deleted | Events retained, multiple consumers replay |
| **Ordering** | Per-queue (SQS FIFO) or best-effort | Per-partition ordering guaranteed |
| **Replay** | No (once consumed, gone) | Yes (consumers track offset) |
| **Fan-out** | Separate queue per consumer | Consumer groups on same topic |
| **Best for** | Task queues, work distribution | Event sourcing, data pipelines, CDC |

### Key Patterns

**Fan-out**: One event → multiple consumers
```
User posts message → Kafka topic "posts"
    → Feed Service (build timelines)
    → Notification Service (push notifications)
    → Analytics Service (track engagement)
    → Search Indexer (update Elasticsearch)
```

**Dead Letter Queue (DLQ)**: Failed messages go to a separate queue for investigation. Never silently drop messages.

**Idempotent consumers**: Messages may be delivered more than once. Use idempotency keys or deduplicate by message ID.

**Backpressure**: When consumers are slower than producers:
- Queue-based: queue grows (bounded queue rejects when full)
- Stream-based: consumer lag increases, monitor and alert

### Event Sourcing
Store **events** (immutable facts) instead of current state:
```
Event Store: [UserCreated, NameChanged, AddressUpdated, ...]
Current State = replay all events (or read from materialized view)
```
**Pros**: Complete audit trail, rebuild state from any point, easy temporal queries.
**Cons**: Complexity, eventual consistency, schema evolution is hard.

---

## Batch & Stream Processing

### When to Use Which (from DDIA)

| | Batch Processing | Stream Processing |
|---|---|---|
| **Input** | Bounded dataset (finite) | Unbounded stream (ongoing) |
| **Latency** | Minutes to hours | Seconds to milliseconds |
| **Throughput** | Very high (processes everything) | Moderate (processes as it arrives) |
| **Examples** | MapReduce, Spark, data warehouse ETL | Kafka Streams, Flink, Spark Streaming |
| **Use case** | Analytics, reports, ML training, reprocessing | Real-time dashboards, alerting, event-driven updates |

### MapReduce Mental Model

```
Input → Map (extract key-value pairs)
      → Shuffle (group by key)
      → Reduce (aggregate per key)

Example: Count word frequency in 1TB of text
  Map:     "hello world hello" → (hello, 1), (world, 1), (hello, 1)
  Shuffle:  (hello, [1, 1]), (world, [1])
  Reduce:   (hello, 2), (world, 1)
```

**Limitation**: Multi-stage MapReduce jobs are clumsy. Modern systems (Spark, Flink) use DAG-based execution with in-memory processing.

### Stream Processing Patterns

| Pattern | Description | Example |
|---|---|---|
| **Event-driven microservices** | Services react to events on a shared bus | Order placed → inventory reserved → payment charged |
| **Change Data Capture (CDC)** | Stream DB changes to downstream systems | Debezium captures MySQL binlog → Kafka → Elasticsearch |
| **Stream-table join** | Enrich streaming events with reference data | Join click events with user profile table |
| **Windowed aggregation** | Aggregate events within time windows | Count clicks per URL per 5-minute window |

### Window Types (for Aggregations)

| Window | Description |
|---|---|
| **Tumbling** | Fixed-size, non-overlapping (every 5 min exactly) |
| **Hopping** | Fixed-size, overlapping (5-min window every 1 min) |
| **Sliding** | Event-triggered, exact time range |
| **Session** | Gap-based, groups events with no gap > threshold |

### Stream Processing Guarantees

| Guarantee | Meaning | How |
|---|---|---|
| **At-most-once** | May lose messages | Fire and forget, no retry |
| **At-least-once** | May duplicate messages | Retry on failure, consumer must be idempotent |
| **Exactly-once** | No loss, no duplicates | Kafka transactions + idempotent producers, or Flink checkpoints |

**Staff+ insight**: "True exactly-once is expensive. In most cases, I'd design for at-least-once delivery with idempotent consumers — it's simpler, cheaper, and achieves the same end result."

---

## Caching Strategies

### Cache Placement

```
Client Cache → CDN → Application Cache (Redis) → Database
```

### Strategies

| Strategy | How It Works | Best For |
|---|---|---|
| **Cache-aside (lazy)** | App checks cache → miss → read DB → write cache | General purpose, most common |
| **Read-through** | Cache itself fetches from DB on miss | Simplifies app code |
| **Write-through** | Write to cache AND DB synchronously | Strong consistency, higher write latency |
| **Write-behind** | Write to cache, async flush to DB | High write throughput, risk of data loss |
| **Write-around** | Write to DB only, cache populated on read | Infrequently-read data |

### Cache Invalidation
The two hard problems in CS: cache invalidation and naming things.

| Approach | Tradeoff |
|---|---|
| **TTL-based** | Simple, but stale for up to TTL duration |
| **Event-driven** | Write triggers cache invalidation/update — fresher but more complex |
| **Version-based** | Cache key includes version — append-only, no invalidation needed |

### Cache Stampede Prevention
When a popular cache key expires, thousands of requests hit DB simultaneously.

**Solutions**:
- **Lock/mutex**: Only one request fetches, others wait
- **Early refresh**: Refresh before TTL expires (background thread)
- **Jitter**: Add random TTL offset to spread expirations

### Redis Patterns

| Pattern | Use Case |
|---|---|
| **String** | Simple KV cache, counters (`INCR`) |
| **Hash** | Object storage (`HSET user:123 name "Alice"`) |
| **Sorted Set** | Leaderboards, rate limiting windows |
| **List** | Recent items, activity feeds |
| **Set** | Unique visitors, intersection/union operations |
| **Pub/Sub** | Real-time notifications (no persistence) |
| **Streams** | Lightweight event streaming with consumer groups |

---

## Storage Decision Guide

### Comparing Storage Technologies

| Technology | Strengths | Weaknesses | Use When |
|---|---|---|---|
| **PostgreSQL** | ACID, rich queries, JSON support | Vertical scaling limits | Default choice, < 10TB, complex queries |
| **MySQL** | Battle-tested, good replication | Less feature-rich than PG | Legacy systems, read replicas |
| **DynamoDB** | Infinite scale, single-digit ms | Limited query patterns, expensive scans | Known access patterns, massive scale |
| **Cassandra** | High write throughput, multi-DC | Eventual consistency, limited queries | Time-series, IoT, write-heavy |
| **MongoDB** | Flexible schema, developer-friendly | Transactions less mature | Prototyping, document-oriented data |
| **Redis** | Sub-ms latency, rich data structures | Memory-bound, not durable by default | Cache, sessions, leaderboards |
| **Elasticsearch** | Full-text search, aggregations | Not a source of truth, resource-heavy | Search, log analytics |
| **S3** | Infinite capacity, cheap, durable | High latency, no queries | Files, media, backups, data lake |
| **Kafka** | High-throughput streaming, replay | Not a database, operational complexity | Event streaming, CDC, data pipelines |

### SQL vs NoSQL Decision

```
Need transactions across multiple tables?     → SQL
Need complex joins and ad-hoc queries?        → SQL
Schema changes frequently?                     → NoSQL (or SQL with JSON columns)
Need horizontal write scaling?                 → NoSQL
Access patterns are simple and well-known?     → NoSQL (DynamoDB)
Need strong consistency?                       → SQL (or DynamoDB with strong reads)
```

---

## Encoding & Schema Evolution

### Serialization Formats

| Format | Type | Schema | Human-Readable | Use Case |
|---|---|---|---|---|
| **JSON** | Text | Optional (JSON Schema) | Yes | REST APIs, config, logging |
| **XML** | Text | XSD | Yes (verbose) | Legacy, SOAP |
| **Protobuf** | Binary | Required (`.proto`) | No | gRPC, high-throughput internal APIs |
| **Avro** | Binary | Required (`.avsc`) | No | Kafka, data pipelines (schema in header) |
| **Thrift** | Binary | Required (`.thrift`) | No | Facebook-era services (less common now) |
| **MessagePack** | Binary | No | No | Compact JSON replacement |

### Why Schema Matters for Evolution

Systems evolve. Old producers talk to new consumers and vice versa. You need:

| Compatibility | Direction | Rule | Example |
|---|---|---|---|
| **Backward** | New code reads old data | New schema can read data written with old schema | Add a field with a default value |
| **Forward** | Old code reads new data | Old schema can read data written with new schema | Old code ignores unknown fields |
| **Full** | Both directions | Both backward and forward compatible | Safest for rolling deployments |

### Safe Schema Changes (Protobuf/Avro)

| Safe | Unsafe |
|---|---|
| Add optional field with default | Remove a required field |
| Add new enum value | Rename a field (Protobuf uses field numbers, so OK there) |
| Deprecate a field (don't reuse its number) | Change a field's type |

### Staff+ Insight
"For our Kafka topics, I'd use Avro with a Schema Registry. This gives us full compatibility checking on every schema change — a producer can't accidentally break consumers. For gRPC services, Protobuf's field numbering gives us backward/forward compatibility naturally, as long as we never reuse field numbers."

---

## Rate Limiting & Load Management

### Algorithms

| Algorithm | How It Works | Pros | Cons |
|---|---|---|---|
| **Token Bucket** | Bucket fills at rate R, request takes 1 token | Allows bursts up to bucket size | Burst can overwhelm backend briefly |
| **Leaky Bucket** | Queue with fixed drain rate | Smooth output rate | Doesn't handle legitimate bursts well |
| **Fixed Window** | Count requests per fixed time window | Simple | Spike at window boundary (2x burst) |
| **Sliding Window Log** | Track timestamp of each request | Precise | Memory-intensive (stores every timestamp) |
| **Sliding Window Counter** | Weighted sum of current + previous window | Good precision, low memory | Approximate |

### Implementation
```
Redis-based sliding window counter:
  key = "rate:{user_id}:{minute}"
  INCR key
  EXPIRE key 120  (keep 2 minutes for sliding calc)
```

### Load Shedding
When the system is overloaded, gracefully reject low-priority traffic:
1. **Priority queues**: Critical requests (payments) always served; best-effort (recommendations) shed first
2. **Circuit breaker**: Stop calling a failing dependency, return cached/default response
3. **Adaptive throttling**: Backend reports capacity, gateway adjusts admission rate

---

## Observability & Reliability

### Three Pillars of Observability

| Pillar | What | Tools |
|---|---|---|
| **Metrics** | Aggregated numbers over time (QPS, latency, error rate) | Prometheus, Datadog, CloudWatch |
| **Logs** | Discrete events with context | ELK stack, Splunk, CloudWatch Logs |
| **Traces** | Request flow across services | Jaeger, Zipkin, AWS X-Ray |

### SLI / SLO / SLA

| Term | Definition | Example |
|---|---|---|
| **SLI** (Indicator) | Metric measuring service health | P99 latency, error rate |
| **SLO** (Objective) | Target for the SLI | P99 < 200ms, 99.9% success rate |
| **SLA** (Agreement) | Contract with customers (with consequences) | 99.99% uptime or credit issued |

**Error budget**: If SLO is 99.9%, you have 0.1% error budget. When budget is exhausted → freeze deployments, focus on reliability.

### Reliability Patterns

| Pattern | Purpose |
|---|---|
| **Retry with exponential backoff + jitter** | Handle transient failures without thundering herd |
| **Circuit breaker** | Stop cascading failures by failing fast |
| **Bulkhead** | Isolate resources per dependency (separate thread pools) |
| **Timeout** | Bound wait time; always set timeouts on external calls |
| **Fallback / graceful degradation** | Serve stale cache or simplified response when dependency is down |
| **Idempotency** | Safe retries — same request produces same result |

### Retry Formula
```
delay = min(base_delay * 2^attempt + random_jitter, max_delay)
```
Always set a **max retries** limit. Without it, retries amplify load on an already struggling system.

---

## Security Considerations

Mention these proactively — staff+ candidates think about security without being asked.

### Authentication & Authorization
- **AuthN**: Who are you? (OAuth 2.0, JWT, API keys)
- **AuthZ**: What can you do? (RBAC, ABAC, per-resource ACLs)
- **JWT**: Stateless, but can't revoke easily. Use short TTL + refresh tokens.
- **API Gateway**: Centralize auth checks; services trust the gateway's identity headers.

### Data Protection
- **Encryption at rest**: AES-256 for databases, S3 default encryption
- **Encryption in transit**: TLS everywhere, mTLS between services
- **PII handling**: Separate PII store, field-level encryption, data retention policies
- **Secrets management**: Never in code/config. Use Vault, AWS Secrets Manager, etc.

### Common Threats to Mention
- **SQL injection** → parameterized queries
- **DDoS** → rate limiting, CDN, WAF
- **Insider threat** → audit logging, least-privilege access
- **Data exfiltration** → VPC isolation, egress controls

---

## Common System Design Problems

### Tier 1: Must-Know (Very Commonly Asked)

| Problem | Key Challenges | Core Components |
|---|---|---|
| **URL Shortener** | Hash collisions, redirect latency, analytics | Hash/counter, KV store, cache, 301 vs 302 |
| **News Feed / Timeline** | Fan-out (push vs pull), ranking, real-time updates | Kafka, cache, social graph, ranking service |
| **Chat / Messaging** | Real-time delivery, ordering, presence, group chat | WebSocket, message queue, per-conversation store |
| **Rate Limiter** | Distributed counting, accuracy, multi-tier | Redis, sliding window, API gateway |
| **Notification System** | Multi-channel, priority, dedup, user preferences | Queue per channel, template service, preference store |

### Tier 2: Frequently Asked

| Problem | Key Challenges | Core Components |
|---|---|---|
| **Design Twitter** | Feed generation, celebrity problem, search | Fan-out on write (small) + fan-out on read (celebrities), Elasticsearch |
| **Design YouTube / Netflix** | Video upload pipeline, adaptive streaming, recommendations | Object storage, CDN, transcoding pipeline, ML ranking |
| **Design Uber / Ride Sharing** | Location matching, ETA, surge pricing, dispatch | Geospatial index, matching service, pricing engine |
| **Design Dropbox / Google Drive** | File sync, conflict resolution, chunked upload | Block storage, metadata DB, sync protocol, CDC |
| **Design Web Crawler** | Politeness, dedup, scale, priority | URL frontier (queue), DNS cache, bloom filter, robots.txt |

### Tier 3: Advanced / Staff+ Level

| Problem | Key Challenges | Core Components |
|---|---|---|
| **Design Google Search** | Inverted index, PageRank, query processing at scale | Crawl → index → serve pipeline, distributed index |
| **Design Distributed Cache** | Consistent hashing, replication, eviction, hot keys | Hash ring, replication protocol, LRU/LFU |
| **Design Distributed Task Scheduler** | Exactly-once execution, fault tolerance, priority | DB-backed queue or Kafka, lease-based execution |
| **Design Payment System** | Exactly-once processing, reconciliation, compliance | Idempotency, saga pattern, ledger, audit log |
| **Design Distributed ID Generator** | Uniqueness, ordering, high throughput | Snowflake (timestamp + worker + sequence), or UUID |
| **Design Ad Click Aggregator** | Real-time aggregation, dedup, scale | Kafka + Flink/Spark, HyperLogLog, OLAP store |
| **Design Ticketmaster / Booking** | Seat reservation, concurrency, double-booking prevention | Optimistic locking, distributed lock, reservation expiry |
| **Design Yelp / Proximity Search** | Geospatial queries, nearby search, ranking | Geohash / Quadtree, PostGIS, weighted ranking |
| **Design Instagram** | Photo upload, feed, stories, explore | Object storage + CDN, fan-out, ML ranking, ephemeral storage |

### Feed Design Deep Dive (Most Common)

**Fan-out on write** (push model):
```
User A posts → immediately write to all followers' feeds (precomputed)
Pro: Fast reads (feed is pre-built)
Con: Expensive for celebrities (millions of followers), wasted writes for inactive users
```

**Fan-out on read** (pull model):
```
User B opens feed → query all followed users' posts, merge + rank
Pro: No wasted writes
Con: Slow reads (N queries for N followees)
```

**Hybrid** (what real systems do):
- Push for users with < 10K followers (most users)
- Pull for celebrities (merge at read time)
- Cache hot feeds in Redis

### Key-Value Store Deep Dive (Staff+ Favorite)

Based on Dynamo/Cassandra architecture. Tests understanding of distributed systems fundamentals.

**Core Architecture**:
```
Client → Coordinator Node → Consistent Hash Ring → N Replicas
         (any node can     (data partitioning)    (data replication)
          be coordinator)
```
Fully decentralized — no single point of failure, every node has same responsibilities.

**Write Path (LSM Tree / SSTable)**:
```
Write Request
  → 1. Append to Write-Ahead Log (WAL / commit log) — durability
  → 2. Write to in-memory table (memtable) — fast writes
  → 3. When memtable full → flush to SSTable on disk (sorted, immutable)
```
- **WAL**: Crash recovery — replay log to rebuild memtable
- **Memtable**: Sorted in-memory structure (e.g., red-black tree)
- **SSTable**: Sorted String Table — immutable, sorted key-value pairs on disk. Periodically compacted (merge-sort) to remove duplicates/tombstones

**Read Path**:
```
Read Request
  → 1. Check memtable (in-memory) — fast
  → 2. If miss → check Bloom filter to identify which SSTables might have the key
  → 3. Read candidate SSTables from disk
  → 4. Return most recent value
```

**Bloom Filter**: Probabilistic data structure. Answers "is this key in this SSTable?" with:
- **No** → definitely not there (skip this SSTable)
- **Yes** → probably there (check it)
- False positives possible, false negatives impossible. Saves unnecessary disk reads.

**Conflict Resolution: Vector Clocks**:
```
D1([Sx, 1])           — initial write by server Sx
D2([Sx, 2])           — updated by Sx again
D3([Sx, 2], [Sy, 1])  — branched: updated by Sy based on D2
D4([Sx, 2], [Sz, 1])  — branched: updated by Sz based on D2
→ D3 and D4 are siblings (conflict!) — client must resolve
D5([Sx, 3], [Sy, 1], [Sz, 1]) — client resolved, written to Sx
```
Rule: Version X is ancestor of Y if all of X's counters ≤ Y's counters. Otherwise → conflict → client resolves.

**Failure Detection: Gossip Protocol**:
- Each node maintains membership list with heartbeat counters
- Periodically sends heartbeats to random nodes → propagated further
- If a node's heartbeat hasn't incremented for threshold time → marked as down
- Decentralized — no need for a central health checker

**Failure Handling**:

| Failure Type | Technique |
|---|---|
| **Temporary** | Sloppy quorum + hinted handoff (healthy nodes temporarily handle requests, hand data back when failed node recovers) |
| **Permanent** | Anti-entropy with **Merkle trees** — compare tree root hashes between replicas; if different, traverse to find divergent buckets and sync only those |
| **Data center outage** | Cross-datacenter replication |

**Merkle Tree**: Hash tree where each leaf = hash of a data bucket, parents = hash of children. To compare two replicas: compare root hash → if different, recurse into children → only sync the buckets that actually differ. Proportional to differences, not total data.

**Summary Table**:

| Goal | Technique |
|---|---|
| Store big data | Consistent hashing |
| High availability reads | Replication + multi-DC |
| High availability writes | Versioning + vector clocks |
| Partition data | Consistent hashing + virtual nodes |
| Tunable consistency | Quorum (W, R, N) |
| Temporary failures | Sloppy quorum + hinted handoff |
| Permanent failures | Merkle tree anti-entropy |
| Failure detection | Gossip protocol |
| Storage engine | WAL + memtable + SSTable (LSM tree) |
| Efficient reads from disk | Bloom filter |

**Staff+ insight**: This problem is a favorite because it touches almost every distributed systems concept. If asked, lead with the consistency model choice (CP vs AP), then walk through the architecture systematically. The write path (WAL → memtable → SSTable) and quorum tuning (W + R > N) are the two areas interviewers probe deepest.

### Search Autocomplete Deep Dive

Also called "design top K" or "design typeahead". Unique because it combines a specialized data structure (Trie) with an offline data pipeline.

**Requirements**: Return top 5 suggestions for a prefix in < 100ms. 10M DAU, ~24K QPS (~48K peak).

**Two Services**:
```
1. Data Gathering Service (offline):
   Analytics Logs → Aggregators (weekly) → Workers → Build Trie → Trie DB

2. Query Service (online):
   Client → LB → API Server → Trie Cache (distributed) → return top 5
                                    ↑
                              Trie DB (on cache miss)
```

**Core Data Structure: Trie with Cached Top-K**

Basic trie: each node = one character, path from root = prefix. Finding prefix = O(p), then traverse subtree O(c), sort O(c log c). Too slow.

**Two key optimizations**:
1. **Limit prefix length** (e.g., 50 chars) → O(1) prefix lookup
2. **Cache top-K results at each node** → O(1) to return suggestions (no subtree traversal)

```
Example: node for prefix "be" stores:
  [best: 35, bet: 29, bee: 20, be: 15, beer: 10]

Lookup "be" → return cached list immediately → O(1)
```

**Tradeoff**: Uses more space (top-K at every node), but response time drops to O(1). Worth it for autocomplete's strict latency requirement.

**Data Gathering Pipeline**:
```
Analytics Logs (append-only, raw queries with timestamps)
  → Aggregators (batch, weekly for most use cases)
  → Aggregated Data (query, time_window, frequency)
  → Workers (rebuild trie from aggregated data)
  → Trie DB (serialized trie in document store, or prefix→top-K in KV store)
  → Trie Cache (weekly snapshot in distributed cache)
```

**Why not real-time updates?**
- Billions of queries/day → updating trie on every query is too expensive
- Top suggestions don't change much → weekly rebuild is sufficient for most products
- For trending/real-time (e.g., Twitter): use streaming (Kafka/Flink), shorter aggregation windows, weight recent queries higher

**Trie Storage Options**:

| Option | How | Best For |
|---|---|---|
| **Serialized document** | Snapshot entire trie, store in MongoDB | Simple, periodic full rebuild |
| **KV store** | Each prefix → top-K list (e.g., `"be" → [best:35, bet:29, ...]`) | Incremental updates, distributed |

**Trie Sharding** (when too large for one server):
- Naive: shard by first character (a-m on server 1, n-z on server 2)
- Problem: uneven distribution ('c' has far more words than 'x')
- Better: **shard map manager** — analyze historical query distribution and assign prefix ranges to shards based on actual load, not alphabet position

**Query Service Optimizations**:
- **AJAX requests** — no page refresh
- **Browser caching** — `Cache-Control: private, max-age=3600` (suggestions don't change within an hour)
- **Data sampling** — log only 1/N queries to reduce storage/processing

**Trie Operations**:

| Operation | Approach |
|---|---|
| **Create** | Workers build from aggregated data (offline) |
| **Update** | Option 1: rebuild weekly (replace old trie). Option 2: update node + all ancestors (expensive, only for small tries) |
| **Delete** | Filter layer in front of Trie Cache removes hateful/explicit suggestions. Physical deletion happens async in next rebuild cycle |

**Follow-up Questions**:
- **Multi-language**: Store Unicode characters in trie nodes
- **Per-country suggestions**: Build separate tries per country, serve from regional CDN
- **Real-time trending**: Stream processing (Kafka/Flink), shorter aggregation windows, recency-weighted ranking

**Staff+ insight**: The key architectural decision is separating the offline data pipeline (build trie weekly) from the online serving path (read from cache). This is a classic batch-serving pattern. For the deep dive, focus on the trie optimization (cached top-K at each node → O(1) lookup) and the sharding strategy for the trie.

### Proximity Service Deep Dive (Yelp / Google Maps Nearby)

Core question: given a user's location and radius, return nearby businesses. Read-heavy (5K QPS), write-light (business updates effective next day).

**High-Level Architecture**:
```
Client (lat, lng, radius)
  → Load Balancer
  → Location-Based Service (LBS) — stateless, read-only, horizontally scalable
      → Geohash Redis Cache (geohash → list of business IDs)
      → Business Info Redis Cache (business_id → business object)
  → Business Service — CRUD for business owners (low write QPS)
      → Primary DB (writes) → Read Replicas (reads)
```

**Geospatial Indexing Options**:

| Option | How It Works | Pros | Cons |
|---|---|---|---|
| **Geohash** | Encode lat/lng into a string; longer shared prefix = closer. Query: `WHERE geohash LIKE 'prefix%'` | Simple, easy to index in DB, easy updates | Fixed grid size per precision level; boundary issues |
| **Quadtree** | In-memory tree; recursively subdivide until ≤ K businesses per cell | Adaptive grid density (dense areas = smaller cells); good for k-nearest | In-memory only, ~1.7GB for 200M businesses; complex updates (locking); minutes to build at startup |
| **Google S2** | Maps sphere to 1D via Hilbert curve | Great for geofencing (arbitrary shapes); variable cell sizes | Complex to explain in interview |

**Recommendation**: Use **geohash** for simplicity or **quadtree** for adaptive density. S2 is overkill for interviews.

**How Geohash Works**:
```
1. Recursively divide globe into quadrants using lat/lng bits
2. Encode as base32 string
3. Precision levels 4-6 are most useful:
   Length 4 → ~39km × 19.5km  (radius 5-20km)
   Length 5 → ~4.9km × 4.9km  (radius 1-2km)
   Length 6 → ~1.2km × 609m   (radius 0.5km)
```

**Geohash Boundary Issues**:
1. **Close but no shared prefix** — two locations near the equator/prime meridian can be very close but have completely different geohashes (e.g., `u000` vs `ezzz`, only 30km apart)
2. **Same prefix, different grids** — two points with long shared prefix can be in adjacent grids

**Solution**: Always fetch businesses from current grid + 8 neighboring grids. Neighbor geohashes can be computed in O(1).

**Not enough results?** Remove last digit of geohash → larger grid → repeat until enough businesses found.

**How Quadtree Works**:
```java
public void buildQuadtree(TreeNode node) {
    if (countBusinesses(node) > 100) {
        node.subdivide();  // split into 4 children
        for (TreeNode child : node.getChildren())
            buildQuadtree(child);
    }
}
```
- Memory: ~1.71 GB for 200M businesses (leaf: 832 bytes, internal: 64 bytes)
- Build time: few minutes — must do rolling deploys to avoid brownout
- Search: traverse from root to leaf containing user's location, expand to neighbors if needed

**Geohash vs Quadtree**:

| | Geohash | Quadtree |
|---|---|---|
| **Grid size** | Fixed per precision level | Adaptive (denser areas = smaller cells) |
| **Storage** | DB rows (easy to shard/replicate) | In-memory tree on each LBS server |
| **Updates** | Simple row insert/delete | Tree traversal O(log n), needs locking |
| **Best for** | "businesses within radius R" | "k-nearest businesses" (variable radius) |
| **Used by** | Bing, Redis, MongoDB, Lyft | Yext, Elasticsearch |

**Caching Strategy**:

| Cache Key | Cache Value | Notes |
|---|---|---|
| `geohash` | List of business IDs in that grid | Pre-cache for all 3 precision levels (4, 5, 6). ~5GB total for 200M businesses × 3 precisions |
| `business_id` | Full business object | For rendering detail pages. Updated via nightly job |

**Why geohash is a good cache key**: Unlike raw lat/lng (which changes slightly with every GPS reading), all users in the same grid map to the same geohash → high cache hit rate.

**Scaling**:
- **LBS**: Stateless → horizontal scaling, multi-region deployment
- **Geospatial index**: Fits in memory (~1.7GB). Don't shard — use **read replicas** instead (simpler)
- **Business table**: Shard by `business_id` if needed
- **Multi-region**: Deploy LBS + cache in each region for lower latency + privacy law compliance (GDPR)

**Query Flow**:
```
1. Client sends (lat, lng, radius=500m) to LBS
2. LBS computes geohash length 6 for 500m radius
3. LBS computes 9 geohashes (current + 8 neighbors)
4. For each geohash, fetch business IDs from Redis (parallel)
5. Hydrate business objects from Business Info cache
6. Calculate actual distances, filter by radius, rank, return top results
```

**Follow-ups**:
- **Filter by type/hours**: Fetch IDs first, hydrate, then filter (dataset per grid is small enough)
- **Moving user**: GPS changes slightly, but geohash stays same → cache still works. No need to refresh constantly

**Staff+ insight**: The key decision is geohash vs quadtree. Lead with the tradeoff: geohash is simpler and DB-native (good default), quadtree is better when you need adaptive density or k-nearest queries. For scaling, resist the urge to shard the geospatial index — read replicas are sufficient since the dataset is small (~1.7GB). Save sharding for the business table.

### Stock Exchange Deep Dive (Ultra-Low Latency)

Unique because it's the opposite of most system design problems: instead of distributed microservices, modern exchanges put **everything on a single server** for minimal latency. Tests event sourcing, determinism, and HA without typical distributed patterns.

**Scale**: 100 symbols, 1B orders/day, ~43K QPS (215K peak). P99 latency target: microseconds.

**Three Flows**:
```
1. Trading Flow (critical path, ultra-low latency):
   Client → Broker → Client Gateway → Order Manager → Sequencer → Matching Engine
                                                                        ↓
   Client ← Broker ← Client Gateway ← Order Manager ← Sequencer ← Executions

2. Market Data Flow (near real-time):
   Matching Engine → Market Data Publisher → Data Service → Brokers/Subscribers

3. Reporting Flow (not latency-sensitive):
   Orders + Executions → Reporter → Database (compliance, tax, reconciliation)
```

**Matching Engine — The Heart**:
- Maintains an **order book** per symbol (buy book + sell book)
- Matches buy/sell orders → emits two executions (fills) per match
- Must be **deterministic**: same input sequence → same output, always

**Order Book Data Structure** (O(1) for all operations):
```java
class OrderBook {
    Book<Buy> buyBook;          // sorted price levels
    Book<Sell> sellBook;
    PriceLevel bestBid;
    PriceLevel bestOffer;
    Map<OrderID, Order> orderMap;  // O(1) cancel lookup
}
class PriceLevel {
    Price limitPrice;
    long totalVolume;
    DoublyLinkedList<Order> orders;  // O(1) add/remove
}
```
- **Place**: append to tail of PriceLevel's doubly-linked list → O(1)
- **Match**: remove from head → O(1)
- **Cancel**: lookup in orderMap → O(1), delete from doubly-linked list → O(1)

**Sequencer**: Stamps every order and execution with a sequential ID.
- Guarantees ordering for deterministic replay
- Detects missing messages (gaps in sequence)
- Functions as both sequencer and message queue (like Kafka but lower latency)

**Why Single Server?** Latency breakdown:
- Network round trip: ~500μs per hop. Multiple hops on critical path → single-digit ms
- Disk access: ~10ms even for sequential writes
- Solution: eliminate network hops, replace disk with mmap over `/dev/shm` (memory-backed filesystem)
- Result: sub-microsecond inter-component communication

**mmap Event Store**:
```
Components on same server communicate via memory-mapped files:
  Gateway → [mmap event store] → Order Manager → [mmap] → Matching Engine → [mmap] → out
No network. No disk I/O. Sub-microsecond messaging.
Like Kafka, but for single-server ultra-low latency.
```

**Application Loop Pattern** (per component):
- Single-threaded while loop, pinned to a dedicated CPU core
- **No context switches** (CPU fully dedicated)
- **No locks** (single writer, no contention)
- Both contribute to low, stable P99 latency

**Event Sourcing**:
- Don't store current state → store immutable log of all events (NewOrderEvent, OrderFilledEvent, CancelEvent, etc.)
- Current state = replay events in sequence
- Benefits: complete audit trail, deterministic replay for recovery, debugging

```
Traditional DB:        | order_id | status  | price | qty |
                       | 123      | FILLED  | 100   | 50  |  ← how did we get here?

Event Sourcing:        | seq | event          | order_id | price | qty |
                       | 1   | NEW_ORDER      | 123      | 100   | 50  |
                       | 2   | ORDER_MATCHED  | 123      | 100   | 30  |
                       | 3   | ORDER_MATCHED  | 123      | 100   | 20  |  ← full history
```

**High Availability**: Hot-warm architecture
- **Hot** (primary): processes events, sends results to event store
- **Warm** (standby): receives same events, processes them, but doesn't emit results
- If hot fails → warm takes over immediately (state already up to date)
- Recovery = replay events from event store (deterministic, so state is identical)

**Fault Tolerance** (multi-server):
- Replicate event store across multiple servers using **Raft** consensus
- 5-server Raft cluster: needs 3/5 votes (quorum) for writes
- Leader sends events to followers via RPC; if leader fails → automatic leader election
- RPO ≈ 0 (no data loss with Raft); RTO = seconds (automatic failover)

**Market Data Publisher**:
- Rebuilds order books and candlestick charts from execution stream
- Uses **ring buffers** (pre-allocated circular buffers) — no object allocation, lock-free
- Fairness: use **multicast UDP** to send data to all subscribers simultaneously (no first-subscriber advantage)

**Candlestick Chart**: `{open, close, high, low, volume, timestamp, interval}` per time window. Stored in ring buffers in memory, persisted to columnar DB (KDB) for analytics, archived after market close.

**Key Design Decisions Summary**:

| Decision | Choice | Why |
|---|---|---|
| Architecture | Single server | Eliminate network latency on critical path |
| IPC | mmap over `/dev/shm` | Sub-microsecond, no disk I/O |
| Threading | Single-threaded + CPU pinning | No context switch, no locks → stable P99 |
| State management | Event sourcing | Deterministic replay, audit trail, easy recovery |
| Order book | Doubly-linked list + HashMap | O(1) for place/match/cancel |
| HA | Hot-warm + Raft | Immediate failover, zero data loss |
| Market data distribution | Multicast UDP | Fairness — all subscribers receive simultaneously |

**Staff+ insight**: This problem tests a fundamentally different mindset from typical distributed systems design. The key insight to lead with: "For an exchange, latency is the dominant constraint. Unlike most systems where we scale horizontally, here we want everything on one server to eliminate network hops. We use event sourcing for determinism and recovery, and mmap for zero-copy IPC." This shows you understand that architecture choices are driven by requirements, not dogma.

### Digital Wallet Deep Dive (Distributed Transactions + Event Sourcing)

Core question: design a wallet service supporting balance transfers between accounts at 1M TPS with correctness, reproducibility, and 99.99% availability. Tests distributed transaction patterns and event sourcing in depth.

**Three Progressive Designs**:

| Design | Approach | Limitation |
|---|---|---|
| **1. In-memory (Redis)** | Shard accounts across Redis nodes, wallet service updates two nodes per transfer | No atomicity — crash between two updates = inconsistent state |
| **2. Distributed transactions** | Replace Redis with relational DBs, use 2PC/TC/C/Saga for atomicity | Correct but no audit trail, can't reproduce historical state |
| **3. Event sourcing** | Immutable event log + deterministic state machine → reproducible state | Best: correct, auditable, reproducible |

**Distributed Transaction Options**:

**2PC (Two-Phase Commit)** — database-level:
```
Phase 1 (Prepare): Coordinator asks all DBs to prepare (locks held)
Phase 2 (Commit/Abort): If all say "yes" → commit all. If any "no" → abort all.
```
- Locks held across both phases → poor performance
- Coordinator is single point of failure
- Uses X/Open XA standard

**TC/C (Try-Confirm/Cancel)** — application-level:
```
Try phase:     Deduct $1 from A (committed). NOP on C.
                → A and C are in separate local transactions (no cross-DB lock)
Confirm phase: If Try succeeded → Add $1 to C
Cancel phase:  If Try failed → Reverse: add $1 back to A
```
- Each phase is a separate local transaction (no long-held locks)
- Must handle **out-of-order execution**: Cancel may arrive before Try → use out-of-order flag
- Must deduct first, add second (choice 1 is the only valid order — prevents double-spending)
- **Phase status table** tracks progress for crash recovery

**Saga** — application-level, linear execution:
```
Step 1: A - $1  →  Step 2: C + $1
        ↓ fail          ↓ fail
   (already done)    Compensate: A + $1 (reverse step 1)
```
- Operations execute in strict linear order (no parallelism)
- Each step is an independent local transaction
- Rollback = compensating transactions in reverse order
- Two coordination modes: **Choreography** (decentralized, event-driven) vs **Orchestration** (central coordinator)

**TC/C vs Saga**:

| | TC/C | Saga |
|---|---|---|
| Execution order | Any (parallel possible) | Strictly linear |
| Latency | Lower (parallel) | Higher (sequential) |
| Complexity | Higher (out-of-order handling) | Lower |
| Best for | Latency-sensitive, many services | Simpler flows, microservice standard |

**Event Sourcing Architecture**:

```
Commands (transfer requests) → [Command Queue (Kafka)]
  → State Machine:
      1. Validate command against current state
      2. If valid → generate Event(s) (immutable facts)
      3. Apply event to update State (account balances)
  → [Event Queue] → CQRS read-only state machines → external queries
```

**Key terms**:
- **Command**: intention ("transfer $1 from A to C") — may be invalid
- **Event**: validated fact ("transferred $1 from A to C") — immutable, deterministic
- **State**: current account balances (derived from events)
- **State Machine**: validates commands, generates events, applies events — must be deterministic

**Why event sourcing wins for wallets** (answers auditor questions):
1. "What was the balance at time T?" → Replay events up to T
2. "Is the current balance correct?" → Replay all events, verify
3. "Is the code correct after a change?" → Replay events with new code, compare results

**Performance Optimization Progression**:

| Level | Command/Event Store | State Store | Latency |
|---|---|---|---|
| **Naive** | Kafka (remote) | Remote DB | Network + disk for every operation |
| **File-based** | Local disk via mmap | Local RocksDB (LSM tree) | Sequential disk + OS cache |
| **+ Snapshots** | Same | Periodic state snapshots to HDFS | Fast recovery (don't replay from beginning) |

**mmap optimization**: Map files to memory → OS caches recent data → append-only writes are nearly as fast as memory writes. Commands, events, and state all stored locally → no network hops.

**Snapshots**: Periodically freeze state to a file. Recovery = load snapshot + replay events since snapshot (not from the beginning). Finance teams often require daily snapshots (00:00) for reconciliation.

**Reliability via Raft**:
```
3 or 5 nodes in Raft group
Leader: receives commands, generates events, replicates event list to followers
Followers: receive replicated events, update their own state
If leader crashes → Raft elects new leader → immediate failover
Client retries command to new leader (idempotent via transaction_id)
```
- Only the **event list** needs Raft replication (state + snapshots can be rebuilt from events)
- Event generation may be non-deterministic (I/O, random) → can't just replay commands → must replicate events

**CQRS (Command Query Responsibility Segregation)**:
```
Write path: Commands → State Machine → Events → State (leader)
Read path:  Events → Read-only State Machines → Various views
                     (balance queries, audit trails, analytics)
```
- Read-only state machines are eventually consistent
- Can build different views from same event stream (balance view, audit view, time-series view)

**Distributed Event Sourcing** (for 1M TPS):
```
Shard accounts across multiple Raft groups (partitions)
Each partition: independent event sourcing node group
Cross-partition transfers: Saga coordinator orchestrates

User → Saga Coordinator → Partition 1 (A - $1) → success
                        → Partition 2 (C + $1) → success
                        → respond to user
```
- Saga coordinator tracks phase status for crash recovery
- Each partition internally uses event sourcing + Raft
- Reverse proxy converts async event sourcing to sync for external users (push model)

**Back-of-Envelope**: 1M TPS ÷ 1K TPS per node = 1000 nodes (×2 for debit+credit = 2000 nodes). Optimize per-node TPS to reduce total nodes.

**Staff+ insight**: This problem is a masterclass in progressive design refinement. Lead with: "The core challenge is atomicity across sharded accounts with auditability. I'd start with the transaction model choice — Saga for simplicity since our flow is linear (debit then credit). But for reproducibility and audit, I'd layer event sourcing on top. The event log becomes the source of truth, state is derived, and we can answer any auditor question by replaying events." This shows you understand both the distributed transaction landscape and why event sourcing is the right architecture for financial systems.

### Payment System Deep Dive (E-Commerce Payments)

Core question: design the payment backend for an e-commerce site (like Amazon). 1M transactions/day (~10 TPS). Focus is on correctness, not throughput. Tests idempotency, reconciliation, exactly-once delivery, and PSP integration.

**Two Flows**:
```
Pay-in:  Buyer pays → money flows to e-commerce bank account
Pay-out: E-commerce pays sellers → money flows to seller bank accounts
```

**Pay-in Architecture**:
```
User clicks "Place Order"
  → Payment Service (risk check, orchestration)
    → Payment Executor (one per payment order)
      → PSP (Stripe/PayPal — processes credit card)
        → Card Scheme (Visa/MasterCard)
    → Wallet Service (update seller balance)
    → Ledger Service (double-entry accounting record)
```

**PSP Integration — Hosted Payment Page**:
```
1. Client → Payment Service: send payment order info
2. Payment Service → PSP: register payment (amount, currency, redirect URL, nonce)
3. PSP → Payment Service: returns token (UUID for this payment)
4. Payment Service: stores token in DB
5. Client: displays PSP-hosted payment page (Stripe JS / SDK)
6. User enters card info on PSP page (card data never touches our system)
7. PSP processes payment, returns status
8. Browser redirects to our success/failure page
9. PSP → Payment Service: async webhook with final payment status
```
**Key**: We never store credit card numbers → avoids PCI DSS compliance burden. PSP handles all sensitive data.

**Double-Entry Ledger**:
```
Every transaction records two entries that sum to 0:
  Debit:  buyer  -$1
  Credit: seller +$1
```
Fundamental accounting principle — provides end-to-end traceability. Use an immutable append-only ledger.

**Exactly-Once Delivery** = At-Least-Once (retry) + At-Most-Once (idempotency):

**At-Least-Once — Retry**:
- Retry with exponential backoff for transient failures
- Use **retry queue** for retryable errors
- Use **dead letter queue (DLQ)** for messages that fail repeatedly (investigation needed)
```
Payment fails → retryable? → yes → retry queue → retry
                                     → still fails? → retry count < threshold → retry queue
                                                     → retry count ≥ threshold → DLQ
               → no → store error in DB (non-retryable)
```

**At-Most-Once — Idempotency**:
- Every payment request carries an **idempotency key** (UUID) in the HTTP header
- DB uses this key as primary key → duplicate insert fails → second request returns previous result
- For PSP: the `payment_order_id` (nonce) serves as the deduplication key

**Two double-payment scenarios**:

| Scenario | Solution |
|---|---|
| User clicks "pay" twice | Same idempotency key → second request returns cached result (or 429) |
| PSP succeeds but response lost, user retries | Same token sent to PSP → PSP returns previous execution status |

**Reconciliation** — the last line of defense:
```
Every night:
  PSP/Bank sends settlement file (all transactions + final balance)
  Reconciliation system compares settlement file vs internal ledger
  Mismatches → classify → auto-fix OR manual finance team queue
```
Also used internally: compare ledger vs wallet for consistency.

**Mismatch categories**:
1. **Classifiable + automatable** → write program to auto-fix
2. **Classifiable + not automatable** → manual fix queue for finance team
3. **Unclassifiable** → special investigation queue

**Payment State Tracking**:
```
payment_order_status: NOT_STARTED → EXECUTING → SUCCESS / FAILED
```
Persisted in append-only table. Scheduled job monitors in-flight orders and alerts if stuck past threshold.

**Handling Delays**: PSP may hold payments for risk review or 3D Secure authentication (hours/days).
- PSP returns "pending" status → client shows pending page with status check
- PSP notifies us via webhook when complete
- Alternative: payment service polls PSP for status updates

**Communication Patterns**:

| Pattern | Pros | Cons | Use When |
|---|---|---|---|
| **Synchronous** (HTTP) | Simple | Tight coupling, poor failure isolation, hard to scale | Small-scale, simple flows |
| **Async — single receiver** (message queue) | Decoupled, buffered | More complex | One consumer per message |
| **Async — multiple receivers** (Kafka) | Fan-out to many services, messages retained | Most complex | Payment events → analytics, billing, notifications |

**Data Model**:

| Table | Key Fields |
|---|---|
| **Payment Event** | `checkout_id` (PK), buyer_info, seller_info, credit_card_info, is_payment_done |
| **Payment Order** | `payment_order_id` (PK), buyer_account, amount, currency, checkout_id (FK), payment_order_status, ledger_updated, wallet_updated |

- One checkout (payment event) → multiple payment orders (one per seller)
- `payment_order_id` = idempotency key for PSP
- Amount stored as **string** (not double) to avoid precision loss

**Security**:

| Threat | Mitigation |
|---|---|
| Eavesdropping | HTTPS everywhere |
| Man-in-the-middle | SSL + certificate pinning |
| Card theft | Tokenization (PSP stores real card numbers, we store tokens) |
| DDoS | Rate limiting + firewall |
| PCI compliance | Hosted payment page (we never see card data) |
| Fraud | Address verification, CVV, behavior analysis |

**Staff+ insight**: The key architectural decisions to highlight: (1) Use hosted payment pages to avoid PCI compliance burden — this is what real companies do. (2) Exactly-once = retry + idempotency, not a magic protocol. (3) Reconciliation is the safety net — assume things will go wrong between async systems and design for nightly reconciliation. (4) Double-entry ledger is non-negotiable for any financial system. This problem is less about scale and more about correctness and operational maturity.

### Notification System Deep Dive

Core question: design a system that sends 10M push notifications, 1M SMS, and 5M emails per day. Soft real-time. Tests fan-out, message queues, third-party integration, reliability, and rate limiting.

**Three Notification Channels**:

| Channel | Third-Party Service | Token/Address |
|---|---|---|
| **iOS push** | Apple Push Notification Service (APNS) | Device token |
| **Android push** | Firebase Cloud Messaging (FCM) | Device token |
| **SMS** | Twilio, Nexmo | Phone number |
| **Email** | SendGrid, Mailchimp | Email address |

**Data Model**:
```
user table:       user_id, email, phone_number, created_at
device table:     id, user_id, device_token, platform (iOS/Android), last_active
notification_setting: user_id, channel, opt_in (boolean)
notification_log: notification_id, user_id, channel, status, retry_count, created_at
```
One user → multiple devices → push notification sent to all active devices.

**High-Level Architecture**:
```
Services (1..N)  →  Notification Servers (stateless, horizontally scaled)
                      ├── Validate input, check opt-in settings
                      ├── Fetch user/device info from cache/DB
                      ├── Rate limit check
                      ├── Build payload from notification template
                      └── Enqueue to per-channel message queue
                              ├── iOS Push Queue → Workers → APNS → iOS devices
                              ├── Android Push Queue → Workers → FCM → Android devices
                              ├── SMS Queue → Workers → Twilio → phones
                              └── Email Queue → Workers → SendGrid → inboxes
```

**Key design decisions**:

1. **Separate message queue per channel**: Outage in one third-party (e.g., APNS down) doesn't affect email/SMS delivery
2. **Workers pull from queues**: Decouples notification creation from delivery — natural backpressure
3. **Notification log DB**: Persist every notification before sending — no data loss even if worker crashes
4. **Deduplication**: Check event ID before sending — if seen before, discard (prevents duplicate notifications on retry)

**Reliability**:
```
Worker pulls notification from queue
  → Attempt delivery to third-party service
    → Success: mark as delivered in notification log
    → Failure: put back in queue for retry (with backoff)
      → Exceeds retry limit: move to DLQ, alert engineers
```
- **Cannot guarantee exactly-once delivery** in distributed systems — aim for at-least-once with dedup
- Notification log provides audit trail and supports retry

**Additional Components**:

| Component | Purpose |
|---|---|
| **Notification templates** | Pre-formatted payloads with variable substitution. Consistent format, less error-prone |
| **User notification settings** | Per-channel opt-in/opt-out. Always check before sending |
| **Rate limiting** | Cap notifications per user per time window. Prevents user from turning off all notifications |
| **Authentication** | appKey/appSecret for push notification APIs. Only verified clients can trigger notifications |
| **Event tracking** | Track sent → delivered → opened → clicked. Feed into analytics service for engagement metrics |
| **Queue depth monitoring** | Alert when queue backlog grows — indicates workers can't keep up, need to scale out |

**Scaling Considerations**:
- **Notification servers**: Stateless → horizontal autoscaling
- **Workers**: Scale per channel independently based on queue depth
- **Cache**: User info, device tokens, templates — high read frequency, low write
- **DB**: Notification log is append-only, can be sharded by user_id or time

**Staff+ insight**: The key insight is the per-channel queue separation — it provides fault isolation (APNS outage doesn't block emails) and independent scaling. For the deep dive, focus on: (1) reliability via notification log + retry + dedup, (2) rate limiting to protect user experience, (3) extensibility for new channels (just add a new queue + worker). This is a common Stripe question since webhooks are essentially a notification delivery system.

### Rate Limiter Deep Dive

Core question: design a distributed rate limiter for server-side API throttling. Tests algorithm knowledge, Redis usage, race conditions, and distributed synchronization. Directly relevant to **Stripe** (rate limiting is a core product feature) and **Anthropic/OpenAI** (API throttling).

**Five Algorithms**:

| Algorithm | How It Works | Pros | Cons |
|---|---|---|---|
| **Token Bucket** | Bucket fills at fixed rate; each request consumes a token. Excess requests dropped when bucket empty | Memory efficient, allows short bursts | Hard to tune bucket size + refill rate |
| **Leaking Bucket** | FIFO queue; requests processed at fixed rate. New requests dropped when queue full | Smooth output rate, memory efficient | Bursts fill queue with old requests; recent requests starved |
| **Fixed Window Counter** | Divide time into windows, count requests per window. Drop when count > threshold | Simple, memory efficient | Edge-of-window burst: 2× allowed rate across window boundary |
| **Sliding Window Log** | Store timestamp of each request in sorted set. Remove outdated entries. Count remaining | Perfectly accurate — no boundary issue | High memory (stores every timestamp, even rejected ones) |
| **Sliding Window Counter** | Hybrid: weighted sum of current window count + previous window count × overlap % | Memory efficient, smooths spikes, ~99.997% accurate | Approximate (assumes even distribution in previous window) |

**Used by**: Token Bucket → Amazon, Stripe. Leaking Bucket → Shopify. Sliding Window → Cloudflare.

**Where to Place It**: API Gateway middleware (most common in microservices) or server-side. Not client-side (easily forged).

**High-Level Architecture**:
```
Client → Rate Limiter Middleware → API Servers
              ↕
         Redis (counters + TTL)
              ↕
         Rules Cache (loaded from config on disk by workers)
```

**Redis Implementation** (Token Bucket / Fixed Window):
- `INCR key` — atomically increment counter
- `EXPIRE key ttl` — auto-delete after time window
- Use Lua scripts for atomic check-and-increment (avoids race conditions)

**Response Headers**:
```
X-Ratelimit-Remaining: 4      # requests left in current window
X-Ratelimit-Limit: 10         # total allowed per window
X-Ratelimit-Retry-After: 30   # seconds until reset
HTTP 429 Too Many Requests     # when throttled
```

**Distributed Challenges**:

| Challenge | Problem | Solution |
|---|---|---|
| **Race condition** | Two threads read same counter, both increment → under-counting | Lua script in Redis (atomic read+increment) or Redis sorted sets |
| **Synchronization** | Multiple rate limiter servers don't share state → client can exceed limit by hitting different servers | Centralized Redis store (not sticky sessions — not scalable) |
| **Multi-datacenter latency** | Users far from Redis → high latency on every request | Edge servers with local Redis, eventual consistency sync |

**Rate Limiting Rules** (Lyft open-source format):
```yaml
domain: messaging
descriptors:
  - key: message_type
    value: marketing
    rate_limit:
      unit: day
      requests_per_unit: 5
```
Rules stored on disk → workers pull periodically → cached in memory.

**Bucket Granularity**:
- Per user per API endpoint (e.g., 1 post/sec, 150 friends/day, 5 likes/sec → 3 buckets per user)
- Per IP address (DDoS protection)
- Global bucket (system-wide max QPS)

**When Rate Limited**:
- Return 429 + retry headers
- Optionally enqueue for later processing (e.g., rate-limited orders during flash sales)

**Hard vs Soft Rate Limiting**:
- **Hard**: Strict — never exceed threshold
- **Soft**: Allow brief bursts above threshold

**Staff+ insight**: For Stripe/Anthropic interviews, the key is showing you understand the algorithm tradeoffs and distributed challenges. Lead with: "I'd use token bucket for its burst tolerance, backed by Redis with Lua scripts for atomicity. The main distributed challenge is synchronization — centralized Redis solves it, with edge servers for latency. Rules should be config-driven and hot-reloadable." Also mention that rate limiting exists at multiple layers (L3/IP via iptables, L7/HTTP via middleware) and that monitoring is essential to tune rules without over-throttling legitimate traffic.

### Unique ID Generator Deep Dive

Core question: generate unique, 64-bit, time-sortable, numeric IDs at 10K+ IDs/sec in a distributed system. Quick chapter but frequently asked as a warm-up or sub-problem (transaction IDs, idempotency keys, order IDs).

**Four Approaches**:

| Approach | How It Works | Pros | Cons |
|---|---|---|---|
| **Multi-master replication** | DB auto_increment by K (K = number of servers) | Simple | IDs not time-ordered across servers; hard to scale when adding/removing servers |
| **UUID** | 128-bit random ID, generated independently per server | No coordination needed, easy to scale | 128 bits (not 64), not sortable by time, non-numeric |
| **Ticket Server** (Flickr) | Centralized DB with auto_increment | Numeric, simple | SPOF; multiple ticket servers need sync |
| **Snowflake** (Twitter) | 64-bit ID divided into sections: timestamp + datacenter + machine + sequence | 64-bit, time-sortable, no coordination, high throughput | Clock sync required across servers |

**Winner: Snowflake** — meets all requirements.

**Snowflake ID Layout** (64 bits):
```
| 1 bit  | 41 bits    | 5 bits       | 5 bits     | 12 bits        |
| sign=0 | timestamp  | datacenter ID| machine ID | sequence number|
```

| Section | Bits | Range | Notes |
|---|---|---|---|
| **Sign** | 1 | Always 0 | Reserved |
| **Timestamp** | 41 | ~69 years of milliseconds | Custom epoch (e.g., 2010-11-04). IDs sortable by time |
| **Datacenter ID** | 5 | 32 datacenters | Fixed at startup |
| **Machine ID** | 5 | 32 machines per DC | Fixed at startup |
| **Sequence** | 12 | 4096 per millisecond per machine | Reset to 0 each ms. Max 4096 IDs/ms/machine |

**Throughput**: 4096 IDs/ms × 32 machines × 32 DCs = **~4 billion IDs/sec** theoretical max.

**Key Considerations**:
- **Clock synchronization**: Servers must have synchronized clocks (NTP). Clock drift can cause duplicate or out-of-order IDs
- **Section length tuning**: Adjust bit allocation based on needs — fewer sequence bits + more timestamp bits for low-concurrency long-term apps
- **69-year limit**: 2^41 ms ≈ 69 years from custom epoch. Plan for epoch migration
- **High availability**: ID generator is mission-critical — deploy redundantly

**Staff+ insight**: This is often a sub-problem inside larger designs (e.g., "how do you generate transaction IDs for your payment system?"). Know Snowflake cold — it takes 2 minutes to explain and shows you understand distributed ID generation tradeoffs. The key insight: "We need IDs that are time-sortable without coordination between servers, which rules out UUID and centralized approaches. Snowflake embeds timestamp + machine ID + sequence into 64 bits, giving us sortability, uniqueness, and independence."

### Chat System Deep Dive

Core question: design a chat system supporting 1-on-1 and group chat (≤100 members), 50M DAU, online presence, multi-device sync, push notifications. Tests WebSocket, stateful services, message delivery, and presence.

**Communication Protocols**:

| Protocol | How It Works | Drawbacks |
|---|---|---|
| **Polling** | Client periodically asks server for new messages | Wasteful — most polls return empty |
| **Long Polling** | Client holds connection open until server has new data or timeout | Sender/receiver may hit different servers; can't detect client disconnect well |
| **WebSocket** | Bi-directional persistent connection over port 80/443 | Best choice — real-time, works through firewalls. Use for both send and receive |

**High-Level Architecture**:
```
Stateless Services (HTTP):         Stateful Service (WebSocket):
  ├── API Servers (login,            Chat Servers
  │   signup, profile)                 ├── Maintain persistent WS connections
  ├── behind Load Balancer             ├── Route messages between users
  └── Service Discovery                └── Coordinate with Presence Servers
       (Zookeeper — assigns
        best chat server to client)

Storage:                            Third-Party:
  KV Store (chat history)             Push Notification Servers
  ├── HBase (Facebook)
  └── Cassandra (Discord)
```

**Why KV Store for Chat History** (not relational DB):
- Enormous volume (60B messages/day at Facebook+WhatsApp scale)
- Access pattern: mostly recent messages, occasional random access (search, mentions)
- Read:write ratio ≈ 1:1
- Relational DB handles long-tail poorly (indexes grow huge → expensive random access)
- KV stores: easy horizontal scaling, low latency

**Data Model**:
```
1-on-1 messages:
  PK: message_id
  Fields: message_from, message_to, content, created_at

Group messages:
  PK: (channel_id, message_id)   ← channel_id is partition key
  Fields: message_from, content, created_at
```
- `message_id`: Snowflake ID (time-sortable, unique). Can't use `created_at` for ordering (two messages may have same timestamp)
- For group chat, local sequence numbers suffice (unique within channel, not globally)

**Service Discovery** (Zookeeper):
```
1. User A logs in → API server authenticates
2. Service discovery picks best chat server (by geo, capacity)
3. Returns chat server address to client
4. Client opens WebSocket to assigned chat server
```

**1-on-1 Message Flow**:
```
1. User A sends message via WebSocket to Chat Server 1
2. Chat Server 1 gets message_id from ID generator
3. Message → message sync queue
4. Message stored in KV store
5a. If User B online → forward to Chat Server 2 (where B is connected) → deliver via WebSocket
5b. If User B offline → push notification server
```

**Multi-Device Sync**:
- Each device tracks `cur_max_message_id` (latest message ID seen on that device)
- On reconnect, device fetches all messages with ID > `cur_max_message_id` from KV store
- Simple and effective — each device independently catches up

**Small Group Chat** (fan-out on write):
```
User A sends message to group (A, B, C)
  → Message copied to User B's message sync queue (inbox)
  → Message copied to User C's message sync queue (inbox)
Each recipient reads only from their own inbox
```
- Good for small groups (≤100-500): simplifies sync, each client checks one inbox
- WeChat uses this approach (groups capped at 500)
- **Not suitable for large groups** — storing a copy per member is too expensive

**Online Presence**:

| Event | Action |
|---|---|
| **Login** | Save `{user_id: online, last_active_at: now}` in KV store |
| **Logout** | Update status to offline |
| **Disconnect** | Don't immediately mark offline — use **heartbeat mechanism** |

**Heartbeat**: Client sends heartbeat every 5 seconds. If no heartbeat received within 30 seconds → mark offline. Prevents flapping during brief network interruptions (e.g., tunnel).

**Presence Fanout** (pub-sub):
```
User A's status changes → publish to channels A-B, A-C, A-D
User B subscribes to A-B → gets notified
```
- Works for small friend lists
- For large groups (100K members): don't fan out — fetch presence on demand (when user opens group or refreshes)

**Staff+ insight**: The key architectural decisions: (1) WebSocket for real-time bidirectional messaging — but HTTP for everything else (login, profile, etc.). (2) Stateful chat servers + Zookeeper for service discovery — clients stick to one server. (3) KV store for chat history (HBase/Cassandra) — not relational DB. (4) Fan-out on write for small groups (inbox per user), but switch to fan-out on read for large groups. This maps directly to the Airbnb Messaging Staff role.

### YouTube / Video Streaming Deep Dive

Core question: design a video streaming service (YouTube/Netflix). 5M DAU, upload + stream videos, multiple resolutions, global. Tests video transcoding pipeline, CDN cost optimization, and DAG-based processing. Directly relevant to **Netflix** roles.

**Back-of-Envelope**:
- 5M DAU × 10% upload × 300MB avg = **150 TB/day** new storage
- CDN cost: 5M × 5 videos/day × 0.3GB × $0.02/GB = **$150K/day** (CDN is the dominant cost)

**Two Core Flows**:
```
1. Video Upload Flow:  Client → API servers → Original blob storage → Transcoding → CDN
2. Video Streaming Flow:  Client → CDN edge server (closest) → stream video chunks
```

**Video Upload Architecture**:
```
Client uploads video
  ├── Flow A: Upload actual video
  │     1. Upload to Original Storage (blob)
  │     2. Transcoding servers fetch & transcode
  │     3a. Transcoded videos → Transcoded Storage → CDN
  │     3b. Completion event → Completion Queue → Completion Handler
  │     4. Handler updates Metadata DB + Cache
  │     5. API server notifies client: ready for streaming
  │
  └── Flow B: Upload metadata (parallel with Flow A)
        Client → API servers → Metadata DB + Cache
        (file name, size, format, etc.)
```

**Video Transcoding Pipeline** (DAG Model — inspired by Facebook SVE):
```
Original Video
  ├── Video → Inspection → Video Encoding (multiple resolutions/codecs) → Watermark
  ├── Audio → Audio Encoding
  └── Metadata extraction → Thumbnail generation
```
- **DAG** (Directed Acyclic Graph) defines task dependencies → enables parallel execution of independent tasks
- **Preprocessor**: Split video into GOPs (Group of Pictures, ~few seconds each), generate DAG, cache segments
- **DAG Scheduler**: Split DAG into stages, enqueue tasks
- **Resource Manager**: Task queue (priority) + Worker queue (utilization) + Running queue + Task scheduler
- **Task Workers**: Execute encoding, thumbnailing, watermarking, etc.
- **Temporary Storage**: Cache metadata in memory, video/audio in blob storage. Freed after processing

**Streaming Protocols**: MPEG-DASH, Apple HLS, Microsoft Smooth Streaming, Adobe HDS. Key point: different protocols support different encodings/players. Videos stream from CDN edge servers closest to user.

**Speed Optimizations**:

| Optimization | How |
|---|---|
| **Parallel upload** | Client splits video by GOP → upload chunks in parallel → fast resumable uploads |
| **Upload centers** | Multiple global upload centers (use CDN as upload points) |
| **Pipeline parallelism** | Message queues between download → encode → upload stages. Each stage processes independently |

**Safety Optimizations**:

| Optimization | How |
|---|---|
| **Pre-signed upload URL** | Client gets pre-signed URL from API server → uploads directly to blob storage. Only authorized uploads |
| **DRM** | Apple FairPlay, Google Widevine, Microsoft PlayReady |
| **AES encryption** | Encrypt video, decrypt on playback with authorization |
| **Visual watermark** | Overlay identifying info on video |

**Cost-Saving Optimizations** (CDN is expensive):
1. **Popular videos only on CDN** — long-tail videos served from origin storage servers
2. **Fewer encoded versions for unpopular content** — encode on-demand for short/rare videos
3. **Regional distribution** — region-popular videos stay in that region's CDN only
4. **Build your own CDN** (Netflix approach) — partner with ISPs for last-mile delivery

**Error Handling**:

| Component | Error Strategy |
|---|---|
| Upload | Retry |
| Video splitting | Server-side fallback for old clients |
| Transcoding | Retry on new worker |
| DAG scheduler | Reschedule task |
| Resource manager queue | Use replica |
| API server down | Stateless → route to another server |
| Metadata cache down | Read from replica, spin up replacement |
| Metadata DB master down | Promote slave |

**Staff+ insight**: For Netflix interviews, emphasize: (1) The DAG model for transcoding — it's how Facebook and Netflix actually build their encoding pipelines, enabling flexible parallel processing. (2) CDN cost optimization is the real engineering challenge — long-tail distribution means most videos are rarely watched, so tiered storage (CDN for hot, origin for cold) is critical. (3) GOP-aligned chunked uploads enable resumable parallel uploads and adaptive bitrate streaming. (4) Pre-signed URLs are the standard pattern for secure direct-to-storage uploads without proxying through your API servers.

### Web Crawler Deep Dive

Core question: design a web crawler for search engine indexing. 1B pages/month (~400 QPS, peak 800). Tests distributed task scheduling, URL frontier design, politeness, deduplication, and robustness. Good for infrastructure-heavy roles at any company.

**Back-of-Envelope**:
- 1B pages/month ÷ 30 days ÷ 86400 sec ≈ **400 pages/sec** (peak ~800)
- 500KB avg page size × 1B pages = **500 TB/month**
- 5-year retention: 500 TB × 60 months = **30 PB**

**High-Level Workflow** (BFS-based):
```
1. Seed URLs → URL Frontier (queue of URLs to download)
2. URL Frontier → HTML Downloader (fetches pages via HTTP)
3. HTML Downloader → DNS Resolver → download page
4. Downloaded page → Content Parser (validate, reject malformed)
5. Content Parser → "Content Seen?" (hash-based dedup — skip if duplicate)
6. If new content → Content Storage + URL Extractor
7. URL Extractor → extract links → URL Filter (exclude blacklisted, bad extensions)
8. URL Filter → "URL Seen?" (Bloom filter — skip if already visited)
9. If new URL → URL Frontier (loop back to step 2)
```

**URL Frontier** — the key component. Two modules:

**Front Queues (Priority)**:
```
URLs → Prioritizer (compute priority by PageRank, traffic, update frequency)
  → Queue f1 (high priority)
  → Queue f2 (medium priority)
  → Queue fn (low priority)
  → Queue Selector (weighted random pick — bias toward high priority)
```

**Back Queues (Politeness)**:
```
→ Queue Router (route URL to queue by hostname)
  → Queue b1 (wikipedia.com only)
  → Queue b2 (apple.com only)
  → Queue bn (nike.com only)
  → Queue Selector → Worker Thread (one thread per queue)
     Each thread downloads one page at a time from same host with delay between requests
```
- **Key insight**: Separate priority (what to crawl next) from politeness (don't overwhelm any single host)
- Storage: Hybrid — most URLs on disk, enqueue/dequeue buffers in memory, periodic flush

**Deduplication**:

| Component | What It Deduplicates | Technique |
|---|---|---|
| **"Content Seen?"** | Page content (29% of web is duplicate) | Compare hash values of HTML (not character-by-character) |
| **"URL Seen?"** | URLs already visited or in frontier | Bloom filter or hash table |

**HTML Downloader Optimizations**:

| Optimization | How |
|---|---|
| **Distributed crawl** | Partition URL space across multiple servers, each running multiple threads |
| **DNS caching** | Cache DNS lookups (DNS is 10-200ms, synchronous — major bottleneck). Update via cron |
| **Geo-locality** | Place crawl servers near target websites for faster downloads |
| **Timeouts** | Short max wait time per request — don't block on unresponsive servers |
| **robots.txt caching** | Download and cache robots.txt per domain, refresh periodically |

**Robustness**:
- **Consistent hashing** for distributing load across downloaders (easy add/remove servers)
- **Save crawl state** to storage — restart from checkpoint after failure
- **Exception handling** — graceful error handling, no full-system crashes
- **Spider trap detection** — max URL length, manual identification of trap sites

**Freshness**: Recrawl strategy based on page update history + priority (important pages recrawled more frequently).

**Extensibility**: Plugin architecture — add new modules (e.g., PNG Downloader, Web Monitor) without redesigning core system.

**Problematic Content**:
- **Redundant content**: Hash-based dedup (~30% of web is duplicate)
- **Spider traps**: Infinite URL loops (e.g., `/foo/bar/foo/bar/...`) — max URL depth
- **Data noise**: Ads, spam, code snippets — filter before storage

**Staff+ insight**: The URL frontier is the heart of this design — it's where you show depth. Lead with: "The frontier has two concerns: priority (what's most valuable to crawl next) and politeness (don't DDoS any host). I'd split it into front queues for priority ranking and back queues for per-host rate limiting with one worker thread per host." Also emphasize distributed crawling with consistent hashing, DNS caching as a critical performance optimization, and Bloom filters for URL dedup at scale. This problem tests your ability to design a robust distributed task processing system.

### Distributed Message Queue Deep Dive

Core question: design a distributed message queue (Kafka-like) with long retention, ordered delivery, configurable delivery semantics, and high throughput. Tests partitioning, replication (ISR), consumer groups, and delivery guarantees. Foundational for **Stripe** (workflow engine), **Netflix** (event-driven arch), **Coinbase** (async processing).

**Message Queue vs Event Streaming Platform**:
- Traditional MQ (RabbitMQ, ActiveMQ): no retention, no ordering guarantee, point-to-point
- Event Streaming (Kafka, Pulsar): long retention, ordered within partition, pub-sub + consumer groups
- Lines are blurring — this design covers the streaming platform flavor

**Core Concepts**:

| Concept | Definition |
|---|---|
| **Topic** | Named category for messages. Producers write to topics, consumers subscribe to topics |
| **Partition** | Shard of a topic. FIFO within partition. Distributed across brokers for scalability |
| **Offset** | Position of a message within a partition. Monotonically increasing |
| **Broker** | Server that holds partitions. Multiple brokers form the cluster |
| **Consumer Group** | Set of consumers that collectively consume a topic. Each partition assigned to exactly one consumer in the group |
| **Message Key** | Optional. `hash(key) % numPartitions` determines partition. Same key → same partition → ordering preserved |

**High-Level Architecture**:
```
Producers → Brokers (hold partitions on disk as WAL segments)
               ↕
          Coordination Service (Zookeeper/etcd)
            ├── Leader election (one broker = active controller)
            ├── Metadata storage (topic config, partition assignments)
            └── State storage (consumer offsets, partition-consumer mapping)
               ↕
          Consumer Groups ← pull messages from partitions
```

**Why WAL on Disk** (not database):
- Sequential read/write access pattern → rotational disks achieve hundreds of MB/sec
- OS aggressively caches disk data in memory
- Append-only segments: active segment receives writes, old segments are read-only
- Segments truncated after retention period (e.g., 2 weeks)
- Database is not ideal: hard to support both write-heavy and read-heavy at scale

**Messaging Models**:

| Model | How | Our Design |
|---|---|---|
| **Point-to-point** | Each message consumed by exactly one consumer | Put all consumers in same consumer group → each partition → one consumer |
| **Pub-sub** | Each message consumed by all subscribers | Multiple consumer groups subscribe to same topic → each group gets all messages |

**Key Constraint**: One partition → one consumer per group. This guarantees ordering within partition and prevents duplicate processing.

**Producer Flow**:
```
Producer (with routing logic + batch buffer built into client library)
  → hash(message_key) % numPartitions → select partition
  → batch messages in memory buffer (throughput vs latency tradeoff)
  → send batch to leader replica of target partition
  → leader writes to WAL, followers pull from leader
  → ACK returned based on config
```

**ACK Settings** (durability vs performance):

| ACK | Behavior | Use Case |
|---|---|---|
| **ack=all** | Wait for ALL ISRs to sync | Strongest durability. Financial data |
| **ack=1** | Wait for leader only | Low latency, occasional loss acceptable |
| **ack=0** | Fire and forget, no retry | Lowest latency. Metrics, logging |

**Consumer Flow** (pull model — consumers control rate):
```
1. Consumer joins group → finds coordinator broker (hash of group name)
2. Coordinator assigns partitions to consumer
3. Consumer reads from last committed offset (stored in state storage)
4. Consumer processes message, then commits offset
```
**Pull > Push**: consumers control consumption rate, supports both real-time and batch modes, scales by adding consumers. Long polling avoids busy-waiting when no messages.

**Consumer Rebalancing** (triggered by join/leave/crash):
```
1. Coordinator detects change (heartbeat timeout or explicit leave)
2. Notifies all consumers to rejoin group
3. Elects consumer leader → generates new partition assignment plan
4. Coordinator broadcasts plan → consumers start consuming from new assignments
```

**Replication & In-Sync Replicas (ISR)**:
```
Each partition: 1 leader + N-1 follower replicas across different brokers
Producers write to leader → followers pull from leader
ISR = replicas that are "in-sync" (within configured lag threshold)
Committed offset = all ISRs have synced up to this point
```
- If follower falls behind → removed from ISR → can rejoin when caught up
- Leader fails → new leader elected from ISR
- Replicas must be on different broker nodes (same node = no fault tolerance)

**Broker Failure Recovery**:
```
Broker 3 crashes → controller detects via Zookeeper
  → generates new replica distribution plan
  → assigns new replicas on remaining brokers
  → new followers catch up from leaders
```

**Broker Scaling** (add new broker):
```
1. New broker 4 added
2. Controller assigns some partition replicas to broker 4
3. New replicas copy data from leaders (temporarily > configured replica count)
4. Once caught up, remove old redundant replicas
→ No data loss during scaling
```

**Partition Scaling**:
- **Increase**: New partition created, new messages go to all partitions. No data migration needed
- **Decrease**: Decommission partition (stop receiving new messages). Keep serving reads until retention expires, then truncate

**Delivery Semantics**:

| Semantic | Producer | Consumer | Use Case |
|---|---|---|---|
| **At-most-once** | ack=0, no retry | Commit offset before processing | Metrics, logging (loss OK) |
| **At-least-once** | ack=1 or all, retry on failure | Commit offset after processing (may re-consume on crash) | Most use cases. Dedup on consumer side |
| **Exactly-once** | Idempotent producer + ack=all | Transactional offset commit | Financial systems (expensive to implement) |

**Advanced Features**:
- **Message filtering**: Tags in message metadata → broker filters before delivery (no payload decryption needed)
- **Delayed messages**: Store in temporary topic → timing function delivers to real topic when time expires (e.g., "check payment after 30 min")
- **Batching everywhere**: Producer batches in memory, broker writes large sequential batches, consumer fetches in batches → critical for throughput

**Staff+ insight**: This is foundational infrastructure knowledge. Key points to lead with: (1) "Partitions are the unit of parallelism and ordering — I'd use `hash(key) % partitions` for deterministic routing and guarantee ordering within a partition." (2) "ISR is the durability knob — ack=all with ISR gives us strong durability, ack=1 trades durability for latency." (3) "Consumer groups give us both pub-sub (multiple groups) and point-to-point (single group) from the same primitive." (4) "WAL on disk with sequential I/O outperforms databases for this access pattern, and OS page cache gives us near-memory speed for hot data." This directly applies to Stripe's workflow engine role and any event-driven architecture discussion.

---

## Numbers Every Engineer Should Know

### Latency

| Operation | Time |
|---|---|
| L1 cache reference | 1 ns |
| L2 cache reference | 4 ns |
| Main memory reference | 100 ns |
| SSD random read | 16 μs |
| HDD random read | 2 ms |
| Round trip within data center | 0.5 ms |
| Round trip cross-continent | 150 ms |

### Throughput

| System | Capacity |
|---|---|
| Single PostgreSQL | ~10K–50K QPS (depending on query complexity) |
| Single Redis | ~100K–500K QPS |
| Single Kafka broker | ~100K–1M messages/sec |
| Single machine network | 1–10 Gbps |

### Storage

| Unit | Size |
|---|---|
| 1 char (ASCII) | 1 byte |
| 1 tweet (text) | ~300 bytes |
| 1 image (compressed) | ~300 KB |
| 1 min video (compressed) | ~10 MB |
| 1 million users × 1 KB each | 1 GB |
| 1 billion rows × 100 bytes | 100 GB |

### Quick Math
- **Seconds in a day**: ~86,400 ≈ ~100K
- **Seconds in a year**: ~31M ≈ ~30M
- **1M QPS**: need sharding / distributed system
- **10K QPS**: single beefy DB can handle
- **100K QPS**: Redis / Memcached territory

---

## Staff+ Differentiators

Things that separate staff/principal candidates from senior candidates:

### 1. Drive the Conversation
- Don't wait for prompts. Propose the agenda: "I'd like to spend 5 min on requirements, sketch the architecture, then deep dive into [hardest part]."
- Proactively identify scope boundaries: "I'm going to defer [X] and focus on [Y] since that's the core challenge."

### 2. Multi-Dimensional Tradeoffs
- Never present one option. Always compare 2–3 approaches.
- Include non-technical dimensions: "Option A is simpler but requires the team to learn [technology]. Option B uses our existing stack but introduces operational complexity."

### 3. Think in Phases
- **Phase 1** (MVP): Simple architecture, single DB, monolith. Handles 10K users.
- **Phase 2** (Growth): Add caching, read replicas, separate hot services. Handles 1M users.
- **Phase 3** (Scale): Shard DB, event-driven architecture, multi-region. Handles 100M users.
- Explicitly state migration strategy between phases.

### 4. Organizational Awareness
- "This service sits at the boundary between the Payments team and the Orders team. I'd define a clear API contract and use async events to decouple them."
- Consider on-call burden, team size, hiring plan.
- Think about cross-team dependencies and how to minimize them.

### 5. Failure as a First-Class Concern
- For every component: "What happens when this fails?"
- Data loss scenarios: "If this cache goes down, we lose [X]. To mitigate, we'd [Y]."
- Graceful degradation: "If recommendations are down, we show chronological feed instead."

### 6. Know When NOT to Over-Engineer
- "We could add a message queue here, but with 100 QPS writes, a synchronous call with a retry is simpler and sufficient. We'd add the queue when we hit 10K QPS."
- Simple solutions that work > complex solutions that scale to infinity.

---

## Quick Reference: System Design Checklist

Before you finish, make sure you've covered:

- [ ] **Functional requirements** scoped and prioritized
- [ ] **Non-functional requirements** quantified (QPS, latency, availability)
- [ ] **Back-of-envelope math** done
- [ ] **API design** with clear endpoints and pagination
- [ ] **High-level diagram** with labeled components and data flows
- [ ] **Data model** with storage choice justified
- [ ] **Deep dive** into 1–2 hardest subproblems with tradeoff analysis
- [ ] **Caching strategy** if read-heavy
- [ ] **Scaling approach** stated (what happens at 10x, 100x)
- [ ] **Failure modes** identified with mitigation
- [ ] **Monitoring** — how you know it's healthy
- [ ] **Security** — auth, encryption, PII handling

---

## Recommended Resources

### Core Reading

| Resource | What It Covers | Priority |
|---|---|---|
| **[System Design Primer](https://github.com/donnemartin/system-design-primer)** | Comprehensive reference: CAP, caching, DB, load balancing, async, communication protocols, 8 worked problems with solutions | Must-read — best single free resource |
| **[Designing Data-Intensive Applications (DDIA)](https://www.goodreads.com/book/show/23463279-designing-data-intensive-applications)** by Martin Kleppmann | Replication, partitioning, transactions, consistency, batch/stream processing, encoding — the theoretical foundation | Must-read — the "bible" of system design depth |
| **[DDIA Notes](https://github.com/keyvanakbary/learning-notes/blob/master/books/designing-data-intensive-applications.md)** | Chapter-by-chapter summary of DDIA | Quick review if you've read the book |
| **[ByteByteGo / Alex Xu's Course](https://bytebytego.com)** | Visual walkthroughs of common system design problems, interview-focused | Great for visual learners, paid course |

### System Design Interview Practice

| Resource | What It Covers | Priority |
|---|---|---|
| **[Grokking System Design](https://github.com/Jeevan-kumar-Raj/Grokking-System-Design)** | Educative course mirror: basics (consistent hashing, proxies, queues, CAP) + 12 designs (URL shortener, Instagram, Dropbox, Uber, Ticketmaster, etc.) | Good walkthrough of common problems |
| **[Grokking the System Design Interview PDF](https://github.com/judylime/grokking)** | PDF collection: System Design Interview, Advanced System Design, OOD | Reference PDFs for offline study |

### Coding Interview Patterns (Supplementary)

| Resource | What It Covers | Priority |
|---|---|---|
| **[Grokking Coding Interview Patterns](https://github.com/dipjul/Grokking-the-Coding-Interview-Patterns-for-Coding-Questions)** | 28 coding patterns with problems: Two Pointers, Sliding Window, Cyclic Sort, Monotonic Stack, Knapsack, Trie, Union-Find, Multi-thread, etc. | Supplementary — overlaps with your Java playbook |

### How to Use These Resources

1. **Start with this playbook** — it's tailored for staff+ level and covers the framework + building blocks
2. **Read DDIA chapters 5-9** (replication, partitioning, transactions, consistency, batch/stream) for depth — this is where interview questions about "why" come from
3. **Practice 5-6 problems end-to-end** using the Grokking System Design walkthroughs, applying this playbook's framework
4. **Reference the System Design Primer** for any building block you need to review (caching strategies, load balancing algorithms, etc.)
5. **Do mock interviews** — practice talking through a design in 35-40 minutes, hitting all checklist items
