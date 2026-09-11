# S3 / object storage: roles, transfer mechanics, unused surface

**Date:** 2026-08-19
**Question that started it:** S3 shows up everywhere in the systems I've studied. What are the actual use cases?

---

## The governance insight worth leading with

The most interesting finding wasn't mechanical. Leaf/browser-facing apps are **forbidden** from owning durable relational or document state — they must get it from a platform service. But **object storage is explicitly permitted**, and the stated reasoning is the payoff:

- objects are identified by URL and **enforce no schema**, which "significantly reduces the risk of coupling between different systems"
- there is **no complex querying or transactional capability**, "further reducing the risk of coupling"

So the exact properties that make a *database* dangerous to share (a schema everyone couples to, joins/transactions that entangle two systems through the data layer) are **absent**. Object storage is blessed *because it's too dumb to create coupling.*

This is the same lens as the whole GraphQL thread: the risk was never "storage," it was "a shared queryable schema as a hidden coupling surface."

## Three distinct roles (not one)

I initially lumped these together. They're genuinely different patterns:

1. **Build-once artifact store** — a dedicated ingestor builds a dataset + search index, uploads both; nodes bootstrap from the artifact. Serves *both* routine deploys/scale-ups **and** disaster recovery — same artifact, double duty.
2. **Durable checkpoint / warehouse backing store** — the analytical-ingest path uses object storage both as the table-format warehouse *and* as the durable **watermark** for incremental loads (advanced only after successful upserts; idempotent by document ID). Chosen deliberately over storing the watermark in the search index because "a dedicated object is durable, single-purpose, and only this flow writes to it."
3. **Firehose landing buffer** — model-endpoint capture dumps to object storage, then a loader moves it to the warehouse (~5 min). Decouples a high-rate producer from an analytical consumer. Runs in both directions (training exports out, predictions back).

All three exploit the same property: a **schema-less, durable, URL-addressed blob tier** holding big immutable things some other system reads or replays later.

## Snapshot mechanics (I asked who/when/how/versioned)

- **Who:** a **separate service**, not the primary node — and only **one instance at a time** via leader election. Three replicas run; one builds. This is the direct fix for the old pattern where 21 nodes each queried the source for the same data.
- **Frequency:** cron, **3× daily**, plus manual trigger. Deliberately throttled — a request to run every 2 hours was pushed back on because each generation is a full dump that pressures the upstream. Same "verify the bottleneck is downstream" discipline as the Kafka thread.
- **Chunked or streaming:** **batched**, via a producer/consumer queue — parallel per-group queries push batches; upload workers drain and write. JSON goes up in batches (50 groups per upload); the search index is zipped and uploaded as **one archive at the end**, followed by a metadata file written last as the completion marker.
- **Versioned:** yes, by **timestamp prefix**, not overwritten — with a per-version metadata file acting as "this snapshot is complete" and an embedded **Kafka offset** so a booting node knows where to resume.
- **TTL:** could **not** confirm an expiry policy for these snapshots. Logged as an open question — an unbounded 3×/day bucket is a quiet cost leak. (The newer platform *does* clean up old indices daily and uses versioning for config rollback.)

## Transfer mechanics — my phrasing conflated two layers

I asked whether files transfer "in chunks, batched." Two different things:

- **Logical batching** (what the application chose) — how many records per object. Combining many records avoids a swarm of tiny objects, where per-request latency and cost dominate.
- **Transfer chunking** (what the SDK does) — splitting *one object's bytes* into parts for parallel upload, above a size threshold.

The size framework: single PUT below ~100MB; multipart from ~100MB (mandatory above 5GB, up to 5TB / 10,000 parts); aggregate first for swarms of tiny objects. Multipart exists for **parallelism, per-part retry granularity, and resumability** — not just "it won't fit." In practice the high-level transfer managers decide automatically (default thresholds ~8MB), so you rarely choose manually.

Download side is symmetric, plus **range GETs** — fetch a byte range without pulling the whole object. That's how table-format readers read column chunks efficiently.

Two gotchas: tiny-object overhead is real, and **incomplete multipart uploads leave billed-but-invisible orphaned parts** — needs a lifecycle rule to auto-abort.

## Unused surface (I asked what we're missing)

Mostly correct absences: transfer acceleration (co-located, no benefit), requester-pays (not a use case), in-place SQL query (the warehouse path already covers it better), object-lambda and multi-region access points (niche).

The five worth actually checking, at the intersection of "plausibly underused" and "would matter":
1. **Lifecycle policies** — expiring old snapshots + aborting incomplete multipart uploads (likely a real quiet cost leak)
2. **Intelligent-Tiering** on artifact/capture buckets (near-free win)
3. **Event notifications** replacing polling in ingestion/ML pipelines (latency *and* cost)
4. **Presigned URLs** — the missing idiomatic tool if a user-facing direct upload/download need appears
5. **Cross-region replication** for buckets whose contents aren't reconstructible

Standing caveats: "not in the docs" ≠ "not used," and most gaps are **correct choices, not oversights**.

## The public-access pattern

Buckets stay **private**; public reads go through a static/CDN domain rather than an object-storage URL directly. Worth noting the irony against the GraphQL thread: this path gets **real** HTTP/CDN edge caching — which is exactly why images and static assets live here instead of behind a dynamic service.

---

## What changed in the reference

- `S3 / Object Storage` tool entry — three roles, size framework, unused-surface list
- `Tiered Storage` — lifecycle and multipart-abort as concrete practice
- `Part 2.3` — snapshot anatomy and cadence
- `corrections.md` — logical batching vs transfer chunking
- `open-questions.md` — four object-storage items
