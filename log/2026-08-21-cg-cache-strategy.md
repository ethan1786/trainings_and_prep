# CarGurus cache strategy: eager local snapshots and Kafka fan-out

**Date:** 2026-08-21
**Question that started it:** What read/write strategy is CG using when caches are populated at boot, writes update the DB and local cache, and Kafka propagates the change to the cluster? Is it common for web applications?

---

## The path

The read side is an **eagerly loaded local L1 cache** or **full-snapshot cache**: each application instance loads the expected dataset at startup and targets a 100% hit rate on the hot path. This is not lazy cache-aside or read-through behavior.

The write side is best described explicitly as **DB-first cache update with asynchronous event-driven propagation**:

```text
DB commit → writer’s local cache update → Kafka event → peer local-cache updates
```

Strict write-through is a different ownership model: the application writes the cache, and the cache synchronously writes the DB. This CG pattern should not be called write-behind either, because Kafka is not the durability buffer. “Cache-aside with explicit cache update” is a reasonable shorthand, but the full sequence is more precise.

The cluster behavior is **broadcast update propagation** across per-pod local caches. If Kafka carries the new value, it is update replication; if it carries only a key/version, it is invalidation followed by reload. Other pods converge asynchronously, so the pattern is eventually coherent rather than atomically consistent across the fleet.

## Is it common?

Yes, for bounded, read-mostly, latency-sensitive data: feature flags, configuration, reference data, and selected product metadata. It is not the usual default for arbitrary mutable web-application data because startup time, per-pod memory, full-refresh load, event gaps, and eventual consistency become expensive.

The design is attractive because reads are local and predictable. The permanent obligations are equally important: readiness during warmup, partial/failed snapshot behavior, rolling-deploy load, missed-event recovery, event ordering and idempotency, deletion handling, and the fact that DB write, cache update, and Kafka publish are not automatically atomic.

## The wrong turn worth keeping

Calling the whole design simply “write-through” hides two important facts: the DB is written first, and cluster propagation is asynchronous. The taxonomy label matters less than documenting the ordering and the failure window.

## Pressure I applied

The strongest version of the pattern is not “100% cache hit forever.” It is “100% hit for the successfully warmed snapshot, with a defined policy for new keys, partial warmup, stale entries, missed Kafka events, and cache rebuild.” That turns a performance target into an operational contract.

---

## What changed in the reference

* `Caching → Read/write strategies` — added the CG pattern, precise terminology, common use cases, tradeoffs, startup contract, and event-coherence requirements
* `corrections.md` — clarified that DB-first cache update plus Kafka fan-out is not canonical write-through and is not automatically atomic
* `log/README.md` — registered this entry
