# Crypto Exchange Order System (Broker)

**Category:** System Design
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** Async order lifecycle, multi-exchange routing, idempotency, timeout recovery, financial consistency

### Key Insights from hack2hire (Staff-level framing)

**The core tension:** The user taps "buy" and expects an instant response. The exchange is external, slow, may partially fill over minutes, and may lose a callback entirely. If you pretend these two worlds operate at the same speed, your design will either lie to users or overdraw their accounts.

**The aha moment:**
> "The hold is NOT the trade. The exchange fill is the trade. Your system is a reliable state machine that bridges the gap between what the user requested and what the exchange actually did."

**Two-phase split (say this early):**
> "Phase 1 is synchronous and user-facing: validate buying power, create a hold, accept the order, return immediately. Phase 2 is asynchronous and exchange-facing: submit, process fills, adjust holds. This split is the backbone."

**Golden principles:**
- **"HTTP is truth, WebSocket is optimization"** — same as Explore. GET /orders/{id} is always authoritative. WebSocket pushes are hints.
- **"The exchange is the authority on execution"** — broker can REQUEST a cancel, but the exchange DECIDES. Fills always win over cancel requests.
- **"Reconciliation is not error handling, it's a safety net that runs continuously"** — mention the poller early, it signals you understand external integration is inherently unreliable.

**Cancel-fill race (the signature edge case):**
- User taps cancel. Exchange fills the order simultaneously. Both are valid. Only one terminal state can win.
- **Rule: exchange decides.** If exchange already filled → FILLED wins, cancel is discarded. If exchange hasn't matched → CANCELLED wins.
- State machine: CANCEL_REQUESTED allows transitions to BOTH Cancelled and Filled. Whichever the exchange reports first wins. PostgreSQL transaction serialization on the order row picks the winner.
- "If you answer 'cancel always wins' or 'fill always wins' without explaining the exchange's role as authority, you have missed the point."

**Buying power under concurrency:**
- Two concurrent buy orders for same account → both check balance before either writes a hold → overdraft.
- **Fix:** SERIALIZABLE isolation in PostgreSQL for the buying-power transaction. DB detects read-write conflicts and aborts one. Narrow transaction scope: balance check + hold creation only.
- Redis cache as fast filter ("clearly insufficient → reject without touching DB"), but NEVER the decision-maker.

**Partial fill accounting:**
- Hold adjustment uses ACTUAL execution price, not the limit price.
- 200 shares filled at $49.95 → reduce hold by $9,990, not by 200 × limit_price.
- Residual difference released when order reaches terminal state.

**Senior bar (from interviewer expectations):**
> "A senior candidate should drive the core tension between user-facing certainty and exchange-side uncertainty from the start. The clearest senior signal is the ability to explain why the hold is not the trade, and why the state machine exists to bridge the gap between user intent and exchange execution."

**Clarifying question to ask first:**
> "Are we handling limit orders only, or market orders too? And is the exchange a single venue or do we route to multiple exchanges for best price?"

---

## Problem Statement

Design a crypto brokerage order system that routes market orders to external exchanges (Binance, Kraken, etc.), finds the best price, and manages the full async order lifecycle. External exchange APIs are slow and unreliable — a placed order may not confirm for seconds or may silently fail. The system must never lose money through duplicate execution or unreconciled fills.

Scope: market orders only.

---

## Requirements

### Functional
- Accept buy/sell market orders from users
- Query multiple exchanges simultaneously and route to best price
- Track order lifecycle: pending → price_quoted → submitted → filled/failed/timed_out
- Handle timeouts without risking double execution
- Serve order status and history in realtime
- Reserve user funds at submission, release/apply on resolution

### Non-Functional
| Requirement | Target |
|---|---|
| Consistency | No duplicate orders, no lost fills |
| Availability | 99.9% uptime (crypto never stops) |
| Latency | Price quote < 500ms; order placement < 1s |
| Fault tolerance | Survive exchange outages and webhook failures |
| Scalability | 10M users; handle 1000x traffic spike during market crashes |

### Scale Estimates
| Metric | Value |
|---|---|
| Total users | 10M |
| Normal daily orders | 50K (~0.6 TPS average) |
| Peak TPS (market crash) | 1,000+ TPS |
| Storage/year | ~18 GB |

Traffic spikes are the primary scaling challenge. The queue is the buffer.

---

## Data Model

```
Order
├── id: UUID (PK)
├── user_id: UUID (FK)
├── symbol: VARCHAR (e.g. "BTC-USD")
├── side: ENUM (buy, sell)
├── type: ENUM (market)
├── quantity: DECIMAL
├── status: ENUM (pending, price_quoted, submitted,
│              partially_filled, filled, failed, cancelled, timed_out)
├── exchange_id: VARCHAR
├── exchange_order_id: VARCHAR
├── idempotency_key: VARCHAR — UNIQUE with user_id
├── quoted_price: DECIMAL
├── filled_price: DECIMAL    — avg fill price
├── filled_quantity: DECIMAL
├── reserved_amount: DECIMAL — funds locked on submission
├── failure_reason: VARCHAR
├── retry_count: INTEGER (default 0)
├── max_retries: INTEGER (default 3)
├── created_at, updated_at, expires_at: TIMESTAMP

PriceQuote
├── id: UUID (PK)
├── order_id: UUID (FK)
├── exchange_id: VARCHAR
├── bid_price, ask_price: DECIMAL
├── quoted_at: TIMESTAMP
└── expires_at: TIMESTAMP

Exchange
├── id: VARCHAR (PK, e.g. "binance")
├── status: ENUM (active, degraded, offline)
├── priority: INTEGER
├── rate_limit_per_sec: INTEGER
└── updated_at: TIMESTAMP

OrderEvent  — append-only audit log
├── id: UUID (PK)
├── order_id: UUID (FK)
├── event_type: ENUM (created, quoted, submitted, partially_filled,
│                    filled, failed, cancelled, timed_out)
├── payload: JSONB
└── created_at: TIMESTAMP
```

---

## API Design

### User REST

```
POST /api/orders
Headers: Idempotency-Key: <client UUID>
Body: { symbol, side, type: "market", quantity }
Response: { order_id, status: "pending", created_at }

GET /api/orders/{order_id}
Response: { order_id, status, symbol, side, quantity,
            filled_price, exchange_id, created_at, updated_at }

GET /api/orders?limit=50&cursor={cursor}
```

### WebSocket (realtime status)

```
WS /ws/orders

Server push:
{ "type": "order_update", "order_id": "ord_456",
  "status": "filled", "filled_price": 51234.50, "timestamp": "..." }
```

### Internal Exchange APIs (all async)

```
POST /internal/exchanges/{exchange_id}/quote
Body: { symbol, side, quantity, callback_url }
→ Response is async, comes back via callback

POST /internal/exchanges/{exchange_id}/orders
Body: { symbol, side, type, quantity,
        idempotency_key: "{order_id}_{exchange_id}_v{attempt}",
        callback_url }
→ Result comes back via webhook (not in response body)

GET /internal/exchanges/{exchange_id}/orders/{exchange_order_id}
→ Manual status check for timeout recovery
```

---

## Architecture

| Component | Role |
|---|---|
| API Servers | Validate request, check idempotency key, lock funds (`reserved_amount`), enqueue order, return `{ status: pending }` |
| Order Engine | Core state machine. Reads from queue. Drives order through price_quoted → submitted → filled/failed. Publishes to WebSocket. Writes every transition to `OrderEvent`. |
| Price Router | Fans out quote requests to all active exchanges in parallel. Picks best ask (for buys) or best bid (for sells). Re-quotes if quote expires before submission. |
| Exchange Adapters | Per-vendor translators. Handle request format, auth, rate limiting (token bucket). Emit callbacks back to Order Engine. |
| Timeout Monitor | Watches for orders stuck in `submitted` > 30s. Queries exchange for status before deciding whether to retry or mark failed. |
| Reconciliation Job | Runs every 5 minutes. Compares internal order state against exchange fill records. Detects and applies missed webhooks. |
| Price Cache (Redis) | Streams live quotes from exchanges via WebSocket into Redis. Price Router reads from cache instead of making synchronous quote calls per order. |

### Key Data Flow

```
User → API Servers
  → Lock funds, write Order(pending), check idempotency
  → Enqueue to Order Queue
  → Return "pending" to user

Order Queue → Order Engine
  → Price Router: fan out quote requests (or read from Price Cache)
  → Select best exchange → mark Order(price_quoted)
  → Exchange Adapter: submit order with idempotency key
  → Mark Order(submitted)

Exchange → Webhook callback → Order Engine
  → Write OrderEvent, update filled_price/quantity
  → Mark Order(filled or partially_filled)
  → Release/apply reserved_amount
  → Push WebSocket update

Timeout Monitor (async, every 30s)
  → Find Order(submitted, updated_at > 30s ago)
  → GET /internal/exchanges/{id}/orders/{exchange_order_id}
  → If filled: apply, mark filled
  → If not filled: cancel on exchange, retry with next-best exchange
```

---

## Deep Dives

### Timeout Recovery: The Double-Execution Trap

The most important rule: **never retry a timed-out order without first querying the exchange.**

```
timed_out → [query exchange]
              ├── filled → apply fill, mark filled (no retry)
              └── not filled → cancel on exchange → re-route to next exchange
```

If you skip the query and blindly retry, the user may end up with 2x the intended BTC position. This is a financial loss, not just a bug. Make this explicit in the interview.

### Idempotency (3 layers)

**Layer 1 — Client key:** API rejects if `(user_id, idempotency_key)` already exists.

```sql
CREATE UNIQUE INDEX uq_orders_user_idempotency ON orders (user_id, idempotency_key);

INSERT INTO orders (user_id, idempotency_key, symbol, side, quantity, status)
VALUES ($1, $2, $3, $4, $5, 'pending')
ON CONFLICT (user_id, idempotency_key) DO NOTHING
RETURNING id, status;
```

**Layer 2 — Engine lock:** Redis distributed lock on `order_id` prevents two workers from processing the same order simultaneously during crash recovery.

**Layer 3 — Exchange key:** Each submission uses `{order_id}_{exchange_id}_v{attempt}` as the vendor idempotency key. A retried submission does not create a second order on the exchange.

### Handling Traffic Spikes (1000x)

The queue is the shock absorber:
- API servers accept orders at full speed and enqueue them.
- Order Engine workers process at a controlled rate.
- If queue depth exceeds threshold → return HTTP 429 ("system busy") before accepting new orders. Fail fast rather than accept and lose.
- Auto-scale Order Engine workers based on queue depth.
- Rate limit outbound calls per exchange (token bucket) to avoid being blocked by the exchange.

### Price Routing Latency

Querying 3 exchanges per order in series = unacceptable. Two strategies:
1. Fan out quote requests in parallel (fan-in with timeout).
2. Better: stream live exchange order books into Redis via persistent WebSocket connections. Price Router reads from Redis — no per-order outbound latency.

---

## Key Trade-offs

| Decision | Choice | Why |
|---|---|---|
| Order placement | Async (return pending) vs. sync (wait for fill) | Async handles 1000x spikes without blocking connections |
| Exchange routing | Multi-exchange vs. single | Multi gives better prices; complexity is manageable with adapter pattern |
| Price source | Live quote per order vs. cached order book | Cached is faster; acceptable staleness if TTL is short (< 500ms) |
| Timeout recovery | Query before retry vs. blind retry | Query is mandatory — blind retry is financial risk |
| Reconciliation | Periodic job vs. event-driven only | Both: webhook for normal path, job as safety net for missed events |

---

## Staff+ Angle

- **The timeout problem is the interview.** Every candidate gets idempotency right eventually. What separates staff-level answers is deeply explaining the `timed_out → query → conditionally retry` flow and why skipping the query is a financial hazard. Draw this state machine transition explicitly.
- **Fund reservation.** `reserved_amount` at submission prevents a user from spending the same funds twice while an order is in flight. At resolution, either apply (fill) or release (failure). This is easy to forget and signals you've thought about financial correctness.
- **Reconciliation as a safety net.** Webhooks fail. Networks partition. A periodic reconciliation job that cross-checks internal state against exchange fill records is the last line of defense. Treat it as a required component, not an afterthought.
- **Coinbase-specific angle:** Coinbase Advanced Trade is itself one of the exchanges Coinbase broker routes to, alongside third-party venues. The adapter pattern handles this naturally, but the "best price" logic must account for Coinbase's own liquidity first (regulatory/competitive reasons). Worth mentioning.
- **Proactive to mention:** The price cache pattern. Asking every exchange for a fresh quote per order is O(N exchanges) outbound latency on the critical path. Streaming order books into Redis and reading from cache is the production pattern — it also decouples quote freshness from order volume.

---

## Interview Checklist

- [ ] Justified async ("return pending") before designing the state machine
- [ ] Drew the full state machine including `timed_out → query → conditional retry`
- [ ] Explained why you must query before retrying a timed-out order
- [ ] Defined Order, PriceQuote, Exchange, OrderEvent tables
- [ ] Included `idempotency_key`, `reserved_amount`, `exchange_order_id` on Order
- [ ] Described all three idempotency layers (client, engine, exchange)
- [ ] Explained queue as the traffic spike buffer + backpressure (HTTP 429)
- [ ] Described Price Router fan-out or Redis price cache
- [ ] Covered Timeout Monitor and Reconciliation Job as distinct components
- [ ] Addressed what happens when an exchange goes completely offline
