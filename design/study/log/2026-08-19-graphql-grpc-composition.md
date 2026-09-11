# GraphQL Federation, gRPC, and where composition logic belongs

**Date:** 2026-08-19
**Question that started it:** We don't have gRPC — should we?

---

## The path

Started as a tooling question and turned into the longest thread of the series, because answering it required getting three separate models right: what gRPC actually is, what GraphQL actually is, and where logic belongs.

## Round 1: "should we adopt gRPC?"

The honest answer was "narrowly, if at all" — but the interesting discovery was that gRPC is already present in the **infrastructure** layer (metrics backends, telemetry collectors, cloud client libraries) while absent from application service-to-service traffic. So "we don't have it" was wrong; "we don't use it as a contract between our own services" was right.

The reason not to adopt broadly: federation was already the strategic bet for typed cross-domain composition, and a third contract paradigm (REST + GraphQL + protobuf) fragments tooling and mental models. The reason to keep a door open: wire-level performance on a *proven-hot* internal hop, and true bidirectional streaming — the one thing GraphQL structurally cannot do.

## Round 2: I pushed back on "they overlap"

My objection: gRPC solves performance, GraphQL is "just a data store" for reads, and can't do more than GETs.

Two of those were wrong, and fixing them is what made the overlap visible:

- **GraphQL stores nothing.** It's an API contract + execution/composition layer in front of real datastores. A federated gateway splits one query, fans out to owning subgraphs, and stitches. "A typed contract layer clients call to invoke backend logic and get structured data back" also describes gRPC — *that's* the overlap.
- **`mutation` and `subscription` are first-class.** Writes staying on REST is a *choice*, not a protocol limit — and a good one, because federation has **no cross-subgraph atomicity**. So writes needing transactional integrity belong on the owning service.
- **Both address performance, on different axes.** GraphQL attacks round-trips and over-fetch; gRPC attacks wire serialization. Neither optimizes the other's axis.

## Round 3: my gRPC model was 60% right

I described gRPC as "a simple replacement for a REST request that opens HTTP/2 and keeps a long connection." The connection part is right; it's one of four pillars, and the least interesting:

1. HTTP/2 multiplexing over a persistent connection
2. **Protobuf binary serialization** — arguably the bigger perf win, independent of connection reuse
3. **IDL + code generation** — the `.proto` *is* the contract, with numeric field tags giving clean compat rules
4. **Four call types** — unary, server-streaming, client-streaming, bidirectional

Only unary maps onto "a REST request." The streaming modes are a genuinely different capability, and that's where gRPC is non-redundant.

## Round 4: lock-in, and where I was right

I argued RPC is a platform you can't easily leave, like event sourcing, so adopt only if necessary. Correct instinct, but the analogy needed splitting: event sourcing's lock-in is in the **bones** (truth *becomes* the log — you can't revert to storing current state without reconstructing what "correct" means). gRPC's is at the **seams** (transport + contract at service edges) — invasive, but migratable one edge at a time.

The uncomfortable symmetry I hadn't seen: **federation is also a platform you can't casually leave.** So the real reason for the GraphQL bet isn't "it avoids lock-in" — it's *choosing which lock-in matches the dominant workload*. There is no commitment-free option at this layer.

## Round 5: "why do we need GraphQL at all?"

The honest answer: it doesn't earn its place by making a healthy backend faster. It solves a **client × service fan-out** problem — N clients each composing M fragmented services — plus decoupling frontend iteration from backend deploys. Below that threshold it's a liability.

The tell isn't a latency number, it's organizational: **how often does a UI change require a backend change today?** If never, even that argument evaporates.

## Round 6: the caching misconception (mine)

I believed the router's built-in caching improved performance. Almost the opposite:

- REST gets caching nearly free because **the URL is the cache key**. GraphQL is `POST /graphql` — opaque to every HTTP cache.
- What the router caches is **query plans / normalization** (router CPU) and optionally persisted queries (payload size). The expensive part — the actual subgraph fetches — still happens every time.
- Verified against config: the router is documented as **non-caching by default**; entity caching is a paid-tier feature that was consciously deferred, and an in-house plugin spike didn't ship. Resilience features that *are* on: circuit breakers, fail-open timeouts (3s default, 15s for the batch-heavy subgraph). Retries deliberately disabled to avoid storms.

So caching is a *tax* GraphQL pays for composition, not a benefit it provides. Measured router overhead was ~4ms, and multi-service queries can be faster purely from **parallel planning**.

## Round 7: what the real performance win is here

I proposed it's DataLoader dedup, and that consolidation isn't the winner because an orchestration service already fans out server-side and the graph is deliberately one level deep. Both largely right — with two refinements:

- **Split batching from dedup.** Batching: 30 distinct IDs → one call. **Dedup**: 30 references → 8 unique IDs → the downstream fetches *8 entities*. The dedup case reduces actual work and downstream load, scaling with the fan-in ratio.
- **The win belongs to the pattern, not the protocol.** A hand-written orchestrator *could* dedup. GraphQL's contribution is making it **automatic, uniform, and impossible to forget**.
- **Bounded to one request.** Neither router batching nor DataLoader caches across requests. Repeat load still needs a cache tier.

Then I corrected myself on consolidation: a bespoke orchestrator only composes for *one* surface. Federation builds fan-out **once** so every current and future consumer inherits it. That's an **N-consumers** argument, not an N-round-trips one — and it *is* a real win.

## Round 8: mechanics — how batching actually works

The confusion worth recording: it is **not** collecting 50 separate HTTP requests. It's batching the 50 field-resolutions **within one query**. So there's no cross-request transaction to reconcile.

- The loader defers: `load(id)` queues a key and returns a future immediately; dedup happens on the key.
- **Dispatch timing differs by runtime.** Event-loop runtimes flush on the next microtask. JVM implementations use explicit **level-tracking** instrumentation — "N loads expected at this level, N queued, dispatch now."
- **The Spring transaction concern dissolves** for two reasons: the loader is **request-scoped** (a fresh instance per execution — leaking it across requests would be a correctness bug), and this is *remote read composition*, not enrolled in a local transaction.
- In federation it's two layers: the router batches entity **representations** into one `_entities` call, and the owning subgraph's own loader batches the datastore fetch.

## Round 9: why subgraphs stay one level deep

Four reasons, and they're all consequences of keeping resolution **flat**:

1. Deep nesting **fragments dedup** — a foreign entity resolved inside another subgraph can't join the router's batch for that entity type.
2. It creates a **hidden sequential waterfall** invisible to the router, so it can't parallelize it or apply per-field timeouts.
3. **Fail-open granularity collapses** — the router can null one field; a nested failure takes the whole parent field.
4. It **duplicates ownership** — a subgraph would need to know how to call and shape a domain it doesn't own.

## Round 10: the exception — dependent keys and `@provides`

I asked why a nested foreign entity couldn't just be returned as a reference for the router to batch. Real finding: because that key is **derived** — knowable only *after* the subgraph's own call plus business logic. The other reference is known upfront, so they land in **different resolution phases** and can't share a batch. A resolvable reference would add a third sequential hop.

Where the reference approach *was* adopted, it uses **`@provides` + `resolvable: false`** — because that service already holds the fields as part of its own job, so it declares them and the router skips hydration entirely.

I then mis-modeled `@provides` twice, and both corrections matter:
- It's a **declaration**, not a fetch mechanism — "these fields are already here, don't hydrate."
- **A subgraph never calls back into the router.** Re-entrant is circular, wastes planning, doubles router QPS, complicates auth/tracing. If a subgraph must fetch, it calls the owning service **directly**.

## Round 11: the caching/routing orthogonality

I suggested direct-calling the owning service "gets free caching back." It doesn't:

- Free edge caching lives at the **client edge** only. Internal hops never had a CDN.
- **Caching and routing are orthogonal.** Cache the *owning service* and you get caching under either pattern — including alongside the router's batching. That's strictly better than routing around the router to build a cache you'd have to build anyway.
- Direct-calling to "get caching" also forfeits fail-open, circuit breaking, cross-query dedup, and observability uniformity.

Then the sharper point: the client edge **moved** when SSR was introduced. Browser↔SSR is now the real edge (and *can* re-host HTTP/CDN caching); SSR↔router is just another internal hop. So "the loss is real" is only true if the old content was genuinely cacheable **and** the SSR layer isn't caching now. For personalized content, personalization killed cacheability, not the paradigm. Logged as an open question.

## Round 12: the placement rule

My formulation was "logic is logic, data is data." Too clean — taken literally it exiles a computed flag over a domain's own fields from that domain, leaving it homeless. The corrected axis is **whose** logic:

- **Domain-semantic derivation over one domain's own data** → that domain. A domain owns its facts *and* derivations of its facts.
- **Cross-domain composition** → an orchestrating service. Never a domain subgraph.
- **Presentation / page logic** → the app.

And the guardrail: **"everyone already calls it" is gravity, not architecture.** Convenience is a legitimate tiebreaker *between* correct homes; it can't *make* a home correct.

---

## What changed in the reference

- `Part 2.2 API Composition and Ownership` — the whole section
- `GraphQL Federation`, `gRPC` tool entries
- `Part 6` meta-principles — convenience-as-tiebreaker, consequences-aren't-justifications
- `corrections.md` — nine entries
- `open-questions.md` — SSR cache headers, router representation dedup, entity caching status
