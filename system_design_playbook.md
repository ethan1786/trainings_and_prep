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
10. [Scalability Patterns](#scalability-patterns)
11. [Consistency & Coordination](#consistency--coordination)
12. [Messaging & Async Patterns](#messaging--async-patterns)
13. [Caching Strategies](#caching-strategies)
14. [Storage Decision Guide](#storage-decision-guide)
15. [Rate Limiting & Load Management](#rate-limiting--load-management)
16. [Observability & Reliability](#observability--reliability)
17. [Security Considerations](#security-considerations)
18. [Common System Design Problems](#common-system-design-problems)
19. [Numbers Every Engineer Should Know](#numbers-every-engineer-should-know)
20. [Staff+ Differentiators](#staff-differentiators)

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
