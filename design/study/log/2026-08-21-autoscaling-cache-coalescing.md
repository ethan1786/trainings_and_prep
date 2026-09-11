# Autoscaling caches: coalescing and pre-loaded distributed state

**Date:** 2026-08-21
**Question that started it:** Is coalescing the popular production solution, how complicated is it for a large auto-scaling cluster, and should the cache be pre-loaded as a distributed cache?

---

## The answer

Coalescing is common, but “coalescing” has two scopes. Local single-flight collapses concurrent misses within one process and is relatively straightforward. Distributed coalescing coordinates a single key refresh across nodes and is more involved because leases expire, owners fail, work can exceed the lease, and followers need bounded behavior.

A permanent leader is not required. A short-lived per-key lease with a version or fencing check is a narrower and more failure-local mechanism. Followers can wait briefly, serve stale data, fall back to the source, or fail according to an explicit policy.

For a large auto-scaling fleet, the practical default is a shared L2 cache plus local L1 where worthwhile, local single-flight, and a distributed per-key lease only on an L2 miss. This prevents a new pod from causing a full source reload and prevents a cluster-wide hot-key miss from multiplying into one source request per pod.

A pre-loaded distributed cache is often better for a bounded, read-mostly snapshot. One controlled builder populates the shared cache once; newly-scaled nodes consume the warm L2 rather than rebuilding the dataset. Use a versioned namespace or double buffer and atomically publish the completed snapshot. The trade is that L2 is still remote, shared, and operationally significant; local L1 is required for memory-speed reads.

## The wrong turn worth keeping

“Everyone waits for the coalescer” is not automatically safe. A blocking wait without a timeout can turn a cache miss into a queue, especially when the source is already unhealthy. “Pre-loaded distributed cache” is also not the same as “every application has a pre-loaded local cache”: the former avoids duplicated warmup but keeps a network hop.

## Pressure I applied

The design should state what happens for a new autoscaled pod, a missing L2 key, a lease-holder crash, a slow refresh, an invalid snapshot, and a source outage. The primitive is only a small part of the production design; the degraded paths are the real system.

---

## What changed in the reference

* `Caching` — added local versus distributed coalescing, the autoscaling L1/L2 recommendation, pre-loaded shared-cache design, atomic snapshot publication, and selection rules
* `corrections.md` — clarified that coalescing is not one mechanism and that a pre-loaded distributed cache is not equivalent to pre-loading every application node
* `log/README.md` — registered this entry
