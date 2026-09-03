# Adding a queue: greenfield design versus retrofit

**Date:** 2026-08-25
**Question that started it:** Is adding a queue straightforward in a new system but difficult in an existing synchronous system?

## Decision

Yes. In a new system, a queue is often a direct expression of the delivery contract: the caller does not need the result immediately, work can be retried independently, or consumers should scale and deploy separately. Traffic affects sizing, but a queue can be justified before exact traffic is known because the semantics are already asynchronous.

In an existing system, adding a queue crosses several boundaries at once:

* What does a successful response mean?
* When is the data durable?
* Which component owns the transaction?
* What happens if publishing succeeds but the database write fails, or vice versa?
* Are retries and duplicate messages safe?
* Can existing callers handle `202 Accepted` and an operation ID?

The safest retrofit usually extracts non-critical side effects. Keep the synchronous source-of-truth transaction, write an outbox record in that same transaction, relay it to the queue, and process the side effect with an idempotent worker.

If the primary operation itself can be deferred, make that a deliberate asynchronous contract: enqueue a durable command, return `202 Accepted` plus an operation ID, provide status, and define idempotency and retry behavior. Do not change from completed-response semantics to accepted-response semantics only during a traffic spike.

A queue placed in front of work while the request waits for the worker is a third, limited pattern. It can act as an internal concurrency limiter, but it adds queueing latency and request-timeout ambiguity; it does not create more database capacity and should not be confused with asynchronous delivery.

## Retrofit sequence

1. Identify the existing response and durability contract.
2. Separate core transactional work from deferrable side effects.
3. Prefer an outbox for post-transaction events.
4. If the primary operation moves async, introduce an explicit command/status contract.
5. Make consumers idempotent and assume at-least-once delivery.
6. Canary the consumer and observe lag, retries, duplicate handling, and end-to-end latency.
7. Only then make the asynchronous path authoritative.



## Follow-up observation

True asynchronous workflows are usually designed that way from the beginning. The queue decision propagates into API response semantics, UI state transitions, operation tracking, retries, notifications, permissions, auditability, and recovery. That is why a retrofit more commonly queues side effects behind an unchanged synchronous transaction, or introduces a separate explicit async workflow, rather than silently converting an existing endpoint during load.

## What changed in the reference

* `Message Queue / Async Processing` — added greenfield versus retrofit guidance, outbox-based side-effect extraction, explicit async command contracts, and the internal-smoothing caveat
