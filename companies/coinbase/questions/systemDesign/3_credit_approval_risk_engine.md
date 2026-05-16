# Credit Approval Risk Engine + Credit Card System

**Category:** System Design
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** Async workflows, idempotency, state machines, external provider fan-out, financial auditability

### Key Insights from hack2hire (Staff-level framing)

**The core tension:** Applicants want a fast answer. Evidence comes from slow, flaky, contradictory providers. The architecture earns its keep when the deadline turns that conflict into a predictable branch instead of a lottery.

**Three deep-dive areas that matter (ignore everything else if short on time):**
1. **Bounded deadline orchestration** — hard 5s cap. If mandatory evidence isn't ready, return `manual_review` honestly. Don't hang the HTTP response.
2. **Reproducible decision snapshots** — the score is NOT the decision. Decision = versioned policy + model outputs + signal snapshots, frozen immutably. Replay must produce same outcome months later.
3. **Manual review as first-class lifecycle** — not a "vague escalation." It's ~5% of volume with queues, SLAs, assignments, and structured overrides that append (never rewrite) history.

**Clarifying question to ask first:**
> "Am I allowed to return `manual_review` when key evidence is missing? That single permission changes latency, API semantics, and how hard I lean on async callbacks."

**What separates Senior from Staff here:**
- Senior: separates intake from underwriting, mentions idempotency and manual review
- **Staff: owns the tension between applicant latency and evidence completeness. Articulates deadline-bounded orchestration with mandatory gates. Treats decision snapshots with policy/model versions as the compliance boundary. Connects audit to snapshot design, not "we have logs."**

**Golden line:**
> "Provider dashboards are not authoritative. Our rows are. If a callback arrives twice, the second is a no-op. If conflicting payloads show up, policy routes toward manual review and we preserve both observations."

---

## Problem Statement

Design a system that accepts credit card applications, fans out to multiple slow/unreliable external risk providers (credit bureau, fraud, KYC, income verification), and produces an approved/denied/manual_review decision. The user must never wait for external checks — return a `processing` status immediately and finish in the background.

---

## Requirements

### Functional
- Accept application, return an ID and `processing` status instantly
- Fan out to 4-8 external risk providers asynchronously
- Apply versioned rules + ML score to produce: `approved`, `denied`, or `manual_review`
- Allow users and support to poll status and retrieve the final decision
- Never run a check or approve a user twice (idempotent at every layer)

### Non-Functional
| Requirement | Target |
|---|---|
| Accuracy | Zero duplicate applications or provider calls |
| User-facing latency | Ack < 10s; full decision < 5 min |
| Availability | 99.95% |
| Auditability | Append-only event log (regulatory requirement) |
| Scalability | Handle marketing-campaign spikes (>500 req/s) |

### Scale Estimates
| Metric | Value |
|---|---|
| Applications/day | 2,000,000 (~23/s avg, 500+/s peak) |
| External calls per app | 4-8 |
| External traffic peak | 2,000-4,000 calls/sec |
| Storage | ~12 TB/year |

Key insight: backend external-call throughput is 10-20x user-facing throughput.

---

## Data Model

```
Application
├── id: UUID (PK)
├── applicant_id: UUID (FK)
├── product_type: VARCHAR
├── channel: ENUM (web, mobile, partner_api)
├── status: ENUM (received, processing, awaiting_external,
│              ready_for_decision, approved, denied, manual_review, expired)
├── decision_id: UUID (FK, nullable)
├── idempotency_key: VARCHAR — UNIQUE with applicant_id
├── created_at, updated_at, expires_at: TIMESTAMP

RiskSignal
├── id: UUID (PK)
├── application_id: UUID (FK)
├── provider: ENUM (bureau, kyc, fraud, income)
├── provider_request_id: VARCHAR — idempotency key for external call
├── signal_type: VARCHAR
├── signal_payload: JSONB
├── status: ENUM (pending, success, failed, timed_out)
└── received_at, expires_at: TIMESTAMP

Decision
├── id: UUID (PK)
├── application_id: UUID (FK)
├── outcome: ENUM (approved, denied, manual_review)
├── risk_score: DECIMAL
├── reason_codes: JSONB
├── ruleset_version: VARCHAR   — required for audit/rollback
├── model_version: VARCHAR
├── decided_at: TIMESTAMP
└── decided_by: ENUM (system, human_reviewer)

ApplicationEvent  — append-only, never updated
├── id: UUID (PK)
├── application_id: UUID (FK)
├── event_type: VARCHAR
├── payload: JSONB
└── created_at: TIMESTAMP
```

State machine rule: external provider callbacks **only** write to `RiskSignal`. A single central Decision Service reads signals and writes the final `Application.status`. No distributed decision writes.

---

## API Design

### Public REST

```
POST /api/credit-applications
Headers: Idempotency-Key: <client-generated UUID>
Body: { product_type, applicant: { legal_name, dob, ssn_last4, annual_income } }
Response: { application_id, status: "processing", next_poll_after_seconds: 3 }

GET /api/credit-applications/{id}
Response: { application_id, status, latest_step, updated_at }

GET /api/credit-applications/{id}/decision
Response: { application_id, outcome, risk_score, reason_codes }
```

### Internal Kafka Topics

```
credit.application.submitted   → triggers workflow start
credit.external.requested      → provider fan-out
credit.external.completed      → signal processor ingests result
credit.decision.ready          → all signals gathered, trigger decision
credit.decision.finalized      → outcome written
```

### Provider Callback (Internal)

```
POST /internal/providers/{provider}/callbacks
Body: { provider_request_id, status, payload, signature: <HMAC> }
```

---

## Architecture

| Component | Role |
|---|---|
| Application API | Auth, idempotency check, write `Application` row, publish `submitted` event, return 202 |
| Outbox Relay | Transactional outbox — reads DB-committed events, publishes to Kafka. Guarantees no lost events on crash. |
| Workflow Orchestrator | Temporal/Step Functions. Manages provider fan-out, timeouts, retries. One workflow per Application ID. |
| Worker Pools | Pick tasks from queue, call external adapters, write `RiskSignal` on return |
| External Adapter Gateway | Per-vendor translation + rate limiting (token bucket). Decouples internal format from vendor APIs. |
| Signal Processor | Listens on `credit.external.completed`. When all required signals are present, publishes `decision.ready`. |
| Decision Service | **Single writer** for `Application.status`. Runs rules engine + model, writes `Decision` row, publishes `decision.finalized`. |
| Status Cache (Redis) | Caches current application status for fast polling. TTL-invalidated on state transitions. |

### Key Data Flow

```
User → API → DB (Application row + Outbox event)
           ↓ Outbox Relay
         Kafka (submitted)
           ↓ Workflow Orchestrator
     [Fan out to 4-8 providers in parallel]
           ↓ Worker Pools → External Adapters → Providers
     Provider callbacks → Signal Processor → RiskSignal rows
           ↓ (when all signals received)
         Decision Service → Decision row + Application status update
           ↓
         Kafka (finalized) → Status Cache invalidation
```

---

## Deep Dives

### Idempotency (3 layers)

**Layer 1 — API:** `UNIQUE(applicant_id, idempotency_key)` with `ON CONFLICT DO NOTHING`. Handles double-click / client retry.

**Layer 2 — Workflow:** Workflow engine enforces one active workflow per `application_id`. A crashed and restarted workflow resumes from its last checkpoint, not from the beginning.

**Layer 3 — Provider calls:** Each external call uses a deterministic key: `{app_id}_{provider}_{attempt}`. If a worker crashes mid-flight and retries, the vendor deduplicates on their end.

```sql
CREATE UNIQUE INDEX uq_applicant_idempotency
ON credit_applications (applicant_id, idempotency_key);

INSERT INTO credit_applications (id, applicant_id, idempotency_key, status, created_at)
VALUES (gen_random_uuid(), $1, $2, 'processing', NOW())
ON CONFLICT (applicant_id, idempotency_key) DO NOTHING
RETURNING id;
```

### Failure Handling

| Failure | Response |
|---|---|
| Client timeout on submit | Idempotency key allows safe retry — returns existing `application_id` |
| Worker crash mid-check | Workflow engine detects timeout, restarts task from last checkpoint |
| Provider down | Circuit breaker trips; defaults to `manual_review` for that signal |
| Kafka outage | Outbox persists in DB; replay resumes when Kafka recovers |
| Bad rule deployment | Ruleset is versioned; roll back version, re-run Decision Service against existing signals |

### Scaling Bottlenecks

**External call volume:** Fan-out generates 10-20x user-facing traffic. Worker pools must be sized for 2,000-4,000 calls/sec peak. Use per-vendor token buckets to respect rate limits.

**DB write amplification:** Each application triggers writes to `Application`, multiple `RiskSignal` rows, `WorkflowExecution`, `Decision`, and N `ApplicationEvent` rows. Separate the audit log (`ApplicationEvent`) onto a write-optimized store (append-only, partitioned by time).

**Status polling under spike:** Cache status in Redis with a TTL. Invalidate on every state transition. Prevents read amplification from `next_poll_after_seconds: 3` polling patterns.

---

## Key Trade-offs

| Decision | Choice | Why |
|---|---|---|
| Workflow engine | Managed (Temporal/Step Functions) vs. custom | Managed handles retry logic, timeouts, checkpointing — worth the cost |
| Provider integration | Async Kafka vs. direct RPC | Kafka decouples workers from providers; provider failures don't cascade |
| Decision writer | Single service vs. distributed | Single writer prevents race conditions on final status |
| Audit log | Append-only vs. mutable | Regulatory requirement; also enables replay for rule version rollbacks |
| External call idempotency | Per-attempt key vs. per-application key | Per-attempt allows retries without re-running successful prior attempts |

---

## Staff+ Angle

- **Regulatory surface area:** In financial systems, the audit log is not optional — it's the evidence trail regulators pull. Every state transition, rule version applied, and human override must be captured.
- **Rollback capability:** Rule and model versioning is what separates a production system from a prototype. If a bad rule ships and denies 10% of valid applicants, you need to replay decisions against the stored signals with the corrected ruleset — without re-calling external providers.
- **Single-writer pattern:** Proactively mention this. The classic failure mode is multiple workers racing to write `approved` — you can end up with multiple `Decision` rows or a corrupt final state. Centralizing the write is the fix.
- **Crypto-specific angle (Coinbase):** KYC/AML checks are more complex for crypto than traditional credit. There may be on-chain history signals, jurisdictional compliance (OFAC screening), and Travel Rule requirements layered on top of traditional bureau checks. The provider fan-out architecture handles this naturally — just add more adapter types.
- **Proactive to mention:** The outbox pattern. Most candidates forget that if the API writes to the DB and then crashes before publishing to Kafka, the event is lost. The transactional outbox solves this without distributed transactions.

---

## Interview Checklist

- [ ] Justified async response ("never block the user") before touching the design
- [ ] Mentioned idempotency at all three layers (API, workflow, provider)
- [ ] Defined Application, RiskSignal, Decision, ApplicationEvent tables
- [ ] Showed state machine transitions (received → processing → ... → approved/denied)
- [ ] Used a workflow engine for fan-out and timeout management
- [ ] Single writer for final decision (no race conditions)
- [ ] Circuit breaker for provider failures → default to manual_review
- [ ] Append-only audit log with rule versioning
- [ ] Addressed retry storm risk (retry budgets, exponential backoff)
