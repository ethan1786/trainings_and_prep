# S3-Like Object Storage System

**Category:** System Design — Low Frequency (1 occurrence: "blob storage")
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** Content-addressable chunking, deduplication, reference counting, garbage collection, replication, metadata/data separation

---

### Key Insights from hack2hire (Staff-level framing)

**The architectural insight:**
> "You do not store objects. You store content-addressed chunks and keep a manifest that maps each object key to its ordered list of chunk hashes. Dedup and replication both become simpler once the chunk hash is the universal address."

**The hard part is NOT the API.** It's keeping a tiny, consistent metadata index in sync with a massive distributed data layer where the same bytes may be shared across millions of objects. Every delete must know whether anyone else still needs those chunks before it can safely reclaim storage.

**Core tension:** Dedup makes writes cheap (skip existing chunks) but makes deletes dangerous (can't reclaim chunks others still reference).

**Two deep-dive areas that differentiate:**
1. **Dedup lifecycle + garbage collection safety** — the race between GC deleting a zero-ref chunk and a concurrent upload referencing that same hash
2. **Replication + failure recovery** — rack-aware placement, re-replication throttling, heartbeat-based detection

**Clarifying question to ask first:**
> "Are we designing the storage engine (chunk placement, dedup internals) or just the API layer (request routing)? That tells me where to focus."

---

## Requirements

### Functional
- PUT/GET/DELETE objects by bucket + key
- Deduplicate identical content (same bytes stored once)
- LIST objects with prefix filtering + cursor pagination
- Support objects from few KB to multiple GB

### Non-Functional
| Requirement | Target |
|---|---|
| Durability | 11 nines (99.999999999%) via 3x replication |
| Read availability | 99.99% (route to surviving replicas) |
| Scale | Petabytes, 10B+ objects |
| First-byte latency | < 200ms for objects up to 1MB |
| Dedup savings | ~30% (workload-dependent) |

### Scale Estimates
| Metric | Value |
|---|---|
| Total objects | 10 billion |
| Avg object size | 1 MB |
| Total raw storage | ~10 PB (30 PB with 3x replication) |
| Daily uploads | 100M (~1.2 GB/s sustained) |
| Peak read QPS | 50,000 |
| Chunk size | 64 MB |

---

## Architecture (Three Layers)

```
Client → API Gateway (metadata + coordination, NEVER proxies blob bytes)
              ↓
         Metadata Service (PostgreSQL — bucket/object/chunk relationships)
              ↓                          ↓
         Redis (hot path cache)     Data Nodes (commodity disks, chunks as files)
```

**Critical principle:** API gateway handles only metadata and coordination. Large uploads/downloads go directly between client and data nodes via **presigned URLs**. This prevents the gateway from becoming a throughput bottleneck.

---

## Data Model

```
Buckets: bucket_id, name (globally unique)

Objects: object_id, bucket_id, key, size, created_at
  → UNIQUE(bucket_id, key)

Object_Chunks: object_id, chunk_index (ordered), chunk_hash
  → manifest linking object to its chunks in order

Chunks: chunk_hash (PK, SHA-256), reference_count, size, replica_nodes[]
  → reference_count is the correctness linchpin
```

**Key invariant:** reference_count must ALWAYS reflect the true number of live manifests pointing to a chunk. Drift below = premature deletion = data loss. Drift above = storage leak.

---

## Core Flows

### Upload (PUT)
1. Gateway splits byte stream into 64 MB chunks, computes SHA-256 per chunk
2. For each hash: check metadata — exists? Skip upload, just increment ref count
3. For new chunks: select data nodes (rack-aware), issue presigned upload URLs
4. Client uploads directly to data nodes (gateway never touches bytes)
5. Once all chunks replicated (3x): commit manifest transaction atomically
   - Insert object row + object_chunks rows + increment ref counts — ALL in one txn
6. Object visible only after manifest commits (no partial visibility)

### Download (GET)
1. Gateway looks up manifest (Redis cache → PostgreSQL fallback)
2. Returns ordered chunk hashes + presigned download URLs per chunk
3. Client fetches chunks directly from data nodes in parallel
4. If one data node is down → fallback to another replica (3 copies exist)

### Delete
1. Remove object row + decrement ref counts for all chunks in manifest — one txn
2. Chunks reaching ref_count = 0 → enqueue for garbage collection
3. **DO NOT delete immediately** — GC runs with a safety window (see below)

---

## Deep Dive: Garbage Collection Safety

**The race condition:** Client A uploads object with chunk X. GC sees chunk X has ref_count = 0 and deletes it. Client A's manifest commits AFTER the delete → manifest points to deleted bytes → DATA LOSS.

**Solution: Deferred GC with grace period**

```
Chunk ref_count drops to 0 → record timestamp → add to GC candidate queue
                                                        ↓
GC runs periodically → checks each candidate:
  - ref_count still 0 AND grace period elapsed (24h)? → safe to delete
  - ref_count > 0? → remove from queue (new upload referenced it)
```

**Grace period must be > max upload duration** (if uploads can take 6h, grace period ≥ 6h, ideally 24h).

**Physical deletion is two-phase:**
1. Confirm ref_count still 0
2. Mark "pending deletion" in metadata
3. Send delete commands to data nodes
4. After all replicas confirmed deleted → remove chunk row from metadata

---

## Deep Dive: Replication + Failure Recovery

**Placement:** 3 replicas across 3 different racks (rack-aware). Single rack failure can't destroy all copies.

**Failure detection:** Data nodes send heartbeats every 10s. Missing > 30s → node marked failed.

**Re-replication:**
1. Identify all chunks on failed node
2. Check remaining replica count per chunk
3. Priority: chunks with 1 remaining copy > chunks with 2 remaining copies
4. Copy from surviving replica to new node in different rack
5. Throttle: limit concurrent re-replication per source node (don't overwhelm survivors)

**Node comeback:** If failed node recovers, reconcile via heartbeat. Extra replicas marked surplus for later cleanup.

---

## Key Trade-offs

| Decision | Choice | Why |
|---|---|---|
| Chunk size | 64 MB fixed | Keeps file counts manageable (~160K per 10TB disk). Small objects = single chunk. |
| Dedup granularity | Chunk-level SHA-256 | Falls out naturally from content-addressing. No extra work. |
| Replication vs erasure coding | 3x replication | Simple, fast recovery, easy to reason about. EC (6+3) saves storage but adds complexity. Dedup already reduces redundancy. |
| Metadata store | PostgreSQL | ACID txns for ref-count correctness. Shard by bucket_id at scale. |
| GC timing | 24h grace period | Prevents race with in-flight uploads. Conservative > risky. |
| Blob transfer | Presigned URLs (direct to data nodes) | Gateway stays lightweight, never bottlenecked on bandwidth |

---

## Staff+ Angle

- **"You don't store objects. You store content-addressed chunks."** — say this early, it's the design's foundation
- **GC safety is the correctness linchpin** — if you don't explain the race condition between GC and concurrent uploads, you haven't solved the hard problem
- **Presigned URLs are the scalability insight** — separates coordination (metadata QPS) from throughput (data bandwidth)
- **Reference counts must be transactional** — PUT and DELETE wrap ref-count updates in the same txn as the object row mutation
- **Rack-aware placement** — not "replicate to 3 nodes" but "replicate to 3 nodes in 3 different racks"

---

## Interviewer Expectations (Senior Bar)

> "A senior candidate drives to the hardest problems without prompting. They should design chunk-based architecture with content-addressed dedup from the start. Walk the full dedup lifecycle: hash on write, ref-count on create/delete, deferred GC with safety window, and what happens when GC races with an in-flight upload. On replication: rack-aware placement, re-replication throttling, and why 3-way replication before erasure coding."

---

## Connection to Your Experience

- **Presigned URLs** = same pattern as your payment system (client talks directly to external provider, your service just coordinates)
- **Reference counting + GC** = similar to your cache invalidation thinking (when is it safe to remove shared data?)
- **Metadata/data separation** = same principle as your orchestration layer (thin coordinator, heavy workers)
- **Append-only audit** = same as your event-sourced payment actions
