# System Design Reference — NFR Solutions & Estimation Numbers

> Pure reference. Moved out of [playbook.md](playbook.md) because none of this changes a design decision on its own — it's the setup detail and the arithmetic behind the decisions. Use it as talking-point backup ("for 99.99% we'd need multi-AZ active-active…") and for building intuition. In the interview, use the **Scale → Component lookup** in the playbook instead.

## Contents

1. [NFR Solutions — How to Satisfy Each Constraint](#nfr-solutions--how-to-satisfy-each-constraint)
2. [Back-of-Envelope Estimation (full worksheet)](#back-of-envelope-estimation-full-worksheet)
3. [Numbers Every Engineer Should Know](#numbers-every-engineer-should-know)

---

## NFR Solutions — How to Satisfy Each Constraint

**Scale / Traffic (high QPS)**

| QPS Range | Read Strategy | Write Strategy |
|---|---|---|
| < 10K | Single DB, maybe Redis cache | Single Postgres |
| 10K-50K | Redis cache + read replicas | Single Postgres with connection pooling |
| 50K-500K | Redis cluster + multiple replicas | Sharded Postgres (by user/tenant) |
| 500K+ | In-memory cache (per-instance) + Redis L2 | Sharded + CQRS (separate write from read path) |

Key levers:
- **Read-heavy:** add cache layers (in-memory L1 → Redis L2 → DB). Most systems are 10:1 read:write.
- **Write-heavy:** shard the DB, batch writes, use async queues for non-critical writes, CQRS.
- **Both:** separate read and write paths entirely. Write to primary, async replicate to read replicas/cache.
- **Connection pooling:** always use (HikariCP for Java). A Postgres node can handle more QPS than most people think if you're not exhausting connections.

---

**Latency (reducing P50 / P99)**

| Technique | P50 Impact | P99 Impact | Tradeoff |
|---|---|---|---|
| In-memory cache (Caffeine) | Huge (sub-ms) | Huge | Memory cost, staleness |
| Redis cache | Good (~1ms) | Good | Network hop, serialization cost |
| Async fan-out (parallel calls) | Big (total = max, not sum) | Big | Complexity, partial failure handling |
| CDN for static content | Big for global users | Big | Cache invalidation complexity |
| Connection pooling | Moderate | Big (eliminates connection setup spikes) | Pool sizing tuning |
| DB index optimization | Moderate | Big (prevents full scans on edge cases) | Write overhead per index |
| JVM warmup / pre-compilation | None for steady state | Big (eliminates cold-start spikes) | Startup time |
| Pre-computation / materialized views | Big | Big | Staleness, storage cost |

P99 specifically (tail latency):
- **GC pauses:** tune JVM heap, use G1/ZGC for low-pause collection
- **Cold starts:** JVM warmup routine before accepting traffic (your DGS story)
- **Outlier dependencies:** circuit breaker + timeout so one slow call doesn't block entire request
- **Retry amplification:** capped retries with backoff, otherwise slow calls cascade
- **Per-service timeout budgets:** "inventory gets 30ms max, pricing gets 20ms max, total budget is 50ms"

---

**Availability (pushing toward 99.9% → 99.99%)**

| SLA | Allowed Downtime/Year | What You Need |
|---|---|---|
| 99% | 3.65 days | Basic monitoring, manual failover |
| 99.9% | 8.76 hours | Multi-AZ, health checks, auto-restart |
| 99.99% | 52.6 minutes | Multi-AZ active-active, zero-downtime deploys, automatic failover, no SPOF |
| 99.999% | 5.26 minutes | Multi-region active-active, consensus protocols, extensive automation |

Key levers by tier:

**99% → 99.9%:**
- Deploy in multiple AZs (RDS Multi-AZ, EKS across AZs)
- Readiness/liveness probes → auto-restart failed pods
- Load balancer health checks → remove unhealthy instances
- Basic alerting (PagerDuty on 5xx spike)

**99.9% → 99.99%:**
- Eliminate ALL single points of failure (every component has a replica/fallback)
- Zero-downtime deploys (rolling updates, blue-green)
- Circuit breakers → graceful degradation (serve partial response vs. 500)
- Redundant dependencies (if Redis dies, fall back to DB with degraded latency)
- Auto-scaling (handle traffic spikes without manual intervention)
- Chaos engineering (test failure modes before they happen in prod)

**99.99% → 99.999%:**
- Multi-region active-active (survive entire region failure)
- Conflict resolution for multi-region writes (CRDTs, last-write-wins, or single-leader per entity)
- Sub-minute failover detection + automatic rerouting (DNS failover or global load balancer)
- No maintenance windows — everything upgradable in-place

---

**Consistency (strong vs eventual — what each requires)**

| Consistency Level | Implementation | Use When | Cost |
|---|---|---|---|
| **Strong (linearizable)** | Single leader, sync replication, or consensus (Raft) | Money, inventory counts, auth | Higher latency, lower throughput |
| **Read-your-writes** | Route user reads to same replica they wrote to (session affinity) | User-facing UX (see your own post) | Sticky routing complexity |
| **Eventual** | Async replication, event-driven updates | Display data, feeds, analytics | Stale reads (seconds to minutes) |
| **Causal** | Version vectors, logical clocks | Chat ordering, collaborative editing | Moderate complexity |

How to implement strong consistency:
- Single-leader Postgres (all writes to primary, reads from primary for critical paths)
- Distributed transactions (2PC) — expensive, avoid if possible
- Saga with compensating actions — eventual but semantically correct
- Idempotency keys — safe retries without duplicating effects

How to implement eventual consistency safely:
- Accept that reads can be stale — design UI to tolerate it ("updating..." indicators)
- Use event-driven: write to primary → publish event → consumers update their read models
- Reconciliation jobs to catch drift between primary and derived stores
- Versioned data (optimistic concurrency) — detect conflicts on write, resolve or reject

---

**Durability (can we lose data?)**

| Durability Level | Implementation | RPO (Recovery Point Objective) |
|---|---|---|
| **Zero data loss** | WAL + sync replication to standby | RPO = 0 (no data loss even on crash) |
| **Minimal loss** | Async replication + frequent WAL archiving | RPO = seconds (lose last few uncommitted) |
| **Best effort** | Single node, periodic backups | RPO = hours (lose data since last backup) |

Key levers:
- **WAL (Write-Ahead Log):** every write is logged before acknowledged. On crash, replay WAL to recover.
- **Synchronous replication:** standby confirms write before primary acknowledges to client. Zero data loss, higher latency.
- **Point-in-Time Recovery (PITR):** WAL archiving lets you restore to any second within retention window.
- **Backups:** automated daily snapshots + continuous WAL archiving. Test restores regularly.
- **Multi-AZ:** data exists in 2+ availability zones. Survives AZ failure without data loss (RDS Multi-AZ does this automatically with sync replication).

For financial systems (Coinbase):
- Sync replication (non-negotiable for transactions)
- Append-only ledger (never delete/mutate financial records)
- Event sourcing (full audit trail, replayable)
- Reconciliation (verify internal state matches external sources)
- NO Redis-only storage for anything financial (Redis persistence is best-effort)

---

**Volume (large data — how to handle 10TB, 100TB, PB)**

| Data Size | Strategy |
|---|---|
| < 500 GB | Single Postgres, no special handling |
| 500 GB - 5 TB | Postgres with partitioning (by time or key), archive old data |
| 5 TB - 50 TB | Sharded Postgres or move to DynamoDB/Cassandra |
| 50 TB+ | Data lake (S3 + Parquet), query with Athena/Spark. Hot data in DB, cold in S3. |

Key levers:
- **Table partitioning:** split large tables by time (monthly partitions). Drop old partitions cheaply. Queries on recent data only scan relevant partitions.
- **Hot/warm/cold tiering:** recent data in fast store (memory/SSD), older in cheaper store (S3/Glacier). Lifecycle policies automate transitions.
- **Compression:** columnar formats (Parquet, ORC) compress 5-10x vs raw. Use for analytics/archive.
- **TTL / data retention:** delete or archive data older than X days. Don't keep everything forever unless compliance requires it.
- **Separate OLTP from OLAP:** transactional DB for real-time operations, data warehouse (Snowflake, BigQuery, Redshift) for analytics on historical data.

---

## Back-of-Envelope Estimation (full worksheet)

Always do this. Show you can reason about scale. The goal isn't precision — it's to demonstrate you can identify bottlenecks, pick the right storage/compute, and justify design decisions with numbers.

### The One Magic Number: 86,400

**1 day = 86,400 seconds ≈ 100K seconds.** This is the only number you need to memorize for QPS conversion.

```
Daily events → QPS:  divide by 100K (86,400 rounded up)
QPS → Daily events:  multiply by 100K

Example: 1M requests/day ÷ 100K = 10 QPS
Example: 500 QPS × 100K = 50M requests/day
```

For **peak QPS**: multiply average by 2–5× (2× for steady traffic, 5× for bursty/event-driven).

### Powers of 2 You Must Know

| Power | Exact | Approx | Name |
|---|---|---|---|
| 2^10 | 1,024 | ~1 Thousand | 1 KB |
| 2^20 | 1,048,576 | ~1 Million | 1 MB |
| 2^30 | 1,073,741,824 | ~1 Billion | 1 GB |
| 2^40 | | ~1 Trillion | 1 TB |

**Shortcut**: Every 10 powers of 2 ≈ 3 powers of 10. So 2^30 ≈ 10^9 (1 billion).

### Common Data Sizes to Memorize

| Data | Size |
|---|---|
| **1 ASCII character** | 1 byte |
| **UUID / ULID** | 36 bytes (string) or 16 bytes (binary) |
| **A tweet / short text message** | ~200-500 bytes (text + metadata) |
| **A database row** (typical) | ~500 bytes – 2 KB |
| **A JSON API response** | 1–10 KB |
| **A profile photo / thumbnail** | 50–200 KB |
| **A high-res image** | 2–5 MB |
| **A 1-minute video (compressed)** | 5–10 MB (720p), 20–50 MB (1080p) |
| **1 hour of video** (1080p) | ~1.5–3 GB |

### Latency Numbers to Know

| Operation | Latency |
|---|---|
| L1 cache reference | ~1 ns |
| L2 cache reference | ~4 ns |
| RAM access | ~100 ns |
| SSD random read | ~100 μs |
| HDD seek | ~10 ms |
| Network round trip (same datacenter) | ~500 μs |
| Network round trip (cross-continent) | ~150 ms |
| Read 1 MB sequentially from SSD | ~1 ms |
| Read 1 MB sequentially from network | ~10 ms |
| Redis GET (network + lookup) | ~0.5–1 ms |
| Simple DB query (indexed) | ~1–5 ms |
| Complex DB query (join/scan) | ~10–100 ms |

**Key takeaway**: Memory is 1000× faster than SSD. SSD is 100× faster than HDD. Network within a datacenter is ~500μs. Cross-region is ~150ms. This is why caching matters.

### Throughput Numbers to Know

| System | Throughput |
|---|---|
| **MySQL / Postgres** (single node) | ~1K–5K QPS (writes), ~10K–50K QPS (reads, indexed) |
| **Redis** (single node) | ~100K–500K QPS |
| **Kafka** (single broker) | ~100K–500K messages/sec |
| **Nginx / API Gateway** | ~50K–100K req/sec (per instance) |
| **Single web server** (Node/Go/Java) | ~5K–50K req/sec (depends on work per request) |

### The 4-Step Estimation Framework

Use this every time. Say it out loud in the interview:

**Step 1: Start with users**
```
"Let's say we have 100M DAU..."
```

**Step 2: Estimate actions per user**
```
"Each user does ~10 reads/day and ~1 write/day..."
→ Reads: 100M × 10 = 1B reads/day → 1B ÷ 100K = 10K QPS reads
→ Writes: 100M × 1 = 100M writes/day → 100M ÷ 100K = 1K QPS writes
→ Read:Write ratio = 10:1 (read-heavy → cache aggressively)
```

**Step 3: Estimate storage**
```
"Each record is ~1KB..."
→ New data per day: 100M writes × 1KB = 100GB/day
→ Per year: 100GB × 365 = ~36TB/year
→ With replication (3×): ~110TB/year
```

**Step 4: Identify the bottleneck & state the implication**
```
"10K QPS reads is well within a single Redis instance (100K+ QPS).
 1K QPS writes is fine for a single Postgres with connection pooling.
 The bottleneck is storage growth at 36TB/year — we'll need sharding within 2 years."
```

> **This is the staff+ move**: Don't just compute numbers. State what the numbers *mean* for your design. "This is read-heavy, so I'll add a cache layer." "This write volume exceeds single-node Postgres, so I'll shard."

### Worked Examples

**Example 1: URL Shortener**
```
Given: 100M new URLs/day, 10:1 read:write ratio

Writes: 100M/day ÷ 100K = 1K QPS (low, single DB is fine)
Reads:  1B/day ÷ 100K = 10K QPS (moderate, cache hot URLs in Redis)
Peak:   10K × 3 = 30K QPS reads (Redis handles this easily)

Storage per URL: short_url (7B) + long_url (200B) + metadata (100B) ≈ 300B
Daily: 100M × 300B = 30GB/day
Yearly: ~11TB/year
5 years: ~55TB → will need sharding or archival

Implication: Read-heavy → Redis cache for hot URLs. Storage is manageable for years.
             Single DB for writes. The design challenge is hash collisions, not scale.
```

**Example 2: Chat System (WhatsApp)**
```
Given: 50M DAU, 40 messages/user/day

Messages: 50M × 40 = 2B messages/day ÷ 100K = 20K QPS (moderate)
Peak:     20K × 5 = 100K QPS (need distributed message queue)

Storage per message: text (200B) + metadata (100B) = 300B
Daily: 2B × 300B = 600GB/day
Yearly: ~220TB/year → Cassandra/HBase (wide-column, good for time-series chat data)

Concurrent WebSocket connections: 50M DAU, ~30% online at any time = 15M connections
Each WS connection: ~10KB memory → 15M × 10KB = 150GB RAM for connections alone
→ Need ~150 WebSocket servers (1GB RAM each for connections, leaving room for app logic)

Implication: The bottleneck is concurrent connections, not message QPS.
             Need stateful WebSocket servers + service discovery (user → server mapping).
```

**Example 3: Video Platform (YouTube)**
```
Given: 5M DAU, 10% upload daily, avg video 300MB

Uploads: 5M × 10% = 500K videos/day
Storage: 500K × 300MB = 150TB/day raw
With 3 resolutions (360p, 720p, 1080p): 150TB × 3 = 450TB/day transcoded
Yearly: 450TB × 365 = ~164PB/year (massive — object storage like S3)

Streaming: 5M users × 5 videos/day × 300MB avg = 7.5PB/day bandwidth
CDN cost: 7.5PB × $0.02/GB = $150K/day = $55M/year

Implication: Storage and CDN cost are the dominant concerns, not QPS.
             CDN optimization (cache popular videos at edge) is critical.
             Transcode only popular resolutions eagerly; rare ones on-demand.
```

**Example 4: Ride-Sharing (Uber)**
```
Given: 5M active drivers, GPS update every 4 seconds

Location writes: 5M ÷ 4 = 1.25M writes/sec (very high write throughput!)
→ Single DB can't handle this → need Redis/in-memory geospatial index
→ Partition by city (100 cities → ~12.5K writes/sec per city partition — manageable)

Ride requests: 20M rides/day ÷ 100K = 200 QPS (low — not the bottleneck)

Storage per location update: (driver_id, lat, lng, timestamp) ≈ 50B
Daily: 1.25M/sec × 86,400 × 50B = ~5.4TB/day (only need latest, not historical)
→ Use Redis with TTL (overwrite previous location). No need to persist all updates.

Implication: The bottleneck is location write throughput (1.25M/sec).
             Use in-memory store (Redis geospatial) partitioned by city.
             Ride matching QPS is low — the hard part is the geospatial query, not scale.
```

### Quick Conversion Cheat Sheet

| From | To | Formula |
|---|---|---|
| X per day → QPS | | X ÷ 100K |
| QPS → per day | | QPS × 100K |
| MB/sec → TB/day | | MB/sec × 86.4 ÷ 1000 |
| N users × B bytes | | N × B (use powers of 10, simplify) |
| Replication factor | | Multiply storage by 3 (standard) |
| 5-year retention | | Multiply yearly by 5, ask about archival |
| Single DB limit | | ~5K writes/sec, ~50K reads/sec |
| Single Redis limit | | ~100K–500K ops/sec |
| Single Kafka broker | | ~100K msgs/sec |

### Common Mistakes to Avoid

1. **Don't over-precision**: Say "~10K QPS" not "9,723 QPS". Round aggressively.
2. **Don't forget peak**: Average QPS ≠ peak. Always multiply by 2-5× for peak load.
3. **Don't forget replication**: Storage × 3 for replicas (standard).
4. **Don't forget growth**: "At current growth, we'll hit X in Y months — that's when we need to shard."
5. **Don't compute without concluding**: Every number should lead to a design decision. If it doesn't, you wasted time.

### Practice Drill

Pick any problem from the Common System Design Problems section and do this in 2 minutes:
1. Estimate QPS (reads + writes separately)
2. Estimate storage (daily, yearly, 5-year)
3. Estimate bandwidth (if media involved)
4. State the bottleneck and what it means for your design

Do this for 5 different problems and the pattern becomes automatic.

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
