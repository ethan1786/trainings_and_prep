# MongoDB: where it fits, how it's chosen, how it's tuned

**Date:** 2026-08-18
**Hypothesis I brought in:** It's mostly a persistent caching store. Business data stays relational; Redis is a poor persistence cache and size-limited.

---

## What held up, and what didn't

The Redis half was right, and more strongly than I expected: guidance explicitly treats Redis data as **ephemeral** — fsync roughly once per second rather than per write, journals not necessarily backed up, no guaranteed restore. Anything durable goes elsewhere.

The relational-source-of-truth half was right too.

**"Persistent caching store" undersold it.** The accurate framing is three tiers, and the document store is genuinely durable in two of its three roles:

1. **Derived read store** — the cache-like role I was picturing. But the reason it's a document store rather than Redis is precisely **durability and fast recovery**, not speed.
2. **Primary datastore for document-shaped domains** — one domain was extracted from the monolith *because* its data (nested categories, scores, votes) was being forced into flat relational tables with complex joins. Millions of documents, cache in front, document store as system of record. Not a derived copy at all.
3. **Agent conversation memory and observability spans** — durable operational state.

So: relational = transactional truth; document store = durable denormalized/document domains; Redis/Valkey = ephemeral cache in front of both.

## The decision framework

Not left to taste. Roughly: relational for transactional/relational data and source of truth; document store when data is naturally document-shaped or schema flexibility matters; Redis only for ephemeral cache/session state; warehouse for analytics and never operational queries.

The live wrinkle: a recent ADR makes a *cheaper managed* document engine the default for new workloads, keeping the premium managed service as a justified exception — driven by cost, since a dedicated-tier floor per cluster is misaligned with many low-traffic non-prod clusters. "Document store by default" is being actively revised on cost grounds.

## The tuning material that mattered most

**Connection pooling.** The formula that made it click:

```
connections = pods × workers × clients × poolSize
```

19 pods × 3 workers × 2 clients × 5 min-pool = 570 idle connections, with ~985 observed per node including active. Fix was dropping the dev floor to 1. I confirmed my reading of each factor — workers are per-pod processes each with its own event loop, and each constructs two clients (storage + vector), each with an **independent** pool.

The architectural consequence matters more than the arithmetic: on a single-event-loop runtime, all requests on a worker share one pool, so a burst of write flushes can queue a read. On a thread-per-request runtime, a read lands on its own thread with its own connection. Same pool size, very different starvation behavior.

**Write pressure.** The biggest CPU contributor was a span collection writing 28–43KB documents — fix is stripping payloads before write. A deeper case study cut CPU from 92% to ~72% via TTL/retention, bulk writes instead of per-record saves, dropping unused indexes, and compound indexes.

**Indexing.** Index only proven hot queries; more than ~4 indexes on a collection signals a design problem. Prefer high-cardinality leading fields and compound/covered indexes for very frequent queries.

## The misconception I had to unlearn

I inferred: "frequent light operations are preferred, therefore bulk operations are discouraged — unlike relational batch reads/updates of 30–50 rows."

**Backwards, because it conflates two different things.** Multi-document *ACID transactions* are what the schema philosophy tells you to design around (embed related data so single-document atomicity suffices). **Bulk writes** are strongly *recommended* for volume — evidence on both sides: a per-record save loop (millions of ops/day) flagged as an anti-pattern with batched persist prescribed, and a migration replacing thousands of individual queries+writes with one unordered bulk upsert, calling per-record queries "the primary bottleneck."

So the relational batching habit translates directly and is encouraged. A bulk write is **one command carrying many independent atomic single-document ops** — not a long transaction.

---

## What changed in the reference

- `MongoDB / DynamoDB` tool entry — three usage patterns, pool formula, bulk-vs-transaction table
- `Caching` — the durable-vs-ephemeral tier distinction
- `Part 2.1` — the connection taxonomy (pool hold time vs stream hold time)
- `corrections.md` — bulk-vs-transaction, Redis-as-persistence, pool-per-request
