# Cache-miss stampedes: preloading versus coalescing

**Date:** 2026-08-21
**Question that started it:** Is a pre-loaded cache the only or best solution for high read volume, especially when a cluster has no leader or primary election?

---

## The path

Preloading is not the universal answer. It specifically prevents cold-start misses when the complete dataset is known, bounded, and small enough to load into every node. It does not inherently solve expiry stampedes, new keys, missed events, or oversized/unbounded datasets.

A cache-miss stampede can be split into several shapes:

* Cold-start stampede: many nodes begin empty after deploy or restart.
* Expiry stampede: many requests encounter the same expired key.
* Hot-key miss: many requests need one key that has never been populated or was evicted.
* Cluster amplification: each application node independently refreshes the same missing key.

The remedies match the shape: eager snapshots for bounded data; per-process single-flight for duplicate misses on one node; shared L2 plus short-lived per-key leases for cross-node coordination; stale-while-revalidate and TTL jitter for expiry; and source-side indexes, replicas, or materialized views when reuse is too low for caching to help.

A permanent leader is not required. A short-lived lease gives one node temporary ownership of refreshing one key, while other nodes wait, serve stale data, or fall back according to policy. This is narrower and more failure-local than electing one application-wide primary.

## The design judgment

For a web application, the practical high-read-volume design is often a hybrid:

```text
local L1 → shared L2 → per-key single-flight/lease → source
```

But the hybrid is not automatically better. It adds two cache layers, two failure modes, and more observability. Preloading wins when the dataset is bounded and predictable. Lazy shared caching wins when the keyspace is large or access is skewed. Neither is the right answer if most reads are unique or the source query is simply inefficient.

## The wrong turn worth keeping

“Request coalescing is hard in a cluster without leader election” is only partly true. Global coordination is hard, but whole-cluster leadership is unnecessary. The problem can be reduced to temporary ownership per key, with timeouts, fencing/version checks, and a defined behavior when the owner fails.

## Pressure I applied

“100% hit rate” should be read as a contract for the warmed snapshot, not a universal guarantee. The design must name the behavior for partial warmup, new keys, expired keys, missed Kafka events, source outages, and rolling deployments.

---

## What changed in the reference

* `Caching` — added stampede shapes, a strategy comparison, the per-key lease model, the L1/L2 hybrid, and selection criteria
* `corrections.md` — clarified that preloading is not the only high-read-volume solution and that cluster coalescing does not require permanent leader election
* `log/README.md` — registered this entry
