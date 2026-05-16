# Coinbase Explore: Realtime Market Data

**Category:** System Design — **#1 Most Frequent SD Topic (5 occurrences in 2026 Q2 data)**
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** Stream processing, WebSocket fanout, hot cache, exchange feed resilience, window aggregation

### Interview Intel (2026 Q2 Blog)
- Appeared in 5 out of 10 system design interviews — by far the most common
- Framed as "Coinbase Explore" — real-time price stream with subscriptions
- Candidates must **self-clarify** real-time vs subscription vs brokerage boundaries — interviewer won't hand it to you
- Bar is high for this round — lead with the hard problem (fanout) not the easy one (ingestion)
- Other SD topics seen: crypto exchange order flow (failure handling, 1 occurrence), stock trading platform (1), blob storage (1)

---

## Problem Statement

Design the backend for Coinbase Explore — a page showing ~20K crypto assets with realtime price changes and pre-computed time windows (1m, 5m, 30m, 1h, 1d). Data flows in from external exchanges. The system must handle exchange feed failures gracefully, marking data as stale rather than silently serving bad data.

Scope: focus on ingest, stream processing, serving, and failure handling. Exclude long-term historical storage.

---

## Requirements

### Functional
- Display ~20K assets with last price, % change per window, volume
- Serve initial page load via REST (supports pagination, sorting, search)
- Push realtime updates to subscribed clients via WebSocket
- Compute rolling windows (1m/5m/30m/1h/1d) continuously
- Mark individual assets as stale when their feed stops updating

### Non-Functional
| Requirement | Target | Rationale |
|---|---|---|
| Tick-to-client latency | < 1s p95 | Market data must be live |
| Snapshot API latency | < 250ms p95 | Page load must be fast |
| Availability | 99.95% | Must work even during exchange outages |
| Consistency | Eventual (1-2s lag) | Speed/availability over perfect sync |

### Scale Estimates
| Metric | Value |
|---|---|
| Upstream symbols | ~1,000,000 tickers (stress case) |
| Avg tick rate | ~1 tick/s per active ticker |
| Ingestion throughput | ~1,000,000 events/s |
| Raw ingress bandwidth | ~120 MB/s |
| Visible assets (Explore) | ~20,000 symbols |
| Concurrent clients | 2,000,000 |
| Client update cadence | Batched delta every 250-500ms |

The fanout problem (pushing to 2M clients) is harder than the ingestion problem. Say this early.

---

## Data Model

```
Asset
├── symbol: VARCHAR (PK, e.g. "BTC-USD")
├── base_asset, quote_asset: VARCHAR
├── display_name: VARCHAR
├── status: ENUM (active, halted, delisted)
├── market_cap_rank: INTEGER
└── updated_at: TIMESTAMP

Tick  — raw event, short-lived (hot store or stream only)
├── symbol: VARCHAR
├── exchange_id: VARCHAR
├── sequence_id: BIGINT      — dedup key
├── trade_price: DECIMAL
├── trade_size: DECIMAL
├── event_time: TIMESTAMP
└── ingest_time: TIMESTAMP

WindowAggregate
├── symbol: VARCHAR
├── window: ENUM (1m, 5m, 30m, 1h, 1d)
├── bucket_start: TIMESTAMP
├── open, high, low, close: DECIMAL
├── volume: DECIMAL
├── change_pct: DECIMAL
├── is_stale: BOOLEAN
└── updated_at: TIMESTAMP

MarketSnapshot  — denormalized read model, updated on each tick
├── symbol: VARCHAR (PK)
├── last_price: DECIMAL
├── change_{1m,5m,30m,1h,1d}_pct: DECIMAL
├── volume_24h: DECIMAL
├── source_count: INTEGER
├── is_stale: BOOLEAN
└── updated_at: TIMESTAMP

ExchangeFeedStatus
├── exchange_id: VARCHAR (PK)
├── status: ENUM (healthy, degraded, down)
├── last_heartbeat_at: TIMESTAMP
├── error_rate_1m: FLOAT
└── lag_ms_p95: INTEGER
```

`MarketSnapshot` is the hot read model — the list API and WebSocket delta stream both read from this. Keep it in Redis.

---

## API Design

### REST (initial page load)

```
GET /api/explore/assets
  ?cursor=<opaque>&limit=100
  &sort=market_cap&order=desc
  &search=eth

Response:
{
  "items": [
    {
      "symbol": "ETH-USD",
      "last_price": 3120.25,
      "change_1m_pct": 0.12,
      "change_5m_pct": -0.09,
      "change_1d_pct": 2.37,
      "is_stale": false,
      "updated_at": "2026-02-10T19:40:01Z"
    }
  ],
  "next_cursor": "..."
}

GET /api/explore/assets/{symbol}/windows?windows=1m,5m,30m,1h,1d
Response:
{
  "symbol": "BTC-USD",
  "windows": {
    "1m": { "open": 67500.1, "close": 67504.2, "change_pct": 0.01 },
    "5m": { "open": 67480.0, "close": 67504.2, "change_pct": 0.04 }
  }
}
```

### WebSocket (live updates)

```
WS /ws/explore

# Client subscribes to visible rows only
{ "type": "subscribe", "symbols": ["BTC-USD", "ETH-USD"], "channels": ["ticker"] }

# Server: initial snapshot on subscribe
{ "type": "snapshot", "symbols": [{ "symbol": "BTC-USD", "last_price": 67504.2, ... }] }

# Server: batched delta (every ~250-500ms)
{ "type": "delta_batch", "updates": [
    { "symbol": "BTC-USD", "last_price": 67508.9, "change_1m_pct": 0.03, "seq": 987654321 }
  ]
}
```

### Internal Kafka Topics

```
ticks.raw.{exchange}    → { symbol, exchange_id, sequence_id, price, size, event_time }
ticks.normalized        → { symbol, sequence_id, price, size, event_time, ingest_time }
market.snapshots        → { symbol, last_price, change_{1m..1d}_pct, is_stale, updated_at }
```

---

## Architecture

| Component | Role |
|---|---|
| Exchange Connectors | Maintain persistent WS connections to external exchanges. Normalize symbol names (XBT → BTC). Apply per-feed rate limits. Emit to `ticks.raw.{exchange}`. |
| Normalizer + Sequencer | Validate ticks, drop duplicates on `(exchange_id, sequence_id)`, align timestamps to system clock. Emit to `ticks.normalized`. |
| Stream Aggregator | Partitioned by symbol hash for horizontal scale. Maintains O(1) ring-buffer windows for each time window. Emits updated `MarketSnapshot` on each new tick. |
| Hot Store (Redis) | Latest `MarketSnapshot` per symbol. TTL-based staleness detection. Source of truth for list API and initial WS snapshot. |
| Snapshot API | Reads from Redis. Handles pagination, sorting (by pre-indexed fields), search. |
| WebSocket Gateways | Subscription registry (symbol → connection set). Consume `market.snapshots` Kafka topic, fan out to subscribed connections. Batch updates every 250-500ms per symbol. |
| Reconciliation / Replay Jobs | On restart: replay recent ticks from Kafka log to rebuild in-memory window state. Detect and fill gaps. |

### Key Data Flow

```
Exchange feeds
  → Exchange Connectors (WebSocket, per exchange)
  → Kafka: ticks.raw.{exchange}
  → Normalizer + Sequencer (dedup, validate)
  → Kafka: ticks.normalized
  → Stream Aggregator (partitioned by symbol)
      ├── Updates WindowAggregate (in-memory ring buffer)
      └── Emits MarketSnapshot
  → Kafka: market.snapshots
      ├── Hot Store (Redis) ← Snapshot API reads
      └── WebSocket Gateways → 2M clients (batched deltas)
```

---

## Deep Dives

### Window Aggregation at Scale

1M ticks/s across 20K visible symbols = ~50 ticks/s per symbol average, but spiky.

- Partition the stream by `hash(symbol) % N_workers` so all ticks for a symbol go to one worker.
- Use ring buffers indexed by epoch second: O(1) insert and expiry. No need to scan all ticks to compute a window.
- Allow 2-3s late-arrival tolerance before closing a bucket. Beyond that, mark is_stale.

### Exchange Failure Handling

Show stale, never pretend data is fresh.

- Each connector sends a heartbeat every second. If `ExchangeFeedStatus.last_heartbeat_at` is > threshold, mark the feed `down`.
- When a feed goes down, set `is_stale = true` on all affected `MarketSnapshot` rows. Surface this in the UI.
- Circuit breaker per exchange: if error rate > threshold in 1m window, stop reconnecting immediately and use backoff.
- Multi-source strategy: for top symbols (BTC, ETH), ingest from 2-3 exchanges simultaneously. If one goes down, the snapshot stays fresh from the others.

### WebSocket Fanout to 2M Clients

This is the hardest part — say so.

- Client subscribes only to **visible rows** (typically 20-50 at a time). Do not broadcast all 20K symbols to everyone.
- Coalesce multiple ticks for the same symbol within a 250-500ms window into a single delta. Avoids message storm to clients.
- Shard WebSocket gateways by connection ID range. Each gateway handles ~50K connections. Scale horizontally.
- Compress delta payloads (gzip/deflate). The batched delta format is already compact.

---

## Key Trade-offs

| Decision | Choice | Why |
|---|---|---|
| Aggregation timing | On-write (stream precompute) vs. on-read | On-read is too slow for 20K symbols × 2M clients. Precompute on the stream. |
| Client protocol | REST + WebSocket hybrid | REST for initial load (SEO, caching); WS for low-latency updates |
| Stale data | Show stale badge vs. hide | Better to be honest about feed health than silently serve bad prices |
| Delivery guarantee | At-least-once + dedup by sequence_id | Exactly-once is too expensive; a duplicate tick on a dashboard is acceptable |
| Hot store | Redis vs. reading from stream processor | Redis gives sub-250ms list API at scale without hitting stream state |

---

## Staff+ Angle

- **Fanout is the hard problem.** Ingesting 1M ticks/s is a stream processing problem with known solutions. Pushing correct, low-latency, deduplicated deltas to 2M concurrent clients with subscriptions is where most designs break down. Lead with this.
- **Staleness as a first-class feature.** Most candidates handle the happy path but ignore feed failures. At Coinbase, showing a wrong price is worse than showing no price. Design staleness detection into the data model and surface it to the UI.
- **Sequence number discipline.** The `(exchange_id, sequence_id)` dedup key prevents a reconnecting connector from replaying old ticks into window aggregates. Without it, a reconnect after a 30s outage would corrupt every open window.
- **Operational observability.** Production market data systems live or die on monitoring. You need metrics for: per-exchange feed lag, tick drop rate, stale symbol count, WebSocket connection count, and delta delivery latency. Mentioning this signals production experience.
- **Coinbase-specific angle:** Coinbase ingests from its own exchange (Coinbase Advanced Trade) plus external feeds. The connector abstraction handles this naturally. Also, some symbols are only on one exchange — worth noting that multi-source redundancy isn't available for every ticker.

---

---

## Key Framing (from hack2hire — memorize these)

### The Four Questions to Answer

Frame your design around these four problems:
1. **How do we choose one displayed reference price?** (multi-source normalization, canonical asset ID)
2. **How do rankings and search stay fast?** (materialized sort keys, pre-ranked top movers, not full-catalog scan)
3. **How do deltas reach clients cheaply?** (coalesce, group subscriptions, batch per interval)
4. **How does the UI stay honest when a source goes stale?** (heartbeat → threshold → stale flag → surface to client)

### Two Stories in One System

> "One pipeline owns authoritative ingest, normalization, and incremental rollups. Another layer serves precomputed snapshots and rankings and fans out small deltas. They are NOT the same subsystem."

Say this early — it shows you understand the separation.

### Golden Principles

- **"HTTP is truth, WebSocket is optimization."** If the stream lies by omission, the user still has a way to recover via REST. Streams can batch, drop, or gap under load — HTTP cannot hide staleness.
- **"Fanout is a scheduling problem, not a socket problem."** Coalesce, group subscriptions, and make recovery cheap with snapshots.
- **"Show stale, never pretend data is fresh."** Availability > consistency, but NEVER silently serve old prices as if they're current.

### Recovery Semantics

When WebSocket disconnects or detects a sequence gap:
1. Server sends `resync_required` flag
2. Client discards local optimistic state
3. Client refetches via GET /assets (HTTP snapshot)
4. Client re-subscribes to stream with fresh cursor

### Reference Price — Clarify Before Designing

> "Before I lock the stale-data rules, I'd ask: is the displayed number a last trade, a midpoint, or a vendor-normalized reference?"

This shows domain awareness. The answer changes your fallback policy.

### Clarifying Question for the Interviewer

Ask early: "When we say real-time prices — are we aggregating from multiple exchanges into one canonical price per asset, or showing per-exchange prices?" This scopes the normalization layer.

---

## What the Interviewer Expects at Senior/Staff Level

From hack2hire's grading rubric:

> "Senior answer should own incremental rolling aggregates, replayable event semantics, explicit stale-data policy tied to source health. Expect subscription grouping and coalescing for fanout, cursor pagination against materialized sorts, and a clear line that HTTP is authoritative while streams are best-effort freshness."

**Must-hit to pass:**
1. Incremental window computation (not "scan all ticks per request")
2. Replayable events (Kafka retention → rebuild state on crash)
3. Explicit stale policy (heartbeat → threshold → mark stale → UI flag)
4. Coalesce + group subscriptions for fanout
5. HTTP authoritative, WebSocket best-effort
6. Clarify reference price definition early

**Differentiators (Staff+ signal):**
- Explain HOW rolling windows update in O(1) per tick (ring buffer or running OHLCV)
- Explain WHY materialized rankings (top movers) instead of full-catalog sort
- Mention backpressure: what happens when aggregator can't keep up with ingest burst
- Mention per-asset rate limiting: one viral asset shouldn't starve fanout for others

---

## Quick Skim Checklist (Before Interview)

**Architecture (draw this):**
- [ ] Exchange WS adapters (2-3, active-active) → Kafka raw ticks
- [ ] Normalizer/dedup → Kafka normalized ticks  
- [ ] Aggregator (partitioned by symbol, stateless, ring buffer windows) → Kafka snapshots + Redis
- [ ] REST API reads from Redis (initial page load)
- [ ] WS Gateways (20-40 nodes) consume Kafka snapshots → fan out to 2M clients
- [ ] Exchange health monitor → stale flags propagate through pipeline

**Key numbers (mention naturally):**
- 20K visible assets, 1M total catalog
- 1-2M ticks/sec peak ingest
- 2M concurrent WebSocket clients
- 50-100K connections per WS gateway node → 20-40 nodes
- 250-500ms delta batch interval
- < 1s tick-to-client latency target
- 99.95% availability target

**Verbal (don't draw, say when asked):**
- Data entities: Tick, WindowAggregate, MarketSnapshot, ExchangeFeedStatus
- APIs: GET /assets (paginated, sorted), WS /market-stream (subscribe visible symbols)
- Window math: O(1) update per tick (running OHLCV in memory)
- Dedup: (exchange_id, sequence_id) — prevents replay corruption
- Recovery: resync_required flag → client refetches HTTP → re-subscribes

**Stale policy (say proactively):**
- Heartbeat per exchange every 1s
- Missing > 10s → mark feed degraded
- Missing > 30s → mark stale, surface flag to UI
- Multi-source: hot assets (BTC, ETH) have 2-3 feeds. If one goes down, others keep it fresh.
- Single-source assets: last known price + stale badge. NEVER hide the badge.

**Operational (mention at the end if time):**
- Per-exchange feed lag metric
- Stale symbol count alert
- Consumer lag (aggregator falling behind)
- WS connection count + delta delivery latency
- On-call: "Check exchange status first. If our aggregator is lagging, check consumer lag and restart."
