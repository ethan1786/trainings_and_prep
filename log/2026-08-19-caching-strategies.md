# Caching: layers, strategies, and when it's actually needed

**Date:** 2026-08-19
**Question that started it:** Every component can have a caching layer — CDN, Redis, in-memory, and the DB's own L1/L2. But I think the DB ones usually aren't enabled. Insights?

---

## The framing that fixed it

My mental model was a single spectrum of caches at different layers. The correction: **each layer caches a different thing and carries a different correctness risk.** The mistake is treating them as interchangeable.

The hierarchy, with what each actually buys:

| Layer | Scope | Benefit |
|---|---|---|
| CDN / HTTP | global/regional | avoids reaching the application at all |
| Local in-process | one pod | fastest possible lookup |
| Distributed (Redis/Valkey) | shared across pods | shared view + lower DB load |
| ORM L1 (persistence context) | one transaction | identity map within a unit of work |
| ORM L2 (second-level) | across sessions, if configured | entity reuse across requests |
| DB engine (buffer pool) | DB node | avoid disk reads |
| Query/plan cache | driver/DB | reduce execution overhead |

## The correction I most needed

I said DB caches "usually aren't enabled." Half right, and the half matters:

- **Engine caches are fundamental and always on.** Buffer pool, WiredTiger cache — these keep hot pages in memory. Disabling them would make the DB unusable.
- **What's deliberately disabled is the ORM second-level / query cache.** Confirmed in multiple service configs, set to `false`.

The reasons to avoid ORM-level shared caching are instructive: invalidation is hard, data may be updated outside the application, contents duplicate across pods, query-cache invalidation is broad and expensive, stale-data debugging is painful — and **the engine already caches pages and indexes**. ORM L1 is different: scoped to a session/transaction, useful for avoiding duplicate entity loads, not durable or globally shared.

## The three-tier example that justified itself

One service documents local in-process + distributed + event-synchronized in-memory maps. That looked redundant until the roles separated:
- local → microsecond reads, but per-pod copies
- distributed → shared view, but a network hop and an external dependency
- event-synchronized maps → fast local reads with **explicit** update propagation, at the cost of synchronization complexity

And the concrete counterexample to "distributed is always better": a cache whose payload exceeded ~500KB made distributed operations take *seconds* and exhausted the connection pool. The fix was moving it **local**, accepting one copy per pod and a cold miss after startup. **Object size is a first-class admission criterion.**

## When caching is actually needed (my question, refined)

My position: needed when organic traffic grows and the system can't meet its performance requirements; *not* needed early, even in production, because it adds a failure point and hurts debuggability.

That's right — with two refinements:

1. **Traffic is the amplifier, not the trigger.** The trigger is `repeat rate × source cost`. High traffic with a low repeat rate gains nothing but memory consumption. Caching a 2ms indexed lookup buys almost nothing while costing invalidation forever.
2. **The instinct applies only to *coherent* caches.** Caches of mutable data (entity caches) carry every cost I named. But **coherence-free** caches — content-hashed assets behind a CDN, the buffer pool, query-plan caches — cache immutable or content-addressed things, so there is *nothing to invalidate* and no staleness risk. Adopt those on day one.

The pre-launch question that matters most: **can the source survive 100% miss at peak?** A cache hides the inefficiency it papers over, which is why a cache outage is a **capacity** incident, not a latency one. Real evidence: a runbook treats a cache circuit-breaker opening as dangerous precisely because all requests then fall through, raising latency ~2–5× and risking pool saturation.

## Browser cache — who controls it (my question)

Control is **entirely server-side** via `Cache-Control`, `ETag`, and `Vary`; the browser enforces what you send. No per-browser handling is needed because this is settled HTTP, not a compatibility minefield — and the one case where browsers *do* guess differently is when you send **no** headers. So the rule that eliminates the risk: **always send explicit headers.**

What *does* belong in design is the **policy per response class**: content-hashed asset → `immutable, max-age=1yr`; personalized → `private, no-cache`; sensitive → `no-store`. Two failure modes to avoid: caching a personalized response publicly, and long-TTL-ing an un-hashed asset you can't purge. And one caveat — the user can always hard-refresh, so browser caching is **never** valid load-protection in capacity math.

## Read/write strategies — how much they matter (my question)

I asked whether these are design decisions or good-to-know. The answer: **name the read strategy as a one-line implementation note; it rarely changes the architecture.** Only two warrant a real design decision.

The mechanisms, with the details that carry correctness:

- **Cache-aside** — the default for durable business data. Two details do most of the work: **source first, cache second** (invalidating before commit lets a concurrent read repopulate the stale value for a full TTL), and **delete, don't update** (updating lets concurrent writers interleave so the cache keeps the older value indefinitely).
- **Write-through** — I had it as "strong consistency, higher latency." Wrong: cache and DB writes are **not atomic**. Cache-succeeds + DB-fails leaves the cache serving data the source never accepted — worse than stale, because it's *fabricated*. Prefer write-DB-then-invalidate.
- **Write-behind** — genuinely changes your **durability guarantees**, so it needs a durable log in the diagram. Redis alone is a data-loss design; Kafka-then-batch is the same idea done safely. Appropriate for counters and telemetry, not for orders or payments.
- **Write-around** — write DB, invalidate; good when writes are frequent but rarely reread.
- **Refresh-ahead** — the other real design decision, because it changes source load and your staleness contract.

## Invalidation approaches — what I was missing

My three (TTL, event-driven, versioned keys) were right but incomplete:

- **TTL should be a backstop, not the only mechanism** when freshness matters. The robust combination is event-driven invalidation **plus a long TTL safety net** — so a missed event eventually expires.
- **Event-driven needs a durable path.** Publishing from application code loses the event if the DB commit succeeds but publishing fails. A **transactional outbox** or CDC closes that gap. Events should carry a version/timestamp so consumers can ignore out-of-order arrivals.
- **Versioned keys need a pointer and garbage collection.** Immutable versions plus a current-version pointer; old versions still need lifecycle rules.

Additions that mattered:
- **Request coalescing** (`singleflight`) — 100 concurrent misses become 1 source request + 99 waiters. This is the stampede fix.
- **Negative caching** — cache "not found" briefly, with a short TTL since the object may be created later.
- **Stale-while-revalidate** — serve expired-but-recent while refreshing in background; needs a max stale age and refresh-failure monitoring.
- **Cache admission/eviction** — max object size, LRU/LFU, minimum access frequency before admission. A large rarely-reused object makes a cache *slower*.

## The validation checklist

Before adding any cache, define: source of truth, allowed staleness, read-after-write requirement, failure behavior (can it fall back?), invalidation guarantee, stampede protection, **key correctness** (tenant, locale, permissions, filters, version), size/eviction behavior, warmup behavior, observability (hit rate, stale serves, fallback load), rebuild path, and security (could one tenant read another's cached result?).

## The one-line principle

**A cache is not free performance. It is a second, potentially stale copy whose value must exceed the cost of maintaining, invalidating, warming, monitoring, and recovering it.**

---

## What changed in the reference

- `Caching` — rewritten as the decision-oriented template: escalation ladder, coherent vs coherence-free, browser-cache policy table, mechanism-first read/write strategies with verdicts, expanded invalidation, validation checklist
- `corrections.md` — five entries
- Became the template for the other eleven Part 1 patterns
