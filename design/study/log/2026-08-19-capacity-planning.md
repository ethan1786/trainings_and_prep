# 2026-08-19 — Throughput and capacity planning

**Date:** 2026-08-19
**Question that started it:** Part 2.4 covers "why is it slow." What about "will it hold at 10x?"

---

## Why this is a separate section, not an extension of 2.4

They look like the same topic because both are about latency, but the causality is inverted. In latency investigation, load is held constant and latency is the symptom you're explaining. In capacity planning, **load is the independent variable and latency is the signal that you're near a limit.** One ends in a fix; the other ends in a number, a limit, and a plan for exceeding it.

**The routing question that separates them:** *is it slow at 1 request/sec?* If yes → latency problem, use 2.4. If it only degrades above some rate → capacity problem, use 2.5. Worth asking before an investigation rather than discovering it halfway through.

## The two laws that carry most of the reasoning

**Little's Law, in the form that's actually useful:** `required concurrency = throughput × latency`. 1,000 req/s at 200 ms = 200 requests in flight, so you need ≥200 workers/connections or things queue. The consequence I hadn't internalized: **latency reduction is a throughput multiplier** — drop to 50 ms and the same rate needs 50 instead of 200. That means every fix in 2.4 is simultaneously a capacity fix. Inverted, it sizes pools: 50 connections × 10 ms = 5,000 queries/sec ceiling, and nothing in the app raises it.

**The utilization knee.** Wait time scales as `1/(1−utilization)`: 50% → 2×, 80% → 5×, 90% → 10×, 95% → 20%, 99% → 100×. Three consequences:
- A system at 50% CPU is **not** "half capacity" — it's near as loaded as you want.
- A 10% traffic bump from 85% → 94% triples latency. This is why capacity incidents feel sudden; the system is fine until abruptly it isn't.
- Target **50–70%** steady state on the binding resource. Variance makes it worse — bursty arrivals queue even at low average utilization.

## Binding constraint vs. busy resource

Capacity is set by exactly one thing at a time, and it's usually not the most-monitored one. In rough order of how often it's the real answer: connection pool, thread/worker pool, single-writer node, partition count, downstream quota, disk IOPS, memory/GC, network, lock/hot-key contention, and *then* CPU.

Two rules:
1. **Adding capacity to a non-binding resource changes nothing.** More pods behind an exhausted connection pool make the pool worse.
2. **The constraint moves when you relieve it.** Fix the pool, the DB becomes binding. A capacity answer without naming the *next* constraint is incomplete.

## Estimate before testing

Peak (not average) → fan-out multiplication → Little's Law → per-unit capacity → units ÷ 0.6 → failure headroom. Two mistakes this catches: planning for average when peak:avg is commonly 3–10×, and forgetting fan-out amplification — 10× traffic on a page issuing 20 queries is **200× at the database**.

The point of estimating first is that a load test contradicting your estimate means your mental model is wrong, which is worth more than the number.

## Four tests, four questions

Load (does it meet SLO at peak) / stress (where's the knee, what breaks first) / soak (leaks, unbounded growth) / spike (autoscaling lag, cold cache, connection storms). Running one and calling it "load testing" is how ceilings get missed.

**The stress test's most valuable output isn't the throughput number — it's the identity of the first thing to break.** That's the binding constraint under real conditions instead of on paper.

Two things that routinely invalidate results: unrealistic data distribution (uniform synthetic keys → 100% cache hit rate, no hot-key contention, so you measured a system that doesn't exist) and testing warm (the Class A caveat again).

## Failure modes that only exist under load

These don't appear in single-request profiling at all:
- **Retry amplification** — load → latency → timeout → retry → more load. Positive feedback; brownout becomes outage. Retry budget at one layer, backoff **with jitter**, breakers.
- **Thundering herd / cold cache** — restart or failover sends 100% of traffic to a source sized for 5%. The capacity face of "can the source survive full miss at peak?"
- **Autoscaling lag** — 30 s to 3 min to detect, schedule, boot, warm, become healthy. **Autoscaling handles trends; headroom handles spikes.** Also, scaling on CPU misses constraints that aren't CPU-bound, which is most of them.
- **Cascading failure via shared dependency** — blast radius follows shared resources, not org charts.
- **Coordinated omission** — a closed-model load generator waits for responses, so it stops sending during a slowdown and under-reports latency at exactly the interesting moment.
- **Queue as hidden liability** — a buffer converts a throughput deficit into growing latency instead of errors, which is often right, but unbounded it hides the deficit until recovery is impossible. Bound queues; alert on depth *trend*.

## "Can it handle 10x?" — the procedure

Which 10x (traffic / data / users / tenants — they stress different constraints) → estimate on paper → stress to the knee → name the binding constraint **and the one after it** → state headroom and failure headroom → define the shedding path for when 10× arrives before the capacity does.

## The one-line principle

**Capacity is set by one binding constraint at a time; find it with arithmetic before you find it with an outage — and the last 20% of utilization is not capacity you own, it's the latency budget you're spending.**

---

## What changed in the reference

- **New Part 2.5** — `Throughput and Capacity Planning`: 2.4-vs-2.5 comparison table and load-independence routing test, Little's Law and utilization-knee tables, binding-constraint table (10 rows), back-of-envelope procedure, four test types, scaling-lever table with per-lever ceilings, six load-only failure modes, the 10x procedure
- `Part 2.4` — closing note routing load-dependent slowness to 2.5
- **Part 4** — nine new capacity-symptom rows (slow only above threshold, latency high with DB CPU low, writes plateau, round-number throughput, CPU-idle plateau, brownout→outage, spike-only failure, shedding)
- **Part 6** — meta-principle 12: headroom is not waste; one binding constraint at a time
- TOC updated with 2.5 subsections
