# System Design Component Decision Tree

> Quick reference for choosing the right technology in system design interviews.
> Start with requirements, follow the tree to a recommendation.

---

## 1. Database Selection

```
START: What kind of data?

├─ RELATIONAL (with complex queries, JOINs, transactions)
│  ├─ Strong consistency required? (financial, inventory)
│  │  └─> PostgreSQL / MySQL
│  │      Why: ACID transactions, foreign keys, referential integrity
│  │      Scale: Vertical (powerful single node) + read replicas
│  │      Limit: Write bottleneck on primary (5K-10K TPS single node)
│  │
│  └─ Eventually consistent OK? (social, analytics)
│     └─> PostgreSQL with read replicas OR CockroachDB / Yugabyte
│         Why: Distribute reads, partition for writes
│         Scale: Horizontal (with sharding or distributed SQL)

├─ KEY-VALUE (simple lookups by primary key)
│  ├─ Low latency required? (< 10ms)
│  │  ├─ Small dataset (< 100 GB)?
│  │  │  └─> Redis (in-memory)
│  │  │      Why: Sub-millisecond reads, 100K+ QPS per node
│  │  │      Use: Cache, session store, rate limiter
│  │  │      Limit: Dataset must fit in RAM
│  │  │
│  │  └─ Large dataset (> 100 GB)?
│  │     └─> DynamoDB / Cassandra
│  │         Why: Consistent single-digit ms latency at any scale
│  │         DynamoDB: Managed, simpler (AWS)
│  │         Cassandra: Self-hosted, more control
│  │         Scale: Horizontal (partition by key)
│  │
│  └─ Latency not critical? (10-100ms OK)
│     └─> DynamoDB / PostgreSQL (depending on other needs)
│         Why: PostgreSQL if you also need relational queries

├─ DOCUMENT (nested JSON, flexible schema)
│  ├─ Need complex queries across documents?
│  │  └─> MongoDB
│  │      Why: Rich query language, indexes on nested fields
│  │      Use: Product catalogs, user profiles, CMS
│  │      Scale: Sharding (but complex)
│  │
│  └─ Simple document retrieval by ID?
│     └─> DynamoDB (with document attributes)
│         Why: Simpler, managed, scales easily

├─ TIME-SERIES (metrics, logs, sensor data)
│  ├─ High write throughput? (100K+ writes/sec)
│  │  └─> Cassandra / InfluxDB / TimescaleDB
│  │      Cassandra: Generic wide-column, DIY time-series
│  │      InfluxDB: Purpose-built for time-series
│  │      TimescaleDB: PostgreSQL extension (SQL familiarity)
│  │      Why: Write-optimized, time-based partitioning
│  │
│  └─ Medium throughput but need analytics?
│     └─> TimescaleDB / ClickHouse
│         TimescaleDB: PostgreSQL-compatible, easier migration
│         ClickHouse: Columnar, faster analytics

├─ WIDE-COLUMN (sparse data, many columns per row)
│  └─> Cassandra / HBase
│      Cassandra: Easier ops, better for general use
│      HBase: Hadoop ecosystem, batch processing
│      Use: IoT data, event logging, activity feeds
│      Scale: Horizontal (partition by row key)

├─ GRAPH (relationships are first-class, many hops)
│  └─> Neo4j / Amazon Neptune
│      Why: Traversals are O(edges) not O(N²)
│      Use: Social networks, recommendation engines, fraud detection
│      Limit: Doesn't scale as well as other NoSQL (graph partitioning is hard)

└─ SEARCH / FULL-TEXT
   └─> Elasticsearch / OpenSearch
       Why: Inverted indexes, fuzzy matching, relevance scoring
       Use: Search bars, log analysis, APM (Application Performance Monitoring)
       NOT a primary database (use alongside PostgreSQL/etc)
```

---

## 2. Caching Layer

```
START: What are you caching?

├─ SIMPLE KEY-VALUE (session, user profile, API response)
│  ├─ Dataset < 100 GB, need sub-ms latency?
│  │  └─> Redis
│  │      Why: In-memory, 100K+ QPS, data structures (sets, sorted sets)
│  │      Eviction: LRU, TTL
│  │      Persistence: Optional (RDB snapshots, AOF)
│  │
│  └─ Just need basic cache, no data structures?
│     └─> Memcached
│         Why: Simpler than Redis, multi-threaded (higher throughput on multi-core)
│         Use: Pure cache (no persistence)

├─ QUERY RESULT CACHE (expensive DB queries)
│  └─> Redis + cache-aside pattern
│      Flow: Check Redis → miss → query DB → write Redis
│      TTL: Set based on data freshness requirements
│      Invalidation: TTL-based OR event-driven (delete on update)

├─ COMPUTED RESULTS (ML inference, expensive computation)
│  └─> Redis + TTL
│      Why: Avoid recomputing the same input
│      Alternative: CDN for static content

└─ DISTRIBUTED CACHE (multiple app servers)
   └─> Redis Cluster / Memcached
       Redis Cluster: Sharded across nodes (hash slot partitioning)
       Memcached: Consistent hashing (client-side)
```

---

## 3. Message Queue / Event Streaming

```
START: What's the use case?

├─ HIGH-THROUGHPUT EVENT STREAMING (millions of events/sec)
│  ├─ Need replay / reprocessing?
│  │  └─> Kafka
│  │      Why: Log-based, consumers can rewind, high throughput (millions/sec)
│  │      Use: Event sourcing, analytics pipelines, CDC (change data capture)
│  │      Scale: Partition-based (add partitions = more throughput)
│  │      Trade-off: No message-level routing (filter in consumer)
│  │
│  └─ No replay needed, just streaming?
│     └─> Kafka OR Kinesis (AWS)
│         Kinesis: Managed, simpler ops (AWS)
│         Kafka: More control, ecosystem (Kafka Streams, Connectors)

├─ TASK QUEUE (background jobs, async work)
│  ├─ Simple tasks, prefer managed?
│  │  └─> SQS (AWS) / Cloud Tasks (GCP)
│  │      Why: Fully managed, serverless-friendly
│  │      Use: Email sending, image processing, data exports
│  │      Features: Visibility timeout, dead-letter queue, retries
│  │
│  └─ Complex routing / work distribution?
│     └─> RabbitMQ
│         Why: Rich routing (topic exchange, headers), work queues, DLQ
│         Use: Task distribution, priority queues, RPC
│         Scale: Moderate (thousands to tens of thousands msg/sec)
│         Trade-off: You manage the broker

├─ PUB-SUB FAN-OUT (one message → many consumers)
│  ├─ Simple attribute-based filtering?
│  │  └─> SNS → SQS (AWS)
│  │      Why: SNS does broker-level filtering, SQS queues per consumer
│  │      Use: Notifications (email + SMS + push), event routing to services
│  │      Scale: Managed, auto-scales
│  │
│  └─ Complex pattern matching?
│     └─> RabbitMQ (topic exchange)
│         Why: Wildcard routing (*.error, us-east-1.#)

└─ REAL-TIME MESSAGING (chat, notifications, live updates)
   └─> WebSockets + Redis Pub/Sub
       Redis Pub/Sub: Ephemeral, no persistence (fire-and-forget)
       Use: Live dashboards, chat rooms, collaborative editing
       NOT for task queues (no durability)
```

---

## 4. Storage (Blob / Object / File)

```
START: What are you storing?

├─ LARGE FILES (images, videos, backups)
│  └─> Object Storage: S3 (AWS) / GCS (Google) / Azure Blob
│      Why: Durable (11 9's), cheap, scales to petabytes
│      Use: User uploads, media, backups, data lakes
│      NOT for: Frequent small writes (high latency per write), databases

├─ STATIC ASSETS (HTML, CSS, JS, images for web)
│  └─> CDN in front of S3
│      CDN: CloudFront, Cloudflare, Fastly
│      Why: Edge caching, low latency globally
│      Flow: Browser → CDN (cache hit) → S3 (cache miss)

├─ SHARED FILE SYSTEM (multiple servers need same files)
│  ├─ POSIX filesystem required?
│  │  └─> EFS (AWS) / Cloud Filestore (GCP) / NFS
│  │      Why: Mount as filesystem, POSIX semantics
│  │      Use: Shared config, logs, legacy apps
│  │
│  └─ Object storage OK?
│     └─> S3 (cheaper, more scalable)

└─ TEMPORARY STORAGE (processing pipeline, ephemeral data)
   └─> Local disk OR S3 (depending on durability needs)
       Local disk: Fast, but lost if instance dies
       S3: Durable, but slower
```

---

## 5. Load Balancer

```
START: What layer?

├─ LAYER 4 (TCP/UDP, low latency)
│  └─> AWS NLB / HAProxy / NGINX (stream mode)
│      Why: No TLS termination, just forwards packets (lower latency)
│      Use: Database connections, non-HTTP protocols

├─ LAYER 7 (HTTP/HTTPS, application-aware routing)
│  ├─ Need path-based routing? (/api → service A, /static → CDN)
│  │  └─> AWS ALB / NGINX / Envoy
│  │      Why: Parse HTTP headers, route by path/domain/headers
│  │      Use: Microservices, API gateway, canary deployments
│  │
│  └─ Just need basic round-robin?
│     └─> NGINX / HAProxy
│         Why: Simple, battle-tested

└─ GLOBAL LOAD BALANCING (route across regions)
   └─> AWS Route 53 / Cloudflare / Google Cloud Load Balancer
       Why: DNS-based OR anycast IP routing
       Use: Multi-region apps, disaster recovery
```

---

## 6. Service Discovery

```
START: Static or dynamic infrastructure?

├─ STATIC (fixed IPs, rarely change)
│  └─> DNS (Route 53, etc.)
│      Why: Simple, no extra dependencies

├─ DYNAMIC (containers, auto-scaling)
│  ├─ Using Kubernetes?
│  │  └─> Kubernetes Service / CoreDNS
│  │      Why: Built-in, automatic
│  │
│  └─ Not Kubernetes?
│     └─> Consul / etcd / ZooKeeper
│         Consul: Easier, more features (health checks, KV store)
│         etcd: Simpler, Raft-based
│         ZooKeeper: Older, more complex (but battle-tested with Kafka)
```

---

## 7. Coordination / Configuration

```
START: What do you need?

├─ DISTRIBUTED LOCK / LEADER ELECTION
│  └─> ZooKeeper / etcd / Consul
│      Why: Strong consistency (CP in CAP), atomic operations
│      Use: Leader election, distributed mutex, cluster coordination

├─ CONFIGURATION MANAGEMENT
│  ├─ Dynamic config (update without restart)?
│  │  └─> etcd / Consul / AWS Parameter Store
│  │      Why: Watch for changes, push updates to services
│  │
│  └─ Static config?
│     └─> Environment variables / config files in S3

└─ SECRETS MANAGEMENT
   └─> HashiCorp Vault / AWS Secrets Manager / Google Secret Manager
       Why: Encryption at rest, access control, audit logs
```

---

## 8. Rate Limiting

```
START: Single node or distributed?

├─ SINGLE NODE (one API server)
│  └─> In-memory counter (token bucket / sliding window)
│      Implementation: Library (e.g., Guava RateLimiter in Java)

├─ DISTRIBUTED (multiple API servers)
│  └─> Redis (atomic INCR + TTL)
│      Algorithm: Sliding window counter
│      Why: Redis INCR is atomic, fast (sub-ms)
│      Scale: Redis Cluster for high QPS

└─ GLOBAL RATE LIMIT (across regions)
   └─> Redis + eventual consistency trade-off
       OR: Accept slight over-limit (99% accurate is usually fine)
```

---

## Quick Decision Framework

**For every component choice, ask:**

1. **What's the access pattern?**
   - Read-heavy → cache, read replicas
   - Write-heavy → partition, queue
   - Both → partition + cache

2. **What's the consistency requirement?**
   - Strong → PostgreSQL, Kafka (ordered), Redis (single node)
   - Eventual → Cassandra, DynamoDB, multi-region async replication

3. **What's the scale?**
   - < 10K QPS → Simple setup (single DB, monolith)
   - 10K-100K QPS → Caching + read replicas
   - > 100K QPS → Partitioning + distributed systems

4. **What's the latency requirement?**
   - < 1ms → In-memory (Redis)
   - < 10ms → SSD-backed (DynamoDB, Cassandra)
   - < 100ms → Network-bound (PostgreSQL with optimization)

5. **Do you want to manage infrastructure?**
   - No → Managed (AWS RDS, DynamoDB, SQS)
   - Yes → Self-hosted (PostgreSQL, Kafka, Redis)

---

## Interview Anti-Patterns (Avoid These)

❌ **"Use MongoDB because it's NoSQL and scalable"**
   → No. What's the access pattern? Why not PostgreSQL?

❌ **"Use microservices for everything"**
   → No. Start with a monolith. Scale when needed.

❌ **"Use Kafka for everything"**
   → No. Kafka is for event streaming. Use SQS for simple task queues.

❌ **"Use Cassandra for relational data"**
   → No. Cassandra is for wide-column time-series / event data.

❌ **"Use Redis as primary database"**
   → No. Redis is a cache or fast store. Not ACID, limited durability.

✅ **Instead:** Match the tool to the access pattern and requirements.

---

## Example Walkthrough: Design a Twitter-Like System

**Requirements:**
- Post tweets (text + media)
- Follow users
- Timeline: see tweets from people you follow
- Search tweets

**Database decisions:**

1. **User profiles, follow relationships**
   → PostgreSQL (relational: user ↔ followers is a graph)
   
2. **Tweets (text + metadata)**
   → PostgreSQL (structured, need JOINs for author info)
   
3. **Media (images, videos)**
   → S3 + CDN (large files, static assets)
   
4. **Timeline (feed of tweets)**
   → Redis (cache precomputed timelines for active users)
   → Fallback: PostgreSQL query (for inactive users)
   
5. **Search tweets**
   → Elasticsearch (full-text search, fuzzy matching)
   
6. **Tweet creation event stream**
   → Kafka (fan-out to timeline service, search indexer, analytics)

**Why this combination:**
- PostgreSQL: Strong consistency for user data, relational queries
- Redis: Low-latency timeline reads for active users
- S3 + CDN: Cost-effective media storage, globally distributed
- Elasticsearch: Full-text search (PostgreSQL can't do fuzzy matching well)
- Kafka: High-throughput event streaming, decouples services

---

**Use this tree in interviews:** State the requirement → walk through the decision → justify your choice.
