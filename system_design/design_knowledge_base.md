# Design Knowledge Base — Patterns + Deep Tools

> Philosophy: Know patterns broadly (recognize them, understand the shape). Know tools deeply (WHY they work, WHEN they break).
> This is not a textbook to memorize. It's a reference for building genuine understanding.

---

## Part 1: Interview Delivery (Quick Reference)

**The one habit:**
> "I need [X]. Options are [A vs B]. Picking [A] because [reason]. Tradeoff: [what I give up]."

**Flow:**
1. Draw the simplest thing that works (API → service → DB)
2. Apply constraints one at a time, each addition JUSTIFIED
3. For each technology choice: one sentence on WHY, not just WHAT
4. Weave failure handling into the walkthrough naturally

**Pacing:**
- 5-8 min on requirements/constraints before drawing boxes
- Name the hardest subproblem explicitly: "The real challenge here is ___"
- Finishing early = signal left on table. Discuss alternatives, edge cases, production concerns.

---

## Part 2: Pattern Recognition (with context)

Each pattern below includes: what problem it solves, how it works (enough to reason about it), when it fits, and when it doesn't.

---

### Caching

**Problem it solves:** Reads are too frequent or too expensive for the database to handle on every request.

**How it works:**
- Store computed/fetched results in a faster layer (memory)
- On read: check cache first → if hit, return immediately → if miss, fetch from DB, populate cache
- Invalidate or expire entries to avoid serving stale data

**Placement options:**
- **In-memory (Caffeine/Guava):** per-instance, sub-ms, no network hop. Each instance has its own copy.
- **Distributed (Redis):** shared across instances, survives restarts, ~1ms. Single source of truth for cache.
- **CDN:** at the edge, for static/semi-static content. Closest to the user.
- **Client-side (browser/app):** reduces requests entirely. Controlled via Cache-Control headers.

**Strategies:**
- **Cache-aside (lazy):** app checks cache, fills on miss. Most common.
- **Write-through:** write to cache AND DB together. Strong consistency, higher write latency.
- **Write-behind:** write to cache, async flush to DB. Fast writes, risk of data loss on crash.

**Cache invalidation approaches:**
- TTL: simple, stale for up to TTL duration
- Event-driven: write triggers invalidate. Fresher but complex.
- Version key: append version to cache key. No invalidation needed, just write new version.

**Dangers:**
- Cache stampede: popular key expires, hundreds of concurrent misses hit DB. Fix: mutex/lock, early refresh, jitter on TTL.
- Thundering herd on node failure: traffic redistributes, overwhelms remaining nodes.
- Stale reads in financial systems: cache may serve outdated balance. Never cache financial source-of-truth.

**Fits when:** Read-heavy (10:1+ read:write), data can tolerate brief staleness, hot data is a small subset.

**Doesn't fit when:** Data must be real-time consistent (payments, inventory counts), writes are as frequent as reads, or the working set is too large to cache.

---

### Message Queue / Async Processing

**Problem it solves:** Decouple producer from consumer, absorb traffic spikes, handle work that doesn't need immediate response.

**How it works:**
- Producer writes a message to a queue
- Consumer pulls messages and processes them independently
- Queue acts as a buffer between the two

**Two flavors:**
- **Work queue (SQS, RabbitMQ):** message consumed once, then deleted. One consumer gets each message.
- **Event stream (Kafka):** messages retained with offsets. Multiple consumer groups can read independently. Replay possible.

**Key patterns:**
- Fan-out: one event → multiple consumers (Kafka consumer groups)
- Dead letter queue: failed messages go to a separate queue for investigation
- Backpressure: when consumers are slower, queue grows. Monitor lag and scale consumers.

**Fits when:** Traffic is bursty (spikes then settles), work is non-critical-path (notifications, analytics), services need independent scaling/deployment.

**Doesn't fit when:** Sustained write volume permanently exceeds processing capacity (queue just delays the problem), caller needs synchronous confirmation (financial transactions), or you need immediate consistency.

**Key insight:** Queues absorb SPIKES. They don't solve SUSTAINED overload. If producer rate permanently > consumer rate, the queue grows forever.

---

### Sharding / Partitioning

**Problem it solves:** Single database can't handle the write throughput, connection count, or data volume.

**How it works:**
- Split data across multiple database instances by a partition key
- Each request routes to the correct shard based on the key
- Each shard operates independently

**Strategies:**
- **Hash-based:** `hash(key) % N` → even distribution, but resharding is painful
- **Range-based:** `A-M → shard1, N-Z → shard2` → range queries work, but hotspots if uneven
- **Consistent hashing:** minimize redistribution when adding/removing nodes

**Choosing a shard key:**
- Query pattern determines key: if all queries are per-user, shard by user_id
- Good key = even distribution + queries stay within one shard
- Bad key = cross-shard queries become scatter-gather (expensive)

**Triggers for sharding:**
- Write QPS > 5K/sec for Postgres (CPU/connection bound)
- Data > 2-5TB (index doesn't fit in RAM, performance degrades)
- Connection pool exhaustion under concurrency

**Fits when:** You've exhausted vertical scaling and read replicas. Clear access pattern exists (per-user, per-tenant, per-region).

**Doesn't fit when:** You need frequent cross-partition joins, data is small, or traffic can be handled by a single node with read replicas.

---

### CQRS (Command Query Responsibility Segregation)

**Problem it solves:** Read and write patterns are fundamentally different — different schemas, different frequencies, different performance needs.

**How it works:**
- Separate the write model (normalized, optimized for correctness) from the read model (denormalized, optimized for queries)
- Writes go to the primary store
- Async events propagate changes to read-optimized stores (materialized views, Elasticsearch, Redis)

**Example:** E-commerce orders
- Write: normalized tables (orders, line_items, payments) with ACID guarantees
- Read: denormalized document per order (pre-joined, cached) for fast retrieval

**Fits when:** Read patterns need heavily denormalized views, write patterns need strict normalization/validation, read:write ratio is very high.

**Doesn't fit when:** Simple CRUD where read and write shapes are the same, system is small enough that a single model works, you can't tolerate eventual consistency on reads.

**Tradeoff:** Introduces eventual consistency between write and read models. You must decide: is "user sees slightly stale data" acceptable?

---

### Event Sourcing

**Problem it solves:** Need complete audit trail, ability to replay/reconstruct state, or temporal queries ("what was the state at time T?").

**How it works:**
- Store every state change as an immutable event (facts that happened)
- Current state = replay all events from the beginning (or from a snapshot)
- Never mutate or delete events

**Example:** Wallet balance
- Traditional: `UPDATE balance SET amount = 50 WHERE user_id = 123` (only current state)
- Event sourced: `[Deposited $100, Withdrew $30, Deposited $20, Withdrew $40]` → balance = $50

**Benefits:**
- Full audit trail (compliance, debugging)
- Rebuild state from any point in time
- Replay events with new logic to test correctness
- Natural fit for event-driven architectures

**Costs:**
- Complexity (need snapshots for performance, can't just SELECT current state)
- Schema evolution of events is hard
- Eventually consistent reads (unless you query the event store directly)

**Fits when:** Financial systems, compliance-heavy domains, systems where "how did we get here" matters, undo/replay is needed.

**Doesn't fit when:** Simple CRUD, no audit requirements, team isn't familiar with the pattern, state is simple and rarely disputed.

---

### Fan-out (Push vs Pull)

**Problem it solves:** One event needs to reach many recipients (feed, notifications, timeline).

**Three approaches:**

| Approach | How | Pro | Con |
|---|---|---|---|
| **Push (fan-out on write)** | When event happens, immediately write to all recipients' feeds | Fast reads (pre-built) | Expensive for high-follower accounts. Wasted for inactive users. |
| **Pull (fan-out on read)** | When recipient opens feed, query all sources and merge | No wasted writes | Slow reads (N queries), high compute at read time |
| **Hybrid** | Push for normal accounts, pull for celebrities | Best of both | Implementation complexity |

**The celebrity problem:** A user with 10M followers → push means 10M writes per post. Solution: don't push for celebrities. Merge their posts at read time.

**Fits when:** Social feeds, notification delivery, any 1-to-many distribution.

**Key decision:** What's the follower distribution? If 99% of users have <10K followers, push works for most. Pull only needed for the 1% celebrities.

---

### Saga Pattern (Distributed Transactions)

**Problem it solves:** A business operation spans multiple services/databases, and you need atomicity (all succeed or all compensate).

**How it works:**
- Break the operation into a sequence of local transactions
- Each step has a compensating action (undo)
- If any step fails, execute compensations in reverse order

**Example:** Book a trip (flight + hotel + car)
1. Reserve flight → success
2. Reserve hotel → success
3. Reserve car → FAILS
4. Compensate: cancel hotel, cancel flight

**Two coordination modes:**
- **Choreography:** each service listens for events and acts. Simple, decoupled. But hard to track overall progress.
- **Orchestration:** a central coordinator directs each step. Easier to reason about. But coordinator is a dependency.

**Alternatives:**
- **2PC (Two-Phase Commit):** database-level atomicity. Locks held across both phases → poor performance. Coordinator is SPOF.
- **TC/C (Try-Confirm/Cancel):** application-level, allows parallel execution. More complex (handle out-of-order).

**Fits when:** Microservices that can't share a database, operations that can be compensated, eventual consistency is acceptable.

**Doesn't fit when:** You can use a single database transaction (simpler!), compensating actions are impossible (sent an email, can't unsend), or you need real-time consistency.

---

### Circuit Breaker

**Problem it solves:** A failing dependency causes cascading failures — requests pile up waiting for timeouts, thread pools exhaust, entire system degrades.

**How it works (three states):**
1. **Closed (normal):** requests flow through. Track failure rate.
2. **Open (tripped):** after N failures, stop calling the dependency entirely. Return fallback or error immediately. No waiting.
3. **Half-open (probing):** after a cooldown, allow one request through to test if dependency recovered. If success → close. If fail → reopen.

**Key parameters:** failure threshold (how many failures to trip), timeout (how long to wait before half-open), fallback (what to return when open).

**Fits when:** Calling external services that can be slow or unavailable, you have a reasonable fallback (cached data, degraded response, default).

**Doesn't fit when:** The dependency is mandatory and there's no fallback (e.g., must charge the card — can't just skip it).

---

### Rate Limiting

**Problem it solves:** Protect services from overload (DDoS, misbehaving clients, thundering herd).

**Key algorithms:**
- **Token bucket:** fills at rate R, request takes one token. Allows bursts up to bucket size. Most common (Amazon, Stripe).
- **Sliding window counter:** weighted sum of current + previous window counts. Good accuracy, low memory.
- **Leaky bucket:** fixed drain rate, smooth output. Penalizes bursts.

**Implementation:** Redis + Lua script for atomic check-and-increment. Key = `rate:{identifier}:{window}`.

**Granularity:** Per user, per IP, per API key, per endpoint, global. Often multi-tier (check all levels).

**Fits when:** API protection, billing enforcement, fair usage, DDoS defense.

---

### Consistent Hashing

**Problem it solves:** Distributing data across nodes where adding/removing a node shouldn't require reshuffling everything.

**How it works:**
- Hash both nodes and keys onto a ring (0 to 2^32)
- Each key maps to the first node clockwise from its position
- Adding a node only affects keys between the new node and its predecessor
- Virtual nodes (100-200 per physical node) ensure even distribution

**Used in:** Cassandra, DynamoDB (partition data), CDN (map URLs to edge servers), distributed cache (key → cache node).

**Fits when:** Dynamic cluster membership (nodes join/leave), need stable mapping with minimal disruption, distributed KV stores.

**Doesn't solve:** Hot KEY problem (one key getting disproportionate traffic). That needs replication of the specific key or local caching.

---

### Tiered Storage (Hot/Warm/Cold)

**Problem it solves:** Data grows unbounded but most queries only touch recent data. Keeping everything in fast storage is expensive.

**How it works:**
- Hot: in-memory or SSD. Active data, frequently accessed. Highest cost per GB.
- Warm: primary DB or cheaper SSDs. Recent data, queryable but not latency-critical.
- Cold: object storage (S3), archive. Old data, rarely accessed. Cheapest.
- Lifecycle policies automatically move data between tiers based on age or access patterns.

**Fits when:** Data has strong temporal locality (90% of reads hit last 7 days), retention requirements are long (compliance), cost matters.

---

### Lease-Based Execution (Exactly-Once in Distributed Systems)

**Problem it solves:** Ensuring a job/task runs exactly once when workers can crash at any time.

**How it works:**
1. Worker acquires a lease (time-bounded lock) on a task
2. Worker must heartbeat to extend the lease
3. If worker crashes → no heartbeat → lease expires → task re-queued for another worker
4. Handler must be idempotent (at-least-once delivery, but same result)

**Implementation:**
```sql
UPDATE jobs SET status='RUNNING', worker_id=me, lease_expires=now()+5min
WHERE job_id=X AND status='QUEUED'
-- 0 rows affected = another worker got it
-- 1 row affected = I have the lease
```

**Fits when:** Distributed job schedulers, task queues, any "run this once" in unreliable environments.

---

### Change Data Capture (CDC)

**Problem it solves:** Keep derived stores (search index, cache, analytics) in sync with the source database without dual-write problems.

**How it works:**
- Read the database's transaction log (binlog in MySQL, WAL in Postgres)
- Stream changes to downstream consumers via Kafka
- Consumers update their own stores based on the change events

**Why not dual-write (write to DB + write to Elasticsearch):** If the second write fails, you have inconsistency. CDC guarantees: if it's in the DB, it will reach downstream.

**Tools:** Debezium (reads binlog → Kafka), AWS DMS, pg_logical.

**Fits when:** Need to sync data to multiple stores, want guaranteed consistency between primary and derived stores, need an event stream of all changes.

---

## Part 3: Deep Tool Knowledge

For each tool: understand WHY it works the way it does, WHEN it's the right choice, and WHEN it breaks.

---

### PostgreSQL

**What it is:** Relational database with ACID transactions, rich SQL, and extensibility.

**RIGHT choice when:**
- Need transactions across multiple tables (ACID)
- Need complex queries (joins, CTEs, window functions, aggregations)
- Need strong consistency (linearizable reads and writes)
- Data has clear relationships and schema
- Need constraints enforced at the DB level (foreign keys, unique, check)

**WRONG choice when:**
- Write throughput exceeds ~5K TPS on a single node and you can't shard cleanly
- Schema is genuinely unknown/rapidly changing (document-shaped data)
- Access pattern is simple key-value lookup at extreme scale (100K+ QPS)
- Data is naturally document-shaped with no cross-document queries

**Alternatives:**
- DynamoDB/Cassandra: trades rich queries for horizontal write scaling
- MongoDB: trades ACID for flexible schema and document model
- Redis: trades durability for sub-ms latency (cache, not source of truth)

**Failure modes:**
- Connection exhaustion: max_connections hit under concurrency. Fix: connection pooling (PgBouncer, HikariCP).
- Vacuum lag (MVCC bloat): dead tuples accumulate, table/index bloat, queries slow down. Fix: tune autovacuum.
- Lock contention: long transactions hold locks, block others. Fix: short transactions, optimistic locking.
- Replication lag: read replicas serve stale data. Fix: route critical reads to primary, or use synchronous replication (costs latency).
- Index bloat: over-indexing costs write performance and disk. Each index = overhead on every INSERT/UPDATE.

**Deciding question:** "Do I need ACID transactions or complex joins? If yes → Postgres. If my access pattern is simple lookups at massive scale → look elsewhere."

**Capacity reference:**
- Single node: ~5K writes/sec, ~50K reads/sec (indexed)
- Comfortable data size: up to 2-5TB before operations (backup, vacuum, restore) become painful
- Connection limit: ~500-1000 connections with pooling. Direct connections saturate much sooner.

---

### Redis

**What it is:** In-memory data structure store. Sub-millisecond latency. Rich data structures beyond simple KV.

**RIGHT choice when:**
- Need sub-ms latency for hot-path reads
- Data fits in memory (or you accept eviction)
- Need rich data structures: sorted sets (leaderboards), HyperLogLog (cardinality), streams, pub/sub
- Cache layer in front of a database
- Session storage, rate limiting counters, distributed locks (simple cases)
- Shared state across multiple application instances

**WRONG choice when:**
- Data must be durable (Redis persistence is best-effort — RDB snapshots lose seconds of data, AOF is slower)
- Source of truth for financial data (crash = potential data loss between snapshots)
- Data doesn't fit in memory and eviction isn't acceptable
- You need complex queries (joins, range scans across multiple keys, ad-hoc filtering)
- Single instance, single service → in-memory cache (Caffeine) is simpler, no network hop

**Alternatives:**
- In-memory cache (Caffeine/Guava): no network hop, per-instance, simpler. Doesn't share state.
- Memcached: simpler than Redis (pure KV, no data structures), multi-threaded (better for simple cache workloads).
- DynamoDB DAX: managed cache for DynamoDB specifically.

**Failure modes:**
- Memory exhaustion: eviction kicks in (LRU/LFU), performance degrades, or OOM kill. Fix: monitor memory, set maxmemory + eviction policy.
- Single-threaded bottleneck: one slow command (KEYS *, large SORT) blocks everything. Fix: never use KEYS in production, use SCAN.
- Split-brain in cluster: network partition → two masters → data divergence. Fix: proper quorum config, Redis Sentinel.
- Thundering herd on restart: cold cache → all requests hit DB simultaneously. Fix: warm cache before accepting traffic, or stagger TTLs.
- Replication lag: replica serves stale data. Fix: don't read from replicas for consistency-critical paths.

**Deciding question:** "Do multiple instances need shared, fast state? → Redis. Single instance, hot-path only? → In-memory cache. Source of truth for data that can't be lost? → Not Redis."

**Capacity reference:**
- Single node: 100K-500K ops/sec
- Latency: ~0.5-1ms per operation (network + lookup)
- Memory: what you buy is what you get. 1M keys × 1KB = ~1GB.

---

### Kafka

**What it is:** Distributed event streaming platform. Append-only log with configurable retention.

**RIGHT choice when:**
- Need replay for crash recovery or reprocessing
- Multiple independent consumers need the same data (consumer groups)
- Need ordering guarantees within a partition
- Need high throughput event streaming (100K+ msgs/sec)
- Need decoupling with retention (events persist for days/weeks)
- Building CDC pipelines, event sourcing, or data lake ingestion

**WRONG choice when:**
- Single consumer, simple work queue, low volume → Kafka's operational overhead isn't justified
- Need message-level routing/filtering (RabbitMQ does this natively)
- Need request-reply pattern (Kafka is fire-and-forget by design)
- Don't need replay AND don't need multiple consumers → SQS is simpler and managed
- Latency must be sub-ms (Kafka adds batching latency by design for throughput)

**Alternatives:**
- SQS: managed, cheap, simple. No replay, no ordering across messages (FIFO variant has limits). Best for simple task queues.
- RabbitMQ: message routing (exchanges, bindings), per-message acknowledgment, lower latency per message. No replay.
- Redis Streams: lightweight, lower latency, but not as durable or scalable. Good for moderate throughput where you already have Redis.
- Direct HTTP: simplest. Coupled. No buffer. Fine for low-volume synchronous calls.

**Failure modes:**
- Consumer lag grows unbounded: consumers can't keep up. Backlog grows. Fix: scale consumers (add to consumer group), or address root cause (slow processing).
- Partition rebalancing storms: consumers join/leave frequently → constant rebalancing → no progress. Fix: stable consumer group membership, increase session timeout.
- Offset management bugs: commit offset before processing → lose messages. Commit after processing → duplicate on crash. Fix: at-least-once + idempotent consumers.
- Broker disk full: retention exceeds disk capacity. Fix: monitor disk, set retention limits (time or size based).
- Uneven partition load: hot partition key → one partition gets disproportionate traffic. Fix: choose partition key carefully, or add salt for hot keys.

**Deciding question:** "Do I need replay OR multiple independent consumers? If yes → Kafka. Simple fire-and-forget task queue? → SQS. Need routing/filtering? → RabbitMQ."

**Capacity reference:**
- Single broker: 100K-500K messages/sec (depending on message size)
- Partition: unit of parallelism. More partitions = more throughput but more metadata overhead.
- Latency: 5-50ms end-to-end (producer batch → broker → consumer poll interval).

---

### Elasticsearch

**What it is:** Distributed search and analytics engine built on Apache Lucene. Inverted index for full-text search.

**RIGHT choice when:**
- Need full-text search (fuzzy matching, relevance scoring, tokenization)
- Need complex aggregations on semi-structured data (analytics dashboards)
- Need to search across multiple fields with flexible queries
- Log analytics (ELK stack: Elasticsearch + Logstash + Kibana)
- Need near-real-time search index (seconds after write, not ms)

**WRONG choice when:**
- Source of truth (ES can lose writes, lacks ACID). Always pair with a primary store.
- Simple exact-match lookups (Postgres with index or Redis is faster and simpler)
- High write throughput with strong consistency requirements
- Small dataset that fits in a single DB query easily
- Need transactions or relational integrity

**Alternatives:**
- Postgres full-text search: built-in, simpler ops, good for moderate search needs. Worse relevance tuning than ES.
- Algolia: managed, optimized for typo-tolerance and speed. Expensive at scale. Best for user-facing search.
- Meilisearch/Typesense: lighter alternatives to ES for smaller scale.
- OpenSearch: AWS fork of Elasticsearch. Functionally equivalent.

**Failure modes:**
- Split brain: network partition → two masters → index corruption. Fix: proper discovery settings, minimum_master_nodes.
- GC pauses: large heaps → long GC pauses → node appears dead → rebalancing storm. Fix: heap ≤ 32GB, proper GC tuning.
- Shard explosion: too many small shards → overhead per shard. Fix: plan shard count based on data volume (target 20-50GB per shard).
- Mapping explosion: dynamic mapping creates fields unboundedly → memory exhaustion. Fix: strict mapping, limit total fields.
- Stale reads after write: documents aren't searchable until segment refresh (default 1s). Fix: explicit refresh for critical paths (but costs performance).

**Deciding question:** "Do users type free-text queries and expect relevant, fuzzy results? → Elasticsearch. Exact match on known fields? → Database index."

---

### MongoDB / DynamoDB (Document / NoSQL)

**What they are:** Schema-flexible stores optimized for known access patterns and horizontal scaling.

**RIGHT choice when:**
- Data is naturally document-shaped (nested objects, arrays, no cross-document joins)
- Access patterns are simple and well-known at design time (DynamoDB requires this)
- Need horizontal write scaling beyond what Postgres can handle
- Schema evolves frequently (MongoDB's flexible schema)
- Single-digit ms latency at any scale (DynamoDB's strength)

**WRONG choice when:**
- Need transactions across multiple documents/collections (MongoDB has limited multi-doc txns, DynamoDB has limited txns)
- Need complex ad-hoc joins or aggregations across entities
- Access patterns are unknown or frequently change (DynamoDB's single-table design is rigid)
- Data is highly relational (user → orders → line_items → products with many-to-many)

**DynamoDB-specific:**
- Must design access patterns FIRST, then model data. Adding a new access pattern later often means a new GSI or table redesign.
- Partition key choice is critical. Hot partition → throttling.
- GSI is eventually consistent (seconds of lag).

**MongoDB-specific:**
- Flexible schema is double-edged: no constraints means app must enforce consistency.
- Write concern + read concern give tunable consistency (similar to Cassandra).
- Sharding requires choosing a shard key upfront. Bad choice is expensive to fix.

**Deciding question:** "Is my data document-shaped with known access patterns? → DynamoDB/Mongo. Do I need joins, transactions, or ad-hoc queries? → Postgres."

---

### gRPC

**What it is:** High-performance RPC framework using HTTP/2 and Protocol Buffers (binary serialization).

**RIGHT choice when:**
- Service-to-service communication (internal, not browser-facing)
- Need strong contracts between teams (`.proto` IDL, code generation)
- Need performance: binary encoding is 2-10x smaller than JSON
- Need streaming (bidirectional, server-push, client-push)
- Polyglot environment (proto generates clients in any language)

**WRONG choice when:**
- Public API consumed by browsers (gRPC needs gRPC-Web proxy for browsers)
- Simple CRUD where REST conventions are clear enough
- Team unfamiliar with protobuf tooling (learning curve for proto management)
- Need human-readable payloads for debugging (binary is opaque)

**Alternatives:**
- REST/JSON: universal, human-readable, browser-native. Larger payloads, no streaming (without SSE/WebSocket).
- GraphQL: client specifies exactly what data it needs. Great for mobile (reduce over-fetching). Overkill for service-to-service.

**Failure modes:**
- Proto backward compatibility broken: removing a field or changing a type breaks consumers. Fix: never reuse field numbers, only add optional fields.
- Load balancer misconfiguration: gRPC uses HTTP/2 with long-lived connections. L4 load balancers don't distribute well (all requests on one connection go to one backend). Fix: use L7 load balancer (Envoy), or client-side load balancing.
- Deadline propagation: if service A calls B calls C, each needs a timeout budget. Without deadline propagation, C can take forever while A's client has already timed out.

**Deciding question:** "Internal service-to-service, need strong contracts + performance? → gRPC. External/public API or browser clients? → REST."

---

### WebSocket

**What it is:** Persistent, bidirectional communication channel over TCP (upgraded from HTTP).

**RIGHT choice when:**
- Need real-time bidirectional communication (chat, live updates, collaborative editing)
- Server needs to push data to client without polling (notifications, live dashboards)
- Low-latency updates matter (trading, gaming)

**WRONG choice when:**
- Updates are infrequent (polling every 30s is simpler and cheaper)
- One-way server → client only (SSE is simpler, auto-reconnects)
- Stateless request-response pattern (REST is simpler)
- Need to work through all corporate proxies (some don't support WebSocket, though most modern ones do)

**Alternatives:**
- Server-Sent Events (SSE): one-way server→client push. Simpler, auto-reconnect, works with HTTP/1.1. No client→server channel.
- Long polling: client holds request open until server has data. Higher latency, works everywhere. Good for mobile (battery-friendly).
- HTTP/2 push: limited, being deprecated. Not a real alternative.

**Operational concerns:**
- WebSocket servers are STATEFUL: client connects to a specific server. Need service discovery (user → server mapping).
- Horizontal scaling: need a registry (Redis, ZooKeeper) to know which server holds which user's connection.
- Connection limits: each WebSocket = open TCP connection + memory. A server can hold ~50K-100K concurrent connections depending on resources.
- Load balancer: must support WebSocket upgrade. Sticky sessions OR connection-aware routing.

**Deciding question:** "Does the client need to receive updates in real-time without requesting them? → WebSocket (or SSE if one-way). Occasional data fetch? → REST with polling."

---

### S3 / Object Storage

**What it is:** Infinite-capacity, highly durable blob storage. Store anything. Retrieve by key.

**RIGHT choice when:**
- Storing files, images, videos, backups, logs, data lake
- Need effectively infinite storage capacity
- Need high durability (99.999999999% — 11 nines)
- Access pattern is write-once, read-many
- Don't need to query INSIDE the objects (just store and retrieve whole objects)

**WRONG choice when:**
- Need low-latency random access (100-200ms per GET is too slow for hot-path)
- Need to query/filter/join data within objects (use a database)
- Need atomic updates to parts of an object (S3 objects are immutable — replace entirely)
- Small, structured data that fits in a database

**Common patterns:**
- Pre-signed URLs: generate a temporary URL that allows direct upload/download without proxying through your server
- Lifecycle policies: automatically transition objects to cheaper tiers (S3 Standard → Infrequent Access → Glacier) based on age
- Event notifications: trigger Lambda/SQS on object creation (useful for processing pipelines)

**Deciding question:** "Is this a blob (file, image, video, archive)? → S3. Is this structured data I need to query? → Database."

---

### ZooKeeper / etcd

**What they are:** Distributed coordination services. Store small amounts of critical metadata with strong consistency (consensus protocol).

**RIGHT choice when:**
- Leader election (only one scheduler/coordinator should be active)
- Distributed configuration (all nodes need the same config, updated atomically)
- Service discovery (which servers are alive, where are services hosted)
- Distributed locks (stronger than Redis SETNX — based on consensus)
- Cluster membership (who's in the cluster, detect node failures)

**WRONG choice when:**
- Storing large amounts of data (designed for KB-MB, not GB)
- High-throughput reads/writes (not a database — 10K ops/sec ceiling)
- Application data storage
- Simple cases where a database advisory lock suffices

**ZooKeeper vs etcd:**
- ZooKeeper: older, Java, used by Kafka/HBase/Hadoop ecosystem. Complex API (watches, ephemeral nodes).
- etcd: newer, Go, used by Kubernetes. Simpler API (gRPC, key-value with leases). Raft-based.

**Failure modes:**
- Leader election split: network partition → two leaders briefly. Fix: consensus protocol (Raft/ZAB) prevents this, but understand the transient behavior.
- Session expiry: client loses heartbeat → ephemeral nodes deleted → downstream thinks leader died. Fix: tune session timeout, handle reconnection.
- Storage too small for data volume: these are NOT databases. Don't store more than a few MB.

**Deciding question:** "Do I need distributed coordination (leader election, locks, config)? → ZooKeeper/etcd. Storing application data? → Use a database."

---

### CDN (Content Delivery Network)

**What it is:** Globally distributed cache of content, served from edge locations close to users.

**RIGHT choice when:**
- Static content served to global audience (images, JS, CSS, videos)
- Need to reduce latency for geographically distributed users
- Need to offload origin servers (absorb traffic at the edge)
- Semi-static API responses (cacheable for seconds/minutes)

**WRONG choice when:**
- Content is highly personalized per request (cache key explosion, low hit rate)
- Content changes every request (dynamic, user-specific)
- Users are all in one region (single-region deployment is simpler)
- Need strong consistency (CDN cache can serve stale content until TTL)

**Pull vs Push:**
- Pull: CDN fetches from origin on cache miss. Simpler, good for most cases. First request is slow (cold cache).
- Push: You push content to CDN proactively. Good for predictable large content (video platform preloading popular content).

**Key concern:** Cache invalidation. Options:
- TTL-based: set expiry, accept staleness for that duration
- Purge API: explicitly invalidate when content changes
- Versioned URLs: `/static/app.v42.js` → never invalidate, just deploy new version

**Deciding question:** "Is content static/semi-static AND served to users in multiple regions? → CDN. Dynamic, personalized, single-region? → Serve from origin."

---

### Flink / Stream Processing

**What it is:** Distributed stream processing framework. Process unbounded data streams in real-time.

**RIGHT choice when:**
- Need real-time aggregations (count clicks per minute, sum transactions per hour)
- Need sliding/tumbling window computations
- Processing event streams with ordering/timing guarantees
- Complex event processing (detect patterns across events)
- Need exactly-once processing semantics with checkpointing

**WRONG choice when:**
- Simple stateless transformation (Kafka consumer is enough)
- Batch processing on bounded datasets (Spark batch is simpler)
- Low volume where a single-threaded consumer handles it easily
- Team doesn't have stream processing expertise (operational complexity is high)

**Key concepts:**
- **Windowing:** tumbling (non-overlapping), sliding (overlapping), session (gap-based)
- **Watermarks:** track event time progress, determine when a window is "complete"
- **Late events:** what happens when an event arrives after its window closed? Side output or update previous result.
- **Checkpointing:** periodic snapshots of state → exactly-once recovery on failure
- **State backends:** RocksDB for large state, in-memory for small state

**Alternatives:**
- Kafka Streams: library (not cluster), simpler, good for moderate complexity. Runs in your app JVM.
- Spark Structured Streaming: micro-batch (higher latency), familiar to data engineers.
- Simple Kafka consumer: for stateless transformations or simple aggregations.

**Deciding question:** "Need windowed aggregations, event-time processing, or complex patterns in real-time? → Flink. Simple event transformation? → Kafka consumer. Batch analytics? → Spark."

---

## Part 4: Constraint → Solution Mapping (Quick Reference)

When you identify a constraint, this tells you what tool/pattern to reach for:

| Constraint | Pattern | Tool options |
|---|---|---|
| High read volume | Cache | In-memory → Redis → CDN (layered) |
| High write burst (async OK) | Queue/buffer | Kafka (replay) vs SQS (simple) |
| High write burst (sync required) | Scale write path | Shard DB, batch+flush, back-pressure (429) |
| Slow processing | Async job | Message queue + worker pool |
| Read/write contention | Separation | Read replica, CQRS, materialized views |
| Data growing unbounded | Tiering | Hot/warm/cold, TTL, archive to S3 |
| External service unreliable | Resilience | Circuit breaker + retry + timeout + fallback |
| Multiple services need same data | Shared state | Redis, event-driven invalidation, CDC |
| Need audit trail | Append-only log | Event table in DB, Kafka topic, event sourcing |
| Caller needs durability guarantee | Sync persist | Must hit DB before returning 200. Scale DB, don't buffer. |
| Caller only needs acceptance | Fast-ack + async | Accept into fast store, return 200, persist async. Reconcile. |
| Business operation spans services | Distributed transaction | Saga (simple) or TC/C (parallel) |
| Need real-time bidirectional | Persistent connection | WebSocket (bidir) or SSE (server→client only) |
| Global users, static content | Edge delivery | CDN |
| Need unique time-sortable IDs | Distributed ID gen | Snowflake (64-bit, no coordination) |
| Need full-text search | Search index | Elasticsearch (secondary, not source of truth) |
| Need coordination/leader election | Consensus service | ZooKeeper / etcd |

---

## Part 5: Tradeoff Pairs (One-Liners for Interview)

| Decision | A | B | The deciding question |
|---|---|---|---|
| Postgres vs Mongo | ACID, joins, constraints | Flexible schema, horizontal scale | Need transactions or joins? → Postgres |
| Redis vs in-memory cache | Shared across instances, survives restart | Zero latency, no serde cost | Multiple instances need same view? → Redis |
| Kafka vs SQS | Replay, ordering, multi-consumer | Managed, simple, cheap | Need replay or multiple consumers? → Kafka |
| REST vs gRPC | Human-readable, browser-compatible | Binary, fast, typed, streaming | External API? → REST. Internal? → gRPC |
| Sync vs async | Simple, immediate consistency | Decoupled, handles burst | User waiting? → Sync. Background? → Async |
| Push vs pull | Fast reads (pre-built) | No wasted writes | Most users low-follower? → Push. Celebrity problem? → Hybrid |
| Strong vs eventual consistency | Correct, higher latency | Fast, stale possible | Money/inventory? → Strong. Feeds/display? → Eventual |
| Monolith vs microservice | Simple ops, fast iteration | Independent scale, team ownership | Early stage? → Monolith. Clear domain boundaries? → Extract |
| SQL vs NoSQL | Rich queries, ACID | Horizontal scale, flexible schema | Need joins/transactions? → SQL |
| Optimistic vs pessimistic locking | No lock held, conflict on write | Lock held, block others | Low conflict rate? → Optimistic. High contention? → Pessimistic |
