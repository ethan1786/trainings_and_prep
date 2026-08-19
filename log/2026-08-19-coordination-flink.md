# Coordination stores and stream processing

**Date:** 2026-08-19
**Questions:** What are ZooKeeper and etcd? Do we have Flink — and when would we need it?

---

## Coordination: one idea, three packagings

All three (ZooKeeper, etcd, Consul) are the same thing: a **small replicated KV store with a consensus protocol** — ZAB for ZooKeeper, Raft for the other two — answering questions that are hard when nodes crash and networks partition: who's the leader, who's alive, what's the current config (notify me on change), grant exactly one holder this lock.

Two primitives make them more than a tiny consistent database:
- **Watches** — subscribe to a key, get notified instead of polling.
- **Ephemeral state tied to a session/lease** — if the client stops heartbeating, its keys **disappear**. This is the magic behind leader election and liveness.

Quorum math explains the deployment shape: 3 nodes tolerate 1 failure, 5 tolerate 2, even counts are pointless. Hence always 3 or 5. And the engineering consequence: **writes are expensive** (round-trip to a majority), so these are for *coordination metadata that changes rarely and must be globally agreed* — never a database.

## Where each actually lives

- **ZooKeeper** — under Kafka, storing broker membership, topic configs, partition metadata. The important note: Kafka is **removing** it in favor of KRaft (consensus folded *inside* Kafka). Version pinning to stay pre-4.0 is literally a ZooKeeper dependency problem; a greenfield project already runs KRaft with no ZK.
- **etcd** — under **every Kubernetes cluster**, storing all cluster state. Invisible but total.
- **Consul** — the deliberate choice for *application-level* coordination: service discovery, and **leader election over the KV store** for singleton workloads (the snapshot builder, writers, ingestors).

## Three misconceptions I brought in

1. **"Distributed tools always use ZooKeeper."** *Was* true for the Hadoop-era generation; now actively reversing. The flagship example (Kafka) is the flagship example of *leaving*.
2. **"etcd is only for k8s, and we don't use it."** If you run Kubernetes you use it constantly — every pod, secret, and configmap lives there. Saying "we don't use etcd" is like saying "we don't use the filesystem."
3. **"Consul is a service mesh tool, like Linkerd from Twitter."** Four pillars — discovery, health, **KV**, multi-DC — and the KV+sessions leader election is often the heaviest real use. Also a factual fix: Linkerd is a separate product (Finagle lineage), not Consul.

## The SPOF correction

I said ZooKeeper "becomes a single point of failure." **A 3/5-node ensemble is quorum-fault-tolerant** — the same model as etcd/Consul Raft. The real costs are:
- **operational weight** — a second distributed system to deploy, monitor, tune, patch
- **shared-fate coupling** — an *external hard dependency* whose degradation impairs everything leaning on it

The war story that teaches it: a migration cleared a leader-election session and a service "could not recover until restarted." Two lessons — a coordination client must **re-establish its session** on failure rather than give up, and the KV store needed marking as a **P1 dependency**. That's the real danger: coordination stores are quiet, so teams forget a loud revenue service depends on them.

## Leader election mechanics

I asked whether it's coupled to health checks. **No** — and there are two different "leaders" being conflated:
1. Consul's **internal** Raft leader among its own servers (uses gossip/health, but it's Consul keeping *itself* consistent).
2. **Application** leader election — built purely on **KV + sessions**, not the service catalog. The liveness signal is *session heartbeat renewal*, not a registered health check.

Then I asked why "first to acquire the lock wins" — isn't that just random? Yes, deliberately, and that's the point:
- **The nodes are interchangeable**, so there's no "best" leader; any selection criterion would add complexity to decide something that doesn't matter.
- **Symmetry means no configuration** — every node runs the identical loop (try acquire → lead or watch).
- **Failover is automatic** — leadership is a lock tied to a TTL session; stop renewing and it auto-releases, watchers race, new leader in seconds.
- **Race-safe by construction** — the acquire is atomic, so a thundering herd resolves correctly; exactly one wins.

The tuning tension: short TTL = fast failover but false positives on a blip; long TTL = stable but slow failover. And the classic hazard — a partitioned leader that still *thinks* it leads for its TTL — is why singleton work should also be idempotent or fenced.

## Stream processing: no Flink, and why that's right

Essentially absent — mentioned only as a *future* idea for real-time index updates. What exists instead:
1. **Plain Kafka consumers** running app logic (the ingestors and writers) — per-event, lightly stateful.
2. **Warehouse ELT** for genuinely analytical stream work — land raw in object storage, transform at rest with SQL. The warehouse absorbs Flink's role.
3. **CDC-invalidate-then-refetch** for freshness — the event says "ID X changed," the consumer re-pulls current truth.

My summary was that it's unneeded because events are consumed immediately with no windowing, and load is small. Both right, but they're **independent** reasons that would fail independently:
- If **load grew** but the pattern stayed per-event → still no Flink; scale consumers horizontally.
- If a **windowing requirement appeared** at *low* volume → Flink (or a streams library) starts to earn its place *despite* volume.

So: **capability is the trigger, volume is only the cost.** The capability trigger is fault-tolerant **state across events** — windows, stream joins, pattern detection (CEP), large keyed aggregates — computed continuously, at low latency, with exactly-once correctness. All four words at once.

The escalation ladder that fell out: stateless/CDC-refetch → plain consumer; tolerates minutes → warehouse ELT; modest stateful streaming → a streams library *in-process* (no cluster); heavy state/CEP/scale → Flink, preferably managed.

The insight I want to keep: **the CDC-refetch design is what keeps the workload stateless.** Because the event carries only an ID and the consumer re-pulls truth, it never has to *reconstruct* state by folding the stream — which is exactly what would demand a stateful processor. The architecture is deliberately shaped to avoid needing windowing.

---

## What changed in the reference

- `ZooKeeper / etcd / Consul` tool entry — rewritten with KRaft, the invisible-etcd point, four Consul pillars
- `Lease-Based Execution and Leader Election` — the acquire-lock mechanism, TTL tuning, fencing
- `Flink / Stream Processing` — the four-word trigger and escalation ladder
- `corrections.md` — six entries
- `open-questions.md` — is the KV store monitored as P1
