# Design Knowledge Base — Patterns + Deep Tools

A working reference. Each entry answers: what problem it solves, how it works, when it fits, when it doesn't — and where it shows up in practice at CarGurus.

Conventions used below:
- **In practice (CG):** a concrete internal example illustrating the generic pattern.
- **Correction:** a claim that is commonly stated but wrong or overstated, and the accurate version.

---

## Contents

Every pattern in Part 1 **and every tool in Part 3** carries a **"When you need it, and when you don't"** subsection — the escalation ladder of cheaper things to try first, the real triggers, the anti-cases, and what you permanently inherit by adopting it. That subsection is the decision content; the surrounding text is reference.

Parts 2.4 and 2.5 are the **diagnostic** counterparts: given a symptom rather than a requirement, how to find the cause (latency) or the ceiling (capacity).

- [Part 1: Pattern Recognition (with context)](#part-1-pattern-recognition-with-context)
  - [Caching](#caching)
    - [When you actually need one (and when you don't)](#when-you-actually-need-one-and-when-you-dont)
    - [Caching design principles — the compact mental model](#caching-design-principles--the-compact-mental-model)
    - [Design-time caching — estimating before metrics exist](#design-time-caching--estimating-before-metrics-exist)
    - [The layer map](#the-layer-map--each-layer-caches-a-different-thing)
    - [Who controls the browser cache](#who-controls-the-browser-cache--and-does-it-belong-in-a-design-doc)
    - [Read/write strategies](#readwrite-strategies)
      - [CarGurus pattern — eager local snapshots and Kafka fan-out](#cargurus-pattern--eager-local-snapshots-and-kafka-fan-out)
    - [Invalidation / freshness strategies](#invalidation--freshness-strategies)
  - [Message Queue / Async Processing](#message-queue-async-processing)
  - [Sharding / Partitioning](#sharding-partitioning)
  - [CQRS (Command Query Responsibility Segregation)](#cqrs-command-query-responsibility-segregation)
  - [Event Sourcing](#event-sourcing)
  - [Fan-out (Push vs Pull)](#fan-out-push-vs-pull)
  - [Saga Pattern (Distributed Transactions)](#saga-pattern-distributed-transactions)
  - [Circuit Breaker](#circuit-breaker)
  - [Rate Limiting and Load Shedding](#rate-limiting-and-load-shedding)
  - [Consistent Hashing](#consistent-hashing)
  - [Tiered Storage (Hot/Warm/Cold)](#tiered-storage-hotwarmcold)
  - [Lease-Based Execution and Leader Election (Exactly-One in Distributed Systems)](#lease-based-execution-and-leader-election-exactly-one-in-distributed-systems)
  - [Change Data Capture (CDC)](#change-data-capture-cdc)
- [Part 2: Deep Dives (mechanisms worth reasoning about)](#part-2-deep-dives-mechanisms-worth-reasoning-about)
  - [2.1 Streaming and Connection Models](#21-streaming-and-connection-models)
    - [Choosing a transport: the decision is direction and timing, not payload size](#choosing-a-transport-the-decision-is-direction-and-timing-not-payload-size)
    - [Why streaming at all — it's latency-to-first-byte, not size](#why-streaming-at-all-its-latency-to-first-byte-not-size)
    - [SSE wire format — the whole protocol](#sse-wire-format-the-whole-protocol)
    - [Why SSE over WebSocket for turn-based chat](#why-sse-over-websocket-for-turn-based-chat)
    - [Correction — connection capacity is not a protocol property](#correction-connection-capacity-is-not-a-protocol-property)
    - [High-frequency binary: why WebSocket, precisely](#high-frequency-binary-why-websocket-precisely)
    - [The three-way connection taxonomy (the thing that collides numerically)](#the-three-way-connection-taxonomy-the-thing-that-collides-numerically)
    - [Proxied streaming pipelines and layer placement](#proxied-streaming-pipelines-and-layer-placement)
  - [2.2 API Composition and Ownership](#22-api-composition-and-ownership)
    - [The three transports, and what each actually optimizes](#the-three-transports-and-what-each-actually-optimizes)
    - [Where GraphQL's performance actually comes from](#where-graphqls-performance-actually-comes-from)
    - [DataLoader: batching vs dedup, and where the real win is](#dataloader-batching-vs-dedup-and-where-the-real-win-is)
    - [Keeping the subgraph graph shallow, and @provides](#keeping-the-subgraph-graph-shallow-and-provides)
    - [The placement rule: whose logic, not logic-vs-data](#the-placement-rule-whose-logic-not-logic-vs-data)
    - [The threshold question: when is federation worth it at all?](#the-threshold-question-when-is-federation-worth-it-at-all)
  - [2.3 Derived-Store Materialization](#23-derived-store-materialization)
    - [The layered truth model](#the-layered-truth-model)
    - [Build-from-source vs dump-a-replica](#build-from-source-vs-dump-a-replica)
    - [Snapshot anatomy and cadence](#snapshot-anatomy-and-cadence)
    - [Correction — snapshots don't re-base the fleet](#correction-snapshots-dont-re-base-the-fleet)
    - [Recovery patterns](#recovery-patterns)
    - [Ingestion sources and the two-path pattern](#ingestion-sources-and-the-two-path-pattern)
    - [Correction — "the ingestor is one process" is a real limitation, not a design ideal](#correction-the-ingestor-is-one-process-is-a-real-limitation-not-a-design-ideal)
    - [Materialization vs stream processing](#materialization-vs-stream-processing)
  - [2.4 Latency Investigation — a decision tree for "it got slow"](#24-latency-investigation--a-decision-tree-for-it-got-slow)
    - [Step 0 — Define the symptom precisely](#step-0--define-the-symptom-precisely-before-touching-anything)
    - [Step 1 — Split the timeline into three buckets](#step-1--split-the-timeline-into-three-buckets-before-going-deeper)
    - [Step 2 — The layer walk, outside in](#step-2--the-layer-walk-outside-in)
    - [Step 3 — Classify the shape](#step-3--classify-the-shape-because-the-shape-determines-the-fix)
    - [Step 4 — Fix in cost order](#step-4--fix-in-cost-order-cheapest-and-most-permanent-first)
    - [The distributed-transaction variant](#the-distributed-transaction-variant)
    - [The anti-patterns that waste the most time](#the-anti-patterns-that-waste-the-most-time)
  - [2.5 Throughput and Capacity Planning — "will it hold at 10x?"](#25-throughput-and-capacity-planning--will-it-hold-at-10x)
    - [The two laws worth actually knowing](#the-two-laws-worth-actually-knowing)
    - [Step 1 — Find the binding constraint](#step-1--find-the-binding-constraint-not-the-busy-resource)
    - [Step 2 — Estimate before you test](#step-2--estimate-before-you-test-the-back-of-envelope-pass)
    - [Step 3 — Measure the ceiling deliberately](#step-3--measure-the-ceiling-deliberately)
    - [Step 4 — Choose the scaling lever](#step-4--choose-the-scaling-lever-the-constraint-actually-admits)
    - [The failure modes unique to high load](#the-failure-modes-unique-to-high-load)
    - [Answering "can it handle 10x?"](#answering-can-it-handle-10x--the-short-procedure)
- [Part 3: Deep Tool Knowledge](#part-3-deep-tool-knowledge)
  *Each entry carries a "When you need it, and when you don't" decision subsection.*
  - [PostgreSQL / MySQL (Relational)](#postgresql-mysql-relational) — the default; what would justify leaving
  - [Redis / Valkey](#redis-valkey) — shared state, not a fast database
  - [MongoDB / DynamoDB (Document / NoSQL)](#mongodb-dynamodb-document-nosql) — when aggregate and document boundaries coincide
  - [Kafka](#kafka) — log semantics vs. just moving work off the request path
  - [Elasticsearch / OpenSearch](#elasticsearch-opensearch) — relevance ranking, not filtering
  - [GraphQL Federation](#graphql-federation) — multiple schema owners is the real trigger
  - [gRPC](#grpc) — typed contract and binary framing are separable wants
  - [WebSocket and SSE](#websocket-and-sse) — direction and timing, not payload size
  - [S3 / Object Storage](#s3-object-storage) — where the blob/record boundary sits
  - [ZooKeeper / etcd / Consul (Coordination)](#zookeeper-etcd-consul-coordination) — idempotency beats consensus
  - [CDN (Content Delivery Network)](#cdn-content-delivery-network) — latency, offload, and protection are three products
  - [Flink / Stream Processing](#flink-stream-processing) — capability trigger vs. cost trigger
- [Part 4: Constraint → Solution Mapping (Quick Reference)](#part-4-constraint-solution-mapping-quick-reference)
- [Part 5: Tradeoff Pairs (One-Liners)](#part-5-tradeoff-pairs-one-liners)
- [Part 6: Recurring Meta-Principles](#part-6-recurring-meta-principles)
- [Part 7: Corrections Index](#part-7-corrections-index)

---


## Part 1: Pattern Recognition (with context)

---

### Caching

**Problem it solves:** Reads are too frequent or too expensive for the source to handle on every request.

**How it works:**
- Store computed/fetched results in a faster layer (memory)
- On read: check cache first → if hit, return immediately → if miss, fetch from source, populate cache
- Invalidate or expire entries to avoid serving stale data

#### When you actually need one (and when you don't)

Default position: **no cache.** A cache is a response to a measured problem, not a design flourish. But "wait until traffic grows" is only half the rule — the sharper version splits caches into two classes, because they carry completely different costs.

**Class A — coherence-free caches. Effectively free, correct from day one.**
These cache something *immutable or content-addressed*, so there is no invalidation problem and no staleness risk:
- Content-hashed static assets behind a CDN (`app.4f2a1c.js`) — a new build produces a new key, so nothing ever goes stale.
- DB engine buffer pool / WiredTiger cache — built in, on by default, invisible.
- Prepared statements and query-plan caches.
- Immutable artifacts in object storage.

Adopt these immediately. They add no failure mode and no debugging surface, because there is nothing to invalidate.

**But invisible is not the same as harmless — Class A caches quietly corrupt your measurements.** You never touch them, so it is easy to forget they exist, and then they show up as phantom behaviour:
- "Why is this query faster the second time?" — the pages are now in the buffer pool. The query did not change; its working set got hot.
- A p99 that looks acceptable is actually **bimodal** — warm reads at 2 ms, cold reads at 200 ms. The aggregate hides it.
- You "fix" a slow query, redeploy, and it is fast — because your test rows are hot, not because the fix worked.
- Latency is terrible for minutes after a DB restart or failover and no code changed. That is a cold buffer pool refilling, not a bug.

The habit this generates: **decide deliberately whether you are measuring warm or cold, and label which.** Both are legitimate — warm reflects steady state, cold reflects post-deploy, post-failover, and first-touch of rare data — but an unlabelled latency number is not interpretable. If you benchmark by running something three times and taking the best, you have measured the cache, not the query.

**Class B — coherent caches. Must be justified.**
These cache *mutable* data, so they introduce a second copy that can disagree with the source: Redis/Valkey entity caches, local entity caches, HTTP caching of dynamic responses. Every one adds staleness, an invalidation obligation, a key-correctness risk, a stampede risk, a cold-start risk, and one more dependency in the failure path. This is the class the "don't add it early" instinct is right about.

**The trigger is not "traffic grew." It is `repeat rate × source cost`.**
Traffic growth is the *amplifier*, not the reason. What makes a cache pay off:
- **Repeat rate** — is the same key read many times before it changes? If every read is a unique key, a cache only consumes memory.
- **Source cost** — is the read genuinely expensive (multi-join, fan-out across services, LLM/compute, cross-region) or a cheap indexed point lookup? Caching a 2 ms primary-key lookup buys almost nothing and costs you invalidation forever.
- **Scarce shared resource** — sometimes the point isn't latency at all, it's *protecting the source* (a shared DB primary, a rate-limited third-party API, a single-writer service).
- **Latency budget** — is the source's p99 blowing a user-facing SLO that can't be fixed at the source?
- **Fan-out amplification** — one page assembling N entity fetches where few unique entities are read many times (the high fan-in case).

High repeat rate + expensive source is the green light. Low repeat rate or a cheap source means a cache is pure downside *regardless of traffic volume*.

**Try these before caching — usually cheaper and permanent:**
1. Fix the query / add the missing index. Most "we need a cache" problems are a missing index or a full scan.
2. Kill the N+1 — batch and dedup instead (one call for 8 unique ids beats 50 cached lookups you shouldn't be making).
3. Shrink the payload — stop fetching fields nobody renders.
4. Add a read replica, or scale the source.
5. Precompute / materialize the read shape if the read pattern is fundamentally different from the write shape (Part 2.3 — that is a materialized view, not a cache).

A cache is the right answer when the work is genuinely repeated and genuinely expensive *after* the source itself is efficient.

**The subtle cost most people miss:** a cache doesn't just risk staleness — it *hides* the underlying inefficiency. The slow query is still slow; you stopped noticing. Traffic keeps growing behind a 95% hit rate, and the day the cache is cold, flushed, or unavailable, the source sees 20x its normal load and falls over. That is why **"can the source survive 100% miss at peak?"** is the single most important pre-launch question, and why a cache outage is a *capacity* incident, not a latency incident.

#### How to actually measure `repeat rate × source cost`

The rule is only useful if you can evaluate it. Sometimes you know the data shape by inspection — configuration and reference data are obviously read repeatedly and change rarely; a per-user activity feed obviously is not. But often you genuinely do not know, and the answer is **you do not need to know, you need to measure cheaply.**

**Repeat rate is computable from logs, with nothing deployed.** This is the step most people skip, and it is nearly free:

1. Log the cache key you *would* use — the full key, including every dimension that changes the response (entity id, tenant, locale, permissions, filters).
2. Over a window equal to your candidate TTL, count total requests and distinct keys.
3. `projected hit rate ≈ 1 − (distinct keys / total requests)`

If 10,000 requests resolve to 9,500 distinct keys, the projected hit rate is 5% and the answer is "do not build it" — discovered for the cost of one log line. If they resolve to 400 distinct keys, you have a 96% hit rate waiting for you. Either way you have a number instead of an intuition, and you never shipped a cache to find out.

**Source cost is a tracing question, and it answers a different question than repeat rate.** These two measurements get conflated constantly:

| Measurement | Question it answers | What it tells you |
|---|---|---|
| Distributed tracing / latency attribution | *Where does the time go?* | **Which** component to fix |
| Key access logging | *Is the work repeated?* | **Whether a cache** is the right fix for that component |

Attribution comes first. If the source call is only 8% of p99, caching it perfectly buys you 8% and you were looking at the wrong layer.

**The realistic investigation ladder** — the path this actually takes in practice:

1. **Symptom** — traffic grew, or "the API feels slow," or an SLO started breaching.
2. **Attribute** — trace the request and break p99 down by component. Find the dominant term. Beware the Class A trap here: know whether you are looking at warm or cold numbers.
3. **Confirm the shape** — is it one slow call, N+1 fan-out, queueing/saturation, or payload size? These have completely different fixes and only one of them is cache-shaped.
4. **Fix the source first** *(the gate people skip)* — missing index, full scan, N+1, over-fetching, no batching. If the source is inefficient, a cache does not solve the problem; it **hides** it, and you inherit invalidation forever to conceal a one-line fix.
5. **Then, and only then, measure repeat rate** on the now-efficient-but-still-hot call.
6. **Decide** — high repeat + expensive source → cache. Low repeat → the cache is pure downside; go back to step 4 or scale the source.

So your instinct is right, with one reordering: the investigation *starts* from the symptom and *goes through* attribution, but the "should this be a cache" question is answered by repeat rate at the end — not assumed at the beginning.

The general form of steps 1–4 — how to attribute latency across edge, gateway, app, and data store when many layers and services are involved — is Part 2.4. This ladder is the caching-specific slice of it.

**If repeat rate comes back too low, that is not necessarily a dead end — try re-shaping the key.** Low repeat rate is usually a **key cardinality** problem, and every dimension in the key multiplies cardinality while dividing repeat rate. A whole-page response keyed by `listingId + userId + zip` has almost no repeats. Split it:

- shared listing block → keyed by `listingId` alone → high repeat, cacheable
- personalized fragment → keyed by user → not cached

Same page, and now the expensive shared part is cacheable. This is the fan-in insight from the composition thread (Part 2.2) applied to caching: **the win comes from many requests mapping to few unique keys**, so cache at the granularity where that is true, not at the granularity of the response.

**Prove it before you build it (all four, or you're not ready):**
- Log key access and measure the actual **repeat rate** — you can compute the hit rate you would get without deploying anything.
- Attribute p99 latency to the source call; confirm it is the dominant term.
- Get the allowed staleness window agreed in writing.
- Confirm the source can serve 100% miss at peak, or design explicit shedding for that case.

**Design cache-ready, not cached.** The early-stage stance isn't "ignore caching" — it's keep the read path *cacheable* so one can be added later without a rewrite: stable and complete cache keys (tenant, locale, permissions, filters), idempotent reads, a single owner per entity, no side effects interleaved into reads. Cache-ability is a property of clean ownership boundaries; you get it for free when the boundaries are right.

#### Caching design principles — the compact mental model

Caching is usually an **invisible optimization layer**: it should not own core business truth or define the authoritative state of the system. Its job is to make an already-correct read path cheaper by avoiding duplicate retrievals, reducing pressure on scarce resources, and improving latency. That is the default posture, not a promise that caching is irrelevant: stale data, incorrect keys, cache leakage, stampedes, or a cache outage can change observable behaviour and can turn a performance mechanism into a correctness or availability concern.

The principles to carry into a design review are:

1. **Start without a Class B cache.** Feature delivery and core correctness normally come first; speculative caching is rarely worth its permanent operational cost. Add it when a measured latency, resource, cost, or availability problem justifies the complexity—not merely because traffic exists.
2. **Treat performance pain as the investigation trigger, not as proof that caching is the answer.** Start from the symptom, attribute the latency, fix source inefficiency, then measure repeat rate × source cost. The evidence chooses the mechanism.
3. **Keep the source authoritative and survivable.** A cache miss, cold start, flush, or cache outage must have a defined fallback. Before launch, ask whether the source can survive 100% misses at peak; otherwise the cache is hiding an unpriced capacity risk.
4. **Assume every mutable cache is a second copy with obligations.** You inherit a freshness contract, invalidation or expiry, key correctness, stampede protection, warmup behavior, eviction policy, observability, and a degraded-mode story.
5. **Cache at the granularity where requests converge.** Shared, expensive fragments often have high fan-in; personalized or highly unique fragments do not. Split the response rather than accepting a high-cardinality whole-response key.
6. **Make the cache removable.** Keep reads idempotent, ownership clear, keys complete, and the source path correct without the cache. A cache should improve the system, not become the only reason the system works.

So the practical summary is: **caching is a useful invisible layer, but invisibility is earned by keeping it out of the source of truth and making its failure harmless.** It is normally prioritized after features unless a concrete performance, capacity, cost, correctness, security, or availability risk makes it worth doing sooner.

#### Design-time caching — estimating before metrics exist

Sometimes a cache belongs in the initial design even though there is no production traffic or measured hit rate yet. That is a legitimate **scope and delivery-planning question**, especially when a Product Manager needs to understand whether the work fits the organizational plan. It is not evidence that the cache will definitely pay off in production. Engineering should answer with assumptions, scenarios, and confidence—not with a made-up hit rate.

Separate these four decisions:

1. **Should the read path be cache-ready?** Usually yes: define a stable cache-key boundary, keep the source path correct, expose latency and source-load metrics, and make the optimization insertable without rewriting the feature.
2. **Should the cache appear in the target architecture?** Include it when the anticipated request/data shape makes it a plausible baseline component, or when omitting it would make the delivery estimate misleading. Label it as an assumption or planned optimization if it is not yet validated.
3. **Must the cache be implemented before launch?** Require that only when a known peak-load, source-capacity, cost, rate-limit, latency, or availability constraint makes the uncached design unacceptable.
4. **What will validate the assumption?** Name the traffic test, shadow measurement, load test, or early-production metric that will confirm or reject the cache after launch.

**Estimate the shape with scenarios, not a single guess.** For each low/base/high scenario, write down:

| Input | What to estimate | Why it matters |
|---|---|---|
| Peak request rate and concurrency | Requests per second, burst size, and duration | Determines cache operations and source miss load |
| Key reuse | Requests per key during the candidate TTL; active distinct keys | Determines projected hit rate and memory cardinality |
| Source cost | Query/service latency, CPU/IO, fan-out, rate limit, or per-call price | Determines the value of each avoided miss |
| Value size | Average and p95 serialized response size | Determines memory, network, and serialization cost |
| Freshness and writes | Allowed staleness, write rate, read-after-write needs | Determines TTL, invalidation, and consistency work |
| Request granularity | Shared versus personalized fields; fan-in across callers | Determines whether the whole response or only fragments are cacheable |

With a candidate TTL window, the first-order estimates are:

* `projected hit rate ≈ 1 − (distinct keys / total requests)`
* `source request rate after warmup ≈ total request rate × (1 − hit rate)`
* `cache memory ≈ active keys × average value size × serialization/entry overhead × headroom`
* `invalidation rate ≈ source write rate` for keys that must be actively invalidated

These are planning estimates, not guarantees. Use ranges because reuse may be seasonal, bursts may not warm the cache, values may vary substantially in size, and the access distribution may be skewed. The candidate TTL must be long enough to represent the intended freshness policy; otherwise the projected hit rate is not measuring the system you plan to build.

**Estimate engineering effort as a set of obligations, not just a cache client call.** The scope normally includes the key and ownership model, cache deployment or provisioning, serialization, TTL and invalidation, stampede protection, cold-start and warmup behavior, eviction limits, metrics and alerts, fallback behavior, security review, load testing, rollout controls, and an owner for incidents. Local L1 caching usually has less infrastructure but more per-pod duplication and inconsistent warmup; shared L2 caching adds a dependency, network hops, capacity planning, and failure handling. Stronger freshness requirements can cost more than the cache itself.

A useful planning output has three layers:

* **Guaranteed scope:** the source-backed feature and the observability needed to measure it.
* **Conditional scope:** the cache implementation, with an estimate based on the stated traffic, reuse, value-size, and freshness scenarios.
* **Decision gate:** the metric or test that promotes the conditional cache to required work—or removes it from the launch plan.

This lets engineering give Product a useful delivery estimate without turning an unverified optimization into an architectural dependency. The right sentence is not “we know we need a cache”; it is “we will keep the path cache-ready, estimate the cache under these scenarios, and implement it before launch if the stated capacity or latency constraint is real.” A cache box in a diagram with no key model, freshness contract, miss behavior, capacity estimate, or validation gate is not a design; it is only scope inflation.

#### The layer map — each layer caches a different thing

| Layer | Typical cache | Scope | Main benefit |
|---|---|---|---|
| Client | Browser cache | One user | Eliminates the request entirely |
| Edge | CDN / HTTP cache | Global/regional | Never reaches the application |
| Service L1 | Caffeine, in-memory map | One process/pod | Fastest lookup, no serde |
| Service L2 | Redis / Valkey | Shared across pods | Shared view, lower source load |
| ORM L1 | Hibernate persistence context | One session/transaction | Identity map within a unit of work |
| ORM L2 | Hibernate second-level cache | Across sessions/pods (if enabled) | Entity reuse across requests |
| DB engine | InnoDB buffer pool, WiredTiger cache | DB node | Avoids disk reads |
| Plan/query | Prepared statements, query plans | Driver/DB/search node | Avoids re-parsing/re-planning |

**Correction — "DB caches are usually not enabled" is two claims, and only one is true.**
Database **engine** caches (InnoDB buffer pool, WiredTiger cache) are fundamental and always on; disabling them would make the DB unusable. What teams commonly disable is the **ORM second-level / query cache**, because invalidation is hard, data can change outside the app, contents duplicate per pod, and the engine already caches pages and indexes.
**In practice (CG):** Several Spring services (Service Provider V2 and multiple cg-main services) explicitly set Hibernate second-level cache and query cache to `false`. Hibernate L1 (session-scoped) is different and useful — it prevents duplicate entity loads inside one transaction.

#### Who controls the browser cache — and does it belong in a design doc?

Short answer: **the server controls it, the browser obeys it, and yes it belongs in the design — but as a small, well-understood set of decisions, not as per-browser handling.**

**Control is server-side, via response headers.** The browser does not decide policy; it enforces what you send:

```text
Cache-Control: public, max-age=31536000, immutable   → cache hard, never revalidate
Cache-Control: public, max-age=60, s-maxage=300      → browser 60s, CDN 5min
Cache-Control: no-store                              → never write to disk/memory
Cache-Control: private, no-cache                     → may store, must revalidate first
ETag / Last-Modified                                 → enables conditional revalidation
Vary: Accept-Encoding, Accept-Language               → which request dims change the response
```

`Cache-Control` is the only mechanism you need in practice. `Expires` and `Pragma` are legacy fallbacks and can be ignored for modern targets.

**You should not design per-browser.** `Cache-Control`, `ETag`, and conditional requests (`If-None-Match` / `If-Modified-Since`) are universally and consistently implemented — this is settled HTTP, not a compatibility minefield like CSS or JS APIs. The cross-browser variability that does exist is in areas you should not be relying on for correctness anyway: heuristic caching when you send *no* headers, eviction timing under storage pressure, back/forward-cache behavior, and private-mode restrictions. The rule that removes all of that risk is simply: **always send explicit caching headers.** Absent headers is the only case where browser-specific guessing occurs.

Two genuine cross-client caveats worth knowing:
- **`no-store` vs `no-cache`** are frequently confused and behave differently. `no-cache` *may* store but must revalidate; `no-store` must not persist at all. For anything sensitive, use `no-store`, and add `private` so shared caches (CDN/proxy) never hold it.
- **The user always wins.** A user can hard-refresh, disable cache in devtools, or run a browser extension that strips headers. So browser caching is a **performance optimization you cannot rely on for correctness or for load protection** — never assume a client cache hit as part of your capacity math.

**What actually belongs in the design phase** is not browser handling but the *policy per response class*:

| Response class | Recommended policy | Why |
|---|---|---|
| Content-hashed static asset | `public, max-age=31536000, immutable` | Filename changes on rebuild; never needs invalidation |
| Un-hashed static file (`/logo.png`) | short `max-age` + `ETag` | Same URL can change; needs revalidation |
| Public, slowly-changing API read | short `max-age` + `s-maxage` + `ETag` | Cheap revalidation, CDN absorbs most load |
| Personalized / authenticated response | `private, no-cache` (or `no-store`) | Must never land in a shared cache |
| Sensitive data (PII, tokens, financial) | `no-store` | Must not persist on disk at all |
| Mutating request (POST/PUT/DELETE) | not cacheable | Method is non-idempotent |

**The two failure modes to design against:**
1. **Caching a personalized response publicly** — the classic leak: user A's page served to user B from a shared cache. Prevented by `private` on anything user-specific, and by making sure `Vary` covers every request dimension that changes the response.
2. **Caching an un-hashed asset too long** — you ship a fix and users hold the broken version for a year with no way to purge a browser cache. The fix is content-hashing rather than long TTLs on stable filenames.

**One-liner:** the server decides caching policy through headers and the browser complies, so design the *policy per response class* — not per browser — and always send explicit headers so no client is left guessing.

#### Read/write strategies

**What this section is actually deciding.** These are not six competing products — they are answers to two independent questions:

1. **On a read miss, who fetches the source?** Your code (cache-aside) or the cache library (read-through).
2. **On a write, what happens to the cached copy?** Update it, delete it, or write to it first and persist later.

For a generic request-scoped mutable cache, the answer is often fixed: **cache-aside for reads, delete-on-write for writes.** That is not a universal CG rule. Treat most of this table as "good to know so you can name what you're doing and reject the wrong variant in review" — with the eager local-snapshot pattern below as an important exception that changes the architecture.

##### Cache-aside (lazy loading) — the default, and what you should assume unless told otherwise

The application talks to both the cache and the source. The cache knows nothing about your database.

```text
READ:
  v = cache.get(key)
  if v != null:      return v                    # hit
  v = db.query(...)                              # miss
  cache.set(key, v, ttl=300)
  return v

WRITE:
  db.update(...)                                 # source first, always
  cache.delete(key)                              # delete, do NOT update
```

Two details carry all the weight:

- **Source first, cache second.** If you invalidate before the DB commits, a concurrent read can repopulate the cache from the *old* row and that stale value now survives for a full TTL.
- **Delete, don't update.** Deleting is idempotent and safe under concurrency. Updating means two concurrent writers can interleave (`W1 writes DB → W2 writes DB → W2 sets cache → W1 sets cache`) and the cache ends up holding W1's older value indefinitely. Deleting forces the next reader to re-read the truth. This one rule prevents most cache-consistency bugs.

Works identically for local (Caffeine) and distributed (Redis/Valkey) caches — the code shape doesn't change, only where the map lives.

**Why it's the default:** the source of truth is never bypassed, only cached data is ever lost on a cache failure, and it degrades gracefully (cache down → all misses → slower but correct).

##### CarGurus pattern — eager snapshot loading + DB-first update + Kafka fan-out

The pattern described in the CG systems is not ordinary lazy cache-aside. It is three separate choices:

**Read path: eager, full-snapshot local cache.** Each application instance loads the expected dataset into memory during startup, aiming for a 100% hit rate on the hot path. This is best named an **eagerly loaded local L1 cache** or a **read-only snapshot cache**. There is no request-time miss for data that was successfully included in the snapshot.

**Write path: DB-first explicit cache update.** The sequence is:

```text
write authoritative DB
  → update this instance’s local cache
  → publish Kafka cache-update event
  → peer instances update their local caches
```

The safest description is **DB-first cache update with asynchronous event-driven propagation**. It is not canonical write-through: in the strict definition, the application writes to the cache and the cache synchronously writes the database. It is not write-behind: Kafka is propagating the committed change, not serving as the durability buffer. It is also not pure cache-aside/delete-on-write, because the writer updates the cached value instead of only deleting it. “Cache-aside with explicit write update” is acceptable shorthand; the sequence above is better than relying on an overloaded label.

**Cluster path: broadcast update propagation.** Each pod owns a local copy. Kafka distributes the change so other pods converge. If the message contains the new value, this is **update replication**; if it contains only a key or version, it is **invalidation**, with each consumer reloading the value. Either way, cross-pod consistency is normally eventual: the writer’s pod updates first, and other pods become current after Kafka delivery and processing.

This is a common pattern for **read-mostly, bounded, latency-sensitive data** such as feature flags, configuration, reference data, and selected product metadata. It is much less suitable as the default for large, highly mutable, user-specific datasets, where eager startup loads and per-pod duplication become expensive and event lag is harder to tolerate.

**What this pattern buys:** local-memory read latency, predictable hot-path behavior, reduced source reads, and no cache miss on ordinary requests after warmup. **What it spends:** startup time, memory multiplied by pod count, rollout-time source load, Kafka dependency, eventual-consistency windows, and a correctness gap between the DB commit, local cache update, and event publication.

The last point is the key design question. DB write, local cache write, and Kafka publish are not automatically one atomic operation. If the process dies after the DB commits but before publishing, peer caches can remain stale. A transactional outbox, CDC, durable event log, replayable topic, or periodic full refresh can close or bound that gap. Events should be idempotent and carry a version or timestamp so duplicates and out-of-order delivery cannot move a cache backward. Deletions need explicit tombstones or invalidation events.

The startup contract also needs to be explicit:

* Does readiness wait until the snapshot is complete?
* What happens when the source is unavailable or the snapshot is partial?
* Does the service serve stale data, fail closed, or fall back to the source?
* Can a rolling deployment cause every new pod to reload the full dataset at once?
* How does a pod recover if it misses a Kafka event?

CG examples reflect these tradeoffs: [finance-transaction’s caching flow](https://code.cargurus.com/cargurus-eng/finance-transaction/blob/main/docs/flows/caching-strategy.md) describes pre-warmed local maps, Kafka-synchronized updates, and Redis-backed caches; [MVT client architecture](https://code.cargurus.com/cargurus-eng/mvt-client-node/blob/main/packages/@cargurus/mvt-client-node/docs/ARCHITECTURE.md) loads active test data into memory and uses Kafka plus a periodic scheduler for freshness; and [Service Provider V2](https://code.cargurus.com/cargurus-eng/service-provider-v2/blob/main/CLAUDE.md) gates readiness on cache warmup. A cache publisher in [cg-main](https://code.cargurus.com/cargurus-eng/cg-main/blob/master/cargurus-iterable-client/src/main/java/com/cargurus/iterable/domain/dao/IterableUserCacheUpdatePublisher.java) also illustrates the important after-commit publication shape.

**Teaching summary:** read strategy = eager snapshot; write strategy = DB-first update; cluster strategy = asynchronous Kafka fan-out. Call it a **pre-warmed, locally replicated cache with event-driven eventual coherence**, and then document the failure and recovery semantics instead of debating whether it fits one taxonomy label.

##### Read-through — same semantics, different ownership

The cache library owns the fetch. You register a loader once instead of writing the miss branch everywhere.

```java
// Caffeine — local, read-through
LoadingCache<Long, Listing> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(5))
    .build(id -> listingRepository.findById(id));   // the loader
```
```java
// Spring — declarative, works over local or Redis depending on CacheManager
@Cacheable(value = "listings", key = "#id")
public Listing getListing(Long id) { return repo.findById(id); }

@CacheEvict(value = "listings", key = "#listing.id")
public void update(Listing listing) { repo.save(listing); }
```

**Verdict:** read-through vs cache-aside is an *ergonomics* choice, not an architectural one — underneath, it is still "check, miss, load, populate." The real reasons to prefer it: the loader is defined once so no caller can forget to populate, and most implementations give you **per-key request coalescing for free** (concurrent misses on the same key trigger one load). That coalescing is worth more than the syntax tidiness.

##### Write-through — write cache and source together, synchronously

```text
WRITE: cache.set(key, v)  AND  db.update(v)      → both before returning
```

Attractive because the cache is always warm and read-after-write is immediate. The problem is that those are **two systems with no shared transaction**:

```text
cache.set succeeds  →  db.update fails  →  cache now serves data the DB never accepted
```

That's worse than stale — it's *fabricated*. And the phantom value has no natural expiry path if a writer retries against a different pod.

**Verdict: avoid for durable business data.** `write DB → delete cache` gives you nearly the same freshness with a strictly better failure mode. Write-through is defensible only where the cache *is* the front of a single storage system that manages both tiers together (some DB/cache-integrated products), not where you are hand-wiring Redis in front of MySQL.

##### Write-around — write the source, don't populate the cache

```text
WRITE: db.update(...)  →  cache.delete(key)      # never cache.set
```

Effectively what cache-aside already does. It's worth naming because it makes an explicit choice: **do not warm the cache on write**, because this data probably won't be read again soon. Prevents write-heavy, rarely-read data from evicting genuinely hot entries. Use it when writes greatly outnumber reads on the same keys (audit rows, event records, bulk imports).

##### Write-behind (write-back) — acknowledge from cache, persist asynchronously

```text
WRITE: cache.set(key, v)  →  return immediately
                          ↘  durable queue/log → batch flush → database
```

This is the one variant that is **architecturally significant**, because it inverts durability: the cache becomes the temporary source of truth. Enormous write-throughput win (collapse 10,000 counter increments into one DB update), but if the buffer is lost before flush, **the write is gone**.

The load-bearing rule: the intermediate buffer must be **durable**, which in practice means a log (Kafka) or a queue — *not* Redis alone, whose data is explicitly ephemeral (fsync ~1s, no restore path). "Write to Redis, flush later" is a data-loss design; "write to Kafka, consumer batches into the DB" is the same pattern done safely.

**Use for:** counters, view/impression tallies, telemetry, metrics, rate-limit buckets — anything where losing a few seconds of increments is acceptable.
**Never for:** payments, orders, leads, inventory, or any business fact a user is told was saved.

##### Refresh-ahead — refresh a hot entry before it expires

```java
Caffeine.newBuilder()
    .refreshAfterWrite(Duration.ofMinutes(1))    // async refresh at 1min
    .expireAfterWrite(Duration.ofMinutes(10))    // hard expiry at 10min
    .build(id -> repo.findById(id));
```

With plain TTL, the unlucky request that arrives at expiry pays the full source latency — and on a very hot key, thousands do at once. Refresh-ahead re-loads in the background while continuing to serve the current value, so users effectively never see a miss.

**Verdict:** the highest-value optimization in this list for a small number of very hot, slowly-changing keys (reference data, config, ontology, feature flags). Costs you slightly staler data and background load on the source even when nobody asked. Pair the two windows: refresh well before expiry, keep expiry as the correctness backstop.

##### The decision, compressed

| If this is true | Use | Why |
|---|---|---|
| Read-heavy durable business data | **Cache-aside + delete-on-write** | Source always authoritative, safest failure mode |
| Same, and you want it enforced consistently | **Read-through** (`@Cacheable` / `LoadingCache`) | Loader defined once, free coalescing |
| Writes ≫ reads on the same keys | **Write-around** | Don't pollute the cache with cold data |
| Extreme write volume, loss of seconds acceptable | **Write-behind over a durable log** | Batching collapses write amplification |
| A few very hot, slowly-changing keys | **Refresh-ahead** | Nobody ever pays the miss |
| You were about to synchronously write both | **Stop — use DB-then-delete** | Write-through can fabricate data the source rejected |

**How much should this influence a design?** Name the read strategy (cache-aside vs read-through) as a one-line implementation note — it rarely changes the architecture. Escalate to an explicit design decision only for **write-behind** (it changes your durability guarantees and needs a durable log in the diagram) and **refresh-ahead** (it changes load on the source and your staleness contract). Everything else is a code-review-level concern.

**In practice (CG):** the finance-transaction service's three tiers map onto exactly these — Caffeine as local read-through, ElastiCache Redis as shared cache-aside, and Kafka-synchronized in-memory maps as the durable-log variant of write-behind-style propagation. The 500 KB payload moved from Redis to Caffeine because serialization cost dominated the shared-view benefit.

#### Invalidation / freshness strategies

| Strategy | Best fit | Main risk |
|---|---|---|
| **TTL** | Bounded staleness, simplest | Stale until expiry |
| **Event-driven invalidation** | Fresh shared data | Missed, duplicated, delayed, out-of-order events |
| **Versioned keys** | Immutable artifacts, static assets | Old versions need GC/lifecycle |
| **ETag / conditional GET** | HTTP/CDN caches | Still costs a validation round-trip |
| **Manual purge** | Rare operational changes | Human process, doesn't scale |
| **Stale-while-revalidate** | Latency/availability priority | Deliberately serves stale for a bounded window |

**TTL should be a backstop, not the only correctness mechanism.** The robust combination is `event-driven invalidation + long TTL safety net` — if an invalidation is missed, the entry still eventually expires.

**Event-driven invalidation needs an outbox, not a fire-and-forget publish:**
```text
DB transaction → durable outbox event → invalidation consumer → evict/refresh
```
Publishing from app code after commit loses the event if the publish fails. Events should carry a version or timestamp so consumers can discard out-of-order invalidations.

**Versioned keys** replace overwriting with immutability plus a pointer:
```text
listing:123      → v42     (pointer)
listing:123:v41  → payload (old)
listing:123:v42  → payload (current)
```
Ideal for object-storage artifacts, search indices, config bundles, and content-hashed assets. Does not remove the need for cleanup.

#### Additions worth knowing

- **Request coalescing (singleflight):** on a miss storm, one request fetches and the rest wait — `100 concurrent misses → 1 source call + 99 waiters`. The primary defense against cache stampede.
- **Negative caching:** cache "not found" briefly (short TTL) so invalid IDs don't hammer the source.
- **Cache warming:** preload hot/reference data before taking traffic; rate-limit it or you create a startup thundering herd.
- **Two-level caching:** `L1 local → L2 shared → source`. L1 is fastest but per-pod; L2 is shared but adds a hop. Invalidation and memory duplication get harder.
- **Admission and eviction policy:** max object size, max entries, LRU/LFU, minimum access frequency before admission. A large, rarely-reused object makes a cache *slower*.

#### Dangers

- **Cache stampede:** hot key expires, concurrent misses hit the source. Fix: coalescing, early refresh, TTL jitter.
- **Cold-start spike:** deploy or cache flush sends all traffic to the source.
- **Cache outage → fallback load:** the failure mode people forget.
  **In practice (CG):** the Dealer Reviews runbook treats the cache circuit breaker opening as dangerous precisely because all requests then fall through to MongoDB — roughly 2–5× latency and potential Mongo pool saturation.
- **Oversized entries in a shared cache:** a CG finance-transaction cache was moved from Redis to Caffeine because the payload exceeded ~500 KB and Redis operations took ~10s, causing connection-pool exhaustion. The accepted tradeoff was one copy per pod plus a DB hit on first request after startup. "Distributed cache is always better" is false.
- **Key correctness bugs:** a key missing tenant/user/locale/permission/filter dimensions leaks one user's result to another.

**In practice (CG) — the three-tier pattern:** the finance-transaction service documents Caffeine (local, microsecond), ElastiCache Redis (shared, cache-aside), and Kafka-synchronized in-memory maps (fast local reads with explicit propagation). Not redundant — three different problems.

**In practice (CG) — cache is not persistence:** internal guidance treats Redis data as **ephemeral** (fsync ~1s, no journal backup, no restore process). Anything durable goes to MySQL/Mongo. Dealer Reviews follows the canonical shape: ElastiCache-Valkey cache, MongoDB durable store, circuit breaker falling back to Mongo.

#### Where caching applies, by data class

| Data class | Approach |
|---|---|
| Public static assets | Content-hashed/versioned keys, long CDN TTL, immutable, lifecycle cleanup |
| Durable transactional data | Cache-aside, DB is truth, event invalidation after commit, TTL backstop, coalescing |
| Stable reference data | Local + optional shared cache, refresh-ahead, longer TTL |
| Derived/search data | Versioned snapshots/indices, incremental events, rebuild-from-source recovery, alias switch (this is a materialized view, not just a cache) |
| Telemetry / counters | Write-behind, batching, durable log, eventual persistence |
| Personalized / volatile | Short TTL or no cache; keys must include every dimension |

#### Correction — where "free" caching actually lives

- Free HTTP/CDN caching exists **only at the client edge**, keyed on a cacheable `GET`. Internal east-west (service→service) hops have **no edge**, so switching an internal call from one routing path to another never "recovers free caching."
- A GraphQL client edge forfeits it too: everything is `POST /graphql`, which HTTP caches can't key on.
- **Caching and call-routing are orthogonal axes.** If a hot, static, high-repeat entity needs caching, cache it **at/in front of the owning service** — then you keep batching/dedup/fail-open/observability *and* get cross-request caching.
- SSR relocates the client edge: with a server-rendered front end, the cacheable boundary becomes browser↔SSR-server, and whether free caching survives is a **config** question (loader/document cache headers + CDN), not a paradigm limitation.

#### Validation checklist before adding any cache

1. Source of truth — which system is authoritative?
2. Allowed staleness — seconds, minutes, never?
3. Read-after-write — must the writer see its own write?
4. Failure behavior — can the request fall back to the source, and can the source take it?
5. Invalidation guarantee — what prevents missed invalidations?
6. Stampede protection — what happens when thousands miss at once?
7. Key correctness — tenant, locale, permissions, filters, version all in the key?
8. Size and eviction — what happens when it fills?
9. Warmup — does deploy create a source spike?
10. Observability — hit rate, miss latency, evictions, stale serves, refresh failures, fallback load.
11. Recovery — can it be rebuilt safely from the source?
12. Security — can one tenant read another's cached result?

**Fits when:** Read-heavy (10:1+), staleness tolerable, hot set is a small subset.
**Doesn't fit when:** Real-time consistency required (payments, inventory), writes ≈ reads, or the working set doesn't fit.

**One-liner:** A cache is not free performance — it is a second, potentially stale copy whose value must exceed the cost of maintaining, invalidating, warming, monitoring, and recovering it.

---

### Message Queue / Async Processing

**Problem it solves:** Decouple producer from consumer, absorb traffic spikes, handle work that doesn't need an immediate response.

**How it works:**
- Producer writes a message to a queue
- Consumer pulls messages and processes them independently
- Queue acts as a buffer between the two

**Two flavors:**
- **Work queue (SQS, RabbitMQ):** message consumed once, then deleted.
- **Event stream (Kafka):** messages retained with offsets. Multiple consumer groups read independently. Replay possible.

**Key patterns:**
- Fan-out: one event → multiple consumers (Kafka consumer groups)
- Dead letter queue: failed messages diverted for investigation
- Backpressure: monitor lag and scale consumers

**Fits when:** Bursty traffic, non-critical-path work, independent scaling/deployment.

**Doesn't fit when:** Sustained write volume permanently exceeds processing capacity, caller needs synchronous confirmation, or immediate consistency is required.

**Key insight:** Queues absorb SPIKES, not SUSTAINED overload. If producer rate permanently exceeds consumer rate, the queue grows forever.

##### When you need one, and when you don't

The trigger is not "we have a lot of traffic" — it is **the caller does not need the result to continue.** Ask what the caller does with the response. If it renders it, you need a synchronous call. If it discards it, you have found async work.

**Real triggers, in rough order of how often they're the actual reason:**
1. **The work is slow and the user shouldn't wait** — sending email, generating a PDF, re-indexing, calling a slow third party. Latency moves off the request path.
2. **Bursty arrival with a smoothable deadline** — traffic arrives at 10x mean for 30 seconds but the work can complete over 5 minutes. The queue is a shock absorber.
3. **Failure must survive a restart** — if a deploy or crash mid-request would lose the work, a durable queue gives you retry and a DLQ. This is a *durability* argument, and it's often the strongest one.
4. **One event, many independent consumers** — you don't want the producer to know who cares (fan-out). Adding a fifth consumer shouldn't require touching the producer.
5. **You must protect a fragile or rate-limited downstream** — the queue lets you drain at a controlled rate instead of hammering it.
6. **Producer and consumer must scale or deploy independently** — different resource profiles, different release cadence.

**Don't reach for it when:**
- **The caller needs the answer now.** Async + polling for a result you could have returned synchronously is strictly worse.
- **Ordering across the whole dataset matters** and you can't partition by entity. You'll fight the queue forever.
- **Sustained load exceeds capacity.** A queue in front of an under-provisioned consumer just relocates the outage and adds unbounded lag. Fix capacity.
- **The work is trivially fast** (a few ms). Queue round-trip and operational surface exceed the work.
- **You need a transaction across produce-and-process.** Publishing is not part of your DB transaction (this is exactly what the outbox pattern exists to fix).
- **Debuggability matters more than throughput and volume is low.** Async turns one stack trace into a distributed trace.

**Cheaper alternatives to try first:** a background thread or scheduled job (fine if losing in-flight work on restart is acceptable), a database-backed job table with a poller (durable, transactional with your write, no new infra — genuinely sufficient at low volume), or simply making the synchronous path faster.

**The three questions that decide the shape:**
- *Does the caller need the result?* → No: queue. Yes: synchronous.
- *Consumed once, or by many?* → Once: work queue (SQS/Rabbit). Many, or needs replay: log (Kafka).
- *Is losing a message acceptable?* → No: durable log + DLQ + idempotent consumers.

**Non-negotiable once you adopt it:** consumers must be **idempotent** (at-least-once delivery means duplicates *will* happen), you must have a **DLQ** with someone actually watching it, and you must **alert on lag, not just errors** — a silently growing backlog is the characteristic failure and it does not raise error rates.

**In practice (CG):** most "stream processing" is plain Kafka consumers reacting per-event — LDS Writer, LSDI, SPDI, IMV, CGSP incremental ingestion. Change events say *what changed*; the consumer re-fetches truth. See Part 2.3 and the Flink entry for why that choice removes the need for a stream-processing framework.

---

### Sharding / Partitioning

**Problem it solves:** A single node can't handle write throughput, connection count, or data volume.

**Strategies:**
- **Hash-based:** `hash(key) % N` — even distribution, painful resharding
- **Range-based:** range queries work, hotspots if uneven
- **Consistent hashing:** minimizes redistribution when membership changes

**Choosing a key:** query pattern determines the key. Good key = even distribution + queries stay within one shard. Bad key = scatter-gather.

**Triggers:** write QPS beyond single-node capacity, data volume where indexes no longer fit in RAM, connection pool exhaustion.

#### Partitioning for ordering vs throughput (Kafka-shaped, but general)

- Order is guaranteed **within** a partition only, never across a topic.
- **Global order for the whole topic** → 1 partition (gives up parallelism).
- **Per-entity order + scale** → multiple partitions keyed by a stable entity id. This is the usual sweet spot.
- **Max throughput, order irrelevant** → default distribution.
- Keyed partitioning creates the **hot-key/skew** problem. Four remedies: accept the skew (ordering matters more), raise total partition count so the rest of the keyspace spreads, shard the hot key (`entityId#0..N`, relaxes strict per-entity order), or isolate the hot workload into its own topic/path.
- Key→partition mapping is stable only relative to the **current** partition count; increasing partitions re-maps future writes.

**Sizing rule:** `partitions ≈ maximum useful consumers`, with modest headroom — not "current pod count," and not "as many as possible."
- Fewer partitions than consumers → idle consumers.
- Far more partitions than needed → broker metadata, coordination, and metrics-cardinality overhead.
**In practice (CG):** internal guidance offers "partitions = consumers" as a conservative default; a 300-partition topic was flagged as over-provisioned and a contributor to Prometheus/metadata pain; and a lag incident was root-caused as a mismatch between 6 partitions and only 3 active consumer pods ([consumer-lead postmortem](https://cargurus.atlassian.net/wiki/spaces/DEV/pages/4342383057)). Separately, one team's request to add partitions was declined because the real bottleneck was a downstream REST API, not Kafka parallelism.

**Correction — "one consumer with two partitions processes them in parallel" is not guaranteed.** Kafka gives partition-level assignment; whether one consumer instance processes its partitions concurrently is a client/framework choice. Parallelism normally comes from **more consumer instances**.

##### When you need it, and when you don't

Sharding is the **most expensive and least reversible** scaling decision in this document, so the bar is correspondingly high. Once data is split, cross-shard joins, distributed transactions, and rebalancing become permanent facts of life.

**Escalate in this order — shard only when everything above is exhausted:**
1. **Fix queries and indexes.** A large fraction of "we need to shard" is one missing index or one full scan.
2. **Scale vertically.** Modern single nodes handle far more than people assume; an instance-size bump is hours of work versus months for sharding.
3. **Add read replicas.** If the problem is read throughput, this solves it entirely and sharding is the wrong tool.
4. **Cache the hot read path.** Removes repeat load from the primary.
5. **Archive or tier cold data.** If indexes no longer fit in RAM because 90% of rows are three years old, move them out. This buys years.
6. **Split by domain first (vertical/functional).** Move a table family into its own database — far simpler than horizontal sharding and often sufficient.
7. **Then shard horizontally.**

**Legitimate triggers (all are about a hard single-node ceiling):**
- **Write throughput** exceeds what one primary can accept — replicas don't help writes.
- **Working set no longer fits in memory**, so index lookups start hitting disk and p99 degrades non-linearly.
- **Data volume** makes operations infeasible — backups, restores, schema migrations, or index rebuilds that no longer fit a maintenance window.
- **Connection ceiling** on a single primary.
- **Blast radius / tenant isolation** — one large tenant must not be able to degrade others.
- **Data residency** — rows must physically live in a given region.

**Don't shard when:**
- Reads dominate (use replicas), or the real problem is a **hot key** rather than total volume (sharding doesn't fix skew — the hot key just lands on one shard).
- You **can't identify a shard key** that keeps the dominant queries inside one shard. No good key means scatter-gather on every query, which is usually *slower* than one well-indexed node.
- Your access patterns are still changing. The shard key is close to permanent; choosing it before the query patterns settle locks in the wrong one.
- The motivation is anticipatory ("we might get big") rather than a measured ceiling.

**Choosing the key — this is the whole decision.** A good key gives even distribution *and* keeps the dominant query within one shard. Those two goals conflict: a highly granular key (user id) distributes beautifully but scatters any query spanning users; a coarse key (region) keeps queries local but creates hotspots. Sharding on the wrong key is worse than not sharding — and the honest test is: *what fraction of my queries can be answered from a single shard?* Below roughly 90%, reconsider.

**Costs you inherit permanently:** no cross-shard joins, no cross-shard transactions (Saga territory), resharding is a migration project, per-shard hotspots, N times the operational surface, and a harder story for uniqueness constraints and aggregate queries.

**Fits when:** vertical scaling and read replicas are exhausted, and a clear access pattern exists.
**Doesn't fit when:** frequent cross-partition joins, small data, or a single node with replicas suffices.

---

### CQRS (Command Query Responsibility Segregation)

**Problem it solves:** Read and write patterns are fundamentally different — different shapes, frequencies, performance needs.

**How it works:** separate the write model (normalized, correctness-optimized) from the read model (denormalized, query-optimized); async events propagate changes.

**In practice (CG):** MySQL is the transactional write model for listings; LDS is a read-optimized denormalized document per listing in MongoDB, fed by a synchronizer and consumed via GraphQL. Explicitly read-only — MySQL remains the only place for listing writes.

##### When you need it, and when you don't

The trigger is a **shape mismatch, not a volume problem.** CQRS earns its cost when the way you must *write* data and the way you must *read* it are structurally incompatible — not merely when reads are frequent.

**Signals that you genuinely have a shape mismatch:**
- Your hottest read requires joining 6+ tables (or fanning out to 4+ services) to assemble one screen, and no index makes that cheap.
- Writes need strict normalization for correctness, while reads want a wide denormalized document.
- Reads need a fundamentally different engine — full-text search, geospatial, aggregation — that your transactional store does badly.
- Read and write scale independently by an order of magnitude.
- Many consumers need the same expensive composition, so each one re-deriving it is wasteful and divergent.

**Cheaper things that usually solve "reads are slow" without CQRS:** the right composite index; a materialized view or summary table inside the same database (this is 80% of CQRS's benefit for 5% of the cost, and it's often the correct stopping point); read replicas; a cache on the read path; or just a well-scoped denormalized column maintained in the same transaction.

**Don't adopt it when:**
- Read and write shapes are basically the same — you'd add a pipeline for nothing.
- **Read-after-write consistency is required.** This is the decisive one: CQRS makes the read model eventually consistent, so a user can save and not see their change. If that's unacceptable and you can't special-case it, CQRS is wrong.
- The system is small or early — you're paying pipeline complexity to solve a problem an index would fix.
- Nobody owns the sync pipeline. An unmonitored read model drifts silently, and drift in a read model is very hard to detect from the outside.

**What you actually sign up for:** a replication pipeline (and its lag), a second store to operate and pay for, monitoring for divergence, a rebuild path for when the read model is wrong, and an explicit product decision about the staleness window. Write that staleness number down and get it agreed — "the read model is a few seconds behind" is a product contract, not an implementation detail.

**Note the relationship to materialization (Part 2.3):** a read model *is* a materialized view. Once you accept a read model, you also inherit its recovery question — can you rebuild it from the source of truth, and how long does that take? If the answer is "we don't know," you have a latent outage.

**Fits when:** reads need denormalized views, writes need strict normalization, read:write ratio is high.
**Doesn't fit when:** read and write shapes are the same, the system is small, or stale reads are unacceptable.

**Tradeoff:** eventual consistency between models. Decide explicitly whether "user sees slightly stale data" is acceptable.

---

### Event Sourcing

**Problem it solves:** Complete audit trail, replay/reconstruct state, temporal queries.

**How it works:** store every state change as an immutable event; current state = replay from the beginning or a snapshot; never mutate or delete events.

**Benefits:** full audit trail, rebuild state at any point in time, replay with new logic, natural fit for event-driven architectures.

**Costs:** snapshots needed for performance, event schema evolution is hard, eventually consistent reads.

**Depth-of-lock-in note:** event sourcing is the deepest commitment in this document, because the **source of truth becomes the append-only log** — state is *derived* by replay. Backing out means reconstructing what "correct" means. Compare: CQRS reshapes the data model; a transport/contract choice like gRPC only reshapes service edges and is reversible per-edge. Weight adoption bars accordingly.

##### When you need it, and when you don't

Highest bar in this document. The question to ask is not "would an audit trail be nice" — it is **"is the sequence of changes itself a business requirement?"** If the history is genuinely part of the domain (ledgers, regulated records, disputes about how a value came to be), event sourcing is the honest model. If you just want to know who changed what, you want an audit log, not event sourcing.

**Genuine triggers:**
- Regulatory or financial requirement that history be immutable and complete (accounting ledgers, trades, claims).
- The business *asks temporal questions* — "what did this look like on March 3?", "why is this value what it is?"
- You need to replay history through *new* logic (recompute a metric, fix a bug retroactively, backfill a derived model).
- Undo/redo or compensation is a first-class domain concept.

**Cheaper things that cover most of the demand:** an append-only audit table written in the same transaction; temporal/versioned rows (`valid_from`/`valid_to`); DB change data capture into a warehouse for history; or a soft-delete plus revision column. These give you "who changed what, when" without making the log your source of truth.

**Don't adopt it when:**
- It's CRUD with an audit *nice-to-have*.
- The team hasn't done it before and there's no strong domain pull. The failure mode isn't "it's slow," it's "nobody can evolve the event schema safely two years in."
- You need straightforward ad-hoc querying of current state. Current state is derived, so every read either replays or depends on a projection you must build and maintain.
- Requirements are still moving. Event schemas are effectively permanent — old events must remain interpretable forever, so you're versioning and up-casting them for the life of the system.

**What you inherit permanently:** snapshotting for read performance, event schema versioning and up-casting, projections to build and rebuild, eventual consistency on every read, GDPR/deletion tension with an immutable log (crypto-shredding or tombstoning), and the fact that **you cannot go back** — "revert to storing current state" means reconstructing what correct means.

**The scoping move that makes it tractable:** apply it to *one aggregate* where history genuinely matters (the ledger, the order lifecycle) and use ordinary CRUD everywhere else. Event-sourcing the whole system because one part needs it is the classic overreach.

**Fits when:** financial/compliance domains, "how did we get here" matters, undo/replay needed.
**Doesn't fit when:** simple CRUD, no audit requirement, state is simple and rarely disputed.

---

### Fan-out (Push vs Pull)

| Approach | How | Pro | Con |
|---|---|---|---|
| **Push (fan-out on write)** | Write to all recipients' feeds on event | Fast reads (pre-built) | Expensive for high-follower accounts, wasted on inactive users |
| **Pull (fan-out on read)** | Query and merge sources at read time | No wasted writes | Slow reads, high read-time compute |
| **Hybrid** | Push for normal, pull for celebrities | Best of both | Implementation complexity |

**The celebrity problem:** 10M followers → 10M writes per post. Don't push for celebrities; merge at read time.

##### When you need it, and which variant

You only face this decision when a read must **assemble content from many sources** and both sides of the relationship can be large. If the fan-out factor is small and bounded, read-time merging is trivially fine and there is no decision to make.

**Choose by measuring two distributions, not by preference:**
- **Fan-out factor (writers → readers):** how many feeds does one write touch? Bounded and small → push. Unbounded/heavy-tailed → you need a hybrid.
- **Read:write ratio:** reads ≫ writes favors precomputing on write; writes ≫ reads favors merging on read.
- **Reader activity:** if most recipients never read, pushing to all of them is wasted work — pull for inactive users.
- **Latency budget:** a strict read SLO pushes work to write time.

**Push (fan-out on write) when:** reads must be fast and predictable, fan-out is bounded, and most recipients are active.
**Pull (fan-out on read) when:** writes are frequent, most recipients are inactive, fan-out is unbounded, or the merge is cheap (few sources, indexed).
**Hybrid when:** the distribution has a heavy tail — which in practice is almost always, for anything social. Push for the ordinary case, pull for the outliers, and set the threshold from data rather than intuition.

**Don't build it when:** the fan-out is small (tens), the read merge is a single indexed query, or you haven't measured the distribution yet — pull is the simpler default and you can add push later for the hot cases.

**Key decision:** what is the follower distribution?

---

### Saga Pattern (Distributed Transactions)

**Problem it solves:** A business operation spans services/databases and needs atomicity (all succeed or all compensate).

**How it works:** a sequence of local transactions, each with a compensating action; on failure, compensate in reverse.

**Two coordination modes:**
- **Choreography:** services react to events. Decoupled, but overall progress is hard to track.
- **Orchestration:** a central coordinator directs steps. Easier to reason about, coordinator is a dependency.

**Alternatives:** 2PC (locks across phases, coordinator SPOF), TC/C (application-level, parallel, more complex).

**Related correction:** a **federated GraphQL mutation has no distributed transaction** — the router cannot give atomicity or rollback across subgraphs. That's a strong reason to keep writes on the owning service (REST or a service-local transaction) rather than composing writes in a graph.

##### When you need it, and when you don't

Sagas exist because you already lost the ability to use one transaction. So the first question is always: **can you avoid needing one?**

**Try these first, in order:**
1. **Put the data in one transaction boundary.** If two "services" always change together atomically, that's evidence your service boundary is drawn in the wrong place. Merging them is often the correct fix, not a compromise.
2. **Make the operation idempotent + retryable.** Many "distributed transactions" are really "do step B eventually, reliably" — an outbox event plus an idempotent consumer covers it without compensation logic.
3. **Relax the requirement.** Ask whether the business actually needs atomicity or just eventual convergence with reconciliation. Often a nightly reconciliation job plus alerting is dramatically cheaper and is what the business truly wants.
4. **Reorder the steps** so the irreversible action happens last. If the only non-compensatable step is at the end, you may not need a saga at all.

**Real triggers:** the operation genuinely spans separately-owned datastores, every step has a meaningful compensating action, the business can tolerate a visible intermediate state, and partial completion has real financial or trust consequences that reconciliation can't clean up later.

**Don't use a saga when:**
- A single database transaction is possible. Use it.
- **A step cannot be compensated** — email sent, payment captured to a third party, physical shipment dispatched. You can only *mitigate* (send a correction, issue a refund), which is a different business process. Design the ordering so these come last.
- The intermediate state is unacceptable to show a user, and you have no way to hide it.
- The flow has many steps and no owner. A 9-step saga with 9 compensations is 18 code paths, most of which will never be tested in anger.

**Choosing choreography vs orchestration:** few steps and loose coupling → choreography. More than about 3–4 steps, or you need to answer "where is order 123 stuck?" → orchestration, because you need a place where the state machine visibly lives. The most common regret is choosing choreography for a long flow and then being unable to observe it.

**Non-negotiables:** every step and every compensation must be **idempotent** (they will be retried); you need **persisted saga state** so a crash mid-flow can resume; you need a **timeout and a stuck-saga alert**; and you need an operational answer for a compensation that itself fails, which usually means a manual intervention queue.

**Fits when:** services can't share a database, operations are compensatable, eventual consistency is acceptable.
**Doesn't fit when:** a single DB transaction is possible, compensation is impossible (sent email), or real-time consistency is required.

---

### Circuit Breaker

**Problem it solves:** A failing dependency causes cascading failure — requests pile up on timeouts, pools exhaust, the system degrades.

**Three states:** Closed (flowing, tracking failures) → Open (short-circuit immediately, return fallback) → Half-open (probe one request; success closes, failure reopens).

**Key parameters:** failure threshold, cooldown, fallback.

**In practice (CG):** the federated router runs native circuit breakers globally and per-subgraph, with **fail-open timeouts** (3s default, 15s for the large-batch subgraph) that null just the affected field and return the rest. Retries are deliberately **disabled** to avoid retry storms; rate limiting is available but not enabled (client-side instead). Dealer Reviews puts a breaker in front of its cache and falls back to MongoDB.

**Design lesson from the fallback side:** always ask what the fallback path costs. A breaker that dumps cache traffic onto the primary datastore trades one outage for another.

##### When you need it, and when you don't

The precondition is often missed: a circuit breaker is only useful if **you have something better to do than wait.** If there is no fallback and no way to degrade, opening the breaker just converts a slow failure into a fast failure — sometimes worthwhile, often not.

**Order of adoption — the first two matter more than the breaker:**
1. **Timeouts.** A call with no timeout is the actual root cause of most cascades. This is non-negotiable and gives you most of the protection.
2. **Bounded concurrency / bulkheads.** Cap how many in-flight calls one dependency can consume so it cannot exhaust the shared pool or thread pool. Often this alone prevents the cascade.
3. **Circuit breaker.** Adds "stop trying for a while" on top of the above.
4. **Retries — last, and carefully.** Retries *amplify* an overload. Only with backoff, jitter, a strict budget, and idempotent operations.

**Real triggers:** the dependency is remote and can be slow or down; a meaningful fallback exists (cache, stale value, degraded response, null field); the call is on a shared resource path where pile-up harms unrelated traffic; and the dependency is optional to the response's core value.

**Don't add one when:**
- **The dependency is mandatory with no fallback** — you can't render the page without the listing. A timeout plus a clean error is the honest design; a breaker adds machinery without changing the outcome.
- Traffic is too low to produce a meaningful failure signal. Thresholds on small samples flap, and a flapping breaker is worse than none.
- It's an in-process call, or a fast local dependency.
- **You haven't thought through the fallback's capacity.** This is the trap: a breaker in front of a cache that falls back to the primary datastore can turn a cache blip into a database outage. Always compute the fallback load.

**Tuning that actually matters:** thresholds should be **rate-based over a minimum sample size** (not "5 consecutive failures"), the cooldown must exceed realistic recovery time, half-open must admit only a trickle, and **slow calls should count as failures** — a dependency answering in 30s is failing even if it eventually returns 200. Scope breakers **per dependency**, never one global breaker.

**Doesn't fit when:** the dependency is mandatory with no meaningful fallback.

---

### Rate Limiting and Load Shedding

**Problem it solves:** Protect a service from overload (DDoS, misbehaving clients, thundering herd) — and protect a **scarce downstream** from your own traffic.

**Algorithms:** token bucket (bursts, most common), sliding window counter (accurate, low memory), leaky bucket (smooth output).

**Implementation:** Redis + Lua for atomic check-and-increment; key = `rate:{identifier}:{window}`. Granularity: user, IP, API key, endpoint, global — often multi-tier.

**Admission control / load shedding is the sibling pattern:** when the constrained resource is *your own* capacity or a costly upstream, cap concurrency and reject early rather than queueing forever.
**In practice (CG):** the AI streaming server caps concurrent streams per worker and returns 503 past the limit, with client-side 503 handling. That cap protects LLM concurrency and per-stream memory — it is a deliberate throttle, **not** a protocol limit (see Part 2.1).

##### When you need it, and which kind

Two different problems wear the same name, and conflating them produces the wrong control:

- **Rate limiting** = *fairness and abuse control.* "No client may exceed N requests per minute." Keyed per caller. Answers "who is allowed how much."
- **Load shedding / admission control** = *self-preservation.* "I will not have more than N of these in flight, regardless of who is asking." Keyed on a resource. Answers "what can I actually survive."

You need rate limiting when you have **untrusted or unequal callers** — a public API, per-tenant quotas, a scraper problem, a costly endpoint. You need load shedding when there is a **hard scarce resource behind you** — a fixed concurrency budget, a connection pool, a rate-limited third party, a costly model or compute call.

**Reach for load shedding, not rate limiting, when the resource is scarce rather than the caller abusive.** A per-user rate limit does nothing to stop 200 well-behaved users from collectively exhausting a 50-slot pool.

**Don't add either when:** callers are internal and trusted, capacity comfortably exceeds realistic peak, autoscaling already absorbs the burst, and no single dependency is a hard ceiling. Premature limits cause self-inflicted incidents — the classic being a limit set from average load that trips on legitimate peak.

**What good behavior looks like:** reject **fast and early** rather than queueing (a queue in front of an overloaded resource just moves the failure and adds latency), return `429`/`503` with `Retry-After`, differentiate **shed** from **error** in your metrics so shedding doesn't page as a bug, prefer shedding low-value traffic first (background jobs before user-facing), and give clients backoff+jitter guidance so they don't synchronize their retries into a second wave.

**The observability trap that makes this hard:** a workload that holds resources while idle (long-lived streams, connections waiting on I/O) shows **flat CPU** while approaching exhaustion. CPU-based alerts and CPU-based autoscaling are blind to it — you must instrument the *held resource count* directly and scale/alert on that.

---

### Consistent Hashing

**Problem it solves:** Distribute data across nodes so adding/removing a node doesn't reshuffle everything.

**How it works:** hash nodes and keys onto a ring; a key maps to the first node clockwise; adding a node only affects keys between it and its predecessor; virtual nodes (100–200 per physical) even out distribution.

**Used in:** Cassandra, DynamoDB partitioning, CDN edge mapping, distributed caches.

##### When you need it, and when you don't

This is a **narrow, specialist** technique, not a general design choice. You need it only when you own the placement logic *and* membership changes while the system is live.

**Real triggers:** you are distributing data or connections across a node set that changes (scale up/down, node failure, rolling deploy) and a plain `hash(key) % N` would remap almost every key on each change; or you need session/cache affinity that survives membership churn; or you're building a distributed cache, sharded router, or gossip-based store yourself.

**Don't use it when:**
- **Your datastore already does it.** Cassandra, DynamoDB, and most managed caches handle placement internally. Reimplementing it above them is redundant.
- **Membership is static.** With a fixed node count, `hash % N` is simpler and fine.
- **A load balancer is enough.** For stateless services, round-robin or least-connections is better — consistent hashing pins traffic to nodes, which *hurts* when nodes are interchangeable.
- **The problem is a hot key, not rebalancing.** Consistent hashing distributes *keys* evenly; it does nothing for one key receiving disproportionate traffic. Remedies there are key replication, key sharding (`key#0..N`), or a local cache in front.

**The practical caveat:** without **virtual nodes** (100–200 per physical node) distribution is visibly uneven, and uneven placement is the most common implementation bug. If you find yourself writing ring code, use a proven library.

**Doesn't solve:** the hot **key** problem. That needs key replication, key sharding, or local caching.

---

### Tiered Storage (Hot/Warm/Cold)

**Problem it solves:** Data grows unbounded but most queries touch recent data.

**Tiers:** hot (memory/SSD) → warm (primary DB/cheaper SSD) → cold (object storage/archive), with lifecycle policies moving data by age or access.

##### When you need it, and when you don't

The trigger is **temporal locality plus a retention obligation** — you must keep data for years but queries overwhelmingly touch the last days or weeks. If either half is missing, tiering is unnecessary complexity.

**Real triggers:** storage cost has become a visible line item; the working set no longer fits in memory *because* of old data (tiering can defer sharding entirely — worth trying first, it's far cheaper); backups, restores, or migrations no longer fit a maintenance window; compliance requires multi-year retention that operational storage shouldn't carry.

**Don't tier when:**
- Queries hit old data as often as new — there is no cold tier, only a slower one.
- Total volume is small. Complexity for no saving.
- **Retrieval latency on the cold tier is unacceptable to any real query path.** Deep-archive restores can take hours; if a user-facing path can reach that data, tiering creates a latency cliff rather than a saving.
- You haven't defined *who deletes what and when*. Undefined lifecycle is how "tiering" becomes "we now pay for three copies."

**The two decisions that matter:** the **age or access threshold** for each transition, and whether cold data is *queryable in place* (Iceberg/Parquet on object storage, queried by an engine) or must be *restored first* (deep archive). Queryable-in-place is usually the better tradeoff for anything analytical; restore-first is only for genuine compliance archives nobody reads.

**Fits when:** strong temporal locality, long retention requirements, cost matters.

**Operational note:** lifecycle policies are also a **cost-leak defense** — expiring old versions/snapshots and aborting incomplete multipart uploads are the two most commonly forgotten rules (see the S3 entry).

---

### Lease-Based Execution and Leader Election (Exactly-One in Distributed Systems)

**Problem it solves:** Some work must be done by **exactly one** instance at a time, but you still want N replicas for availability. Leader election gives you singleton semantics *with* automatic failover.

**How it works (lock + session):**
1. Every replica creates a **session** with a TTL and heartbeats to renew it
2. All replicas race to **atomically acquire** a lock on one key; exactly one wins
3. Winner runs the singleton work; losers watch and wait
4. If the leader dies and stops heartbeating, the session expires, the lock auto-releases, watchers re-race

**Why "any healthy node, first-to-acquire" is the right design, not laziness:**
- Replicas are **interchangeable** — there is no "best" leader, so selection criteria would add complexity for nothing
- **Symmetry** means zero config: every node runs the same loop, replicas can be added/removed freely
- **Failover is automatic and fast** because leadership *is* lock ownership tied to liveness
- The acquire is **atomic**, so the thundering herd on release resolves safely — exactly one winner regardless of who

**Tuning tension:** short TTL = fast failover but false-positive risk on a blip; long TTL = stable but slow failover. A partitioned leader may believe it still leads for up to its TTL, so **singleton work should be idempotent or fenced** rather than assuming perfect exclusivity.

##### When you need it, and when you don't

The trigger is precise: **work that is unsafe to run concurrently, in a service you still want to run with N replicas.** If either half is missing, you don't need leader election.

**Real triggers:**
- **Scheduled work that must not double-fire.** Three replicas each running the same cron means three concurrent runs — for a job that dumps a full dataset or hammers a downstream, that's a 3x load incident.
- **Single-writer invariants.** One instance should own a write position, a change-stream cursor, or an offset, to avoid duplicate processing and write races.
- **Sole ownership of an external resource** — one holder of an outbound connection, one coordinator of a batch.

**Don't reach for it when:**
- **The work is idempotent and cheap.** If running it twice is harmless, coordination is pure cost. Idempotency is almost always the cheaper answer than exclusivity.
- **You can partition instead.** Assigning work by shard/partition key gives you exclusivity *by construction* with no coordinator — every consumer owns its own partition. This is the better design when the work divides naturally, and it scales where a single leader does not.
- **A scheduler can guarantee singleton execution.** A Kubernetes `CronJob` or a scheduler with a singleton guarantee gives you one run without any election logic in your service.
- **You can use a conditional DB write.** For "claim this job" semantics, the `UPDATE ... WHERE status='QUEUED'` lease below needs no separate coordinator at all.
- **The leader would become a throughput bottleneck.** Leader election deliberately serializes work onto one node. If the work needs to scale out, you want partitioning, not a leader.

**What you're signing up for:** the coordination store becomes a **hard dependency** of your service — if it blips, you can lose leadership or fail to acquire it. So budget for: re-initializing the session on coordinator errors, treating the coordinator as a P1 dependency in your dependency map, alerting on "no leader for N minutes" (a silent no-leader state means the scheduled work simply stopped, with no errors anywhere), and making the singleton work **idempotent or fenced** anyway, because a partitioned leader can believe it still leads for up to its TTL.

**Database-lease variant:**
```sql
UPDATE jobs SET status='RUNNING', worker_id=me, lease_expires=now()+5min
WHERE job_id=X AND status='QUEUED'
-- 0 rows = another worker got it; 1 row = I hold the lease
```

**In practice (CG):** a `leader-election` library over Consul sessions + KV locks gates the singleton-shaped services — the search dataset ingestor (its cron only runs on the leader), LDS Writer, SPDI, and IMV. Two hard-won lessons: (1) the client **must** re-initialize its session on coordinator errors, because a Consul blip once left a service unable to recover until restart; (2) the coordination store deserves **P1 dependency** status — a quiet coordinator is a hard dependency of a loud revenue service.

---

### Change Data Capture (CDC)

**Problem it solves:** Keep derived stores (search index, cache, analytics) in sync with the source without dual-write inconsistency.

**How it works:** read the DB transaction log (binlog/WAL), stream changes via Kafka, consumers update their own stores.

**Why not dual-write:** if the second write fails you have divergence. CDC guarantees: if it's committed, it will reach downstream.

**Tools:** Debezium, AWS DMS, pg_logical.

#### Two event shapes — and why the second one matters more than it looks

| Shape | Event carries | Consumer must | Consequence |
|---|---|---|---|
| **Full-payload event** | The new state | Apply the payload | Consumer accumulates state; ordering and completeness are load-bearing |
| **Invalidate-then-refetch** | Only "id X changed" | Re-query the source for current truth | Consumer stays **stateless**; naturally self-correcting |

The refetch shape is quietly powerful: because the consumer never reconstructs state by folding the stream, it needs no windowing, no large keyed state, and no exactly-once operator machinery. **That design choice is a large part of why a stream-processing framework isn't needed** (see the Flink entry).

Its costs: an extra read against the source per change, and freshness bounded by refetch latency.

**In practice (CG):** the listing pipeline is `MySQL → (synchronizer) → LDS/Mongo → Kafka → search nodes`, and CGSP's ingestor listens to Kafka/SQS change topics and **re-fetches only the changed documents**. Deletes/closures propagate as upstream state changes, with full rebuilds as the completeness backstop.

##### When you need it, and when you don't

The trigger is **more than one store must reflect the same truth**, and you refuse to accept dual-write divergence. If there is exactly one store, there is nothing to capture.

**Real triggers:**
- You have a derived store (search index, read model, cache, analytics warehouse) that must track the source.
- You currently **dual-write** and have already seen divergence, or can't rule it out. This is the strongest argument: dual-write has no failure mode that preserves consistency, and CDC does.
- Multiple independent consumers need the same change feed, and you don't want the producer to know about them.
- You need replay — rebuild a downstream from history after a bug or a schema change.
- You want the change feed **without modifying the writing application** (CDC reads the log, so the source needs no code change — often the deciding factor for a legacy monolith).

**Cheaper alternatives to weigh first:**
- **Transactional outbox** — write the event to an outbox table *in the same transaction* as the data, then publish from there. Gives you the same atomicity guarantee as CDC, with an explicitly designed event schema rather than one derived from your table structure. Usually the better choice when you control the writing service.
- **Application-emitted events after commit** — simplest, but loses the event if the publish fails. Only acceptable when a periodic reconciliation job closes the gap.
- **Periodic full reconciliation** — no streaming at all. At low volume with loose freshness needs this is genuinely sufficient, and it's the backstop you need anyway.
- **Just query the source.** If the "derived store" exists only to make reads faster, first confirm you can't fix the read directly.

**Don't adopt CDC when:**
- There's one store and no derived consumer.
- **Nobody can own the schema coupling.** Log-based CDC exposes your *physical table structure* as a public event contract — a column rename can break every consumer. An outbox gives you a stable logical contract instead. This is the most underrated cost of CDC.
- Downstream can't tolerate eventual consistency.
- You need deletes to be reliably reflected but the source does soft-deletes inconsistently — deletes are the classic gap, and often only a full rebuild catches them.
- Operational capacity is thin. CDC adds a connector, a topic, consumers, lag monitoring, and a snapshot/backfill story to run.

**Non-negotiables once adopted:** consumers must be **idempotent** (at-least-once redelivery is guaranteed); events need a **version or timestamp** so out-of-order arrivals can be discarded; you need an **initial snapshot/backfill** path plus a **full-rebuild** path as the completeness backstop; and you must **alert on replication lag**, since a stalled connector produces silently stale downstream data with zero errors.

**Fits when:** syncing to multiple stores, needing guaranteed primary→derived consistency, needing a change stream.

---

## Part 2: Deep Dives (mechanisms worth reasoning about)

Three areas where the generic pattern language above isn't enough, and the mechanism has to be understood directly.

---

### 2.1 Streaming and Connection Models

#### Choosing a transport: the decision is direction and timing, not payload size

| Requirement | Transport |
|---|---|
| Known refresh interval, client-driven | HTTP polling (with `ETag` / `If-None-Match` / deltas) |
| Server must push the moment data changes, one direction | SSE |
| Client must send **while** the server is streaming, on one channel | WebSocket |
| High-frequency binary, dynamic subscriptions, multiplexed interactive streams | WebSocket |

**The dividing rule:** SSE is sufficient whenever the two directions are **temporally separated** (request, then stream). WebSocket earns its cost only when you need **simultaneous** bidirectional traffic on a single connection.

#### Why streaming at all — it's latency-to-first-byte, not size

A chat reply is only a few KB. The reason a plain response won't do is that the content is **produced incrementally over 5–30 seconds**. A blocking response means a blank spinner for the whole generation, then a dump; streaming paints the first tokens in ~1–4s.

Two secondary reasons a single long response is worse: it risks **proxy/LB idle timeouts** with nothing on the wire (heartbeat chunks keep SSE demonstrably alive), and it forfeits **progressive typed events** (see below).

The general trigger: **is this payload slow to produce and revealed progressively?** If it's complete-at-once (a lookup, cached data, a templated welcome message), stream nothing.

#### SSE wire format — the whole protocol

An HTTP response with `Content-Type: text/event-stream` that stays open. Four field names and a blank-line delimiter:

```text
event: text-delta
data: {"content":"The "}

event: text-delta
data: {"content":"Honda "}

event: metadata
data: {"suggestions":["Compare trims"]}

```

- `data:` — payload (the only required field)
- `event:` — names the message **type**; absent means the default `message` event
- `id:` — message id, remembered by the browser for reconnect
- `retry:` — reconnect delay hint
- **A blank line (`\n\n`) terminates one message** — this is the "dispatch now" signal

No framing headers, no length prefixes, no binary. That simplicity is exactly why SSE traverses ordinary HTTP proxies and CDNs (buffering must be off) while WebSocket needs upgrade-aware infrastructure.

One typed stream can therefore express a whole protocol — incremental text, a title, final metadata, an error, and a mid-stream replacement — all as different `event:` labels on the same connection.

#### Why SSE over WebSocket for turn-based chat

The decisive advantages:
- **Stateless / scales horizontally** — SSE is a plain HTTP response, so any node can serve a reconnect provided history lives in a shared store. WebSocket is stateful and wants sticky sessions or a broker to survive deploys.
- **Traverses existing infra** — any HTTP proxy/CDN/firewall.
- **Standard auth, free reconnect, built-in event typing** — `EventSource` auto-reconnects; WebSocket needs custom auth/CSRF, manual reconnect, and a hand-rolled envelope.

Human-in-the-loop does **not** require bidirectionality: the agent's clarifying question streams as a complete response, the stream closes, and the user's answer is a new POST. Because full history is replayed, the agent "remembers" it was mid-clarification.

Revisit WebSocket only for **binary** (voice/audio) or **true low-latency bidirectional control** (interrupt mid-generation) — and then as a small side-channel, not a wholesale migration.

**Note on POST-SSE:** native `EventSource` is GET-only. Carrying a prompt body requires a POST that returns SSE (e.g. the `fetch-event-source` polyfill). The wire format is identical; only the client read differs.

#### Correction — connection capacity is not a protocol property

**Wrong:** "WebSocket holds ~5k connections, SSE holds ~50."

Both are one long-lived TCP connection with near-identical per-connection cost. Capacity is bounded by **file descriptors, per-connection memory, and event-loop/thread capacity** — a tuned server holds tens of thousands of either. If anything SSE is marginally *lighter* per idle connection (no frame decoding, no ping/pong machinery).

- A low per-app stream limit is an **application throttle protecting a scarce downstream** (LLM concurrency, per-stream memory), not an SSE ceiling.
- The one genuine SSE-specific limit is client-side: **~6 connections per domain on HTTP/1.1**, so multiple tabs can starve each other. **HTTP/2 multiplexing removes it.**
- WebSocket's real differentiators are *what flows over* the connection — bidirectionality, lower per-message overhead, binary frames — not *how many* connections.

**HTTP/2 Server Push is not an alternative.** It was deprecated in browsers and does not let a server arbitrarily push application updates.

#### High-frequency binary: why WebSocket, precisely

Not because it's inherently lower-latency — latency is dominated by distance, processing, buffering, and congestion. It's because:
- **binary frames are native**; SSE is UTF-8 text, so binary needs base64 (larger) or a custom text encoding
- Protobuf/CBOR are smaller and far cheaper to parse than JSON
- lightweight framing after handshake
- bidirectional control for dynamic subscribe/unsubscribe, acks, commands

For genuinely ultra-low-latency market data, even WebSocket may not suffice — QUIC/WebTransport or specialized transports enter the picture.

#### The three-way connection taxonomy (the thing that collides numerically)

Different resources, wildly different hold times. Identical numbers mean opposite things.

| Concept | What it caps | Hold time | Scarcity |
|---|---|---|---|
| **Stream slot** (SSE/WebSocket) | End-to-end things happening at once | Full generation, 5–30s | High — fills fast |
| **HTTP/TCP transport capacity** | Sockets the box can hold | Same, but bounded by FD/memory | Tens of thousands |
| **DB pool connection** | Simultaneously **in-flight DB operations** | ~5–10ms per operation | Low — one pool serves hundreds of streams |

A 20-second stream holds **one** stream slot for its whole life while borrowing a DB connection **6–8 separate times** for milliseconds each. That's why the same number (say 50) fills instantly as stream slots but comfortably serves hundreds of concurrent streams as a DB pool.

**Why the DB pool stays open at all:** connection pooling is a universal driver-level practice to amortize the **TCP + TLS + auth (SCRAM) + topology handshake** — easily 10–100ms of setup versus a 5–10ms query. `minPoolSize` keeps warm sockets ready; `maxPoolSize` caps concurrent in-flight operations. It has nothing to do with streaming.

**How a pool nevertheless gets exhausted** (the counter-intuitive part): a connection is held for the **full operation latency**, not the CPU time. A single-threaded event loop can hold **hundreds of concurrent in-flight awaits**, each pinning a connection until it resolves. So `outstanding ops ≈ arrival_rate × op_latency` (Little's Law). Three amplifiers: concurrency × latency, **latency spikes** (maintenance/failover holds each connection longer), and **abandoned work**.

**Pool math worth remembering:** `connections = pods × workers × clients_per_worker × poolSize`. A dev environment at 19 × 3 × 2 × 5 produced ~570 idle connections (observed ~985 per node with bursting); reducing `minPoolSize` to 1 cut idle to 114. Separate clients (e.g. storage vs vector) each get **their own** pool.

**Runtime asymmetry:** on a thread-per-request runtime (JVM/Tomcat), a non-stream read lands on its own thread with its own connection, so stream work can't starve it. On a single-event-loop runtime, stream flushes and reads compete for the **same per-worker pool on the same loop** — so a flush burst can queue a read.

**Zombie streams:** without client-disconnect detection, a stream keeps generating and flushing after the client is gone, inflating concurrency for no user benefit. The fix is to abort on close (`res.on('close', () => abortController.abort())`).

#### Proxied streaming pipelines and layer placement

A two-hop proxied SSE pipeline (`browser → BFF → generation service → LLM`) has an important consequence: **each active stream pins two long-lived connections**, doubling the held-connection count.

The layering rule that matters:

| Layer | Owns | Does **not** own |
|---|---|---|
| Generation service | Token generation, intent routing, **safety enforcement** | Client-specific display shape |
| BFF | Transport, SSE framing, **display hydration** | Safety, generation, routing |

**Mid-stream guardrails** are the payoff of streaming: an output processor inspects accumulated text per chunk (regex, ~1–5ms, no extra model call) and on a violation calls `abort()` — which stops the **LLM generation**, not the connection. The middleware then emits a single `guardrail-replace` event, and the client overwrites the text it was building. **Abort the generation, not the connection; swap the event type, don't tear down the stream.**

Two refinements worth stealing:
- **Severity-gated abort.** High-severity categories abort immediately; low-severity ones defer to finish-time, because partial text false-positives (a half-streamed refusal reads like a violation). The earlier you abort, the less leaks — but the more you risk killing a good response.
- **Enforcement belongs next to generation, not in the BFF.** Put it in the processor and *every* client (web, mobile, internal tools) inherits it; put it in one BFF and only that path is protected.

**IDs-only + downstream hydration.** The model emits **validated ids**, not display payloads; the presentation layer hydrates them fresh. This buys four things at once: data can't be mutated or hallucinated by the model, display data is **fresh at render time** rather than frozen at reasoning time, token cost stays low, and the generation output stays **client-agnostic** so web and mobile can render differently.

Counter-argument worth knowing (and its answer): passing the reasoning-time snapshot through would make text and card consistent — but it makes *both* stale, relocates the fetch to the wrong owner, and couples generation to one client's display shape. Fresh hydration's failure mode (missing card) is safer than stale-but-confident numbers. The residual text-vs-card mismatch is handled by convention: **numbers live in the card, not in prose.**

---

### 2.2 API Composition and Ownership

#### The three transports, and what each actually optimizes

| Axis | REST | GraphQL Federation | gRPC |
|---|---|---|---|
| Mental model | Manipulate resources with HTTP verbs | Typed composition across domains | Call a typed remote **method** |
| Round trips / over-fetch | Client orchestrates | Solves it (one query, fan-out, exact fields) | Doesn't — you call each method |
| Wire serialization cost | JSON | JSON (unchanged) | Solves it (protobuf + HTTP/2) |
| Typed contract | Bolted on (OpenAPI) | Yes (SDL) | Yes (`.proto` IDL + codegen) |
| Writes | Native | `mutation` (no cross-subgraph atomicity) | Unary RPC |
| Streaming | SSE/WebSocket alongside | `subscription` (browser-facing, one direction) | Four call types incl. **bidirectional** |
| Cross-domain composition | Manual | Native | Not a feature |

**Correction — three common misconceptions:**
1. **GraphQL is not a data store.** It's an API contract + execution/composition layer in front of real datastores. A federated router splits one query, fans out to owning subgraphs, and stitches results.
2. **GraphQL is not read-only.** `query` / `mutation` / `subscription` are all first-class. Keeping writes on REST is an *adoption choice* justified by the lack of cross-subgraph atomicity — not a protocol limitation.
3. **"gRPC is for performance, GraphQL isn't"** is the wrong framing. They optimize **different axes**: GraphQL attacks round-trips and over-fetch; gRPC attacks wire serialization and connection multiplexing. That's why they *overlap* — both are typed, contract-first ways to invoke backend capability — and why the overlap is total except at the raw-wire and true-bidi-streaming corners.

**gRPC is not "REST with a better connection."** The persistent HTTP/2 connection is one of four pillars: HTTP/2 multiplexing, **protobuf binary serialization**, **IDL + generated stubs**, and **four call types** (unary, server-streaming, client-streaming, bidirectional). Only unary maps onto a REST request.

**What an RPC framework provides:** IDL + codegen, client stubs / server skeletons, serialization, transport and connection management, and cross-cutting concerns (deadlines, cancellation, retries, load balancing, discovery, auth, interceptors). Examples: gRPC, Thrift, Dubbo, Finagle.

**When RPC is preferred:** internal east-west traffic, high-volume latency-sensitive hot paths, strict evolving contracts across many teams/languages, **true bidirectional streaming**, polyglot environments needing consistent semantics.

**When it isn't:** public/browser-facing APIs, needing HTTP caching/CDN/human-readable payloads, fundamentally asynchronous work (that's messaging), and cross-domain read composition (federation already owns that lane).

**Operational gotcha:** gRPC pins long-lived HTTP/2 connections, which defeats naive L4 round-robin — you need L7-aware balancing or client-side LB. Also: deadline propagation must be threaded through call chains.

#### Where GraphQL's performance actually comes from

Ranked by how much it matters:

1. **Round-trip consolidation (largest).** One client request instead of N sequential ones. The win scales with per-round-trip latency — large for a distant browser, **near-zero for backend hops on a fast internal network**.
2. **Parallel fan-out at the router (modest).** Real, but only a win over a *naive* serial client, and it evaporates when the query has a dependency chain.
3. **DataLoader batching / dedup — damage control that becomes the main win.** See below.
4. **Over-fetch elimination.** Matters mostly for bandwidth-constrained clients.

**And on the other side of the ledger — it forfeits free HTTP/CDN caching**, because everything is `POST /graphql`.

**Correction — the router's caches optimize the router, not your data.**
- **Query plan / normalization cache** — skips parse/validate/plan on repeat operations. Saves **router CPU**; the backend fetches still happen every time.
- **Persisted queries (APQ)** — shrinks request payload, can restore some GET-cacheability. Not a data cache.
- **Response/entity caching** — the thing people mean, and the hard one: federated responses are often personalized and composed from subgraphs with different freshness, and **cross-subgraph invalidation is genuinely hard**.
- **DataLoader batching** — per-request only, caches nothing across requests.

**In practice (CG):** router guidance tells consumers to treat it as **non-caching by default**; entity/sub-entity caching is an enterprise-tier feature that the self-hosted OSS path deliberately deferred (a plugin spike closed without shipping it). Measured router overhead is ~4ms, and multi-service queries can be faster purely from **parallel planning**, not caching. If you want data cached, cache the **owning service**.

**The trade, stated honestly:** round-trip consolidation helps **cold** requests; caching helps **repeat** requests. So:
- **read-heavy, high-repeat, low-fan-out** (same popular object fetched a million times) → REST + CDN wins decisively
- **personalized, low-repeat, high-fan-out** (a logged-in user's tailored screen from many domains) → federation wins
That **repeat-rate × fan-out** interaction is the whole story, and it's why a mixed architecture is correct rather than indecisive.

#### DataLoader: batching vs dedup, and where the real win is

Two distinct behaviors:
- **Batching:** 30 entities → 30 distinct ids → one call instead of 30. Saves round-trips/overhead.
- **Dedup (coalescing):** 30 entities → only 8 **unique** ids → the downstream fetch is for **8**, not 30. Reduces actual work and payload.

Dedup is the bigger deal wherever **fan-in is high** (many listings share few dealers/service providers). The win scales with `N_references / M_unique_entities`, and the savings land on the *downstream service's* QPS and datastore load — not just the caller's latency.

**Mechanism.** Not cross-request batching. It batches the N **field-resolutions inside one query**:
1. resolving the field for item #1 calls `loader.load(id)`, which **queues the key and returns a promise** without calling anything
2. same for #2…#N; the loader **dedupes by key**
3. at dispatch, the batch function fires **once** with the unique keys and resolves all pending promises

**Dispatch timing differs by runtime:**
- **Node/graphql-js:** relies on the event loop — all `load()` calls happen in one tick, dispatch on the next microtask.
- **graphql-java / DGS:** no tick to lean on, so it does explicit **level-tracking** — an instrumentation counts expected field fetches at the current query level and calls `dispatchAll()` once they've queued. Deliberate bookkeeping, not thread scheduling.

**The Spring transaction question dissolves:** (1) the DataLoader is **request-scoped** — a fresh instance per GraphQL execution, mandatory so the dedup cache can't leak across requests; (2) there is **no distributed DB transaction** — the batch function makes a *remote read* to another service that isn't enrolled in your local `@Transactional` boundary. It's read composition, not a distributed write. `@BatchMapping` receives the whole `List<T>` so you can't accidentally write the N+1 version.

**In federation, dedup happens at two layers:** the router collects entity references across the result and sends **one `_entities` query** with an array of `{__typename, id}` representations; the owning subgraph's **entity resolver** then batches the actual data fetch with its own DataLoader. Whether the *router* dedupes identical representations is implementation-specific — but even if it passes all N, the subgraph's loader collapses them, so the fan-in win survives either way.

**Bound:** all of this is **per-request**. The same hot entity requested by two separate requests a second apart is fetched twice. Cross-request repeat load is a **cache-tier** job, not a DataLoader job.

#### Keeping the subgraph graph shallow, and `@provides`

Reference-resolution should be **flat**: a subgraph resolves its own domain and returns foreign entities as **keys**; the router does one hydration phase for all of them. Four things depend on flatness:
1. **Cross-query dedup** — all references to an entity type must flow through the same hydration layer, or you split one deduped fan-in into independent siloed ones
2. **Parallelism and timeout budget** — a nested call inside a subgraph is invisible to the router's per-field deadline
3. **Fail-open granularity** — the router can null just the failed field; a nested failure fails the whole parent field
4. **Single ownership** — otherwise every referencing service reimplements how to call, auth to, and shape a domain it doesn't own

**When a reference is the wrong tool: dependent keys.** If the foreign id is only knowable *after* another subgraph call plus business logic, a resolvable reference doesn't batch — it adds a **third sequential hop**. In that case keep it a plain scalar id and let the consumer hydrate in a second query. Conditional, business-logic-gated references are also awkward to model type-safely.

**`@provides` is a declaration, not a fetch.** It promises the router "these fields are already present in my response — don't hydrate them," typically paired with `@key(fields: "id", resolvable: false)`.
- **Worthwhile only when the subgraph already holds the data** as part of its own job → zero extra calls, and the consumer saves a round-trip.
- **If satisfying it requires an extra fetch, don't** — you've relocated a hop into a place with no router timeout/circuit-breaker coverage and no cross-subgraph batching.
- **Subgraphs never call back into the router.** Resolution flows strictly downward. Re-entrancy is cyclic, wastes plan/validate work for a known id, doubles router QPS, and complicates auth/trace propagation. If a subgraph must fetch, it calls the **owning service directly**.

#### The placement rule: whose logic, not logic-vs-data

"Logic is logic, data is data" is too clean — taken literally it exiles legitimate **derived domain attributes** from their own domain, leaving them homeless in an orchestration layer. The correct axis is **ownership**:

| Kind of logic | Correct home |
|---|---|
| Domain-semantic derivation over **one domain's own data** (a computed flag, a tier, a computed fee) | That domain's service/subgraph — computed or not, a domain owns its facts *and* their derivations |
| **Cross-domain composition** (join several domains into a page shape) | A service that owns that composition. Never a domain subgraph |
| **Presentation / page logic** (which banner, which layout, A/B wiring) | The app / presentation layer |

Corollaries worth keeping:
- **"Everyone already calls it" is gravity, not architecture.** Marginal cost is a legitimate tiebreaker *between* correct homes; it can never *make* a home correct. Otherwise the busiest junction accretes all logic and becomes a distributed monolith with a single critical-path chokepoint.
- **Single-source-of-truth is a code-organization goal with three solutions** — a shared library, one owning service everyone calls, or a subgraph. Same-language pure logic: a **library** is far cheaper. Cross-language consumers: **call the owning service** rather than each reimplementing. Only pick a subgraph when the field is a domain fact and that domain is already in the graph.
- **A composition/orchestration service is defined by what it owns, not by the fact that it fans out.** "Orchestrator" names a mechanism; identity is ownership.

#### The threshold question: when is federation worth it at all?

GraphQL solves a **client × service fan-out** problem, not a raw-throughput problem. Without a composition layer, every client re-implements the same fan-out, stitching, and error handling.

**You need it when the cost of N clients each composing M fragmented services exceeds the cost of running a federation platform.** Below that threshold it's a liability: the router becomes critical-path infrastructure, you take on schema composition, resolver-waterfall latency, and a new observability surface — to solve a problem you don't have.

The strongest argument isn't even latency — it's **decoupling frontend iteration from backend deploys**. So the real tell is organizational: **how often does a UI change require a backend change today?** If endpoints are stable and UI changes rarely need new shapes, even that argument evaporates.

And a depth caveat that is also an **organizational signal**: a subgraph tree that *wants* to be deep usually means the domain boundaries are drawn wrong. When you hit the depth wall, the first question is "should this even be three subgraphs?" — not "how do I optimize the resolver."

**Lock-in framing:** REST, federation, RPC, CQRS, event sourcing, and standardizing on Kafka are all platforms with exit costs. There is no commitment-free option at this layer — only *choosing which lock-in matches the dominant workload*. Weight by blast radius: event sourcing reaches the definition of truth (highest bar), federation reaches client contracts + router, gRPC reaches service edges and is **reversible per-edge** (lowest of the three).

---

### 2.3 Derived-Store Materialization

How a search index or read-optimized store is built, kept fresh, and recovered.

#### The layered truth model

```text
MySQL (transactional source of truth)
  → derived document store (denormalized read model)
    → Kafka change events
      → search index / cache (derived, bounded-staleness)
```

**Every downstream store is a derivative.** Truth lives upstream; the job of the system is to keep staleness **bounded and recoverable** — never to mistake a derivative for the source.

**In practice (CG):** MySQL is the only place for listing writes; LDS is an explicitly read-only denormalized Mongo store fed by a synchronizer; search consumes LDS-derived Kafka updates. A given field's "source of truth for ingestion" (LDS) is not the same as the "source of truth for writes" (MySQL) — keep those distinct.

#### Build-from-source vs dump-a-replica

The instinct "just snapshot a running node's index" is mechanically simpler and architecturally wrong. Six reasons:

1. **A node's index is a cache of a computation, not data** — it's baseline load plus hours of incremental application, including any missed messages, mis-applied updates, or partial corruption. Dumping it backs up a copy of a copy, with the drift baked in.
2. **Which node?** N nodes applying a change stream independently are at slightly different offsets and are **not** byte-identical. Dumping one blesses its particular state as canonical.
3. **No clean resume point.** Recovery needs the snapshot paired with the exact **change-log offset** it corresponds to. A live index has no crisp marker (mid-application, per-segment), so you can't safely replay from it without risking missed or double-applied changes.
4. **Physical coupling.** A node dump is tied to the on-disk/segment format and version. Uploading the **logical dataset (JSON) *and* the physical index** means the index can always be rebuilt if the format moves.
5. **It preserves the single-fetch property.** The reason the ingestor exists is so the source is queried **once, centrally** instead of once per node. "Nodes dump themselves" recreates the fan-out or is circular.
6. **Completeness.** Only a fresh total query against the source guarantees the snapshot is the complete, correct current set (including deletions/closures).

**In practice (CG):** legacy search once had 21 nodes each querying for the same ~4.5M listings, adding ~10 minutes per deploy. Extracting a dedicated ingestor that fetches once and publishes an artifact removed both problems.

#### Snapshot anatomy and cadence

- **Who:** a **separate service**, and within it a **single leader-elected instance** (see Lease-Based Execution). Not the primary node, not every node.
- **How often:** cron, a few times a day (e.g. `0 0 7,12,17 * * *`), plus a manual trigger. The cadence is deliberately conservative because **each full generation is a full dump that pressures the source** — the mitigation for staleness is widening the lookback window, not adding runs.
- **Chunking:** producer/consumer with a bounded queue — parallel per-group source queries push batches; upload workers drain them. **Logical batching** (e.g. 50 groups per object) avoids a swarm of tiny objects. The physical index is closed, zipped, and uploaded as **one archive at the end**, followed by a metadata file written **last as the completion marker**.
- **Versioning:** timestamped path prefixes (`.../<region>/<yy-MM-dd_HH:mm:ss>/...`), never overwritten, each carrying its **change-log offset** so a booting node knows where to resume.
- **TTL:** freshness comes from generating a newer version and pointing at the latest — old-version expiry is a **lifecycle-policy** concern and a common cost leak if unset.

#### Correction — snapshots don't re-base the fleet

A new snapshot landing does **not** trigger fleet recreation. A node adopts a snapshot only when it **starts** (deploy, restart, bounce, scale-up, pod replacement). A long-running pod keeps its on-disk index and stays current purely by **continuous change-stream consumption**.

So the division of labor is:

| Mechanism | Role |
|---|---|
| **Live change-stream consumption** | The *primary* freshness mechanism, running continuously on every node |
| **Periodic from-source snapshot** | *Bootstrap and recovery* — fast startup, plus a known-good baseline + offset so a booting node replays only a short tail |

Consequently, a periodic from-source rebuild corrects accumulated corruption or missed messages **only for nodes that restart**. That's exactly why the standard mitigation for a stale or corrupted node is **bounce it** — a targeted re-base on the latest clean snapshot plus replay.

**One-liner:** nodes hold a derivative (baseline + X hours of changes) that by construction is not a source of truth; drift is an accepted, bounded tradeoff; the from-source snapshot exists to reset it with an authoritative, resumable baseline.

#### Recovery patterns

| Pattern | Mechanism | Guarantee |
|---|---|---|
| **New-version build + alias swap** | Build into a new index version, then atomically repoint a stable alias | Safe cutover, easy rollback, background rebuild |
| **Snapshot + offset replay** | Load artifact at offset X, replay the change log from X | Bounded, resumable catch-up |
| **Watermark checkpoint** | Store progress in durable object storage; advance **only after** successful upserts; upsert by id (idempotent) | Failed runs simply re-read from the old watermark |
| **Rebuild-from-source as backstop** | Periodic total refresh | Catches deletions and completeness gaps incrementals can miss |

Deletes are the classic asymmetry: incremental change feeds often can't express "this no longer exists" reliably, so **full rebuilds are the completeness mechanism** for deletions/closures.

#### Ingestion sources and the two-path pattern

A mature ingestion platform usually needs two source paths, because the fetch shapes differ fundamentally:

| Path | Source | Read mechanism |
|---|---|---|
| **API/graph path** | Operational data already exposed as a service/subgraph | Paged queries, thin denormalized documents |
| **Analytical path** | Warehouse tables not exposed operationally | Table-format reads (Iceberg/Glue/Spark) writing directly to the index |

Design discipline that keeps the API path affordable: **keep the index document lean** — index only what's needed for filtering, sorting, and aggregation, and fetch rich display fields *after* search from the owning services. Also page/group the rebuild rather than issuing one giant query, and schedule rebuilds on cron rather than continuously.

**Text search config note:** dataset config chooses which fields are text and how they're mapped; the **analyzer attached to the field** does the actual tokenization. Common shape: an analyzed root text field plus a `.keyword` subfield for exact match and aggregation. Prefer explicit mappings over dynamic defaults.

**Sharding note:** shards/replicas should be **per-dataset tunable**, not one hardcoded value for every dataset.

#### Correction — "the ingestor is one process" is a real limitation, not a design ideal

Synchronous rebuild in a single leader pod means a wedged rebuild can stall with no recovery. The maturing direction is to **distribute rebuild work across pods via a queue** while keeping the *fetch-once* property. Worth knowing when reasoning about a platform's recovery story.

#### Materialization vs stream processing

The refetch-shaped CDC pattern keeps consumers **stateless**, which is why plain consumers suffice and a stream-processing framework isn't needed. The two triggers are independent:

- **Capability trigger (the real one):** you need fault-tolerant **state across events** — windowing, stream-stream joins within a time bound, pattern detection over sequences, large continuously-updated keyed state, or exactly-once stateful aggregates.
- **Cost trigger:** volume high enough to justify operating a stateful cluster.

Either alone can make plain consumers correct; both together make it obvious. Escalate by operational weight: **plain consumer → warehouse ELT (minutes of latency is fine) → Kafka Streams/ksqlDB (stateful, no cluster) → Flink (heavy state, CEP, batch+stream, multi-source), preferably managed.**

**In practice (CG):** analytical stream work is deferred to the warehouse via ELT (land raw in object storage, transform at rest); real-time freshness comes from invalidate-then-refetch. Flink appears only as a *future* idea for real-time index updates — the threshold hasn't been crossed.

---

### 2.4 Latency Investigation — a decision tree for "it got slow"

Every other section in this document answers *should I adopt X*. This one answers the question you actually get paged for: **something is slow, and there are eight layers between the user and the data.** The pattern sections are the menu of fixes; this is how you find out which one you need.

The governing rule: **each step must end in a number that eliminates layers.** An investigation that produces theories instead of numbers is guessing with extra steps, and it usually ends with someone adding a cache.

#### Step 0 — Define the symptom precisely before touching anything

Most wasted investigations come from skipping this. Answer four questions first:

| Question | Why it changes everything |
|---|---|
| **Which percentile?** p50, p95, p99, or max? | p50 regression = something on the *common* path. p99-only = contention, queueing, GC, a slow tail dependency, or cold cache. These have almost disjoint cause sets. |
| **Which population?** All requests, one endpoint, one tenant, one region, one client version? | Narrow blast radius points to data shape (one tenant's outlier volume) or a deploy, not to capacity. |
| **When did it change?** Step-function at a deploy, or gradual over weeks? | Step = a change (deploy, config, feature flag, traffic shift, dependency version). Gradual = growth crossing a threshold (data volume, index size, connection pool, disk). |
| **Absolute or relative?** Was it always 800 ms, or was it 80 ms last month? | "Always slow" is a design problem. "Recently slow" is a regression, and regressions have a *cause you can revert*. |

**A step-function at a known deploy is the single highest-value finding in this entire tree** — it converts an open-ended performance investigation into a diff review. Check that before anything else.

#### Step 1 — Split the timeline into three buckets before going deeper

Before per-layer analysis, attribute total wall-clock time to three coarse buckets, because they have completely different toolsets:

1. **Client / edge time** — DNS, TLS, connection setup, geographic RTT, request queuing in the browser, payload transfer, client-side render.
2. **Server processing time** — your code, your dependencies, your data stores.
3. **Waiting time** — time the request spent in a queue *not being worked on*: thread pool, connection pool, event loop backlog, upstream concurrency limit.

The third bucket is the one people miss, and it is the most common cause of "everything is slow simultaneously." **Queueing time is invisible in per-call latency metrics** — every individual call looks fine while total latency balloons, because the time is spent *before* the call starts. If server-side spans sum to far less than observed end-to-end latency, the gap *is* the answer, and you should stop looking at the database.

#### Step 2 — The layer walk, outside in

Walk from the user inward. Stop at the first layer that accounts for the dominant share of time — do not continue to the database out of habit.

| Layer | What to measure | Signature of the problem being *here* | Typical fixes |
|---|---|---|---|
| **Client** | TTFB vs. total, render time, request waterfall | Fast TTFB, slow paint. Serial request chains. | Bundle size, defer non-critical calls, parallelize, client cache |
| **Network / geo** | RTT, TLS handshake count, connection reuse | Latency tracks distance; handshake per request | CDN/edge termination, keep-alive, HTTP/2 |
| **Edge / CDN** | Hit ratio, origin fetch time | Low hit ratio; origin sees traffic it shouldn't | Cache headers, key normalization, `Vary` hygiene |
| **Load balancer / gateway** | Queue depth, upstream connect time, retry counts | Time before your app sees the request; retry storms | Pool sizing, timeout hygiene, retry budgets |
| **App: admission** | Thread/worker pool saturation, event-loop lag | Bucket 3 dominates; all endpoints degrade together | Concurrency limits, shed load, async, pool sizing |
| **App: composition** | Number of downstream calls per request, serial vs parallel | Latency ≈ sum of many small calls | Batch/DataLoader, parallelize independent calls, `@provides` |
| **App: compute** | CPU profile, allocation rate, GC pauses | CPU-bound; p99 spikes correlate with GC | Algorithm, serialization cost, object churn |
| **Downstream services** | Per-dependency p50/p99, error and timeout rates | One dependency's p99 dominates | Same tree, recursively, at that service |
| **Data store: query** | Query plan, rows examined vs returned, index usage | One query dominates; rows-examined ≫ rows-returned | Index, rewrite, denormalize, projection |
| **Data store: capacity** | IOPS, cache hit ratio, lock/latch waits, replication lag | All queries slow together; buffer-pool churn | Scale, read replica, tiering, partitioning |

**The rows-examined vs. rows-returned ratio deserves special mention** — it is the highest-signal single number in database investigation. Returning 10 rows after examining 4 million means a missing index or a non-selective predicate, and no amount of caching or scaling fixes the underlying scan.

#### Step 3 — Classify the shape, because the shape determines the fix

Once you know *where*, you still need *what kind*. Five shapes cover nearly everything, and they are distinguishable from the trace alone:

**1. One slow thing.** A single span dominates. → Fix that thing (index, query, algorithm, payload). Cheapest case; no architecture change.

**2. Many small things (fan-out / N+1).** Latency ≈ N × small, and N scales with result-set size. → Batch, dedup, parallelize. The tell: latency grows linearly with the number of items on the page. **This is the most commonly misdiagnosed as "we need a cache"** — a cache over an N+1 hides it; batching removes it.

**3. Serial chaining.** Independent calls executed one after another. Total = sum, when it could be max. → Parallelize. The tell: a trace that looks like a staircase rather than a comb.

**4. Queueing / saturation.** Individual operations are fast; waiting dominates. Latency is highly load-sensitive and rises non-linearly near a capacity limit. → Add capacity, reduce per-request work, add concurrency limits, shed load. **Never cache your way out of saturation** — you may reduce load enough to mask it until the cache goes cold.

**5. Tail amplification.** p50 is fine, p99 is terrible, and the request touches many components. If a request depends on N components each with a 1% slow tail, the chance of hitting *at least one* slow component is ~1−0.99^N — at N=50 that is 39%. → Reduce fan-out, hedge requests, tighten timeouts, make non-critical calls fail-open. The tell: p99 degrades faster than p50 as fan-out grows.

#### Step 4 — Fix in cost order, cheapest and most permanent first

An explicit ladder, because the temptation is always to jump to the bottom rung:

1. **Delete the work.** Do you need this call, this field, this row set at all? Over-fetching is the most common finding and the cheapest fix.
2. **Fix the inefficiency.** Missing index, bad plan, N+1, serialization overhead, oversized payload. Permanent and side-effect-free.
3. **Restructure the calls.** Batch, dedup, parallelize, move work off the request path (async, precompute).
4. **Right-size the resources.** Pool sizes, timeouts, instance sizing, read replicas. Cheap but recurring cost.
5. **Add a cache.** Only after 1–4, and only with repeat rate measured (§ Caching). A cache placed before step 2 hides a permanent fix behind a permanent obligation.
6. **Change the data model / architecture.** Materialized read model, denormalization, partitioning, CQRS. Highest cost, sometimes the only real answer when read shape fundamentally differs from write shape.

#### The distributed-transaction variant

For internal multi-service transactions (a write flowing through several services rather than a user-facing read), the tree is the same with three additions:

- **Trace across the async boundary.** Propagate context through queues and topics, otherwise the timeline breaks exactly where the latency hides. An untraced Kafka hop is an invisible arbitrary delay.
- **Distinguish processing latency from lag.** Consumer lag means work is queued; slow processing means each item is expensive. Lag with fast processing = partition/concurrency limit. Fast-draining queue with slow processing = the per-item work is the problem.
- **Look for retry amplification.** Retries at multiple layers multiply: 3 gateway × 3 client × 3 internal = 27 attempts for one logical request. Retry storms present as latency, then as saturation, then as an outage. Budget retries at exactly one layer.

#### The anti-patterns that waste the most time

- **Starting at the database.** It is the deepest layer and the most instrumented, so it attracts attention — but edge, queueing, and composition problems are more common and cheaper to fix.
- **Averaging away the signal.** A mean latency hides bimodality (warm vs cold, cache hit vs miss, tenant A vs B). Always look at the distribution.
- **Measuring a warm system and shipping for a cold one.** See the Class A caveat under Caching.
- **Fixing the loudest thing instead of the dominant thing.** The error-log-noisiest component is often not on the critical path at all.
- **Stopping at the first plausible cause.** Latency regressions frequently have two causes stacked; verify by *removing* the suspected cause and confirming the number moves.
- **Optimizing before reproducing.** If you cannot make it slow on demand, you cannot tell whether you fixed it.

#### The one-line version

**Attribute before you optimize; classify the shape before you choose a fix; and spend the cheapest, most permanent fix that addresses the dominant term — the cache is the sixth thing to try, not the first.**

**When this tree is the wrong tree:** if the slowness only appears above a certain load level, you are not debugging a request — you are hitting a capacity ceiling, and the procedure is Part 2.5. The routing question is *"is it slow at 1 request/sec?"* If yes, stay here. If no, go there.

---

### 2.5 Throughput and Capacity Planning — "will it hold at 10x?"

Part 2.4 answers *why is this slow*. This answers a different question with different math: **how much load can this take, what breaks first, and what do I need before the traffic arrives.** The two get conflated because both involve latency, but they invert the causality:

| | Latency investigation (2.4) | Capacity planning (2.5) |
|---|---|---|
| Question | Why is one request slow? | How many requests can we serve? |
| Load is | Held constant while you look | The independent variable |
| You want | The dominant *term* in one request | The **binding constraint** of the system |
| Latency is | The symptom | The *signal* that capacity is near |
| Ends in | A fix | A number, a limit, and a plan for exceeding it |

**The load-independence test tells you which one you're doing:** if the slowness is present at 1 request/sec, it is a latency problem. If it only appears above some rate, it is a capacity problem. That single question routes correctly almost every time, and it is worth asking before an investigation rather than after.

#### The two laws worth actually knowing

Almost all capacity reasoning reduces to two relationships. Both are simple enough to do in your head, which is the point.

**1. Little's Law — `L = λ × W`**
Concurrency = arrival rate × time in system. Rearranged for capacity work:

```text
required concurrency = throughput × latency
```

- 1,000 req/s × 200 ms = **200 concurrent requests in flight.** So you need ≥200 workers/threads/connections, or requests queue.
- Cut latency to 50 ms and the same 1,000 req/s needs only 50 — **latency reduction is a throughput multiplier**, which is why 2.4's fixes are also capacity fixes.
- Invert it to size pools: 50 DB connections at 10 ms per query serves 5,000 queries/sec *at best*, and nothing you do to the app raises that ceiling.

This one equation answers most "how many pods / threads / connections" questions, and it is the fastest way to catch a plan that cannot possibly work.

**2. Utilization vs. latency — the knee is real and it is not linear**
For a queueing system, waiting time scales roughly as `1 / (1 − utilization)`:

| Utilization | Relative wait | What it feels like |
|---|---|---|
| 50% | 2× | Fine |
| 70% | 3.3× | Fine |
| 80% | 5× | Getting sensitive |
| 90% | 10× | Latency visibly bad |
| 95% | 20× | Alerting |
| 99% | 100× | Effectively down |

The consequences are the whole reason capacity planning exists:

- **A system at 50% CPU is not "half capacity."** It is close to as loaded as you want it, because the last 20% of utilization buys throughput at brutal latency cost.
- **Small load increases past the knee cause enormous latency increases.** A 10% traffic bump takes you from 85% to 94% and latency triples. This is why capacity incidents look sudden — the system was fine until it very abruptly wasn't.
- **Target 50–70% steady-state utilization** on the binding resource, not 90%. The headroom is not waste; it is the latency budget and the failover budget.
- **Variance makes it worse.** Bursty arrivals queue even when *average* utilization is low. Averages hide the peaks that actually cause the queueing.

#### Step 1 — Find the binding constraint, not the busy resource

Capacity is set by exactly one thing at a time, and it is usually not the one being monitored most. Candidates, in rough order of how often they are the real answer:

| Constraint | How you recognize it | Note |
|---|---|---|
| **Connection pool** | Latency rises, DB CPU low, app threads waiting | The most common surprise. Little's Law sizes it. |
| **Thread / worker pool** | Queueing before work starts; spans ≪ end-to-end | Same signature as 2.4 bucket 3 |
| **Single-writer / leader node** | Writes plateau while reads scale fine | Read replicas do not help writes |
| **Partition / shard count** | Per-partition lag; adding consumers changes nothing | Consumers ≤ partitions is a hard ceiling |
| **Downstream rate limit / quota** | 429s, or throughput pinned to a suspiciously round number | Their capacity is your capacity |
| **Disk IOPS / throughput** | I/O wait, commit latency, replication lag | Often invisible in CPU dashboards |
| **Memory / GC** | p99 sawtooth; throughput drops as heap fills | Allocation rate matters more than heap size |
| **Network / bandwidth** | Large payloads, cross-AZ or cross-region chatter | Also a cost constraint, not just a speed one |
| **Lock / hot key contention** | Throughput plateaus with CPU idle; one key dominates | Serialization point — no amount of scaling helps |
| **CPU** | Actually saturated cores | Frequently *not* the binding constraint |

**Two rules that save the most time:**
1. **Adding capacity to a non-binding resource changes nothing** — more pods behind an exhausted connection pool make the pool worse, not better.
2. **The constraint moves when you relieve it.** Fix the pool and the DB becomes the constraint. Capacity planning is iterative by nature, so always predict *what becomes binding next* before celebrating.

#### Step 2 — Estimate before you test (the back-of-envelope pass)

Do the arithmetic first; a load test that contradicts your estimate is telling you your mental model is wrong, which is more valuable than the raw number.

```text
1. Peak rate, not average.     DAU × actions/day / 86,400 × peak-to-average ratio
                               (peak:avg is commonly 3–10× for consumer traffic;
                                daily-cycle and event-driven traffic are far spikier)
2. Fan-out per request.        1 page → N service calls → M queries. Multiply.
3. Concurrency (Little's Law). peak rate × latency = in-flight work
4. Per-unit capacity.          What does one pod/connection/partition actually do?
5. Units needed + headroom.    required / per-unit ÷ 0.6 target utilization
6. Failure headroom.           Can the remainder carry peak with one AZ/node gone?
```

**The two mistakes this pass exists to catch:** planning for *average* load (peak is what breaks you, and the peak-to-average ratio is often 5×), and forgetting fan-out amplification (a 10× traffic increase on a page issuing 20 queries is a 200× increase at the database).

#### Step 3 — Measure the ceiling deliberately

Four distinct tests that answer four distinct questions. Running one and calling it "load testing" is how ceilings get missed:

| Test | Method | Question answered |
|---|---|---|
| **Load test** | Hold expected peak steady | Does it meet SLO at planned load? |
| **Stress test** | Ramp until it degrades | **Where is the knee, and what breaks first?** |
| **Soak test** | Sustain for hours | Leaks, unbounded growth, log/disk fill, pool exhaustion |
| **Spike test** | Instant step change | Autoscaling lag, cold caches, thundering herd, connection storms |

The stress test is the one that produces the capacity number, and its most valuable output is not the throughput figure — it is **the identity of the first thing to break**, because that is your binding constraint under real conditions rather than in theory.

Two things that invalidate load tests routinely: **unrealistic data distribution** (uniform synthetic keys give a 100% cache hit rate and no hot-key contention, so you measure a system that does not exist), and **testing a warm system** (see the Class A caveat under Caching). Both make the ceiling look higher than it is.

#### Step 4 — Choose the scaling lever the constraint actually admits

| Constraint type | Lever | Ceiling on that lever |
|---|---|---|
| Stateless compute | Horizontal scale-out | Downstream shared resources — you just move the problem |
| Read volume | Read replicas, cache, CDN | Replication lag; cold-cache capacity risk |
| Write volume | Batch, shard, partition | Cross-shard transactions; rebalancing cost |
| Fan-out per request | Batch/dedup, `@provides` | Diminishing after the obvious wins |
| Latency-bound concurrency | Reduce latency, async | Little's Law is the guide |
| Third-party quota | Negotiate, cache, queue, degrade | Not yours to raise |
| Contention / hot key | Shard the key, coalesce, local aggregate | Some serialization is irreducible |
| Everything at once | Shed load and protect the SLO | Not scaling — survival |

**The most important entry is the last one.** Capacity has a floor you cannot always raise in time, so the plan must include what happens *when demand exceeds capacity anyway*: rate limit, shed the lowest-value traffic, degrade features, queue with back-pressure. A system with no shedding path converts an overload into an outage — and it does so at the worst moment, when load is highest.

#### The failure modes unique to high load

These do not appear in single-request investigation at all. They are properties of *systems under load*, which is why they surprise people who only ever profiled one request:

- **Retry amplification.** Load rises → latency rises → timeouts fire → clients retry → load rises further. A positive feedback loop that turns a brownout into an outage. Fixes: retry budgets, exponential backoff *with jitter*, circuit breakers, and retrying at exactly one layer.
- **Thundering herd / cold cache.** A restart, deploy, flush, or failover sends 100% of traffic to a source sized for 5%. This is the capacity face of the caching question — *can the source survive full miss at peak?*
- **Autoscaling lag.** Scaling takes 30 s–3 min (detect → schedule → boot → warm → healthy). Spikes faster than that are absorbed by headroom or not at all. **Autoscaling handles trends; headroom handles spikes.** Also: scaling on CPU misses constraints that are not CPU-bound, which is most of them.
- **Cascading failure via shared dependency.** Two services look independent until both saturate the same pool, database, or coordination store. Blast radius follows *shared resources*, not org charts.
- **Coordinated omission in your own measurements.** If your load generator waits for responses before sending more, it stops sending during the slowdown and *under-reports* the latency at exactly the interesting moment. Open-model generators, or fixed-rate submission, avoid this.
- **Queue as a hidden liability.** A buffer converts a throughput deficit into growing latency instead of errors — which is often correct, but an unbounded queue eventually delivers stale work to nobody, having hidden the deficit until recovery is impossible. Bound your queues and alert on depth *trend*, not depth.

#### Answering "can it handle 10x?" — the short procedure

1. **Which 10x?** Traffic, data volume, users, or tenants? They stress different constraints — 10× data breaks indexes and scans; 10× traffic breaks pools and CPU; 10× tenants breaks per-tenant overhead and noisy-neighbour isolation.
2. **Estimate** with Little's Law and fan-out multiplication. Find what saturates first *on paper*.
3. **Stress test to the knee** and check whether reality agrees with the estimate. Disagreement means the model is wrong — investigate that before trusting either number.
4. **Name the binding constraint and the one after it.** A capacity answer without a *next* constraint is incomplete.
5. **State the headroom target and the failure headroom** — steady-state utilization, plus surviving peak with a node or AZ gone.
6. **Define the shedding path** for the case where the 10× arrives before the capacity does.

#### The one-line version

**Capacity is set by one binding constraint at a time; find it with arithmetic before you find it with an outage — and remember that the last 20% of utilization is not capacity you own, it is the latency budget you are spending.**

---

## Part 3: Deep Tool Knowledge

For each tool: WHY it works the way it does, WHEN it's right, WHEN it breaks — and, in the **"When you need it, and when you don't"** subsection, the escalation ladder of cheaper alternatives, the real adoption triggers, the anti-cases, and the permanent obligations you take on.

**The recurring shape across all twelve:** the cheapest rung is almost never the tool itself, and the rung most often skipped is the one just below it — OpenAPI + codegen below gRPC, a BFF below federation, native full-text search below a search cluster, a unique constraint below a coordination store, a job table below Kafka, a local cache below Redis. Adoption arguments usually fail at that rung rather than on the tool's merits.

---

### PostgreSQL / MySQL (Relational)

**What it is:** Relational database with ACID transactions, rich SQL, and constraints.

**RIGHT choice when:** transactions across tables, complex queries (joins, CTEs, window functions), strong consistency, clear relationships and schema, DB-level constraints.

**WRONG choice when:** write throughput exceeds a single node and you can't shard cleanly; schema genuinely unknown/rapidly changing; simple KV lookup at extreme scale; document-shaped data with no cross-document queries.

**Alternatives:** DynamoDB/Cassandra (rich queries → horizontal write scaling), MongoDB (ACID → flexible schema), Redis (durability → sub-ms latency).

**Failure modes:**
- Connection exhaustion — fix with pooling (PgBouncer, HikariCP)
- Vacuum lag / MVCC bloat — tune autovacuum
- Lock contention from long transactions — keep transactions short, consider optimistic locking
- Replication lag serving stale reads — route critical reads to primary
- Index bloat — every index taxes every write

**Capacity reference:** single node ~5K writes/sec, ~50K indexed reads/sec; comfortable to ~2–5TB before ops (backup, vacuum, restore) hurt; ~500–1000 connections with pooling.

#### When you need it, and when you don't

**This is the default, and "default" is the decision content.** For most workloads the question is not "why relational" but "what would justify anything else." A relational store gives you constraints, transactions, ad-hoc query ability, and forty years of operational tooling; every alternative buys one property by surrendering several of those. Start here and let a *measured* constraint push you off.

**Escalation ladder before leaving relational** — most "we've outgrown Postgres" claims die at step 2 or 3:
1. **Index and query fixes.** Rows-examined ≫ rows-returned (Part 2.4) accounts for most perceived scaling walls.
2. **Connection pooling.** Exhaustion masquerades as the database being slow when the DB is nearly idle. Size with Little's Law (Part 2.5).
3. **Read replicas.** Read-heavy workloads scale a long way here, at the cost of replication lag on read-after-write paths.
4. **Vertical scale.** Unfashionable and frequently correct — a single large node handles far more than people assume, with zero architectural change.
5. **Partition within the database.** Native table partitioning for time-series and large-table maintenance keeps SQL and transactions intact.
6. **Move the read shape out** — search index, cache, materialized read model — keeping relational as the source of truth. This is usually the right answer and is not "leaving relational."
7. **Shard, or adopt a horizontally-scaling store** — only for write throughput a single primary genuinely cannot absorb.

**Real triggers for something else:** sustained write volume beyond one primary with no clean vertical headroom; a genuinely schemaless or per-tenant-variable shape; single-digit-ms KV lookups at a volume where per-query overhead dominates; or a data volume where backup, restore, and migration windows — not query latency — become the operational limit.

**Don't leave relational when:**
- The pain is a missing index, an N+1, or an exhausted pool. You will carry the same query into the new store and it will still be slow.
- The schema is "unknown" only because it hasn't been modelled yet. JSON columns handle genuine variability without giving up transactions.
- Writes are bursty rather than sustained — a queue in front absorbs bursts far more cheaply than a re-platform.
- You need joins and transactions but were told NoSQL is faster. You will reimplement both in application code, incorrectly.

**What you inherit by staying:** schema migrations as a deploy-coupled discipline, vacuum/MVCC or purge maintenance, a single-writer ceiling you must eventually plan around, and connection count as a scarce resource. All well-understood, all with mature tooling — which is precisely the argument for staying.

**Deciding question:** Need ACID or complex joins? → relational. Simple lookups at massive scale? → look elsewhere.

**In practice (CG):** relational remains the durable source of truth for core business data; new services get their own isolated schema. Analytics goes to the warehouse — never operational queries against it (orders-of-magnitude higher latency).

---

### Redis / Valkey

**What it is:** In-memory data structure store. Sub-millisecond latency. Rich structures beyond KV.

**RIGHT choice when:** sub-ms hot-path reads, data fits in memory (or eviction is acceptable), rich structures (sorted sets, HyperLogLog, streams, pub/sub), cache in front of a database, session storage, rate-limit counters, simple distributed locks, shared state across instances.

**WRONG choice when:** data must be durable; source of truth for financial data; data doesn't fit and eviction is unacceptable; complex queries; **or a single service where an in-memory cache is simpler with no network hop**.

**Correction — Redis is not a persistence layer.** Treat it as **ephemeral**: typical config fsyncs ~once per second (not per write), journals may not be backed up, and there may be **no restore process** for corruption. Anything durable belongs in a real database. Recommended uses: session/form/cached ephemeral state.

**Valkey vs Redis:** Valkey is a **Redis-compatible engine**, not a different technology. Clients stay in the Redis ecosystem (e.g. Redisson `RMap`/`RMapCache`); the engine/infra moves to managed ElastiCache-Valkey, which is meaningfully cheaper per GB with a much lower idle-cost floor. When people say "Redis" colloquially, check whether they mean the **client/API** or the **engine**.

**Failure modes:**
- Memory exhaustion → eviction or OOM. Set `maxmemory` + policy, monitor.
- Single-threaded blocking — never `KEYS` in production; use `SCAN`.
- Split-brain on partition — quorum config, Sentinel.
- Thundering herd on restart (cold cache) — warm before taking traffic, stagger TTLs.
- Replication lag — don't read replicas on consistency-critical paths.
- **Large values are a trap** — a >500KB payload can turn a ~1ms op into seconds and exhaust the connection pool. Cap object size; move oversized entries to a local cache.

**Capacity reference:** 100K–500K ops/sec per node; ~0.5–1ms per op; memory is what you buy.

#### When you need it, and when you don't

The mistake is treating Redis as "the fast database." It is a **shared-state service with a memory-shaped cost model and no durability guarantee you should rely on.** That framing gets the adoption decision right every time.

**Escalation ladder — reach for the lowest rung that works:**
1. **No shared state at all.** Can the work be recomputed, or derived per-request? Statelessness is free.
2. **In-process cache (Caffeine, a plain map).** If one pod's view is sufficient, this is faster than Redis (no network hop, no serialization) and adds no infrastructure. The cost is N copies with independent expiry — acceptable for short TTLs and read-mostly data.
3. **The database you already have.** A short-TTL table or an advisory lock is often adequate and one fewer dependency, when sub-ms latency is not required.
4. **Redis/Valkey** — when state must genuinely be *shared and coherent across pods* at low latency.

**Real triggers:** cross-pod coherence matters (a rate-limit counter or lock is wrong if each pod keeps its own); the source is expensive with a measured repeat rate (§ Caching); you need a data structure the database is bad at (sorted sets for leaderboards, HyperLogLog for cardinality, streams for lightweight fan-out); or per-pod memory duplication of a large working set is itself the problem.

**Don't add it when:**
- **A single service with a local cache would do.** This is the most common over-adoption: a network hop and an operational dependency traded for no coherence benefit.
- **The data must survive.** Typical configuration fsyncs about once per second, journals may not be backed up, and there may be no restore path. Anything you would miss belongs in a real database.
- **The working set doesn't fit and eviction is unacceptable.** Memory is the thing you are buying; a cache that evicts your hot set is a slower path to the source.
- **You need queries.** Redis retrieves by key. Secondary-index-shaped access means you picked the wrong store.

**What you permanently inherit:** a memory ceiling and an eviction policy you must choose deliberately; a single-threaded execution model where one `KEYS` or one 500KB value stalls everything (large values are the classic pool-exhausting trap); a cold-start capacity risk — the source must survive full miss at peak; a serialization format that becomes a compatibility contract across deploys; and one more hop in the failure path, which means every read needs defined behaviour for "Redis is down."

**On the Valkey question:** engine-vs-client is the distinction that matters. Moving the *engine* to a Redis-compatible one (Valkey) is an infrastructure and cost decision with clients unchanged; it is not an architectural migration and shouldn't be planned as one.

**Deciding question:** Multiple instances need shared fast state? → Redis/Valkey. Single instance hot path? → in-memory. Can't lose it? → not Redis.

---

### MongoDB / DynamoDB (Document / NoSQL)

**What they are:** Schema-flexible stores optimized for known access patterns and horizontal scaling.

**RIGHT choice when:** naturally document-shaped data (nested objects/arrays, no cross-document joins), access patterns known at design time (mandatory for DynamoDB), horizontal write scaling, frequently evolving schema, single-digit-ms latency at scale.

**WRONG choice when:** multi-document transactions are central, complex ad-hoc joins/aggregations, access patterns unknown or frequently changing, highly relational data.

#### Three distinct usage patterns (don't collapse them into "persistent cache")

| Pattern | Role | Note |
|---|---|---|
| **Derived / denormalized read store** | ETL from the relational source into one document per entity, read-only, fronted by an API | Looks cache-like, but chosen for **durability and fast recovery**, not speed |
| **Primary datastore for a document-shaped domain** | System of record for that domain | e.g. reviews with nested categories, scores, votes — forced into flat tables and joins by an ORM |
| **Operational/agent state** | Conversation history, working memory, observability spans | Durable operational state, often high write volume |

The real cache tier sits **in front** of Mongo (Redis/Valkey), which is where the "fast but ephemeral, size-limited" tradeoff actually lives.

#### Correction — bulk operations are recommended, not discouraged

Two different axes get conflated:

| Concept | Preference | Why |
|---|---|---|
| Multi-document ACID transaction | **Avoid / design around** | Embed related data so single-document atomicity suffices |
| Single-doc update-in-place | **Prefer** over delete+insert | Faster, uses padding |
| **Bulk write (batched ops)** | **Strongly prefer** for volume | One command, many independent atomic ops → large CPU/IO savings |
| Per-record loop of `save()` | **Anti-pattern** | Explodes op count and CPU |

So a relational habit of batching 30–50 rows per read/update **translates directly** via `bulkWrite`/`BulkOperations`. A bulk write is *not* a long transaction — each op is still an independent atomic single-document write.
**In practice (CG):** replacing a per-record `foreach Save()` (millions of ops/day) with `BulkPersist(batchSize: 500)` was projected to cut CPU 40–50% and DB operations ~99%; another migration replaced 2000 individual find+write calls per batch with one unordered bulk upsert.

#### Optimization checklist

- **Document design:** field names repeat in every document — use terse names, omit null/empty fields, stay well under the document size limit, avoid unbounded arrays.
- **Indexing:** index only proven hot queries; every index taxes writes. More than ~4 indexes on a collection is a design smell. Prefer high-cardinality leading fields and compound/covered indexes for the hottest queries. Create indexes manually across environments **before** deploying code — many threads creating the same index concurrently can take a cluster down.
- **Write pressure:** strip large payloads before write; use TTL indexes for retention; drop unused indexes. One CG investigation combined TTL/retention, bulk writes, index cleanup, and compound indexes to move a cluster from 92% → ~72% CPU and defer a costly tier upgrade.
- **Pooling:** see the pool math in Part 2.1. Non-prod and prod need different `min/maxPoolSize`; each client gets its own pool.
- **Platform standards:** Terraform-provisioned, standard cluster families per environment, **autoscaling disabled** to avoid runaway cost, periodic non-prod refresh via snapshot/restore.

**Engine-cache note:** WiredTiger's cache (like InnoDB's buffer pool) is fundamental and always on — distinct from the optional ORM second-level cache that is often disabled.

**Cost note:** the "MongoDB by default" answer is worth re-checking periodically — a managed dedicated-tier floor per cluster is misaligned with a fleet of low-traffic/non-prod clusters, which is why a cheaper compatible engine may become the default for new workloads with the managed option kept as a justified exception.

#### When you need it, and when you don't

The honest framing: a document store is the right call when **the aggregate boundary and the document boundary coincide** — one document is one unit of read, write, and atomicity. When that alignment holds, you get single-round-trip reads with no join and clean horizontal growth. When it doesn't, you get a relational database with no joins, no constraints, and manual referential integrity.

**Escalation ladder:**
1. **Relational with a JSON column.** Handles genuine schema variability while keeping transactions, constraints, and ad-hoc SQL. Covers a surprising share of "we need a document store."
2. **Relational plus a derived read model.** If the problem is read *shape* rather than data model, materialize the shape (Part 2.3) and keep the source relational.
3. **Document store as a derived read store.** Documents built by ETL from a relational source of truth — chosen for durability and fast recovery, not speed.
4. **Document store as source of truth** — only when the domain is genuinely document-shaped.
5. **DynamoDB specifically** — when access patterns are fully known, fixed, and you want operational load near zero at predictable single-digit-ms latency. Its constraint is the strictest: **you must design the keys for the queries you will ever run**, and ad-hoc access later is expensive or impossible.

**Real triggers:** nested structures read and written as a whole (a review with categories, scores, and votes); an ORM visibly fighting the shape by shredding one logical object across many tables and joining it back; per-tenant or per-entity field variability that would otherwise mean sparse columns or an EAV table; write volume needing horizontal distribution; or high-volume operational state (conversation history, spans, working memory) where the document is the natural unit.

**Don't adopt when:**
- **Multi-document transactions are central.** They exist and they are a design smell — if you need them routinely, the document boundary is wrong.
- **Access patterns are unknown or changing fast.** This inverts the usual intuition: schema flexibility does *not* mean query flexibility. Relational is the flexible one for unanticipated queries.
- **The data is relational and you wanted to skip migrations.** You have moved schema management from the database into every reader, forever, with no enforcement.
- **You want it as a persistence layer for cache-shaped data.** The real cache tier sits *in front* of the document store; using it as "durable Redis" gets you the worst of both cost models.

**What you permanently inherit:** schema enforcement as application-layer discipline (nothing stops a malformed document); index cost on every write, where more than about four indexes on a collection is a design smell; field names repeated in every document, so terse names and omitted nulls are real storage decisions; unbounded arrays as a latent document-size failure; and index creation as an operational hazard — many threads building the same index concurrently can take a cluster down, so create them manually ahead of the deploy. On the cost side, managed dedicated-tier floors are misaligned with fleets of low-traffic and non-prod clusters, which is why "document store by default" deserves periodic re-examination.

**Deciding question:** Document-shaped with known access patterns? → document store. Joins, transactions, ad-hoc queries? → relational.

---

### Kafka

**What it is:** Distributed event streaming platform. Append-only partitioned log with configurable retention.

**RIGHT choice when:** replay for recovery/reprocessing, multiple independent consumers of the same data, ordering within a partition, high-throughput event streaming, decoupling with retention, CDC pipelines / event sourcing / lake ingestion.

**WRONG choice when:** single consumer + simple low-volume work queue; need per-message routing/filtering (RabbitMQ); need request-reply; need neither replay nor multiple consumers (SQS is simpler); sub-ms latency required (Kafka batches by design).

**Alternatives:** SQS (managed, simple, no replay), RabbitMQ (routing, per-message ack, lower per-message latency), Redis Streams (lightweight), direct HTTP (simplest, coupled).

**How partitions actually work:**
- A topic is split into partitions, each an **independently ordered log** — order holds within a partition, never across the topic
- The **producer** picks the partition: default distribution, hash of a **key**, or a custom partitioner
- In a consumer group, **each partition is assigned to exactly one consumer at a time**; a consumer death triggers rebalance
- Throughput scales with partitions: N partitions support up to N-way parallel consumption
- **Replication factor** is what provides fault tolerance — partitions give parallelism, replicas give availability

**Sizing and skew:** see Sharding / Partitioning in Part 1 for the full sizing rule, hot-key remedies, and the consumer-count-mismatch failure.

**Failure modes:**
- Unbounded consumer lag — scale consumers, or fix the real bottleneck (often downstream, not Kafka)
- Rebalancing storms from unstable group membership — increase session timeout, stabilize membership
- Offset management bugs — commit before processing loses messages, after processing duplicates; use at-least-once + idempotent consumers
- Broker disk full — monitor, set time/size retention
- Uneven partition load from a hot key
- **Too many partitions/consumer groups** — metadata and metrics-cardinality overhead; excessive consumer-group churn has caused real monitoring and cluster pain

**Producer tuning for volume:** `batch.size`, `linger.ms`, `compression.type`.

**Topic creation note:** in non-prod, auto-created topics get **defaults** (e.g. 3 partitions / 3 replicas) — not traffic-driven autoscaling. Partition count can be **increased but never decreased**, so size it intentionally.

**Capacity reference:** 100K–500K msgs/sec per broker; 5–50ms end-to-end.

**Correction — the ZooKeeper dependency is going away.** Kafka historically used ZooKeeper for broker membership, topic config, and partition metadata; **KRaft** folds consensus inside Kafka itself. Kafka 4.0 removes ZooKeeper support, which means an old client library that can't do KRaft becomes the thing pinning your Kafka version. Greenfield clusters already run KRaft with no ZooKeeper.

#### When you need it, and when you don't

Kafka is a **durable, replayable, partitioned log**, and every one of those four words is a cost as well as a feature. The decision hinges on whether you need the *log* semantics or merely need to move work off the request path — those have very different cheapest answers.

**Escalation ladder:**
1. **A synchronous call.** If the caller needs the result and the work is fast, async adds latency-to-consistency and failure surface for nothing.
2. **An in-process background task or thread pool.** Fine when loss on restart is acceptable.
3. **A database-backed job table.** Transactional with your data, trivially inspectable, easy to re-run. Genuinely adequate at moderate volume and badly underrated.
4. **A managed simple queue (SQS).** Fire-and-forget work distribution with a dead-letter queue, near-zero operations, no partition or offset model to reason about.
5. **A broker with routing (RabbitMQ)** when topic/header-based routing or per-message priority is the actual requirement.
6. **Kafka** when you need retention, replay, ordered partitions, or several *independent* consumer groups reading the same stream at their own pace.

**Real triggers — any one is sufficient:** multiple independent consumers of the same events (the strongest and most common); **replay** — the ability to rebuild a downstream store by re-reading history (this is what makes derived-store recovery cheap, per Part 2.3); per-key ordering with parallelism, which partitions give you and a plain queue does not; sustained high throughput with durable retention; or an event log that is itself the integration contract between teams.

**Don't adopt when:**
- **You need a work queue with per-message acknowledgement and retry.** Kafka's offset model fits streams, not task lifecycles. Per-message failure handling is possible but awkward; SQS is purpose-built for it.
- **You need routing, priority, or selective consumption.** Consumers read partitions, not filtered subsets.
- **There is one producer and one consumer and no replay requirement.** You have adopted a distributed log to move a function call.
- **Ordering is required across all messages.** That means one partition, which means no consumer parallelism — you have bought a distributed system to run single-threaded.

**What you permanently inherit:** partition count as a semi-permanent capacity decision (consumers ≤ partitions is a hard parallelism ceiling, and repartitioning breaks key locality); consumer lag as a first-class operational signal; a serialization and schema-evolution contract across teams, with a registry to run; delivery semantics that are at-least-once unless you do real work, so **consumers must be idempotent**; rebalance behaviour during deploys and scaling; retention as an explicit storage cost decision; and — until KRaft is universal — possibly a coordination ensemble alongside it.

**Deciding question:** Need replay OR multiple independent consumers? → Kafka. Simple fire-and-forget queue? → SQS. Routing/filtering? → RabbitMQ.

---

### Elasticsearch / OpenSearch

**What it is:** Distributed search and analytics engine built on Apache Lucene. Inverted index for full-text search.

**RIGHT choice when:** full-text search (fuzzy matching, relevance scoring, tokenization), complex aggregations on semi-structured data, flexible multi-field queries, log analytics, near-real-time index (seconds, not ms).

**WRONG choice when:** source of truth (**always pair with a primary store**), simple exact-match lookups, high write throughput with strong consistency, small datasets, transactions or relational integrity.

**Cluster model:** cluster → indices → **primary shards** (+ replicas) → documents. Text fields get an **inverted index** built by an analyzer (tokenize, term→doc postings, optional positions for phrase queries); numeric/date/geo fields get range-optimized structures. Queries fan out to relevant shards in parallel and merge.

**Correction — "slow to write, slow to index" is the wrong mental model for how it's maintained.** You don't write to it directly from the transactional DB on every change. The sustainable pattern is:
```text
relational source → derived read store → change events → search index
```
with a **dedicated ingestor** doing full rebuilds plus incremental updates. See Part 2.3 for the full materialization, snapshot, and recovery model.

**Failure modes:**
- Split brain on partition → index corruption. Proper discovery/quorum settings.
- GC pauses on large heaps → node appears dead → rebalancing storm. Keep heap ≤ ~32GB.
- **Shard explosion** — too many small shards, per-shard overhead. Target ~20–50GB per shard, and make shard/replica counts **per-dataset tunable** rather than one hardcoded default.
- **Mapping explosion** — dynamic mapping creating unbounded fields. Use explicit/strict mappings and cap total fields.
- Stale reads after write until segment refresh (default ~1s). Explicit refresh costs performance.
- **Unbounded index versions** — timestamped indices need automatic cleanup, or they accumulate.

**Alternatives:** relational full-text search (simpler ops, weaker relevance tuning), managed search products (typo-tolerance and speed, expensive at scale), lighter engines for smaller scale. OpenSearch is functionally an Elasticsearch fork.

**Platform pattern worth stealing:** make search a **self-service platform** rather than one bespoke service — per-dataset config (source query, searchable/filter/sort fields, rebuild schedule, change topics), timestamped indices with **alias-based atomic cutover**, automatic old-index cleanup, and a standard query interface. That turns one product's search service into infrastructure many teams can use, and separates platform concerns from product-specific business logic.

#### When you need it, and when you don't

A search engine's real product is **relevance ranking over analyzed text** — tokenization, stemming, fuzziness, scoring. If you only need filtering and exact matching, you want an index in your database, not a second data system. The test that separates the two: *does the user expect results ordered by how well they match, rather than by a column?*

**Escalation ladder:**
1. **Database indexes with `LIKE`/prefix matching.** Adequate for typeahead on short fields and for exact/prefix lookups.
2. **Native full-text search in the relational database** (`tsvector`/`MATCH`). Real stemming and ranking, no new infrastructure, transactionally consistent with your data. Handles far more cases than it gets credit for — this is the rung most often skipped.
3. **A managed search service** if the need is genuinely search but the operational appetite is low.
4. **Elasticsearch/OpenSearch** when you need tunable relevance, aggregations over large result sets, multi-field boosting, geo/vector search, or per-field analyzers.

**Real triggers:** free-text queries where ranking quality is the product; faceted navigation with counts across a large corpus (aggregations are a genuine strength); relevance that must be *tuned* — boosts, synonyms, custom analyzers; geo-distance or vector similarity; or read fan-out that would otherwise pressure the primary datastore for the browse path.

**Don't adopt when:**
- **You need exact filtering, sorting, and pagination on structured fields.** That is a database index. Adding a search cluster gives you an eventually-consistent copy of data you already had.
- **You would make it the source of truth.** Never. It is a derived index — always rebuildable from source, never the place data lives.
- **The corpus is small.** A few tens of thousands of rows filter fine in the database, and an index refresh cycle is pure added latency and staleness.
- **Read-after-write is required.** Refresh is near-real-time, not real-time — writes are not immediately searchable, and designs that assume otherwise break intermittently.

**What you permanently inherit:** an ingestion pipeline and its lag as a monitored SLO; **reindex-as-a-routine-operation**, because mapping changes generally require rebuilding — which makes alias-swap deploys and a repeatable rebuild path non-negotiable (Part 2.3); mapping and analyzer choices that are effectively schema decisions with reindex-shaped migration costs; JVM heap and shard-count tuning, where over-sharding is the classic self-inflicted wound; eventual consistency with the source of truth, meaning a drift-detection and reconciliation story; and cluster-level operational weight — this is a distributed stateful system, not a library.

**Deciding question:** Do users type free-text and expect relevant fuzzy results? → search engine. Exact match on known fields? → database index.

---

### GraphQL Federation

**What it is:** An API contract + composition layer. A router takes one query, splits it across owning subgraphs, and stitches results. **Not a datastore.**

**RIGHT choice when:** many clients with different data needs, data fragmented across many services, cross-domain **read** composition for client/browser-facing surfaces, and you want frontend iteration decoupled from backend deploys.

**WRONG choice when:** one or few clients with stable endpoints; data isn't fragmented; backend-to-backend low-latency single-domain hops; **and when the goal is caching** (it forfeits free HTTP/CDN caching).

**Operational profile:** ~4ms router overhead; parallel query planning can make multi-service queries faster than serial client calls; treat it as **non-caching by default**; fail-open per-field timeouts and per-subgraph circuit breakers; retries usually disabled to avoid storms.

**Key mechanisms and their limits:** DataLoader dedup (per-request only), `@provides` (a declaration, only free if the data is already held), flat reference resolution, no cross-subgraph mutation atomicity. Full treatment in Part 2.2.

**Biggest operational risk:** the router becomes a **single point of failure on the critical path** for all composed traffic. Budget for that explicitly.

#### When you need it, and when you don't

Federation solves **client × service fan-out**: many clients each needing data from many services, where the alternative is either chatty clients or a hand-maintained aggregator per surface. It is a *composition* technology, and it earns its keep only when composition is genuinely the problem.

**Escalation ladder:**
1. **A single REST/GraphQL service.** One domain, one team, no composition problem.
2. **Client-side composition.** Two or three parallel calls assembled in the client is perfectly reasonable, and the round trips are often not the bottleneck.
3. **A backend-for-frontend.** One surface, one aggregator, no shared schema governance. The right answer far more often than federation, and the rung most often skipped.
4. **A monolithic GraphQL gateway** that calls services directly — one schema, no subgraph ownership model or registry.
5. **Federation** when multiple teams must own slices of one schema and evolve them independently.

**Real triggers:** the schema needs *multiple owners* deploying independently — this is the actual trigger, and it is organizational as much as technical; clients need cross-domain graphs where entity relationships span team boundaries; over- and under-fetching are measurably hurting mobile or low-bandwidth clients; and BFF proliferation has become the maintenance problem, with each new surface requiring a new aggregator.

**Don't adopt when:**
- **One team owns everything.** You have taken on a registry, a router, and composition rules to solve a coordination problem you do not have.
- **The surface is internal and latency-critical.** A typed RPC call is faster and simpler; composition overhead buys nothing where the caller knows exactly what it wants.
- **Clients need a handful of fixed queries.** REST endpoints shaped for those queries are cheaper to build, cache, and debug.
- **You want it for performance.** Federation's wins are shape and round-trip wins. The router adds a hop, and a naive resolver graph is *slower* than the REST calls it replaced — the performance comes from batching and dedup discipline (DataLoader), which you must actually implement.

**What you permanently inherit:** a router as a critical-path single point of failure needing its own capacity and resilience story; schema composition as a build-time gate, where one team's change can fail the whole graph's check; entity ownership and `@key` design as a cross-team contract that is painful to change later; **N+1 as the default failure mode** unless batching is enforced everywhere; per-field resolver latency attribution as a new observability requirement (a slow field is invisible in endpoint metrics); query cost and depth limiting, since clients can now ask for arbitrarily expensive shapes; and a caching story that is harder than REST's, because the response is client-shaped rather than resource-shaped.

**The subgraph-depth caveat:** keep the resolution graph shallow. A subgraph that re-resolves another team's entity turns one client query into a chain of hops, and that chain is where federation's latency reputation comes from (Part 2.2).

**Deciding question:** Are we past the client × service fan-out threshold on *this* surface? Client-facing and fragmented → yes. Internal, single-domain, latency-critical → no.

---

### gRPC

**What it is:** A contract-first RPC framework: typed remote **methods**, protobuf binary payloads, HTTP/2 multiplexed transport, four call types including bidirectional streaming.

**RIGHT choice when:** internal service-to-service (east-west), strong contracts across teams/languages via `.proto` + codegen, measured serialization- or connection-bound hot paths, **true bidirectional streaming**, polyglot clients needing consistent timeout/retry/auth semantics.

**WRONG choice when:** public/browser-facing APIs (needs gRPC-Web), simple CRUD where REST is clear enough, you need HTTP caching/CDN or human-readable payloads for debugging, the interaction is fundamentally asynchronous (use messaging), or cross-domain read composition (federation owns that).

**Failure modes:**
- Broken proto compatibility — never reuse field numbers; only add optional fields
- **L4 load balancer misconfiguration** — long-lived HTTP/2 connections pin to one backend; use L7 (Envoy) or client-side LB
- Missing deadline propagation across A→B→C chains
- Opaque payloads without protobuf-aware tooling

**Adoption discipline:** it overlaps heavily with federation (both are typed contract layers), so adopting it broadly alongside federation fragments the contract story into two schema/codegen toolchains. The non-redundant zones are **wire-level performance on a proven-hot internal hop** and **true bidirectional streaming**. Adopt **per-edge and benchmark-driven**, never as a blanket mandate — its lock-in is at the service edge and therefore reversible per-edge.

**Note:** gRPC often already exists in the infrastructure layer (metrics backends, OTLP collectors, cloud client libraries) even where it's absent from application service-to-service traffic. "We don't have gRPC" usually means "not between our own services."

#### When you need it, and when you don't

gRPC's real offering is a **typed contract with code generation, plus efficient binary framing over HTTP/2**. Those are two separable benefits, and it matters which one you actually want — the first is available more cheaply elsewhere, the second only matters when you have measured it.

**Escalation ladder:**
1. **REST with JSON.** Universally debuggable, curl-able, cacheable by every intermediary. The default, and correct far longer than people expect.
2. **REST with a shared schema (OpenAPI) and generated clients.** This gets you most of the contract and codegen benefit with none of the transport change. **The rung that is almost always skipped**, and it dissolves the majority of "we should adopt gRPC" arguments.
3. **gRPC** for internal service-to-service paths where payload size, serialization cost, or connection overhead has been *measured* as material.
4. **gRPC streaming** when you genuinely need long-lived bidirectional or server-streaming semantics between services.

**Real triggers:** measured serialization or payload overhead on a hot internal path; strict cross-language contracts where drift between polyglot services is a recurring source of bugs; genuine bidirectional streaming between backend services; very high call volume where per-call overhead is a real fraction of total cost; or strongly-typed streaming where JSON framing has become awkward.

**Don't adopt when:**
- **Browsers are the client.** Native gRPC is not browser-callable; you need gRPC-Web plus a proxy, and you have added infrastructure to reach parity with REST.
- **It's a public or partner API.** You would be imposing tooling on people who want to curl an endpoint.
- **You want typed contracts and nothing else.** OpenAPI plus codegen delivers that without changing transports.
- **The path isn't hot.** Adopting a binary protocol for a call made twice a minute is complexity with no return.
- **Caching intermediaries matter.** HTTP caching semantics that CDNs and proxies understand for free do not apply.

**What you permanently inherit:** proto files as a versioned artifact with an evolution discipline (field numbers are forever, and reuse is a data-corruption bug); a build-time codegen step in every consuming service's pipeline; opaque payloads on the wire, so debugging needs reflection tooling rather than reading a log line; HTTP/2 load-balancing subtleties, since long-lived multiplexed connections stick to a backend and defeat naive L4 balancing — this catches teams out repeatedly; deadline propagation as an explicit discipline; and a second API style to document, secure, and observe alongside the REST surface you almost certainly still have.

**Deciding question:** Internal, typed, measured-hot or genuinely bidirectional? → gRPC. External, browser, or cross-domain composition? → REST/GraphQL.

---

### WebSocket and SSE

**What they are:** WebSocket is a persistent bidirectional channel over TCP (HTTP-upgraded). SSE is a persistent one-directional server→client stream over plain HTTP.

**Choose SSE when:** server→client push only, text/JSON, standard HTTP infrastructure, and the client's sends are temporally separated (request, then stream). You get stateless horizontal scaling, proxy/CDN traversal, standard auth, free auto-reconnect, and typed events.

**Choose WebSocket when:** the client must send **while** the server streams on one channel — dynamic subscribe/unsubscribe, acks/commands, presence/typing, interrupt-mid-generation — or you need **binary frames** or very high message rates.

**Choose polling when:** the refresh interval is known (dashboards on a 5s tick). Use deltas + `ETag`/`If-None-Match`.

**Correction — connection capacity is not a protocol difference.** Both are one long-lived TCP connection with near-identical per-connection cost; ceilings come from FDs, memory, and event-loop capacity, plus any application throttle. SSE's only genuine disadvantage is the **~6-connections-per-domain browser cap on HTTP/1.1**, which HTTP/2 multiplexing removes. **HTTP/2 Server Push is deprecated and not an alternative.**

**Operational concerns:**
- WebSocket servers are **stateful** — client↔server affinity means sticky sessions or a connection registry, and deploys break connections
- SSE is stateless *provided* conversation/session state lives in a shared store
- Both need buffering disabled and idle timeouts understood; heartbeats keep connections demonstrably alive
- A **proxied** stream pins two connections per active stream
- Watch for **zombie streams** — always wire client-disconnect to cancellation

**Scaling a streaming tier:** the right long-term shape is **route isolation** — put streaming routes on their own pods/target group (or a dedicated streaming BFF), because streaming is I/O-bound, long-lived, and **connection-count-scaled** while page-serving is CPU-bound, millisecond, and **RPS-scaled**. Two different resource profiles in one autoscaling group is the problem.

Sequence the fixes by cost: **per-pod concurrency limiter (503 early) → observability (an `active_streams` gauge) → autoscaling on a dual trigger (CPU for SSR + active-stream count for streaming) → route isolation.** Note that naive CPU or RPS signals are **blind to held-open streams** — ~99% idle streams keep CPU flat, so the first visible symptom of exhaustion is OOM or connection refusal. You must instrument the stream count explicitly.

#### When you need it, and when you don't

The decision is **direction and timing**, not payload size or perceived modernity. Ask two questions in order: does the *server* need to initiate, and does the *client* need to send on the same connection concurrently? Those two answers select the transport, and almost every other consideration is secondary.

**Escalation ladder:**
1. **Request/response.** If the client can ask when it needs to know, ask.
2. **Polling with `ETag`/conditional requests.** When a known staleness interval is acceptable, this is stateless, cache-friendly, and trivially debuggable. Underrated — a 30-second poll is frequently the correct engineering answer.
3. **Long-polling.** Legacy fallback; rarely the right new choice.
4. **SSE** when the server must push as events occur, one direction, over plain HTTP.
5. **WebSocket** when the client must also send continuously on the same connection, or the payload is binary, or the message rate is high enough that framing overhead matters.

**Real triggers for SSE:** server-initiated updates with unpredictable timing (progress, notifications, incremental LLM output); a text/event-stream shape that works through ordinary HTTP infrastructure; and automatic client reconnection with `Last-Event-ID` resumption, which you would otherwise build yourself.

**Real triggers for WebSocket:** genuinely simultaneous bidirectional traffic (collaborative editing, multiplayer, live trading input); binary frames; high message rates where per-message HTTP overhead is material; or sub-protocol needs that don't fit event framing.

**Don't adopt streaming when:**
- **A known refresh interval is acceptable.** Polling is cheaper end to end than any persistent-connection design.
- **Updates are rare.** A held-open connection per idle user to deliver an occasional message is a poor trade — that is what push notifications are for.
- **You chose WebSocket for one-way server push.** This is the most common mis-selection. You have taken on a stateful protocol, sticky sessions, and hand-rolled reconnection to do what SSE does over plain HTTP.

**What you permanently inherit — the honest cost:** connection *count* as a capacity dimension rather than request rate, so Little's Law does not apply and you plan for concurrent held connections instead; deploy behaviour becomes a design question, since every restart mass-disconnects clients and the reconnect storm is a thundering herd (stagger with jittered backoff); load balancer and proxy timeouts that must be raised deliberately, plus heartbeats to survive intermediaries that kill idle connections; per-connection memory and file descriptors as the real ceiling — **not a protocol property**, which is the correction worth remembering; and, for WebSocket specifically, statefulness that pushes you toward sticky sessions or an external session store, plus reconnection and message-replay logic you must write yourself.

**The capacity correction, restated because it matters:** WebSocket and SSE hold one long-lived TCP connection each with near-identical per-connection cost. Any large gap between quoted capacities is an application-level throttle or a deployment artifact, not a protocol ceiling. The one genuine SSE constraint is the HTTP/1.1 six-connections-per-domain *browser* cap, removed by HTTP/2.

**Deciding question:** Known interval → poll. Server-driven one-way → SSE. Simultaneous two-way, binary, or high-rate → WebSocket.

---

### S3 / Object Storage

**What it is:** Effectively infinite, highly durable blob storage. Store anything; retrieve by key.

**RIGHT choice when:** files/images/video/backups/logs/data lake, effectively infinite capacity, very high durability, write-once-read-many, and you don't need to query *inside* the objects.

**WRONG choice when:** low-latency random access on a hot path, querying/filtering/joining within objects, atomic partial updates (objects are immutable — replace entirely), small structured data that belongs in a database.

**The governance insight worth internalizing:** object storage is often the **one durable store a browser-facing leaf app is permitted to own**, precisely because of what it *lacks*. It stores files behind URLs, **enforces no schema**, and has **no complex querying or transactional capability** — so it "significantly reduces the risk of coupling between systems." A shared relational schema is a distributed-monolith risk; a shared bucket is just files. **Its limitations are the feature.**

**Three canonical roles:**

| Role | Pattern | Example |
|---|---|---|
| **Build-once artifact store** | Central process builds an artifact; consumers boot from it | Search dataset + zipped index that nodes bootstrap from (serves deploys *and* recovery) |
| **Durable checkpoint** | Watermark/offset advanced only after success; idempotent replay | Incremental-ingestion watermark; table-format warehouse storage |
| **Firehose landing buffer** | Producer lands raw; a loader moves it onward | Model input/output capture → loader → warehouse (minutes of latency) |

All three exploit the same property: big immutable things some other system reads or replays later.

**Transfer mechanics — two upload modes, and the size boundary is the whole game:**

| Object size | Approach | Why |
|---|---|---|
| < ~100 MB | Single `PutObject` | One round-trip is fine |
| ~100 MB – 5 GB | Multipart (parallel parts) | Parallelism + **per-part retry** |
| > 5 GB | Multipart **mandatory** | Single-PUT hard limit is 5 GB |
| Millions of tiny objects | **Aggregate first** | Per-request overhead dominates |

Multipart exists for **reliability and throughput**, not just capacity: parallel parts saturate bandwidth, a failed part retries alone rather than restarting a multi-GB upload, and interrupted uploads can resume (5 MB minimum part, up to 10,000 parts, 5 TB max object).

**Best practice: use the high-level transfer manager, not raw put/get.** Node `@aws-sdk/lib-storage`, Java `S3TransferManager`, boto3 `upload_file`, and the CLI all switch to multipart automatically above a configurable threshold (commonly ~8 MB) and manage part-splitting, concurrency, and retries. Hand-tune `partSize`/concurrency only for specific throughput or memory constraints.

**Don't conflate two kinds of "chunking":** *logical batching* (how many records per object — an application choice, to avoid a swarm of tiny objects) versus *transfer chunking* (how one object's bytes move — an SDK choice based on size).

**Read side:** `GetObject` streams the whole object; transfer managers parallelize large downloads via **ranged GETs**. **Range GETs** are also a first-class tool on their own — read a footer/index, resume a download, or let a columnar/table format read only the needed column chunks without pulling the whole file.

**Two gotchas that cost real money:**
1. **Abort incomplete multipart uploads** — orphaned parts are billed but invisible as normal objects. Add a lifecycle rule.
2. **Expire old versions/snapshots** — a thrice-daily snapshot bucket with no lifecycle rule grows forever.

**Security posture:** private buckets, no public objects — serve public reads through a **CDN/static domain** in front, which is also how you get *real* HTTP/CDN caching for assets. Access via IAM roles and **role assumption** rather than shared keys; provision via a canonical Terraform module (encrypted, versioned, access-controlled, with retention policies).

**Commonly underused capabilities worth knowing:**
- **Presigned URLs** — time-limited GET/PUT without credentials; the idiomatic way to let a client upload/download directly instead of proxying bytes through your app
- **Event notifications** (→ SNS/SQS/Lambda/EventBridge) — the event-driven alternative to polling a bucket
- **Intelligent-Tiering** — near-free cost win on artifact/capture buckets
- **Versioning** — config/artifact rollback
- **Cross-region replication** — a real DR question for a multi-region footprint

**Correctly unused for most shops:** Transfer Acceleration (co-located producers), Requester Pays, S3 Select (superseded by table formats + warehouse), Object Lambda, MRAP, Object Lock (unless compliance demands WORM).

#### When you need it, and when you don't

Object storage is the **cheapest durable place to put bytes you retrieve by name**, and it is close to a default for that job. The decision content is not "should we use it" but **where the boundary sits between a blob and a record** — and what you give up by crossing it.

**Escalation ladder — it runs the other direction here, because object storage is the cheap rung:**
1. **Don't store it.** Can it be recomputed or streamed through?
2. **Object storage** for anything blob-shaped: uploads, artifacts, exports, backups, logs, captures, static assets, raw landing data.
3. **Object storage plus a metadata table.** The pattern that solves most real needs: bytes in the object store, searchable attributes in a database, key as the join. Reach here as soon as you need to *find* objects by anything other than exact key.
4. **A database column** only for small blobs where transactional atomicity with the row genuinely matters.
5. **A table format over object storage** (Iceberg/Delta/Hudi) when the objects are analytical data needing schema, evolution, and time travel — this is the modern answer to "query the data in the bucket."

**Real triggers:** the payload is large or variable-sized; the access pattern is get-by-key; you need durability without operating storage; you want lifecycle-managed retention as a cost mechanism; you need a landing zone that decouples ingestion from transformation (Part 2.3); or you want immutable content-addressed artifacts — which, usefully, are Class A cacheable for free (§ Caching).

**Don't use it when:**
- **You need to query the contents.** Listing and filtering by prefix is not querying. If you are scanning objects to answer a question, you needed a database or a table format.
- **You need low-latency small reads.** Per-request latency is tens of milliseconds — fine for a file, wrong for a hot path lookup.
- **You need transactional updates.** Objects are replaced wholesale; there is no partial in-place update and no cross-object transaction.
- **You need strong ordering or append semantics.** Use a log.
- **It's the source of truth for structured business data.** A JSON file per entity in a bucket is a database with no schema, no index, no transactions, and no concurrency control.

**What you permanently inherit:** **key layout as a permanent design decision** — the prefix scheme determines listing performance, lifecycle-rule targeting, and access-policy granularity, and it is very hard to change once clients depend on it; eventual-consistency reasoning for listings even where object reads are strongly consistent; lifecycle and storage-class policy as an ongoing cost discipline (intelligent tiering is usually a near-free win); versioning as both a rollback superpower and a silent cost accumulator if unpruned; access control at the bucket, prefix, and object layer, where public-by-accident is the classic incident; per-request cost that makes many-small-objects patterns surprisingly expensive; and egress and cross-region charges that make replication a *cost* decision as much as a DR one.

**Deciding question:** Is it a blob? → object storage. Structured data I need to query? → database.

---

### ZooKeeper / etcd / Consul (Coordination)

**What they are:** Distributed coordination stores. A **small** replicated key-value store plus a **consensus protocol**, providing the primitives that are hard in a distributed system: leader election, membership/discovery, config with change notification, and distributed locks.

**The shared core:** a replicated log where a **majority (quorum)** must agree before a write commits. ZooKeeper uses **ZAB**; etcd and Consul use **Raft**. Clusters are almost always **3 or 5** nodes — 3 tolerates 1 failure, 5 tolerates 2; even numbers cost more for no extra tolerance. Consequence: **writes are expensive** (a round-trip to a majority), so these are for rarely-changing metadata, never bulk data.

**The two primitives that make them more than a tiny database:**
- **Watches** — subscribe to a key and be *notified* on change instead of polling
- **Ephemeral state tied to a session/lease** — if the client stops heartbeating, its keys **automatically disappear**. This is what makes leader election and liveness detection work (see Lease-Based Execution in Part 1).

**RIGHT choice when:** leader election, distributed config, service discovery, consensus-backed locks, cluster membership.
**WRONG choice when:** storing more than a few MB, high-throughput reads/writes, application data, or when a database advisory lock suffices.

| | ZooKeeper | etcd | Consul |
|---|---|---|---|
| Consensus | ZAB | Raft | Raft |
| Data model | Hierarchical znodes | Flat KV with prefixes | KV **+ service catalog** |
| Interface | Custom binary client libs | gRPC / HTTP | HTTP / **DNS** |
| Ephemeral primitive | Ephemeral znodes + sessions | Leases | Sessions with TTL |
| Sweet spot | Legacy big-data coordination | **Kubernetes' state store**; cloud-native config | Service discovery + health + multi-DC + mesh |

**Correction — three widespread misconceptions:**

1. **"Distributed systems always use ZooKeeper."** True for the ~2010–2018 big-data generation, now actively reversing. Kafka is moving to **KRaft**; other systems have replaced ZooKeeper with embedded Raft equivalents. ZooKeeper is being **displaced, not deprecated** — it still runs huge legacy fleets and is actively maintained; new systems just stop choosing it.

2. **"ZooKeeper is a single point of failure."** A ZooKeeper *ensemble* is explicitly fault-tolerant — same quorum model as etcd/Consul. The real objections are **operational weight** (a separate distributed system to deploy, tune, patch, and reason about) and **shared-fate coupling** (an external hard dependency whose degradation impairs every system leaning on it). That's the argument for absorbing consensus, not a fragility claim.

3. **"etcd is only for Kubernetes, and we don't use it."** etcd is general-purpose, and if you run Kubernetes you use it **constantly and invisibly** — every pod, service, secret, configmap, and deployment lives in etcd, and every autoscaling decision reads and writes it. Also: gRPC-native is why it's *pleasant to integrate*, not why Kubernetes chose it (simplicity + strong consistency + watches). The category of "needs an **external** coordinator" is shrinking as embedded Raft spreads, but within that category etcd dominates — and it's simultaneously among the most-deployed coordination stores anywhere.

**Also worth separating:** Consul is not only a mesh tool. Its four pillars are discovery, health checking, **KV**, and multi-datacenter federation — and the KV + sessions half is what powers application **leader election**, often the heaviest internal use.

**Failure modes:**
- **Session expiry / lost session** — a coordinator blip can leave a client unable to recover without a restart. The client **must** re-initialize its session on coordinator errors.
- Transient dual-leader behavior during a partition — consensus prevents divergence, but understand the TTL window and make singleton work idempotent or fenced.
- Storage misuse — these are not databases.
- **Forgotten criticality** — a quiet coordination store is a hard dependency of loud, revenue-critical services. Mark it P1 and alert on it.

#### When you need it, and when you don't

The framing that gets this right: a coordination store is **consensus as a service**, and consensus is expensive enough that you should be certain you need it. Most requirements that sound like coordination are really "make this operation safe to run twice," which has far cheaper answers.

**Escalation ladder — the first three rungs eliminate most cases:**
1. **Make the operation idempotent.** If running twice is harmless, you do not need mutual exclusion at all. **This is the single most effective move**, and it removes the requirement rather than satisfying it.
2. **A database row lock, unique constraint, or advisory lock.** You already run a consistent store; a unique key on a natural identifier is a distributed lock with no new infrastructure. Adequate for the large majority of singleton needs.
3. **Your platform's built-in primitive.** A Kubernetes lease, a cloud scheduler with a singleton guarantee, or a managed cron already backed by consensus — use the coordination that is already running rather than adding your own.
4. **The system's embedded consensus.** Modern platforms increasingly ship their own (KRaft and equivalents), removing the external dependency entirely.
5. **An external coordination store** (ZooKeeper/etcd/Consul) when you need watches, ephemeral session-tied state, or leader election across a fleet with genuine fencing requirements.

**Real triggers:** leader election where exactly one instance must act and failover must be automatic; membership and liveness detection where ephemeral session-tied keys do the work for you; configuration with **change notification** (watches, so consumers do not poll); service discovery with health integration; or locks requiring fencing tokens because a stale lock holder must be prevented from acting.

**Don't adopt when:**
- **A unique constraint would do.** Enormously cheaper, and it is the correct answer more often than the coordination store is.
- **The work is idempotent.** You are buying exactly-once semantics for something that does not need them.
- **Volume or size is more than a few MB, or writes are frequent.** Every write is a round trip to a quorum. These are metadata stores; using one as a database is the classic misuse.
- **The call is in-process or single-instance.** No distribution, no coordination problem.
- **You would be adding a second distributed system to avoid one migration.** Weigh the permanent operational weight against the one-time cost.

**What you permanently inherit:** a quorum-sized cluster (3 tolerates one failure, 5 tolerates two; even sizes cost more for no gain) to deploy, patch, monitor, and back up; **session and lease semantics as application-level responsibility** — a client must re-initialize its session on coordinator errors, and forgetting this is the classic bug where a blip leaves an instance permanently unable to recover; a TTL window during which transient dual-leader behaviour is possible, so singleton work must be idempotent or fenced regardless; write cost that permanently caps how much you can put there; **shared-fate coupling**, because a quiet coordination store becomes a hard dependency of loud revenue-critical services; and the operational trap that follows — it must be alerted on as a P1 despite being invisible day to day.

**Correcting the fragility framing:** an ensemble is not a single point of failure; it is quorum-fault-tolerant with the same model as Raft-based alternatives. The real arguments against are operational weight and shared-fate coupling — which is exactly why the industry trend is to *absorb* consensus into systems rather than depend on an external coordinator.

**Deciding question:** Need distributed coordination (leader election, locks, config, discovery)? → a coordination store, sized 3–5 nodes. Storing application data? → a database.

**Industry trend:** toward **self-contained consensus** — absorb the coordinator (KRaft and friends) rather than depend on an external one. Fewer moving parts, fewer hidden coupling surfaces.

---

### CDN (Content Delivery Network)

**What it is:** Globally distributed cache of content served from edge locations near users.

**RIGHT choice when:** static content for a global audience, latency reduction for distributed users, offloading origin traffic, semi-static cacheable API responses.

**WRONG choice when:** highly personalized per-request content (cache-key explosion, low hit rate), content changing every request, single-region users, or strong consistency requirements.

**Pull vs push:** pull fetches from origin on miss (simpler, first request is cold); push preloads proactively (good for predictable large content).

**Invalidation options:** TTL (accept staleness), purge API (explicit), **versioned URLs** (`/static/app.v42.js` — never invalidate, just deploy a new name). Versioned URLs are the lowest-risk choice.

**Why this matters beyond assets:** the CDN/client edge is the **only place free HTTP caching lives**. Internal service-to-service hops have no edge, and a `POST`-based API edge forfeits it. So if a hot, static, high-repeat resource needs caching, the two real levers are **CDN at the client edge** and an **explicit cache tier at the owning service** — nothing in between recovers it for free.

#### When you need it, and when you don't

A CDN is two products sold as one: **geographic latency reduction** and **origin offload**. Separating them clarifies the decision, because a single-region audience may need the second without the first — and increasingly a third reason dominates both, which is that the CDN is where TLS termination, DDoS absorption, and edge routing live.

**Escalation ladder:**
1. **Correct cache headers on your origin.** Costs nothing, makes browsers stop asking, and is a prerequisite for every rung below — a CDN in front of uncacheable responses does nothing.
2. **Content-hashed asset filenames.** Turns static assets into Class A immutable cacheables (§ Caching) with no invalidation problem, forever.
3. **Compression and payload reduction.** Often a larger win than edge placement for a single-region audience.
4. **CDN for static assets.** Near-default for anything public and blob-shaped; effectively free at this point.
5. **CDN for cacheable dynamic responses**, with deliberate keying and short TTLs.
6. **Edge compute** only when a decision genuinely must be made close to the user (routing, auth checks, A/B assignment, personalization at the edge).

**Real triggers:** geographically distributed users where RTT dominates (a physics problem no origin scaling solves); high-volume static or semi-static content where origin offload is the point; traffic spikes needing absorption in front of the origin; TLS termination and connection reuse close to the user, which improves even single-region latency; and DDoS absorption plus WAF, which for many teams is the actual reason to adopt.

**Don't rely on it when:**
- **Every response is personalized.** Per-user content has a hit rate near zero — you have added a hop, not a cache. Split shared fragments from personalized ones first (the key-reshaping idea from § Caching).
- **Users are in one region and the content is dynamic.** The latency win is small; you may still want it for TLS and protection, but not for caching.
- **Content must be strictly fresh.** Purge propagation is not instantaneous, and designs that assume it are the source of "we purged but users still see the old thing."
- **Responses vary on dimensions you have not put in the cache key.** This is not a performance bug, it is a **correctness and security** bug — serving one user's response to another. Auth-varying responses at the edge deserve real paranoia.

**What you permanently inherit:** cache-key and `Vary` correctness as a security-sensitive design surface; **purge as an operational procedure** with propagation delay, which pushes you toward versioned URLs so you never need to purge; another layer in the request path to debug, where cache-status headers become essential and "is it the edge or the origin?" becomes a routine question; origin-shield and cold-edge behaviour, since a low hit ratio means the origin still sees the traffic it thought it had offloaded; configuration that lives outside your application repository unless deliberately managed as code; and a capacity dependency of the uncomfortable kind — the origin must be able to serve a full cache miss at peak, exactly as with any other cache.

**Deciding question:** Static/semi-static AND multi-region? → CDN. Dynamic, personalized, single-region? → origin.

---

### Flink / Stream Processing

**What it is:** Distributed stream processing framework for unbounded data with fault-tolerant state.

**The one thing it is fundamentally for:** computing a result that depends on **many events**, **continuously**, at **low latency**, where intermediate state **survives failure exactly-once**. Remove any one of those four and something simpler wins.

**Capability triggers (the real "why"):**
1. **Windowed aggregation** — running counts/sums/rates over a bounded slice of an unbounded stream; requires recoverable buffered state
2. **Stream-to-stream joins** within a time bound — must hold both sides' recent events in recoverable state
3. **Complex event processing** — ordered pattern detection ("A then B but not C within T"), requires per-key partial-match state
4. **Large continuously-updated keyed state** — millions of keys, needs a spillable checkpointed backend (RocksDB), not a HashMap
5. **Exactly-once stateful pipelines** where state and output must be atomically consistent with input offsets

**Situational triggers (the "when"):** latency requirement is seconds not minutes (which disqualifies warehouse ELT); the same computation is reused by many consumers (compute once centrally); **reprocessing/replay** through updated logic matters (savepoints, unified batch+stream); state outgrows a single process.

**Key concepts:** tumbling/sliding/session windows; **watermarks** (event-time progress, when a window is complete); late-event handling (side output or update); **checkpointing** for exactly-once recovery; state backends.

#### When you need it, and when you don't

**When NOT to jump, and what to use instead:**

| Situation | Right tool |
|---|---|
| Per-event stateless transform | Plain Kafka consumer |
| CDC "id changed → refetch truth" | Consumer + refetch (**this shape avoids needing stream state at all**) |
| Analytics tolerating minutes of latency | Warehouse ELT (land raw, transform at rest) |
| Modest stateful streaming inside Kafka | **Kafka Streams / ksqlDB** — windowing, joins, fault-tolerant state as a *library*, no cluster |
| Heavy state, CEP, big scale, batch+stream, multi-source | Flink — preferably **managed** to shed ops cost |

**The escalation ladder (climb only as far as the workload forces):** plain consumer → warehouse ELT → Kafka Streams/ksqlDB → Flink.

**Two independent triggers, and why keeping them separate matters:** if **volume** grows but the pattern stays per-event and stateless, you still don't need Flink — scale consumers horizontally. If a **windowing/join/pattern requirement** appears even at *small* volume, low volume no longer saves you. Capability is the real trigger; volume is only the cost trigger.

**What you permanently inherit:** a stateful cluster with checkpointing, which is a genuinely different operational class from stateless consumers — checkpoint tuning, state-backend sizing, and recovery time all become your problem; **state as a schema with a migration story**, since savepoint compatibility constrains how freely you can change job logic; event-time and watermark semantics that must be reasoned about explicitly, where late-data policy is a business decision disguised as a config value; backpressure behaviour and its interaction with checkpoint duration, the classic cause of a job that degrades rather than fails; a job-deploy lifecycle separate from your service deploys, with savepoint-restore as a routine procedure; and exactly-once guarantees that hold only when sources and sinks cooperate — a non-transactional sink silently reduces you to at-least-once.

**Deciding question:** Do I need fault-tolerant state **across** events, computed continuously at low latency with exactly-once correctness? → stream processor. Simple per-event transform? → consumer. Batch analytics? → warehouse.

---

## Part 4: Constraint → Solution Mapping (Quick Reference)

| Constraint | Pattern | Tool options |
|---|---|---|
| High read volume | Cache | In-memory → Redis/Valkey → CDN (layered) |
| High write burst (async OK) | Queue/buffer | Kafka (replay) vs SQS (simple) |
| High write burst (sync required) | Scale write path | Shard, batch+flush, back-pressure (429) |
| Slow processing | Async job | Message queue + worker pool |
| Read/write contention | Separation | Read replica, CQRS, materialized views |
| Data growing unbounded | Tiering | Hot/warm/cold, TTL, archive to object storage |
| External service unreliable | Resilience | Circuit breaker + timeout + fail-open + fallback |
| Multiple services need same data | Shared state | Redis, event-driven invalidation, CDC |
| Need audit trail | Append-only log | Event table, Kafka topic, event sourcing |
| Caller needs durability guarantee | Sync persist | Must hit the durable store before 200 |
| Caller only needs acceptance | Fast-ack + async | Accept into fast store, 200, persist async, reconcile |
| Business operation spans services | Distributed transaction | Saga (simple) or TC/C (parallel) |
| Global users, static content | Edge delivery | CDN + versioned URLs |
| Need unique time-sortable IDs | Distributed ID gen | Snowflake-style (64-bit, no coordination) |
| Need full-text search | Search index | Elasticsearch/OpenSearch (secondary, never source of truth) |
| Need coordination / leader election | Consensus service | ZooKeeper / etcd / Consul (3–5 nodes) |
| **Known refresh interval, client-driven** | Polling | HTTP + `ETag`/deltas |
| **Server must push immediately, one direction** | Streaming | SSE (stateless, proxy-friendly) |
| **Simultaneous two-way / binary / high-rate** | Bidirectional channel | WebSocket (stateful — plan sticky sessions) |
| **"It's slow" — cause unknown, many layers** | Attribute before optimizing | Tracing → layer walk → shape classification (Part 2.4) |
| p50 regressed at a deploy | Regression, not capacity | Diff review + revert; skip the capacity work |
| p99 bad, p50 fine, high fan-out | Tail amplification | Reduce fan-out, hedge, timeout, fail-open non-critical |
| Everything slow simultaneously | Saturation / queueing | Pool + concurrency limits, shed load, add capacity |
| Latency ∝ number of items on page | N+1 / fan-out | Batch + dedup (DataLoader), not a cache |
| Spans sum ≪ end-to-end latency | Queueing before the work starts | Thread/connection pool, event-loop lag, admission control |
| Rows examined ≫ rows returned | Missing/non-selective index | Index or rewrite the query — never cache over it |
| **"Will it hold at 10x?"** | Find the binding constraint | Little's Law estimate → stress test to the knee (Part 2.5) |
| Slow only above a load threshold | Capacity, not latency | Utilization knee — target 50–70%, not 90% |
| Latency high, DB CPU low | Connection/thread pool exhaustion | Size with `throughput × latency`; add pool before pods |
| Writes plateau, reads scale fine | Single-writer constraint | Shard/partition; replicas don't help writes |
| Throughput pinned to a round number | Downstream quota or hand-set throttle | Their limit is your capacity — cache, queue, or negotiate |
| Throughput plateaus with CPU idle | Lock / hot-key contention | Shard the key, coalesce; some serialization is irreducible |
| Brownout escalates to outage | Retry amplification | Retry budget at one layer, backoff **with jitter**, breaker |
| Spike breaks it, gradual growth fine | Autoscaling lag | Headroom absorbs spikes; autoscaling only handles trends |
| Demand may exceed capacity regardless | Load shedding | Rate limit + degrade + back-pressure — plan it before you need it |
| **Content slow to produce, revealed progressively** | Stream it | SSE with typed events |
| **N clients each composing M fragmented services** | Composition layer | GraphQL Federation (shallow graph) |
| **Same entity referenced many times in one request** | Intra-request dedup | DataLoader batch loader |
| **Same entity re-requested across requests** | Cache the owner | Redis/Valkey **at the owning service** |
| **Proven-hot internal M2M hop (benchmarked)** | Binary RPC | gRPC (per-edge, L7 LB required) |
| **True bidirectional server-to-server streaming** | RPC streaming | gRPC bidi |
| **Derived store must survive restart/redeploy fast** | Artifact bootstrap | Object storage snapshot + change-log offset |
| **Derived store index must swap safely** | Versioned index + alias | Build new version → atomic alias repoint |
| **Incremental ingestion must be replay-safe** | Durable watermark | Advance only after successful idempotent upsert |
| **Incrementals can't express deletion** | Completeness backstop | Periodic full rebuild from source |
| **Streaming workload starves page-serving pods** | Route isolation | Separate target group / streaming BFF |
| **Autoscaler blind to held-open connections** | Custom metric | `active_streams` gauge + dual trigger (CPU + streams) |
| **Long-held connections exhaust a scarce upstream** | Load shedding | Per-pod concurrency cap, 503 early, client handling |
| **Handshake cost dominates short queries** | Connection pooling | Driver pool with tuned `min`/`maxPoolSize` |
| **Need state across events (windows/joins/patterns)** | Stream processing | Kafka Streams (no cluster) → Flink (heavy state) |
| **Analytics tolerating minutes of latency** | ELT | Land raw in object storage → warehouse transform |
| **Exactly one instance must run a job** | Leader election | Session + KV lock (Consul/etcd/ZK), TTL heartbeat |
| **Large file transfer must be reliable** | Multipart upload | SDK transfer manager (parallel parts, per-part retry) |
| **Swarm of tiny objects** | Logical batching | Aggregate records into right-sized objects |
| **Client needs direct upload/download** | Presigned URL | Time-limited URL, no proxying bytes through the app |
| **Orphaned cost in object storage** | Lifecycle rules | Expire old versions + abort incomplete multipart |

---

## Part 5: Tradeoff Pairs (One-Liners)

| Decision | A | B | The deciding question |
|---|---|---|---|
| Relational vs document | ACID, joins, constraints | Flexible schema, horizontal scale | Need transactions or joins? → relational |
| Redis vs in-memory cache | Shared across instances | Zero latency, no serde | Multiple instances need the same view? → Redis |
| Kafka vs SQS | Replay, ordering, multi-consumer | Managed, simple, cheap | Need replay or multiple consumers? → Kafka |
| REST vs gRPC | Human-readable, browser-compatible | Binary, typed, streaming | External API? → REST. Internal + hot? → gRPC |
| Sync vs async | Simple, immediate consistency | Decoupled, absorbs burst | User waiting? → Sync |
| Push vs pull fan-out | Fast reads (pre-built) | No wasted writes | Most users low-follower? → Push, hybrid for celebrities |
| Strong vs eventual consistency | Correct, higher latency | Fast, stale possible | Money/inventory? → Strong |
| Monolith vs microservice | Simple ops, fast iteration | Independent scale and ownership | Early stage? → Monolith |
| Optimistic vs pessimistic locking | No lock held, conflict on write | Lock held, blocks others | Low conflict? → Optimistic |
| **SSE vs WebSocket** | Stateless, proxy-friendly, one-way | Bidirectional, binary, high-rate | Client sends *while* server streams? → WebSocket |
| **Polling vs streaming** | Simple, cacheable, client-driven | Immediate, server-driven | Is the interval known? → Poll |
| **REST+CDN vs federation** | Free edge caching on repeats | Composition on cold, fragmented reads | High repeat + low fan-out? → REST+CDN |
| **Batching vs dedup** | Fewer round-trips | Less downstream **work** | Is fan-in high (many refs → few entities)? → dedup is the real win |
| **Entity reference vs `@provides`** | Router batches and hydrates | Fields returned inline, zero hydration | Does the subgraph already hold the data? → `@provides` |
| **Reference vs scalar id** | Router-hydrated, batched | Consumer hydrates in a second query | Is the key **dependent** on a prior call? → scalar id |
| **Shared library vs owning service** | Cheapest for same-language pure logic | Works across languages | Are consumers polyglot? → owning service |
| **Fewer vs more partitions** | Less metadata/coordination overhead | Headroom for consumer scale-up | Size to *max useful consumers*, not current pods |
| **Global order vs throughput** | 1 partition, fully serialized | N partitions keyed by entity | Need per-entity order only? → key by entity |
| **Build-from-source vs dump a node** | Authoritative, resumable, format-independent | Mechanically simpler | Is the node a derivative? → always build from source |
| **Snapshot cadence vs source load** | Fresher baseline | Less pressure on the source | Widen the lookback window before adding runs |
| **Multi-doc transaction vs bulk write** | Cross-document atomicity | Throughput, one command many atomic ops | Can the document embed it? → bulk write |
| **Write-through vs write+invalidate** | Cache warm immediately | No cache/DB divergence on partial failure | Durable business data? → write DB, invalidate |
| **TTL vs event invalidation** | Simple, bounded staleness | Fresher, more moving parts | Use **both**: events with a long TTL backstop |
| **Local L1 vs shared L2** | Microsecond, no hop | One consistent view | Is the object large or hot-and-immutable? → local |
| **Consensus store vs embedded Raft** | Reusable across systems | No external dependency to operate | Building the system itself? → embed |
| **Stream processor vs consumer** | State across events | Simplicity | Do you need windows/joins/patterns? → processor |

---

## Part 6: Recurring Meta-Principles

The reasoning that generalizes beyond any single tool.

**1. Truth lives upstream; everything downstream is a bounded-staleness derivative.**
The job of a system is to keep that staleness **bounded and recoverable** — never to promote a derivative into the source. Applies to search indices, caches, read models, and node-local state alike. Corollary: never seed a backup from a replica, because one node's drift becomes everyone's starting point.

**2. Logic belongs with whoever owns the data it derives from.**
Domain-semantic derivations belong in their domain (computed or not). Cross-domain composition belongs to a service that owns that composition. Presentation belongs to the app. The anti-pattern is a shared concern owned in the wrong place — and it wears different costumes at different zoom levels (a monolith, a bespoke orchestrator, a catch-all subgraph, a deep subgraph re-resolving someone else's entity).

**3. Convenience is a tiebreaker, never a justification.**
"It's already wired up" can legitimately choose *between* correct homes; it can never *make* a home correct. Otherwise the busiest junction accretes all logic and becomes a distributed monolith with a single critical-path chokepoint.

**4. Identify the real bottleneck before adding capacity.**
More partitions don't help if the constraint is a downstream API. More replicas don't help if the pool is exhausted by latency. Every scaling lever should follow a measurement, not an intuition.

**5. Distinguish the capability trigger from the cost trigger.**
Volume tells you *when* something becomes expensive; capability tells you *whether* the simpler tool can do the job at all. Adopt heavy platforms only when a capability is genuinely required (state across events, true bidi streaming, cross-domain composition) — then climb the operational-weight ladder only as far as forced.

**6. Every platform has an exit cost — choose which lock-in fits the dominant workload.**
There is no commitment-free option at the architecture layer. Weight by blast radius and reversibility: event sourcing reaches the definition of truth, a composition platform reaches client contracts, a transport choice reaches service edges and is reversible per-edge.

**7. Consequences are not justifications.**
Decomposition is justified by **boundary and independence** (independent deploy, scale, failure domain); the resilience and observability wins are **dividends the boundary pays**, because those controls only become expressible once the concern has its own home. Mistaking the dividend for the reason leads to decomposing the next thing "for speed" — and decomposition usually makes a single request *slower*.

**8. Ask what the failure path costs, not just the happy path.**
A circuit breaker that dumps cache traffic onto the primary datastore. A load shedder that 503s the user. A fail-open timeout that returns a null field. Every resilience mechanism relocates load rather than deleting it — know where it lands.

**9. Symmetry and interchangeability are features.**
Leader election works precisely *because* nodes are interchangeable: zero config, automatic failover, race-safety for free. Optimizing *which* node wins would solve a problem that doesn't exist at the cost of the simplicity that makes it reliable.

**10. Prefer designs that keep the workload simple enough that heavy tooling never becomes necessary.**
Invalidate-then-refetch keeps consumers stateless, which is why a stream processor isn't needed. Keeping numbers in a hydrated card rather than generated prose is why a text/data mismatch stays rare. The best architectural move is often the one that removes the need for a later one.

**11. Simulate the decision in logs before building the mechanism.**
Most design arguments can be converted into a number for the cost of one log line, with nothing deployed and no risk. Log the cache key you *would* use and count distinct values → projected hit rate. Log the shard key you *would* route on → skew. Log the batch you *would* assemble → real fan-in. Log which fields clients actually read → the projection you should have. The pattern generalizes: when a design choice depends on the shape of production traffic, **instrument the hypothesis, don't debate it.** Corollary: prefer measurements available *before* commitment over metrics you'd only see *after* deploying the thing you're trying to justify.

**12. Headroom is not waste — it is the budget you spend on latency, spikes, and failover.**
The last 20% of utilization is bought at a brutal latency price, because waiting scales as `1/(1−utilization)`. A system at 90% is not "efficiently provisioned," it is one traffic bump from a latency cliff and has nothing left to absorb a node loss. This is why capacity incidents look sudden: the knee is non-linear, so the system is fine until it very abruptly isn't. Corollary: capacity is set by **one binding constraint at a time**, so adding capacity anywhere else changes nothing — and relieving the constraint just promotes the next one, which you should name in advance.

---

## Part 7: Corrections Index

Claims that are commonly stated and wrong or overstated. Each is expanded in place above.

| Common claim | The accurate version |
|---|---|
| "WebSocket holds far more concurrent connections than SSE" | Near-identical per-connection cost; capacity is FDs/memory/event-loop plus app throttles. SSE's only real limit is the ~6-per-domain HTTP/1.1 browser cap, removed by HTTP/2 |
| "A low stream cap is an SSE limitation" | It's an application throttle protecting a scarce upstream (LLM concurrency, per-stream memory) |
| "HTTP/2 push can replace SSE" | Deprecated in browsers; not an alternative |
| "Streaming is needed because the payload is large" | It's needed because the payload is **slow to produce and revealed progressively** |
| "DB caches are usually disabled" | Engine caches (buffer pool, WiredTiger) are always on; the *ORM second-level/query* cache is what's often disabled |
| "Write-through gives strong consistency" | Cache and DB writes aren't atomic; prefer write-DB-then-invalidate |
| "Redis is a persistence layer" | Treat as ephemeral: ~1s fsync, journals may not be backed up, restore may not exist |
| "A distributed cache is always better than local" | A >500KB value can turn ~1ms into seconds and exhaust the pool; local was the fix |
| "Going direct instead of via the router restores free caching" | Free edge caching lives only at the **client edge**; internal hops never had it. Caching and routing are orthogonal axes |
| "The router's caching improves data performance" | Plan/normalization cache saves **router CPU**; entity/response caching is the hard, often-unbuilt part |
| "MongoDB prefers many small ops, so avoid bulk" | Conflates multi-doc **transactions** (avoid) with **bulk writes** (strongly preferred) |
| "Elasticsearch is slow to write, so keep it in sync directly" | Maintain it as a derived store: relational → read model → change events → index, with a dedicated ingestor |
| "Elasticsearch/OpenSearch can be the source of truth" | Always pair with a primary store; rebuild-from-source is the recovery model |
| "Snapshot the running index — simpler than rebuilding" | A node index is a derivative with baked-in drift, no crisp resume offset, and physical format coupling |
| "A new snapshot re-bases the fleet" | Nodes adopt a snapshot only on **startup**; continuous change consumption is the freshness mechanism |
| "One consumer with two partitions processes them in parallel" | Not guaranteed by Kafka; parallelism comes from more consumer **instances** |
| "partitions = consumers is the rule" | Conservative default; size to **max useful consumers** with headroom, and avoid over-partitioning overhead |
| "GraphQL is a data store / read-only / can't do writes" | It's a contract + composition layer; `mutation` and `subscription` are first-class. Writes stay on REST because federation has **no cross-subgraph atomicity** |
| "gRPC is REST over a better connection" | Four pillars: HTTP/2 multiplexing, protobuf, IDL+codegen, four call types incl. bidirectional |
| "gRPC is about performance, GraphQL isn't" | Different axes: GraphQL attacks round-trips/over-fetch, gRPC attacks wire serialization |
| "@provides means the subgraph fetches the entity" | It's a **declaration** that fields are already present (`resolvable: false`); only free if the data is already held |
| "A subgraph can call back into the router" | Resolution flows strictly downward; if a subgraph must fetch, it calls the owning service directly |
| "Logic is logic, data is data" | Too clean — it exiles legitimate derived domain attributes. The axis is **whose** logic |
| "Distributed systems always use ZooKeeper" | Being displaced (KRaft and equivalents); still maintained and widely deployed, just not chosen for new systems |
| "ZooKeeper is a single point of failure" | The ensemble is quorum-fault-tolerant; the real costs are operational weight and shared-fate coupling |
| "etcd is only for Kubernetes, and we don't use it" | If you run Kubernetes, you use it constantly and invisibly — it stores all cluster state |
| "Consul is a service mesh tool" | Four pillars: discovery, health, **KV**, multi-DC. KV+sessions powers leader election, often the heaviest use |
| "Decomposition was justified by performance" | Justified by boundary/independence; resilience and observability are dividends the boundary pays |
| "Chunked upload means the SDK split the file" | Distinguish **logical batching** (records per object) from **transfer chunking** (bytes per part) |
