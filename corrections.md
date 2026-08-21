# Corrections Log

Append-only. Each entry records a claim I held or that is commonly stated, the accurate version, and **why the error was tempting** — that last part is what stops the mistake recurring.

Never edit an entry. If a correction is later itself corrected, append a new one referencing it.

---

## 2026-08-19 — Streaming and connections

### WebSocket holds far more concurrent connections than SSE
**Believed:** ~5k (WebSocket) vs ~50 (SSE) — a protocol capability gap.
**Accurate:** Both are one long-lived TCP connection with near-identical per-connection cost. Capacity is set by file descriptors, memory, and event-loop headroom — plus application throttles. If anything SSE is marginally *lighter* per idle connection (no frame decoding, no ping/pong machinery).
**Why it was tempting:** The two numbers were real, but they measured different things — one was a protocol's observed deployment, the other was an app-level throttle. Comparing them implied a protocol difference that doesn't exist.
**The one real SSE limit:** the HTTP/1.1 ~6-connections-per-domain *browser* cap. Removed by HTTP/2 multiplexing. Client-side, not server-side.

### A low stream cap is an SSE limitation
**Accurate:** It's a deliberate load-shedding throttle protecting a scarce *upstream* (LLM concurrency, per-stream memory). Raising it wouldn't help; the bottleneck was never the protocol.
**Generalization:** When you see a suspiciously round limit (50, 100, 1000), suspect a hand-set throttle before a technical ceiling.

### Streaming is needed because the payload is large
**Accurate:** Streaming is needed because the payload is **slow to produce and revealed progressively**. A chat reply is a few KB — tiny. It takes 5–30s to generate. That's the trigger.
**Test that proves it:** the same system returns plain JSON (no streaming) for responses that are already complete, e.g. hydrating existing history. Same size, no streaming, because nothing is being produced over time.

### HTTP/2 Server Push can replace SSE
**Accurate:** Deprecated in browsers, and it was never an application-level server→client push mechanism anyway. Not an alternative.

### The connection pool is held for the request duration
**Believed:** A long-lived stream holds its DB connection the whole time.
**Accurate:** A pooled DB connection is checked out per **operation** (~5–10ms) and returned. One 20s stream may borrow and return a connection 6–8 separate times.
**Consequence:** 50 stream slots and a 50-connection DB pool are opposite scarcities. 50 pooled connections comfortably serve hundreds of concurrent streams; 50 stream slots fill fast. Same number, hold times differing by three orders of magnitude.
**Why pools stay open at all:** amortizing TCP + TLS + auth + topology handshake (10–100ms) against a 5–10ms query. Nothing to do with streaming.

---

## 2026-08-19 — Caching

### DB caches are usually disabled
**Accurate:** Engine caches (buffer pool, WiredTiger cache) are fundamental and always on — disabling them would make the DB unusable. What's often deliberately disabled is the **ORM second-level / query cache**, because invalidation is hard, data changes outside the app, and the engine already caches pages.
**Why it was tempting:** Both get called "the database cache."

### Write-through gives strong consistency
**Accurate:** Cache and DB writes are not atomic. Cache-write-succeeds + DB-write-fails leaves the cache serving data the source never accepted — worse than stale, because it's *fabricated*. Prefer **write DB, then invalidate cache**.

### A distributed cache is always better than a local one
**Accurate:** A >500KB value can turn a ~1ms Redis op into seconds and exhaust the connection pool. Moving to a local in-process cache was the fix — accepting one copy per pod and a cold miss after restart.
**Generalization:** object size is a first-class cache-admission criterion, not an afterthought.

### Redis is a persistence layer
**Accurate:** Treat as ephemeral — ~1s fsync (not per-write), journals may not be backed up, restore may not exist. Anything durable belongs in a real store.

### Caching is needed once traffic grows
**Refined:** Traffic is the *amplifier*, not the trigger. The trigger is `repeat rate × source cost`. High traffic with low repeat rate gains nothing. Caching a 2ms indexed lookup buys almost nothing while costing invalidation forever.
**The question that matters most:** can the source survive 100% miss at peak? A cache hides the inefficiency it papers over, which makes a cache outage a *capacity* incident, not a latency one.
**Also:** the "adds a failure point, hurts debuggability" instinct applies to **coherent** caches (mutable entities). **Coherence-free** caches (content-hashed assets, buffer pool, query plans) have nothing to invalidate — adopt those on day one.

---

## 2026-08-19 — GraphQL, gRPC, composition

### GraphQL is a data store / read-only / can't do writes
**Accurate:** It's an API contract + composition layer over other stores. `mutation` and `subscription` are first-class operations. Writes stay on REST *by choice*, because federation has **no cross-subgraph atomicity** — so writes needing transactional integrity belong on the owning service.

### The router's caching improves data performance
**Accurate:** The plan/normalization cache saves **router CPU** on repeated query shapes. Entity/response caching — the part that would save a backend round-trip — is the hard part and often unbuilt. Verify before assuming.

### Going direct instead of via the router restores free caching
**Accurate:** Free edge caching exists only at the **client edge** (browser↔CDN, keyed on a GET URL). Internal service-to-service hops never had it. Caching and call-routing are **orthogonal axes** — cache the owning service and you get caching under either pattern.
**Why it was tempting:** "GraphQL gives up free caching" is true, but the loss is at the client edge, not on internal hops — so an internal reroute can't recover it.

### gRPC is REST over a better connection
**Accurate:** Four pillars, only one of which is the connection: (1) HTTP/2 multiplexing, (2) protobuf binary serialization, (3) IDL + generated typed stubs, (4) four call types including bidirectional streaming. Only *unary* maps onto a REST request.

### gRPC is about performance, GraphQL isn't
**Accurate:** Different axes. GraphQL attacks round-trips and over-fetch; gRPC attacks wire serialization cost. Neither optimizes the other's axis.

### `@provides` means the subgraph fetches the entity
**Accurate:** It's a **declaration** that the fields are already present in the subgraph's own response (`resolvable: false` tells the router not to hydrate). Only free when the subgraph already holds the data as part of its own job. If it would need an extra call to satisfy it, don't.

### A subgraph can call back into the router
**Accurate:** Resolution flows strictly downward. A subgraph calling back up is re-entrant, wastes planning overhead, doubles router QPS, and complicates auth/tracing. If a subgraph must fetch, it calls the **owning service directly**.

### "Logic is logic, data is data"
**Accurate:** Too clean — taken literally it exiles legitimate derived domain attributes (a computed flag over a domain's own fields belongs in that domain). The axis is **whose** logic: domain-semantic derivation → that domain; cross-domain composition → an orchestrating service; presentation → the app.

### Decomposition was justified by performance
**Accurate:** Justified by **boundary and independence** (independent deploy, scale, failure domain). Resilience and observability are *dividends the boundary pays*, not the reason it was drawn. Mistaking a consequence for a justification leads to decomposing the next thing for speed — and decomposition usually makes a single request *slower*.

---

## 2026-08-19 — Derived stores and search

### Elasticsearch is slow to write, so keep it in sync directly from the DB
**Accurate:** Maintain it as a **derived store**: relational source → denormalized read model → change events → index, with a dedicated ingestor. Not a binlog piped into the index.

### Elasticsearch/OpenSearch can be the source of truth
**Accurate:** Always pair with a primary store. Rebuild-from-source is the recovery model, which only works if the source exists.

### Snapshot the running index — simpler than rebuilding from source
**Accurate:** A node's index is a **derivative** — baseline plus hours of incremental changes. Dumping it captures baked-in drift, gives no crisp resume offset (mid-application, per-segment), couples the artifact to a physical index format, and blesses one node's particular state as canonical for all future nodes.
**Why it was tempting:** mechanically it *is* simpler. It's simpler the way copying a neighbour's answer is simpler.

### A new snapshot re-bases the fleet
**Accurate:** Nodes adopt a snapshot only on **startup** (deploy, restart, bounce, scale-up). A long-running node keeps its on-disk index and stays fresh via continuous change consumption. Snapshots exist for **fast bootstrap + recovery**, not steady-state freshness — which is why "bounce the pod" is the standard fix for a drifted node.

### Chunked upload means the SDK split the file
**Accurate:** Distinguish **logical batching** (how many records per object — an application choice) from **transfer chunking** (multipart: how many byte-parts per object — an SDK choice above a size threshold). Both are called "chunked."

---

## 2026-08-19 — Kafka, coordination, stream processing

### One consumer holding two partitions processes them in parallel
**Accurate:** Not guaranteed by Kafka. Parallelism comes from more consumer **instances**; whether one instance fans work to threads is an application/framework choice.

### partitions = consumers is the rule
**Accurate:** A conservative default. Size to **max useful consumers** with headroom. Over-partitioning has real costs (metadata, coordination, metrics cardinality).

### Distributed systems always use ZooKeeper
**Accurate:** Being **displaced**, not deprecated — still maintained and running huge legacy fleets, but new systems choose built-in Raft (KRaft and equivalents) or etcd. The trend is absorbing consensus into the system to remove an external dependency.

### ZooKeeper is a single point of failure
**Accurate:** A 3/5-node ensemble is quorum-fault-tolerant — the same model as etcd/Consul Raft. The real costs are **operational weight** (a second distributed system to run) and **shared-fate coupling** (its degradation impairs everything depending on it).

### etcd is only for Kubernetes, and we don't use it
**Accurate:** If you run Kubernetes, you use etcd constantly and invisibly — it stores all cluster state (every pod, service, secret, configmap). You don't operate it; you depend on it totally.

### Consul is a service mesh tool
**Accurate:** Four pillars — discovery, health checking, **KV**, multi-datacenter. KV + sessions powers **leader election**, which is often the heaviest real use. Also: Linkerd is a separate product (Finagle lineage), not Consul.

### Leader election uses health checks to pick the leader
**Accurate:** Application leader election is built on **KV + sessions**, not the service catalog or health checks. The liveness signal is session heartbeat renewal. Consul's *internal* Raft leader is a different thing entirely.

### No Flink means a stream-processing gap
**Accurate:** Two independent reasons it isn't needed, which would fail independently. (1) **Capability:** the workload is per-event and stateless — CDC-invalidate-then-refetch deliberately avoids needing cross-event state. (2) **Cost:** low volume doesn't justify a stateful checkpointing cluster.
**The real trigger for Flink:** fault-tolerant **state across events** (windows, stream joins, CEP, large keyed aggregates), computed continuously, at low latency, with exactly-once correctness. Volume alone never forces it; a windowing requirement does — even at low volume.

---

## 2026-08-19 — Caching: measuring the trigger (follow-up)

### If you don't know the data shape, you have to guess whether a cache will help
**Believed:** Repeat rate is knowable by intuition for some data (config data → repeated; per-user data → not) and otherwise unknowable until you build the cache and watch the hit rate.
**Accurate:** Repeat rate is **measurable before building anything.** Log the cache key you *would* use, count total requests and distinct keys over one candidate-TTL window, and compute `projected hit rate ≈ 1 − (distinct keys / total requests)`. That is the hit rate you would have gotten, obtained for the cost of one log line and zero deployment risk.
**Why it was tempting:** Hit rate feels like a runtime property of a cache, so it seems to require a cache to observe. But it is really a property of the *access pattern*, which is fully observable at the call site.

### Latency tracing tells you whether to add a cache
**Accurate:** Tracing and key-logging answer **different questions.** Tracing answers *where does the time go* → which component to fix. Key logging answers *is the work repeated* → whether a cache is the right fix for that component. You need both, attribution first: if the source is 8% of p99, a perfect cache buys 8%.
**Why it was tempting:** Both are "performance investigation," so they collapse into one step mentally — and finding a slow component feels like finding the answer, when it has only located the problem.

### The investigation is: traffic grows → find the bottleneck → add a cache
**Accurate:** There is a mandatory gate between those last two steps — **fix source inefficiency first.** Full ladder: symptom → attribute p99 → identify the shape (slow call / N+1 / queueing / payload size) → **fix the source** → *then* measure repeat rate → decide. Caching an unindexed query does not solve it; it hides it, and you inherit invalidation forever to conceal a one-line fix.
**Why it was tempting:** A cache does make the symptom disappear, and disappearing symptoms feel like fixes. The cost only surfaces at cold-start or cache outage, when the source meets its real load for the first time.

### Low repeat rate means a cache won't help
**Accurate:** Low repeat rate is usually a **key-cardinality** problem, not a verdict. Every dimension in the key multiplies cardinality and divides repeat rate. `listingId + userId + zip` has almost no repeats; split the shared listing block (keyed on `listingId` alone) from the personalized fragment and most of the page becomes cacheable.
**Why it was tempting:** Repeat rate is measured against the key you happened to pick, so a bad key looks like bad data. The fix is to change the cache granularity, not to abandon caching.

### Class A caches are invisible, therefore harmless
**Accurate:** Invisible defaults still **confound measurement.** Warm buffer pools produce "why is it faster the second time," secretly bimodal p99s (warm 2 ms / cold 200 ms), query "fixes" that only worked because test rows were hot, and unexplained slowness for minutes after a restart or failover. Discipline: decide whether you are measuring warm or cold, and label it. Running something three times and taking the best measures the cache, not the query.
**Why it was tempting:** "Nothing to configure and nothing to invalidate" is true, and it reads as "nothing to think about." The correctness risk really is zero; the *interpretation* risk is not.


---

## 2026-08-21 — Caching design principles

### Caching does not serve core business logic, so it cannot affect correctness
**Believed:** Caching is invisible and outside core business logic; therefore it is only a performance concern.
**Accurate:** A cache should not own authoritative business truth, but its **freshness, key scope, fallback, and failure behavior** can affect observable correctness, security, and availability. The source remains authoritative; the cache must be removable and its failure survivable.
**Why it was tempting:** Separating domain truth from optimization is the right architectural instinct. The mistake is extending “does not own truth” into “cannot affect what users observe.”

### Performance is the only reason to prioritize caching
**Believed:** A cache is normally considered only when an API becomes slow; features should always come first otherwise.
**Accurate:** Performance pain is the common investigation trigger, and speculative caching should usually lose to feature delivery. But **resource cost, third-party rate limits, capacity protection, security, correctness, or availability** can independently justify cache work.
**Why it was tempting:** Most cache discussions begin with latency, and caching is often framed as a speed optimization. Its other value is protecting a scarce source and controlling repeated work.


---

## 2026-08-21 — Caching: design-time estimation

### Including a cache in the initial design means it is already proven necessary
**Believed:** If a cache appears in the architecture before production traffic exists, engineering is prematurely optimizing.
**Accurate:** Early inclusion can be a legitimate **scope-estimation and delivery-planning request**. Keep the distinction explicit: cache-ready path, conditional anticipated cache, and cache required before launch are different commitments.
**Why it was tempting:** “Measure before optimizing” is a sound runtime rule, but it does not answer a Product Manager’s need to estimate the full possible engineering effort before launch.

### No production metrics means caching cannot be estimated
**Believed:** Without organic traffic, there is no responsible way to estimate whether a cache will help or how much work it will take.
**Accurate:** Engineering can estimate from **anticipated traffic, key reuse, active cardinality, source cost, value size, freshness, write rate, and fan-out**, using low/base/high scenarios and naming the validation test or metric that will update the estimate.
**Why it was tempting:** Estimates are less certain before launch, and a forecast must not be presented as a measured hit rate. But uncertainty calls for ranges and explicit assumptions, not silence.


---

## 2026-08-21 — CarGurus cache strategy

### DB → cache → Kafka is simply write-through
**Believed:** Any design that updates the cache as part of a write is write-through.
**Accurate:** Canonical write-through usually means the application writes the cache and the cache synchronously persists to the DB. DB-first followed by local cache update and Kafka fan-out is better described as **DB-first cache update with asynchronous event-driven propagation**. It is not write-behind unless the cache or event buffer is the durability boundary.
**Why it was tempting:** The informal term “write-through” is often used for any synchronous-looking cache update, but the ownership and ordering determine the failure semantics.

### Kafka makes the DB write and all cache copies atomic
**Believed:** Once the writer updates its cache and publishes Kafka, the cluster is consistent.
**Accurate:** DB commit, local cache update, and Kafka publication are separate operations unless explicitly coordinated. Peer caches are **eventually coherent** and can miss, duplicate, or receive events out of order. Use after-commit publication plus durable outbox/CDC, idempotent versioned events, replay, or periodic full refresh to bound the gap.
**Why it was tempting:** Kafka feels durable and fast, and normal-case propagation is quick. Durability of the topic does not retroactively make the preceding DB and local-memory operations atomic.
