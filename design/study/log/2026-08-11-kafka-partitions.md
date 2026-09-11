# Kafka partitioning and consumer scaling

**Date:** 2026-08-11
**Question that started it:** How does partitioning work, and can I pin a topic's publishes to one partition for ordering?

---

## The path

Started from a practical observation: creating topics without specifying partitions still works, so something is defaulting. Confirmed — auto-created topics get platform defaults (3 partitions / 3 replicas in the staging cluster), which means partition count is a **configuration decision that gets made for you if you don't make it**. It can be increased later but never decreased.

Then the real question: ordering is only guaranteed *within* a partition, so can I force everything to one partition? Yes — three ways: explicit partition number, a stable message key, or a custom partitioner. But the follow-up mattered more than the answer: **does that violate scaling?**

The resolution is a clean split:
- Pin **everything** to one partition → you've built a single-lane road. Ordering is global, throughput and consumer parallelism are capped at one.
- Key by **entity ID** → per-entity ordering preserved, different entities spread across partitions, consumer group still scales. This is almost always the right answer.

## The wrong turn worth keeping

I initially accepted "partitions = consumers is the guidance, so that's the rule." Pushed on it and the better framing emerged: that's a **conservative default**, not a sizing principle. The architecturally correct version is **size to max useful consumers, with headroom for bursts**.

But then I over-corrected to "so more partitions is always better," which is also wrong — over-partitioning has real costs (broker metadata, coordination, metrics cardinality; a 300-partition topic showed up as a contributor to a monitoring incident). The honest position is a band, not a direction: enough for peak useful parallelism, not more.

## The incident that made it concrete

A consumer-lag postmortem attributed lag growth to "a mismatch between the number of Kafka partitions and the number of active consumers" — 6 partitions but only 3 active pods, where the design expected 3+3 across two regions. Bouncing the service restored the intended pod count and fixed it.

I pushed back on the interpretation from a pure-technology angle: a consumer holding two partitions *could* process them concurrently if the app fans out to threads, so couldn't this be slow handlers or poll-loop starvation instead? And doesn't a bounce just add pods, proving nothing about partitions?

Both objections are technically sound. But the postmortem explicitly reported normal processing times and ruled out processing-time issues. So: **correct in principle, not what that postmortem claims happened.** Worth separating "what's mechanically possible" from "what the evidence says occurred."

Also learned that Kafka does **not** guarantee parallel processing across partitions held by one consumer instance — that's an application/framework choice. Parallelism comes from more *instances*.

## The hot-key problem

Keying by entity ID inevitably creates skew — a hot entity makes a hot partition. Four options: accept it (if ordering matters more), raise partition count so the rest spreads better, shard the key (`entityId#0..N`, but that relaxes strict ordering), or isolate the hot workload entirely.

The underlying constraint is unavoidable: **you cannot both strictly order one entity and spread that entity's writes across partitions.** Strict ordering means serialization somewhere.

## Discipline learned

One example stuck: a team considered adding partitions and concluded it wouldn't help, because the real constraint was a downstream REST API, not Kafka parallelism. **Verify the bottleneck is Kafka before scaling Kafka.** This became a recurring test across every later topic.

---

## What changed in the reference

- `Sharding / Partitioning` — escalation ladder, the ordering-vs-parallelism tradeoff, hot-key mitigations
- `Kafka` tool entry — partition sizing, the "more partitions ≠ better" caveat
- `corrections.md` — "one consumer with two partitions processes them in parallel", "partitions = consumers is the rule"
