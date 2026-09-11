# Caching: compact design principles

**Date:** 2026-08-21
**Question that started it:** What are the design principles for caching before moving on from the caching section?

---

## The path

The summary started from a useful operational model: caching is usually an invisible layer that does not implement core business logic. It helps by saving resources, reducing duplicate retrievals, and improving performance. In practice, performance pain is often what makes caching work worth prioritizing; otherwise feature delivery usually comes first.

The important refinement is that the trigger and the mechanism are separate. A slow API, rising resource pressure, cost growth, or an availability risk can trigger investigation. Tracing, source-efficiency checks, repeat-rate measurement, source-cost measurement, and full-miss capacity checks determine whether caching is actually the right fix.

A mutable cache is not part of the business source of truth, but it is still part of the system’s observable behavior. Stale values, incorrect key dimensions, cache leakage, stampedes, cold starts, and cache outages can affect correctness, security, and availability. The design goal is therefore not merely “keep cache logic out of the domain”; it is “make the cache removable and its failure survivable.”

## The wrong turn worth keeping

“Invisible layer” can be misread as “irrelevant layer.” Class A caches are often invisible defaults, but Class B caches add a second mutable copy and a permanent operational obligation. Even a cache that does not decide business truth can affect what a caller sees and how the source behaves under failure.

“Performance is the trigger” is also a useful default, but not a universal rule. Resource cost, third-party rate limits, capacity protection, security, correctness, and availability can justify cache work even when user-visible latency is acceptable. “Features always go first” is a prioritization heuristic, not a design law.

## Pressure I applied

The compact mental model should preserve both sides:

* Do not introduce mutable caching speculatively; it brings invalidation, freshness, key, stampede, warmup, eviction, and debugging costs.
* Do not treat caching as merely a cosmetic speed layer; it can protect scarce resources and can create failure or correctness risks if its boundaries are wrong.
* Begin with a symptom or concrete risk, then investigate across layers. Only add a cache after the source is efficient, the repeated work is measurable, and the source can survive a full miss at peak.

---

## What changed in the reference

* `Caching` — added a compact design-principles subsection covering invisible optimization, the trigger-versus-mechanism distinction, source authority, inherited obligations, response granularity, and removability
* `corrections.md` — added entries for “caching does not affect core logic” and “performance is the only trigger”
* `log/README.md` — registered this entry
