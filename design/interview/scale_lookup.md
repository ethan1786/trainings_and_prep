# Scale → Component Lookup

> Recognize the pattern, recognize the scale band, name the components. You don't need a worksheet.
> In the interview: "Quick estimate in my head: [one-line derivation], so we're in the [band] range. That means [components]. In practice we'd validate with real traffic, but for this interview I'll start there."
>
> Companion docs: [playbook.md](playbook.md) (framework), [component_decision_tree.md](component_decision_tree.md) (which technology for which requirement), [reference.md](reference.md) (full estimation worksheet, NFR solution tiers, raw numbers).

## Contents

- [How to Use This](#how-to-use-this)
- [Single-Node Limits](#single-node-limits)
- [Generic Axes](#generic-axes) — read QPS, write QPS, data size, connections, fanout
- **Patterns**
  1. [Read-Heavy Lookup](#1-read-heavy-lookup) — URL shortener, catalog, profiles
  2. [Config / Feature Flags](#2-config--feature-flags) — read-massive, write-rare
  3. [Write-Heavy Ingestion](#3-write-heavy-ingestion) — clickstream, IoT, event logging
  4. [Feed / Timeline Fanout](#4-feed--timeline-fanout) — news feed, Twitter
  5. [Chat / Messaging](#5-chat--messaging) — WhatsApp, Slack
  6. [Live Broadcast to Clients](#6-live-broadcast-to-clients) — tickers, live scores, live comments
  7. [Presence / Ephemeral State](#7-presence--ephemeral-state) — online status, typing indicators
  8. [Counters & Aggregations](#8-counters--aggregations) — likes, view counts, ad clicks
  9. [Leaderboard / Top-K](#9-leaderboard--top-k) — gaming, trending
  10. [Rate Limiting](#10-rate-limiting)
  11. [Search & Typeahead](#11-search--typeahead)
  12. [Geospatial / Proximity](#12-geospatial--proximity) — Uber, Yelp
  13. [Contention / Booking / Flash Sale](#13-contention--booking--flash-sale) — tickets, inventory
  14. [Payments / Ledger](#14-payments--ledger) — correctness-bound
  15. [Job Queue / Scheduler](#15-job-queue--scheduler)
  16. [Notifications](#16-notifications) — push, SMS, email
  17. [Media Upload & Delivery](#17-media-upload--delivery) — YouTube, Instagram
  18. [File Sync](#18-file-sync) — Dropbox
  19. [Metrics / Logs / Observability](#19-metrics--logs--observability)
  20. [Analytics / OLAP](#20-analytics--olap)
  21. [Distributed Cache / KV Store](#21-distributed-cache--kv-store)
  22. [Unique ID Generation](#22-unique-id-generation)
  23. [Collaborative Editing](#23-collaborative-editing) — Google Docs
  24. [Web Crawler](#24-web-crawler)
- [Tier-Jump Signals](#tier-jump-signals)

---

## How to Use This

1. **Name the pattern(s).** Most problems are 1 main pattern + 1–2 secondary ones. For example, Twitter = Feed Fanout + Search + Counters, and Uber = Geospatial + Contention + Payments.
2. **Find the driving number.** Each pattern lists the one number that decides the tier. Ignore everything else.
3. **Convert once:** per day ÷ 100K ≈ per second. Peak ≈ 2–5× average.
4. **Read off the tier.** State the components and *what changed from the tier below*. That delta is the staff-level signal ("we're past one Postgres, so…").
5. **Start one tier low and say when you'd jump.** "This works to ~X. Past that I'd move to Y."

---

## Single-Node Limits

These are the numbers that actually get used to say "X won't fit on one node." Ballpark, modern hardware.

| Component | Rough ceiling per node | Notes |
|---|---|---|
| Postgres / MySQL | ~5K writes/s, ~10K–50K indexed reads/s | Comfortable to ~1–5 TB; connections cap first (pool it) |
| Redis | ~100K–500K ops/s | Single-threaded per shard; memory-bound (~25–100 GB practical) |
| Memcached | ~200K–1M ops/s | Multi-threaded, no persistence |
| Kafka broker | ~100K–500K msgs/s | Per **partition** think ~10 MB/s consumer throughput |
| Cassandra / ScyllaDB | ~10K–50K writes/s (Scylla higher) | Linear scale-out; reads costlier than writes |
| DynamoDB partition | 1K WCU / 3K RCU | Hot key = hot partition; adaptive capacity helps a bit |
| Elasticsearch node | ~5K–20K docs/s indexing, hundreds–low-K queries/s | Depends heavily on query shape |
| S3 prefix | 3.5K writes/s, 5.5K reads/s | Scales by adding prefixes; effectively unlimited total |
| App server (Java/Go) | ~5K–50K req/s | Depends on work per request |
| WebSocket gateway | ~100K–1M connections | Memory-bound (~10–50 KB per conn) |
| Nginx / L7 LB | ~50K–100K req/s | Managed LBs scale transparently |
| Flink / stream task slot | ~10K–100K events/s | Depends on state size and window ops |
| Network NIC | 10–25 Gbps | ~1–3 GB/s; matters for media and replication |

---

## Generic Axes

Use these when the problem doesn't fit a named pattern.

### Read QPS

| Range | Components |
|---|---|
| < 10K | Single Postgres, optional Redis |
| 10K–50K | Redis cache-aside + read replicas |
| 50K–500K | Redis cluster, multiple replicas, CDN for anything cacheable |
| 500K+ | In-process L1 (Caffeine) + Redis L2, CQRS read models, CDN/edge |

### Write QPS (sustained)

| Range | Components |
|---|---|
| < 5K | Single Postgres, connection pooling |
| 5K–50K | Shard by entity (user/tenant) or Cassandra/DynamoDB |
| 50K–1M | Kafka in front, write-optimized store, batch/micro-batch writes |
| 1M+ latest-value only | In-memory (Redis), overwrite in place, partition by key/geo |

Queues absorb **bursts**. If writes exceed capacity **sustained**, shard. A queue only delays the problem.

### Data Size

| Range | Where it lives |
|---|---|
| < 100 GB | Fits in memory. Cache the whole working set |
| < 1 TB | Single Postgres |
| 1–10 TB | Postgres with time/key partitioning, archive cold data |
| 10–50 TB | Sharded Postgres / DynamoDB / Cassandra |
| 50 TB+ or media | S3 (+ Parquet for analytics), hot slice in DB |

### Concurrent Connections

| Range | Components |
|---|---|
| < 100K | A few WS/SSE servers, sticky LB |
| 100K–10M | Gateway fleet, user→gateway registry (Redis), pub/sub between gateways |
| 10M+ | Regional gateway clusters, edge termination, hierarchical fanout |

### Fanout per Event

| Recipients | Strategy |
|---|---|
| < ~10K | Fan-out on write (push to each inbox) |
| > ~10K | Fan-out on read (pull + merge at read time) |
| Broadcast (everyone watching X) | Topic pub/sub, no per-user inbox |

---

## Patterns

Format for each: **Driving number**, a tier table, then **Say it** (one line to say out loud).

---

### 1. Read-Heavy Lookup

*URL shortener redirect, product catalog, user profile, metadata service.*

**Driving number:** read QPS and working-set size. (Reads are usually 10–100× writes.)

| Scale | Components | What changed |
|---|---|---|
| < 10K reads/s | Postgres + Redis cache-aside | — |
| 10K–100K | Redis cluster, read replicas, cache TTL + jitter | Cache becomes the primary read path |
| 100K–1M | In-process L1 + Redis L2, CDN / edge cache for public objects | Network hop to Redis is now the cost |
| 1M+ / global | Edge KV (CDN workers), multi-region replicas, DynamoDB global tables | Latency is now about geography |

Writes rarely matter here. If storage reaches 10 TB+ (e.g., 100M URLs/day × 5 years), move to a KV store (DynamoDB/Cassandra) keyed by ID.

**Say it:** "1B redirects/day is about 10K/s, 30K peak. Redis handles that on one shard, so the design challenge is ID generation, not scale."

---

### 2. Config / Feature Flags

*Feature flags, remote config, permission policies, pricing rules.*

**Driving number:** evaluation QPS (huge) vs. change rate (tiny).

| Scale | Components | What changed |
|---|---|---|
| Any QPS, < 10K flags | Postgres as source of truth → push full snapshot to SDKs, evaluate in-process | — |
| Many services / regions | Snapshot to CDN/S3 + streaming updates (SSE) to SDKs | Polling replaced by push |
| Per-user targeting at scale | Segment membership precomputed into a KV store, SDK fetches on login | Rules no longer fit in the snapshot |

Never put a network call on the evaluation path. Evaluation QPS is effectively your whole fleet's QPS.

**Say it:** "Writes are a few per minute, reads are every request across the fleet. So evaluate locally from a pushed snapshot, and the server only distributes."

---

### 3. Write-Heavy Ingestion

*Clickstream, IoT telemetry, audit/event logging, ad impressions.*

**Driving number:** sustained events/s × event size = MB/s.

| Scale | Components | What changed |
|---|---|---|
| < 5K events/s | Postgres (partitioned by time) or direct to S3 batches | — |
| 5K–100K | Kafka → consumers → Cassandra / ClickHouse / S3 | Log decouples producers from storage |
| 100K–1M+ | Partitioned Kafka (100s of partitions), Flink for enrichment, Parquet on S3, tiered retention | Must batch and compress; per-event writes are gone |
| Multi-region | Regional Kafka → MirrorMaker / cross-region replication to central lake | Ingest local, aggregate central |

**Say it:** "500K events/s at 1 KB is about 500 MB/s, roughly 40 TB/day. Nothing transactional survives that, so it's Kafka into columnar storage on S3 with a hot window in ClickHouse."

---

### 4. Feed / Timeline Fanout

*News feed, Twitter home timeline, Instagram feed.*

**Driving number:** posts/s × average followers = fanout writes/s, plus the celebrity follower count.

| Scale | Components | What changed |
|---|---|---|
| Small (< 1M users) | Pull on read: query posts by followees, sort, cache | — |
| Medium (fanout < ~1M writes/s) | Fan-out on write to per-user feed lists in Redis (post IDs only), Kafka for fanout workers | Precompute feeds |
| Large + celebrities | Hybrid: push for normal users, pull for accounts > ~10K followers, merge at read | Celebrity writes would explode |
| Ranked | + Ranking service at read time, feature store, candidate generation from both sources | Chronological → scored |

Store IDs in feeds, hydrate posts from a cache at read time. Cap feed length (~500–1000 IDs).

**Say it:** "5K posts/s × 200 followers is 1M feed inserts/s. That's fine across a Redis cluster, but a 50M-follower account would be 50M writes per post. So it's hybrid push/pull."

---

### 5. Chat / Messaging

*WhatsApp, Messenger, Slack.*

**Driving number:** concurrent connections (not message QPS) and message storage per year.

| Scale | Components | What changed |
|---|---|---|
| < 100K online | WS servers + Postgres, Redis pub/sub between servers | — |
| 1M–10M online | WS gateway fleet, user→gateway registry, Kafka per conversation partition, Cassandra (partition by conversation_id, cluster by seq) | Stateful gateways + wide-column store |
| 10M+ / global | Regional gateway clusters, cross-region routing, push notifications for offline users, media via S3 + CDN | Geography and offline delivery dominate |
| Large groups / channels | Fan-out on read for groups > ~100–1K members | Same as feed celebrity problem |

Ordering: per-conversation sequence numbers, not global ordering.

**Say it:** "50M DAU with ~30% online is 15M connections. At ~100K per gateway that's ~150 gateways. Messages are only ~20K/s, so connections are the real bottleneck."

---

### 6. Live Broadcast to Clients

*Stock tickers, live sports scores, live stream comments, auction prices.*

**Driving number:** subscribers per topic × update rate = outbound messages/s.

| Scale | Components | What changed |
|---|---|---|
| < 100K viewers | SSE/WS servers subscribe to Redis pub/sub per topic | — |
| 100K–10M viewers | Kafka → fanout tier → gateway fleet; gateways subscribe per topic, not per user | Fanout is hierarchical |
| High update rate | Conflate/throttle: send latest value every N ms, drop intermediate ticks | Clients can't consume every tick |
| Global | Edge fanout (regional relays), CDN-style push | Cross-region bandwidth |

For live comments, sample when it gets busy: show a subset to each viewer when comments exceed ~10–50/s.

**Say it:** "1M viewers × 10 updates/s is 10M messages/s outbound. So conflate to ~4 updates/s and fan out per topic through relays, not per user."

---

### 7. Presence / Ephemeral State

*Online/offline, last seen, typing indicators, cursors.*

**Driving number:** heartbeats/s (online users ÷ heartbeat interval) and status-change fanout.

| Scale | Components | What changed |
|---|---|---|
| < 1M online | Redis with TTL keys (`SETEX user:presence 30`) | — |
| 1M–100M online | Sharded Redis, heartbeats aggregated at the gateway, status changes published only to subscribed friends | Fanout on change is the cost |
| Very large friend lists | Lazy presence: fetch on view, don't push | Push doesn't scale |

Never persist presence to a durable DB. It's ephemeral by nature.

**Say it:** "15M online at a 30s heartbeat is 500K writes/s. That's TTL keys across a Redis cluster, and status changes only go to friends who currently have you on screen."

---

### 8. Counters & Aggregations

*Likes, view counts, ad click counting, API usage metering.*

**Driving number:** increments/s on the hottest key, and whether the count must be exact.

| Scale | Components | What changed |
|---|---|---|
| < 1K incr/s | Postgres `UPDATE … SET n = n + 1` | — |
| 1K–100K | Redis `INCR`, periodic flush to DB | Row lock contention avoided |
| Hot keys (viral post) | Sharded counters (`key:0..N`), sum on read; or local aggregation per server → flush every few s | One key exceeds one shard |
| 1M+ events/s, must be exact (billing / ads) | Kafka → Flink windowed aggregation with checkpoints, idempotent sink, reconciliation batch job | Exactly-once becomes the problem |
| Approximate OK (unique viewers) | HyperLogLog (Redis `PFADD`), Count-Min Sketch | Trade accuracy for memory |

**Say it:** "A viral post can take 100K likes/s on one key, which is more than one Redis shard. So I'd shard the counter 10 ways and sum on read. The display count can be a few seconds stale."

---

### 9. Leaderboard / Top-K

*Game leaderboards, trending hashtags, top products.*

**Driving number:** number of ranked entities and score-update rate.

| Scale | Components | What changed |
|---|---|---|
| < 10M entries | Single Redis sorted set (`ZADD`, `ZREVRANGE`) | — |
| 10M–100M+ | Sharded sorted sets by score range or by key + merge top-K; precompute top-N | One ZSET too big / too hot |
| Trending (windowed) | Kafka → Flink sliding-window counts → Count-Min Sketch + heap → Redis top-K | Time decay + approximate |
| Exact global rank for any user | Score-bucket histogram (count per bucket) → rank ≈ sum of higher buckets | Exact rank across shards is expensive |

**Say it:** "50M players fit in one sorted set at ~100 bytes each, about 5 GB. That's fine until updates exceed ~100K/s, then I shard by score range."

---

### 10. Rate Limiting

*API gateway limits per user/IP/key.*

**Driving number:** total checked requests/s and the number of distinct keys.

| Scale | Components | What changed |
|---|---|---|
| Single instance | In-memory token bucket | — |
| < 500K checks/s, multiple gateways | Central Redis + Lua script (atomic sliding-window counter / token bucket) | Shared state |
| 1M+ checks/s | Local token buckets + async sync to Redis (approximate), Redis cluster by key | Network hop per request is too expensive |
| Multi-region | Per-region budgets (global limit ÷ regions), periodic rebalance | Global exact counting isn't worth the latency |

Fail open if the limiter's store is down, unless the limit protects against abuse or cost.

**Say it:** "200K requests/s with a check each is within a Redis cluster, but that adds ~1ms per request. If the latency budget is tight, I'd use local buckets synced every 100ms and accept a little over-admission."

---

### 11. Search & Typeahead

*Full-text search, product search, autocomplete.*

**Driving number:** index size (docs × size), query QPS, and index freshness.

| Scale | Components | What changed |
|---|---|---|
| < 1M docs | Postgres full-text (`tsvector`, GIN index) | — |
| 1M–1B docs | Elasticsearch/OpenSearch, CDC (Debezium → Kafka) from source DB | Separate search tier |
| 1B+ docs / high QPS | Sharded ES by doc (scatter-gather) + replicas for QPS, time-based indices, two-phase ranking (BM25 → ML re-rank) | Shards for size, replicas for QPS |
| Typeahead | Trie / prefix index precomputed offline with top-K per prefix, served from memory/Redis, CDN-cached for top prefixes | Latency < 50ms, read-only |
| Semantic | + Vector index (pgvector < ~10M vectors, dedicated vector DB / ES kNN beyond), hybrid lexical + vector | Embeddings |

**Say it:** "200M products at 2 KB is about 400 GB of index. That's an ES cluster of ~10–20 shards, with replicas added for query QPS. The source of truth stays in Postgres and syncs via CDC."

---

### 12. Geospatial / Proximity

*Uber driver matching, Yelp nearby, delivery dispatch.*

**Driving number:** location updates/s (moving entities ÷ update interval) vs. static POI count.

| Scale | Components | What changed |
|---|---|---|
| Static POIs, < 100M | Postgres + PostGIS, or geohash column + index; cache popular areas | — |
| Moving entities, < 100K updates/s | Redis GEO (`GEOADD`/`GEOSEARCH`), latest location only, TTL | In-memory |
| 1M+ updates/s | Redis GEO sharded by city/region, location service per shard, Kafka for history to S3 | Partition by geography |
| Dense cities / uneven load | Quadtree or H3 cells with adaptive cell size | Geohash cells get hot |

Store only the latest position on the hot path. History goes to the log.

**Say it:** "5M drivers every 4s is about 1.25M writes/s, which no DB takes. So it's latest-location-only in Redis GEO, sharded by city, about 12K/s per city shard."

---

### 13. Contention / Booking / Flash Sale

*Ticketmaster, hotel booking, limited inventory drops.*

**Driving number:** concurrent buyers per item vs. inventory count (contention ratio).

| Scale | Components | What changed |
|---|---|---|
| Low contention | Postgres row lock / optimistic version check (`UPDATE … WHERE version = ?`) | — |
| Moderate (hot event) | Reservation with TTL hold (Redis or DB `held_until`), payment, then confirm; idempotency keys | Hold separates "claim" from "pay" |
| Extreme (1M users, 10K seats) | Virtual waiting room / queue admission at the edge, Redis atomic decrement (Lua) for inventory tokens, DB only for admitted buyers | Admission control protects the DB |
| Seat maps | Per-seat lock in Redis (`SET NX EX`), sharded by event section | Granular locks |

The DB should only see traffic that can actually succeed.

**Say it:** "1M people for 50K seats is 20:1 contention. If they all hit Postgres, row locks melt it. So there's a waiting room, then Redis decrements inventory tokens, and only winners write to the DB."

---

### 14. Payments / Ledger

*Payment processing, wallets, double-entry ledger, payouts.*

**Driving number:** usually *not* QPS (often < 1K TPS). The design is driven by correctness: no loss, no double-charge.

| Scale | Components | What changed |
|---|---|---|
| < 1K TPS (most systems) | Postgres with sync replica, append-only ledger table, idempotency key table, outbox → Kafka, PSP webhooks + polling, daily reconciliation | — |
| 1K–10K TPS | Shard ledger by account, balances as materialized aggregates, saga for cross-account moves | One primary saturates |
| 10K+ / multi-region | Distributed SQL (Spanner / CockroachDB) or per-region ledgers with single-leader per account | Global consistency |
| Hot accounts (merchant) | Sub-account sharding, batched postings | One account row is hot |

There's never Redis-only state, and the reconciliation job is not optional.

**Say it:** "10M payments/day is ~100 TPS. Scale isn't the issue, durability is. So it's sync-replicated Postgres, idempotency keys, an append-only ledger, and reconciliation against the PSP."

---

### 15. Job Queue / Scheduler

*Async task processing, cron at scale, delayed jobs, Airflow-style DAGs.*

**Driving number:** jobs/s dispatched and the number of scheduled (future) jobs.

| Scale | Components | What changed |
|---|---|---|
| < 1K jobs/s | Postgres table as queue (`SELECT … FOR UPDATE SKIP LOCKED`), lease + heartbeat | — |
| 1K–100K jobs/s | SQS / Kafka / RabbitMQ for dispatch, Postgres for job state, DLQ | Dispatch separated from state |
| Many future jobs (100M+) | Time-bucketed storage (partition by fire minute), scheduler scans only the current bucket, sharded schedulers with leader per shard | Can't scan all jobs |
| DAG workflows | Workflow engine (Temporal / Airflow / Step Functions), state machine per run | Dependencies + retries |

Exactly-once doesn't exist here. Design for at-least-once with idempotent jobs.

**Say it:** "50M jobs/day is ~500/s. Postgres with SKIP LOCKED handles that, and I'd only add Kafka for dispatch past ~5–10K/s."

---

### 16. Notifications

*Push (APNs/FCM), SMS, email, in-app.*

**Driving number:** notifications/s at peak (campaign blasts) and per-provider rate limits.

| Scale | Components | What changed |
|---|---|---|
| < 1K/s | Service + per-channel workers, Postgres delivery log for dedup | — |
| 1K–100K/s | Kafka with a topic per channel and priority, worker pools per channel, preferences in Redis/DynamoDB, template service | Isolation per channel |
| Blasts (100M users) | Batch segment expansion offline, throttled dispatch per provider limit, scheduled send windows by timezone | Provider limits dominate |
| Must not double-send | Idempotency key (user + event + channel) in the delivery log, checked before send | Dedup |

Separate transactional (OTP, receipts) from marketing queues so a blast never delays an OTP.

**Say it:** "A 100M-user campaign at a provider limit of ~10K/s takes ~3 hours. So it's a throttled, scheduled pipeline on its own queue, isolated from transactional sends."

---

### 17. Media Upload & Delivery

*YouTube, Instagram photos, video streaming.*

**Driving number:** upload bytes/day (storage) and egress bytes/day (CDN cost). QPS is irrelevant.

| Scale | Components | What changed |
|---|---|---|
| Small | Pre-signed S3 upload, metadata in Postgres, CloudFront | — |
| TB/day | Multipart/resumable uploads, transcode pipeline (queue → workers → S3), thumbnails, HLS/DASH manifests | Async processing DAG |
| PB/month | Popular-only eager transcoding, lazy for long tail, storage tiering (S3 → IA → Glacier), multi-CDN | Cost is the design |
| Global, high egress | CDN edge caching (90%+ hit on popular content), origin shield, ISP peering / own edge | Egress cost |

**Say it:** "500K uploads/day × 300 MB is 150 TB/day raw, ~450 TB with renditions. This is an S3 + CDN cost problem, so I'd transcode lazily for the long tail."

---

### 18. File Sync

*Dropbox, Google Drive, OneDrive.*

**Driving number:** metadata operations/s (the real bottleneck) and total block storage.

| Scale | Components | What changed |
|---|---|---|
| Small | Upload whole files to S3, metadata in Postgres, poll for changes | — |
| Millions of users | 4 MB chunking + SHA-256 content addressing (dedup), upload only changed blocks, metadata sharded by namespace/user, change notifications via long-poll/WS | Delta sync |
| Billions of files | Metadata on sharded MySQL/Postgres (or Spanner), block store on S3 with cross-user dedup, cold tiering | Metadata DB is the bottleneck |

**Say it:** "100M DAU × ~20 file events is ~2B metadata ops/day, about 20K/s, but bursty. Blocks are easy on S3. The sharded metadata store is where the design effort goes."

---

### 19. Metrics / Logs / Observability

*Prometheus/Datadog-style metrics, centralized logging, tracing.*

**Driving number:** data points/s (metrics), GB/day (logs), and **cardinality** (unique series).

| Scale | Components | What changed |
|---|---|---|
| < 1M series | Prometheus per cluster, Grafana | — |
| 1M–100M series | Remote-write to a horizontally scaled TSDB (Mimir / Cortex / VictoriaMetrics / M3), downsampling | Single Prometheus OOMs |
| Logs, TB/day | Agents → Kafka → ClickHouse / Loki / ES; hot 7 days, S3 for the rest | Index cost dominates |
| Traces | Head/tail sampling (keep errors + slow), store in object storage | Can't keep 100% |

Cardinality is what breaks metrics systems. Volume usually isn't. Label by user_id and you're done.

**Say it:** "10K hosts × 1K series is 10M series at a 10s scrape, about 1M points/s. That's past single Prometheus, so it's remote-write to a sharded TSDB with downsampling after 2 weeks."

---

### 20. Analytics / OLAP

*Dashboards, business reporting, ad-hoc queries over events.*

**Driving number:** data scanned per query and query freshness requirement.

| Scale | Components | What changed |
|---|---|---|
| < 100 GB | Postgres read replica + materialized views | — |
| 100 GB–10 TB | Warehouse (Snowflake / BigQuery / Redshift), nightly ETL/ELT | Columnar |
| 10 TB+ / lake | S3 + Parquet/Iceberg, Spark/Trino/Athena, dbt | Separate storage from compute |
| Sub-second, real-time | Kafka → ClickHouse / Druid / Pinot with pre-aggregated rollups | Freshness < 1 min |

Never run analytics on the OLTP primary.

**Say it:** "Dashboards over 50 TB of events need sub-second answers. That's ClickHouse or Pinot with rollups fed from Kafka, plus a lake on S3 for ad-hoc queries."

---

### 21. Distributed Cache / KV Store

*Design Redis/Memcached/DynamoDB itself.*

**Driving number:** total dataset size ÷ per-node memory, and QPS ÷ per-node throughput.

| Scale | Components | What changed |
|---|---|---|
| Fits one node | Single node + replica, LRU eviction | — |
| Multi-node | Consistent hashing with vnodes (or fixed hash slots like Redis Cluster's 16,384), client-side routing | Partitioning |
| HA | Leader-follower per shard (cache) or leaderless N=3, W=2, R=2 quorum (KV store), gossip membership, hinted handoff | Replication |
| Hot keys | Client-side L1, read replicas for hot keys, key splitting | Uneven traffic |

**Say it:** "2 TB at ~64 GB per node is ~32 shards, ×2 for replicas is ~64 nodes. 5M QPS ÷ 64 is ~80K per node, within limits."

---

### 22. Unique ID Generation

**Driving number:** IDs/s per generator and whether IDs must be time-sortable.

| Scale | Components | What changed |
|---|---|---|
| Single DB | Auto-increment / sequence | — |
| Multiple writers, < ~10K/s | Ticket server or DB sequence with range allocation (each server grabs 1K IDs) | Batching |
| High throughput, sortable | Snowflake: 41-bit ms timestamp + 10-bit worker + 12-bit sequence (~4M/s per worker) | No coordination |
| Unordered OK | UUIDv4. Or UUIDv7 / ULID for time-sortable 128-bit | Simplest |

**Say it:** "Snowflake gives 4K IDs per ms per worker with no coordination. The only real risk is clock skew, which I handle by refusing to issue IDs if the clock goes backwards."

---

### 23. Collaborative Editing

*Google Docs, Figma, Notion.*

**Driving number:** concurrent editors per document (usually small) and total active docs.

| Scale | Components | What changed |
|---|---|---|
| Any number of docs, < ~100 editors/doc | Doc session server owns each active doc (sticky routing by doc_id), OT or CRDT, op log in Postgres/Cassandra, periodic snapshots to S3 | — |
| Many active docs | Session servers sharded by doc_id, registry (doc → server), reload from snapshot + op log on failover | Ownership + failover |
| Large audiences (1K+ viewers) | Separate editors from viewers, fan out to viewers via broadcast tier (pattern 6) | Read fanout |
| Offline-first | CRDTs (Yjs / Automerge) for merge without a central server | No single authority |

**Say it:** "Per doc the scale is tiny, maybe 10 editors. The challenge is conflict resolution and single ownership per doc, not throughput. So it's a doc-owner server per active doc with OT and an op log."

---

### 24. Web Crawler

**Driving number:** pages/s (target crawl ÷ time window) and politeness limits per domain.

| Scale | Components | What changed |
|---|---|---|
| < 100 pages/s | Single fetcher, queue in Redis, visited set in a DB | — |
| 100–10K pages/s | URL frontier (priority queue + per-host politeness queues), distributed fetchers partitioned by host hash, Bloom filter dedup, DNS cache, S3 for content | Politeness per host |
| 10K+ pages/s / billions of URLs | Sharded frontier on disk (Kafka / RocksDB), SimHash near-dup detection, recrawl scheduling by change rate | Frontier is larger than memory |

**Say it:** "1B pages/month is ~400/s. With 1-second politeness per host that's fine as long as I partition by host so each fetcher owns its domains."

---

## Tier-Jump Signals

Say these when the interviewer scales the problem up ("what if it's 10× bigger?").

| You hit… | Symptom | Jump to |
|---|---|---|
| ~5K sustained writes/s | Primary CPU / WAL / lock contention | Shard by entity, or a write-optimized store |
| ~50K reads/s | Replica lag, connection exhaustion | Cache tier, CQRS read model |
| Working set > RAM | Cache hit rate drops, disk reads | More cache shards, or accept a DB tier |
| ~1–5 TB in one Postgres | Backups/vacuum/index rebuild take hours | Partition by time, archive, then shard |
| One hot key > one shard | p99 spike on one node | Key splitting, local L1, replicate the hot key |
| ~100K connections per box | Memory / file descriptors | Gateway fleet + registry |
| Fanout > ~10K per event | Write amplification | Fan-out on read for heavy senders |
| Cross-region latency > SLO | 150ms RTT | Regional replicas, edge cache, per-region leaders |
| Exact counts at 1M+/s | Lock/serialization bottleneck | Stream aggregation with checkpoints, or approximate |
| Egress cost dominates | CDN bill | Edge caching, lazy transcode, tiering |
