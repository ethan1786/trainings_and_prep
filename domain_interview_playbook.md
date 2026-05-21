# Domain Interview Prep — Digital Transaction Platform

> For Coinbase VO Domain Interview (Friday).
> Format: Draw system on Miro, explain decisions, handle Q&A.

---

## Reference Diagram (Miro)

**Board URL:** https://miro.com/app/board/uXjVHXu9d5Q=/?focusWidget=3458764672763797588

Open in a separate tab during interview. Contains:
- Full transaction system architecture (orchestrator + services + state machine)
- Payment system deep-dive (state machine + webhooks + reconciliation)

---

## Presentation Flow (no scripts — just hit these points)

1. **Opening** (1-2 min) — context + your role
2. **Layer 1: Transaction System** (5-8 min) — draw final architecture, state WHY at each component
3. **Layer 2: Payment Deep Dive** (5-8 min) — auth-then-capture, state machine, failure modes
4. **Follow their lead** — answer whatever they drill into

---

## Context & Role

| Question | Answer |
|---|---|
| What is this system? | Digital transaction platform for car purchases. Customer sees true fees/taxes/financing/trade-in before putting down a deposit. Dealer gets verified customer info. Both sides see the same truth. |
| Why was it needed? | Pandemic — customers couldn't visit dealerships. Gap between online browsing and actual deal. We close that gap digitally. |
| What was your role? | Sole backend architect + primary implementer. All architecture decisions mine. Started with 2 backend engineers. Got promoted to Principal on this project. |
| What's the hard part? | Not scale (100-200 writes/min). It's correctness — when money is involved, can't lose state, can't double-charge, can't have stale data between customer and dealer. |

---

## Architecture — Key Decisions

| Component | WHY this design |
|---|---|
| **Orchestrator pattern** (core app) | Full visibility into transaction flow. One place to trace where things are, what failed, what to retry. |
| **Sequential sync HTTP to services** | Data dependencies: trade-in → fee/tax → financing → deposit. Can't parallelize. Strong consistency on critical path. |
| **Eventual consistency for leads/notifications** | Dealer notification can lag seconds. Not critical path. Decoupled via Kafka. |
| **Single DB (Postgres)** | 100-200 writes/min. Doesn't justify separate DBs. Config + transactional in same DB, different tables. |
| **In-memory cache (Kafka-invalidated)** | 10-15K rpm config reads. Not TTL-based — events keep cache consistent. No Redis needed. |
| **Feature flags** | Product experiments. Safe retirement. Kill experiments without code deploys. |
| **State machine** (transaction) | CREATED → TRADE_IN → FEE_TAX → FINANCING → DEPOSIT. Enforces data dependency chain. If customer updates trade-in, everything downstream recalculates. |

---

## Payment System — Key Points

| Point | Detail |
|---|---|
| **Auth-then-capture** | Authorize immediately (hold funds). Capture only when dealer confirms. Cancel before capture = free (release hold). "Auth is not the charge." |
| **Payment state machine** | AUTH → CONFIRMED → CAPTURED → PAID_OUT. Branches: CANCELLED, REFUNDED, DECLINED. |
| **Dual communication** | Outbound: sync HTTP to Stripe (auth, capture, cancel). Inbound: async webhooks (confirmation, failure). |
| **Source of truth** | Remote provider (Stripe). Always poll before action. Never act on stale local state. |
| **Idempotency** | Customer_id + vehicle_id as dedup key in Redis. Checked before any auth call. Prevents double-charge. |
| **Audit trail** | Append-only action records (linked list). Never mutate. Full history for disputes/compliance. |
| **Reconciliation** | Daily job compares internal records vs Stripe settlement. Catches missed webhooks, stuck payments. |

---

## Failure Modes (know all of these)

| Failure | Recovery |
|---|---|
| **Stripe returns error on auth** | Roll back to CREATED. Return error to user. Compensating transaction. |
| **Auth succeeds but DB write fails** | Webhook will arrive and create/correct record. Poll-before-action on next operation reads latest from Stripe. |
| **Webhook never arrives** | Don't wait. Actively poll on next action. Daily reconciliation job catches stuck payments. |
| **Duplicate webhook** | Idempotency key saved in DB after processing. Second event is no-op. |
| **Out-of-order webhook** | Some transitions tolerated, some not. Invalid critical transitions prompt support review. |
| **Hold expires (7 days)** | Stripe auto-releases. Expired webhook updates our record. Re-auth available if deal still active. |
| **Cancel-capture race** | Stripe is authority. Only one succeeds. Poll-before-action ensures we check latest state. |
| **Customer clicks pay twice** | Redis dedup key (customer_id + vehicle_id). Second request rejected before hitting Stripe. |
| **Fee/Tax service slow** | Cached by dealer. If cache miss + slow: return partial data with error. Customer fixes before deposit. |
| **Loan service down** | Non-blocking. Customer proceeds without estimate. Can add later. |
| **Refund after capture** | Separate flow, requires support review (we lose processing fee on refunds). |

---

## Orchestration & Architecture Deep Dive

| Question | Answer |
|---|---|
| **Why sequential, not parallel?** | Real data dependencies — trade-in value affects fee/tax, fee/tax affects deposit amount. Nothing can parallelize. |
| **Why orchestration, not choreography?** | Full visibility. One place to see where a transaction is, what failed. Choreography = "which event got lost between which services?" — debugging nightmare. At our scale, orchestration's coupling cost is worth the control. |
| **Why monolith-first?** | No traffic at launch. Didn't know domain boundaries. Monolith = lowest cost to ship + validate business model. Extracted later when we understood the real fault lines. |
| **What triggers extraction?** | Operational readiness: CI/CD supports it, team has bandwidth, product agrees. Technical: different deploy cadence, different ownership, different reliability needs. |
| **Config vs transactional data?** | Same DB, different tables. Config: read-heavy, cached aggressively, long TTL. Transactional: write-heavy, strongly consistent, no cache for active records. |
| **Configurable flows (not all dealers offer trade-in)?** | Config-driven. If feature not configured, skip in UI. Backend validates config before each step. |
| **Adding a new service (e.g., insurance)?** | Add as optional step in backend. Plug in integration, test. Release in UI via feature flag. |

---

## Scale & Performance

| Metric | Value | Implication |
|---|---|---|
| Config/consumer reads | 10-15K rpm | Cached in-memory, Kafka-invalidated |
| Transaction reads | ~2K rpm | Moderate, strong consistency |
| Transaction creates | 100-200/min | Single DB handles fine |
| Read:write ratio | ~10:1 | Cache-first architecture |
| Why no Redis? | Volume doesn't justify it | In-memory cache + Kafka invalidation is sufficient |
| Why no sharding? | 100-200 writes/min | Way below Postgres limits |

**Key line:** "I sized for actual load. Didn't over-engineer. That's judgment."

---

## Operational Excellence

| Question | Answer |
|---|---|
| **What do you monitor?** | Engineering: 200/500 rates, RPM, p50/p99, cache miss rate, DB pool, payment auth errors by code, webhook lag, reconciliation mismatches. Product: funnel conversion, drop-off rates. |
| **On-call at 3 AM — payment auth fails?** | One dealer or all? One = their config, notify them. All = check provider status page. Provider healthy? Check our deploys (rollback if recent), connection pool, credentials. Emergency lever: disable payments via feature flag. |
| **How to deploy safely?** | Canary deploys. Spring Boot graceful shutdown (finish active requests). Risky changes wrapped in feature flags — new transactions use new path, existing ones finish on old path. |
| **How to test end-to-end?** | Staging with real payment provider in test mode (test cards, real API calls, real webhooks, prod DB copy). No mocking the provider — too critical to fake. |

---

## Transaction State Machine Details

| Question | Answer |
|---|---|
| **Payment states?** | CREATED → AUTHORIZED → CAPTURED → PAID_OUT. Branches: CANCELLED, DECLINED, REFUNDED. |
| **Transaction states?** | Not rigid — it's a data processing flow. Steps are optional, any order in UI. Backend enforces dependency chain: trade-in → fee/tax → financing → deposit. Terminal: "deposit placed" or "appointment made." |
| **What triggers transitions?** | Customer or dealer actions. Some triggered by webhooks (payment confirmations). |
| **Concurrent mutations (cancel vs capture)?** | Stripe is authority. Only one succeeds. Poll-before-action pattern. Reconciliation catches edge cases. |
| **State machine enforcement?** | Application code. Checked before DB update. Not DB-level constraints (simpler). |

---

## Staff+ Judgment Questions

| Question | Answer |
|---|---|
| **What would you redesign today?** | Architecture is sound. Would add: (1) CRM integration from day one, (2) GraphQL as data layer earlier, (3) AI features baked in (fraud detection, conversational agent). |
| **How would you use AI?** | (1) Fraud detection — flag suspicious patterns before hitting provider. (2) Conversational AI agent replacing multi-step form — guides customer through trade-in/financing/deposit conversationally. MCP APIs I built are the foundation. (3) Anomaly detection on operational metrics — alert before customers notice. |
| **What was the hardest part?** | Not technical complexity — organizational alignment under shifting requirements. Architecture's job was to absorb uncertainty (configurable flows, feature flags, flexible state model). |
| **Why should Coinbase care?** | Auth-then-capture = limit order. Payment state machine = order lifecycle. Webhook reconciliation = blockchain settlement. Same correctness requirements: can't lose, can't double-execute, must reconcile. |

---

## Key Principles (weave naturally)

- **"Auth is not the charge"** — same as "hold is not the trade"
- **"Provider is the source of truth"** — always poll before acting
- **"Append-only, never mutate"** — audit trail for financial compliance
- **"Reconciliation runs always"** — not error handling, permanent safety net
- **"Strong consistency for money, eventual for everything else"**
- **"Sized for actual load — didn't over-engineer"**
- **"Correctness over performance"** — redundant validation at every step
