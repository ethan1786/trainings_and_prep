# Caching: design-time estimation before metrics

**Date:** 2026-08-21
**Question that started it:** Should a cache be included in the design before production metrics exist, when Product needs an engineering-effort estimate?

---

## The path

The earlier rule was “measure before adding a mutable cache.” The new question exposed a different context: a Product Manager may need the total engineering scope before launch planning is complete, so asking engineering to include caching in the initial design can be reasonable even without organic traffic.

The resolution is to separate scope estimation from production validation. Engineering can estimate from the anticipated source/data shape and request pattern: peak and burst traffic, key reuse and cardinality, source cost, value size, freshness and writes, fan-out, and shared versus personalized response fragments. The estimate should use low/base/high scenarios and state what will validate the assumptions later.

Three implementation commitments should not be conflated:

* Design the path to be cache-ready.
* Include a cache as a conditional or anticipated component in the architecture and delivery estimate.
* Require a cache before launch because the uncached path cannot satisfy a known capacity, latency, cost, rate-limit, or availability constraint.

The first is often cheap and prudent. The second is a valid planning output. The third needs evidence or a clearly stated launch constraint, even if the evidence is a forecast rather than production telemetry.

## The wrong turn worth keeping

“Measure first” can be over-applied to mean “do not mention caching until traffic exists.” That confuses runtime optimization with design estimation. The opposite mistake is also common: placing a cache in the architecture diagram as if it were already proven necessary, without defining keys, freshness, miss behavior, memory, invalidation, or the validation gate.

## Pressure I applied

A useful PM-facing estimate is not just “add Redis” or “no cache.” It separates guaranteed source-backed scope, conditional cache scope with assumptions, and a decision gate that promotes or removes the cache after load testing or early-production measurement. This preserves honest prioritization while giving Product the total possible effort needed for planning.

---

## What changed in the reference

* `Caching` — added design-time estimation guidance, scenario inputs, first-order formulas, obligation-based effort sizing, and the three-layer planning output
* `corrections.md` — added clarifications that upfront inclusion can be a planning request and that no metrics does not mean no estimate
* `log/README.md` — registered this entry
