# Open Questions

Unverified claims and unresolved gaps, each with **what would settle it**. This is the next-investigation queue.

Confidence labels: `verified` (read the source), `inferred` (reasoned from evidence), `unverified` (plausible, untested).

---

## Storage and lifecycle

### Do old search-index snapshots have a TTL?
**Status:** `unverified`
**Context:** Snapshots are generated on a cron a few times a day and written to timestamped object-storage prefixes. Versioning by timestamp is confirmed; an expiry policy is not. An unbounded thrice-daily snapshot bucket is a concrete, quiet cost leak.
**What would settle it:** Read the bucket's lifecycle configuration in the Terraform module or the S3 console. Look for an expiration rule on the snapshot prefix.
**Why it matters:** If absent, it's a cheap, uncontroversial cost win — pure housekeeping, no architectural argument needed.

### Are incomplete multipart uploads being aborted?
**Status:** `unverified`
**Context:** Failed multipart uploads leave orphaned parts that are billed but invisible as normal objects. The standard mitigation is a lifecycle rule to auto-abort after N days.
**What would settle it:** Check for an `AbortIncompleteMultipartUpload` rule on buckets that receive large artifact uploads.

### Is Intelligent-Tiering applied to artifact and capture buckets?
**Status:** `unverified`
**Context:** Snapshot archives, CI artifacts, and ML capture data are written once and read rarely — near-ideal for automatic tiering, which has no retrieval fee.
**What would settle it:** Check storage-class configuration on those buckets.

### Do critical buckets replicate cross-region?
**Status:** `unverified`
**Context:** Given a multi-region footprint, whether critical buckets have cross-region replication for DR is a legitimate gap. The search DR story is "rebuild from source," which is sound — but that doesn't cover buckets whose contents *are* the source.
**What would settle it:** Check replication configuration; more importantly, identify which buckets hold data that is not reconstructible from elsewhere.

---

## Caching and the client edge

### Does the SSR layer set cache headers on loader/document responses?
**Status:** `unverified` — and this is the empirical crux of the whole caching thread.
**Context:** Introducing a server-side rendering layer **moves the client edge** to browser↔SSR. The SSR↔router hop is internal (no edge caching expected, none lost). Whether free CDN caching survives is therefore a *config* question about the SSR layer, not a paradigm limitation.
**What would settle it:** Inspect response headers on a page/loader request — look for `Cache-Control`, `ETag`, and whether a CDN sits in front. Then compare against what the pre-SSR endpoint returned.
**The conditional conclusion:** The "we lost free caching" claim is only true if (a) the old content was genuinely cacheable — static/anonymous/GET — **and** (b) the SSR layer isn't caching now. For personalized content, there was likely nothing to lose; personalization killed cacheability, not the API paradigm.

### Does the federated router deduplicate identical entity representations?
**Status:** `unverified`
**Context:** In the high-fan-in case (many parent records referencing few unique child entities), does the router collapse duplicate representations before sending the batch, or pass all N?
**What would settle it:** Router configuration/docs, or observe the actual `_entities` request payload for a list query with known duplicate references.
**Why the answer doesn't change much:** even if the router passes all N, the owning subgraph's own batch loader collapses them on the datastore side. The fan-in win survives either way — it just moves layer. Worth knowing precisely, not worth blocking on.

### Is response/entity caching enabled anywhere in the router deployment?
**Status:** `inferred` — non-caching by default, treat as today's contract.
**Context:** Plan/normalization caching (router CPU) is present; entity/response caching is the hard part and appears unbuilt. But roadmap language suggests this could change.
**What would settle it:** Read the current router configuration at design time rather than assuming. Don't design against "never caches" as a permanent guarantee.

---

## Event-driven vs polling

### Are object-storage event notifications used, or is everything polled?
**Status:** `unverified`, leaning underused.
**Context:** Several ingestion and ML pipelines use scheduled polling or a third-party polling loader. The idiomatic alternative is object-created events (→ queue/function) to trigger loads — lower latency and cheaper than polling.
**What would settle it:** Check for event-notification configuration on landing buckets, and compare pipeline latency requirements against poll intervals.
**Why it matters:** This is the highest-leverage architectural nit in the S3 material — it's a latency *and* cost improvement with no new platform.

---

## Streaming and concurrency

### What is the measured per-operation latency on the shared connection pool under burst?
**Status:** `unverified`
**Context:** Pool exhaustion is governed by `outstanding_ops ≈ arrival_rate × op_latency` (Little's Law). Without a measured `op_latency` under burst — including during managed-service maintenance windows, when latency spikes hold connections longer — pool sizing is guesswork.
**What would settle it:** Instrument per-operation duration and concurrent-checkout count; compute the concurrency at which a given `maxPoolSize` begins queuing.
**Why it matters:** This is what turns the disconnect/zombie-stream argument from qualitative into quantitative — it produces the number that justifies the fix.

### Does the client-disconnect fix measurably reduce pool pressure?
**Status:** `unverified` — hypothesis is well-grounded, effect size unmeasured.
**What would settle it:** Compare concurrent-stream gauge and pool-checkout metrics before/after abort-on-close.

---

## Coordination

### Is the coordination KV store treated as a P1 dependency in monitoring?
**Status:** `inferred` — a ticket was filed to mark it as such after an incident; whether it landed is unconfirmed.
**Context:** A coordination store's degradation silently impairs every service whose leader election depends on it. The failure surfaces as an application error, not a coordination alert — which is what makes it hard to trace.
**What would settle it:** Check alerting/dependency configuration for the KV cluster.
**Generalizable lesson (already captured):** the danger of coordination stores is that they're quiet, so teams forget a loud revenue service depends on them.

---

## Method notes

Two standing caveats on everything above:

1. **"Not in the docs" ≠ "not used."** Absence of evidence in searchable documentation is weak evidence of absence, especially for pervasive infrastructure.
2. **Most gaps are correct choices, not oversights.** Before flagging something as missing, ask whether it's genuinely shaped for this environment. Several unused capabilities are unused *correctly*.
