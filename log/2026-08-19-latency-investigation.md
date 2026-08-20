# 2026-08-19 — Latency investigation: a decision tree for multi-layer slowness

## Why this entry exists

Noticed a real gap while using the reference as study material. Every section answers *should I adopt pattern X* — but the question you actually get paged for is the inverse: **something is slow, there are eight layers between the user and the data, and I don't know which one to look at.** The pattern sections are the menu of fixes; nothing told you how to pick.

This is also the natural home for the reasoning that came out of the caching follow-up (attribution vs. repeat rate, the source-efficiency gate). That ladder was the caching-specific slice of a general procedure that wasn't written down.

## The governing rule

**Each step must end in a number that eliminates layers.** An investigation that produces theories instead of numbers is guessing with extra steps — and it almost always terminates in "let's add a cache," because that is the fix that makes symptoms disappear without requiring understanding.

## Step 0 is the step everyone skips

Four questions before touching any tool, because each one splits the cause space:

- **Which percentile?** p50 regression = something on the common path. p99-only = contention, queueing, GC, slow tail dependency, cold cache. Nearly disjoint cause sets.
- **Which population?** All traffic, one endpoint, one tenant, one region, one client version? Narrow blast radius points at data shape or a deploy, not capacity.
- **When did it change?** Step-function = a change you can revert. Gradual = growth crossing a threshold.
- **Absolute or relative?** "Always 800 ms" is a design problem. "Was 80 ms last month" is a regression with a revertable cause.

**Highest-value single finding in the whole tree: a step-function at a known deploy.** That converts an open-ended performance investigation into a diff review. Check it first, always.

## The three-bucket split (before per-layer work)

1. Client/edge time — DNS, TLS, RTT, transfer, render.
2. Server processing — your code and dependencies.
3. **Waiting time** — queued and not being worked on.

Bucket 3 is the one that gets missed and the most common cause of "everything is slow at once." **Queueing time is invisible in per-call latency metrics** — every call looks fine while total latency balloons, because the time is spent before the call starts. Diagnostic: if server spans sum to far less than end-to-end latency, *the gap is the answer* and the database is not.

## The layer walk

Outside in, stopping at the first layer holding the dominant share: client → network/geo → edge/CDN → LB/gateway → app admission → app composition → app compute → downstream services (recurse) → data store query → data store capacity. Each row in the reference has what to measure, the signature of the problem being *there*, and typical fixes.

Single highest-signal number in DB investigation: **rows examined vs rows returned.** 10 returned from 4M examined = missing index or non-selective predicate, and neither caching nor scaling fixes the scan.

## Shape classification — the part I hadn't articulated before

Knowing *where* isn't enough; the *shape* determines the fix, and shapes are distinguishable from the trace alone:

1. **One slow thing** — single dominant span → fix that thing.
2. **Many small things (N+1)** — latency ∝ item count → batch/dedup. **Most commonly misdiagnosed as needing a cache.** A cache hides an N+1; batching removes it.
3. **Serial chaining** — total = sum where it could be max → parallelize. Trace looks like a staircase, not a comb.
4. **Queueing/saturation** — operations fast, waiting dominates, load-sensitive and non-linear near capacity → capacity/limits/shedding. **Never cache your way out of saturation** — it masks it until the cache goes cold.
5. **Tail amplification** — p50 fine, p99 terrible, wide fan-out. With N components each having a 1% slow tail, P(at least one slow) ≈ 1−0.99^N; at N=50 that's 39% → reduce fan-out, hedge, fail-open non-critical.

## Fix ladder, cost order

delete the work → fix the inefficiency → restructure the calls → right-size resources → **cache (5th)** → change the data model. The temptation is always to jump to rung 5; a cache placed before rung 2 hides a permanent fix behind a permanent obligation.

## Distributed-transaction variant

Same tree plus three additions:
- **Trace across async boundaries** — an untraced Kafka hop is an invisible arbitrary delay, and the timeline breaks exactly where the latency hides.
- **Lag ≠ slow processing** — lag with fast per-item work = partition/concurrency limit; fast-draining queue with slow items = the work itself.
- **Retry amplification** — 3 × 3 × 3 = 27 attempts per logical request. Presents as latency, then saturation, then outage. Budget retries at exactly one layer.

## Anti-patterns worth naming

Starting at the database (deepest and best-instrumented, so it attracts attention). Averaging away bimodality. Measuring warm, shipping for cold. Fixing the loudest thing rather than the dominant thing. Stopping at the first plausible cause when regressions often stack. Optimizing before reproducing.

## The one-line principle

**Attribute before you optimize; classify the shape before you choose a fix; spend the cheapest, most permanent fix that addresses the dominant term — the cache is the sixth thing to try, not the first.**

---

## What changed in the reference

- **New Part 2.4** — `Latency Investigation — a decision tree for "it got slow"`: step 0 symptom definition table, three-bucket split, ten-row layer walk table, five shape classifications, six-rung fix ladder, distributed-transaction variant, anti-patterns
- `Caching` — cross-link noting the caching investigation ladder is the domain-specific slice of 2.4
- **Part 4** — eight new constraint→solution rows keyed to *symptoms* rather than requirements (p50 regression, p99 with fan-out, everything-slow, latency ∝ items, spans ≪ end-to-end, rows examined ≫ returned)
- **Part 6** — new meta-principle 11: *simulate the decision in logs before building the mechanism*
- TOC updated with 2.4 subsections
