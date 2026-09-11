# Search platform: ingestion, rebuilds, and index lifecycle

**Date:** 2026-08-12
**Question that started it:** Elasticsearch is built for free-text search over semi-structured data but is expensive to write and index. So how is it actually kept up to date?

---

## The path

The premise I brought in was that the index would be updated directly from the transactional DB. Wrong shape. The actual pattern is a chain: **relational source → denormalized read model → change events → index**, with a dedicated ingestion service in the middle.

That resolves the "slow to write" concern differently than expected. The index isn't kept fresh by writing to it faster; it's kept fresh by a **pipeline** that batches, and by accepting eventual consistency. Freshness intervals were described inconsistently across docs (daily full + hourly delta in one place, ~20-minute sync in another) — the architecture evolved, and the durable takeaway is that it's *eventually* consistent by design, not immediate.

## Two generations, and why the second exists

Legacy: each search node pulled from the read model, built an in-memory cache, indexed into a local Lucene index, then started consuming change events. Every node did this independently — 21 nodes querying the same source for the same data, and every deploy rebuilding from scratch (~10 extra minutes).

Newer: a single ingestion service builds the dataset and a Lucene index **once**, uploads both to object storage, and nodes bootstrap from that artifact. This is the same "compute once, centrally" move that shows up later in the DataLoader and orchestration threads.

## What I got wrong about deletes

I assumed there'd be a clean per-document delete path. Couldn't confirm one. What's evidenced: full rebuilds load only *active* records (so anything inactive naturally drops), and closed/inactive state is tracked as a monitored concern. So the defensible statement is "handled through upstream state changes and rebuild flows" — and I explicitly could **not** prove whether incrementals issue literal deletes. Left as an honest gap rather than a guess.

## The newer platform

The strategic direction is a self-service platform on OpenSearch: an ingestion service, a query service, and per-dataset YAML configs (source query, searchable fields, filters, sort fields, rebuild schedule, change topics).

The parts worth remembering:
- **Two ingestion paths.** Operational data comes through the API composition layer; analytical data comes through a warehouse→table-format→batch-job path. Different source shapes justify genuinely different tech.
- **Alias-swap rebuilds.** Build a new timestamped index, then move a stable alias. Replace-not-mutate, which makes schema evolution and rollback safe.
- **Watermark checkpoints** for incremental loads, stored as a dedicated object, advanced only after successful upserts, idempotent by document ID. This is the cleanest recovery pattern in the whole series.

## Pressure I applied

**"Doesn't a full rebuild via the composition layer hammer everything?"** Yes, and the mitigations are architectural: keep the index document *lean* (only what's needed for filter/sort/aggregate; fetch display fields at query time), page/group the fetches rather than one giant query, and schedule rebuilds rather than running them continuously.

**"Only one ingestor — what's the recovery model?"** Weaker than ideal at the time: rebuilds ran synchronously on a leader pod and could stall with no automatic recovery; distributing rebuild work was an open improvement. Good reminder that a clean architecture diagram can hide an immature execution path.

**"Is tokenization config-driven?"** Partly — config selects which fields are text and how they map; the actual tokenization comes from the analyzer attached to the field. Not everything is per-dataset arbitrary; some remains platform-controlled default.

---

## What changed in the reference

- `Part 2.3 Derived-Store Materialization` — the full section
- `Elasticsearch / OpenSearch` tool entry — corrected from "what it is" to "how it's maintained"
- `Change Data Capture (CDC)` — invalidate-then-refetch as the dominant pattern
- `corrections.md` — three entries on ES as derived store / not source of truth
