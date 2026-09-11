# 2026-08-19 — Bringing Part 3 up to the Part 1 decision standard

**Date:** 2026-08-19
**Question that started it:** Part 1 patterns each carry an escalation ladder, triggers, anti-cases, and inherited costs. Part 3 tool entries were descriptive only — "what it is, when it's right, how it breaks." Close the gap.

---

## What was missing, precisely

The Part 3 entries already had `RIGHT choice when` / `WRONG choice when` bullets and a deciding question. What they lacked was the part that does the actual work in Part 1:

- the **escalation ladder** of cheaper things to try first,
- the **real trigger** as distinct from the plausible-sounding one,
- the anti-cases stated as *why the reasoning fails*, not just as a "don't",
- and **what you permanently inherit** by adopting.

That last one is the highest-value section and it was completely absent. A tool entry without it reads as an endorsement.

## The pattern that showed up in all twelve

Writing these back to back surfaced something that isn't visible one entry at a time: **the rung most often skipped is the one immediately below the tool.** Not the trivially cheap rung — the one that's genuinely close in capability and much cheaper in obligation:

| Tool | The skipped rung below it |
|---|---|
| gRPC | REST + OpenAPI + generated clients (gets you the typed contract) |
| GraphQL Federation | a single BFF per surface |
| Elasticsearch | native full-text search in the relational DB (`tsvector`/`MATCH`) |
| Coordination store | a unique constraint or advisory lock |
| Kafka | a database-backed job table |
| Redis | an in-process cache (when per-pod view suffices) |
| Document store | relational with a JSON column |
| Flink | Kafka Streams / ksqlDB (state as a library, no cluster) |
| CDN caching | correct cache headers + content-hashed filenames |

Adoption arguments usually die at that rung rather than on the tool's merits. Added as a framing note in the Part 3 intro.

## Judgment calls worth recording

**Relational's ladder runs "before leaving," not "before adopting."** It's the default, so the decision content is what would justify departure. Ladder ends at shard/horizontal-store, and rung 6 — move the *read shape* out while keeping relational as source of truth — is flagged as usually correct and explicitly *not* "leaving relational."

**Object storage's ladder runs the other direction.** It's the cheap rung, so escalation goes *up* into metadata tables and table formats rather than down into alternatives. Rung 3 (bytes in the bucket, attributes in a database, key as the join) is the pattern that covers most real needs.

**Redis reframed as "shared-state service with a memory-shaped cost model and no durability you should rely on"** rather than "fast database." That framing gets the adoption call right on its own, and it makes the local-cache rung obviously correct for single-service cases.

**Document store reframed around aggregate-vs-document boundary alignment.** When they coincide you get single-round-trip reads and clean growth; when they don't you get a relational DB with no joins and no constraints. Also called out the counter-intuitive bit: schema flexibility is *not* query flexibility — relational is the flexible one for unanticipated queries.

**Federation's trigger named as organizational.** The real trigger is multiple teams needing to own slices of one schema and deploy independently. Also stated plainly that federation is not a performance technology — the router adds a hop and a naive resolver graph is slower than the REST it replaced.

**CDN split into three products** — geographic latency, origin offload, and TLS/DDoS/edge routing. A single-region team may want the second and third without the first, which the old entry couldn't express.

**Coordination store's ladder leads with idempotency**, because making the operation safe to run twice *removes* the requirement rather than satisfying it. That's the highest-leverage rung anywhere in Part 3.

## The inherited-cost sections turned out to be the most useful part

Several are things that bite in production and appear nowhere in vendor material:
- **gRPC:** HTTP/2 long-lived multiplexed connections stick to a backend and defeat naive L4 load balancing.
- **WebSocket/SSE:** connection *count* is the capacity dimension, so Little's Law doesn't apply; every deploy mass-disconnects clients and the reconnect storm is a thundering herd.
- **Kafka:** partition count is semi-permanent, consumers ≤ partitions is a hard ceiling, and repartitioning breaks key locality.
- **Search:** reindex is a routine operation, which makes alias-swap deploys and a repeatable rebuild path non-negotiable.
- **Object storage:** key layout is a permanent decision — it determines listing performance, lifecycle targeting, and policy granularity.
- **Coordination:** clients must re-initialize sessions on coordinator errors, or a blip leaves an instance permanently stuck.
- **Flink:** exactly-once holds only if sources *and* sinks cooperate; a non-transactional sink silently degrades you to at-least-once.
- **CDN:** a response varying on a dimension missing from the cache key is a correctness and security bug, not a performance bug.

---

## What changed in the reference

- **Part 3, all 12 entries** — new `When you need it, and when you don't` subsection with escalation ladder, real triggers, anti-cases with reasoning, and permanent obligations. Verified programmatically: 12/12 have all three of decision heading, ladder, and inherited-cost content
- `Flink` — already had ladder and triggers; added the missing inherited-cost paragraph and aligned its heading to the standard
- **Part 3 intro** — the "skipped rung below the tool" framing note
- **Contents** — updated to state Part 1 *and* Part 3 carry the decision subsection; Part 3 TOC entries annotated with each tool's one-line decision frame
- Part 3 grew from ~34K to ~69K characters
