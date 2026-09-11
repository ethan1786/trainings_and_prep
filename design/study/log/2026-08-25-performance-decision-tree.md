# Performance decision tree: database bottleneck branch

**Date:** 2026-08-25
**Question that started it:** When a performance problem reaches the database, should the system switch from synchronous to asynchronous delivery during traffic spikes?

## Decision

A traffic spike alone should not change the delivery contract. First determine whether the database query is inefficient, whether the same read is repeated, whether concurrency is exhausting database capacity, whether the work can be deferred, and whether capacity is permanently insufficient.

For a database bottleneck:

* Fix query plans, indexes, N+1 behavior, and over-fetching before hiding the issue with a cache.
* Cache repeated read-heavy work when staleness is acceptable and key reuse justifies the complexity.
* Bound database concurrency and apply backpressure when connection, CPU, or lock capacity is the constraint.
* Queue durable work only when the caller can accept deferred completion; workers should run at a database-safe rate.
* Keep synchronous operations synchronous when the caller requires confirmation. Optimize, batch, scale/shard, or return `429`/`503` under overload.

A queue is a capacity shaper and finite-burst buffer, not a solution to sustained arrival rate above processing capacity. Switching from `200 completed` to `202 accepted` solely because the cluster is busy is an API contract change and should not happen implicitly.

## Investigation order

1. Attribute latency and saturation to the application, dependency, cache, or database.
2. If the database is involved, verify the query plan and access pattern.
3. Measure repeatability before choosing a cache.
4. Determine whether the limiting resource is query cost, DB concurrency, connection pool, write throughput, or total capacity.
5. Choose a stable sync or async contract based on caller semantics.
6. Add bounded concurrency, queue depth, worker rate, and overload behavior explicitly.

## Study note

This extends the caching decision tree. The cache is one branch under “repeated read,” not the default response to every slow database call. The queue is one branch under “completion may be deferred,” not a mode switch triggered by temporary traffic pressure.
