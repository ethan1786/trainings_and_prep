# Domain Interview Prep — Digital Transaction Platform

> For Coinbase VO Domain Interview (Friday).
> Format: Draw system on Miro, explain decisions, handle Q&A.

---

## Reference Diagram (Miro)

**Board URL:** https://miro.com/app/board/uXjVHXu9d5Q=/?focusWidget=3458764672763797588

---

## Opening

CarGurus is a car marketplace, we connect buyers with dealers. The gap we solved: before my platform, customers only submitted contact info. Dealers called them blind. I built a transaction platform that gives both sides the full information: trade-in values, fees and taxes, financing, and a way to hold the car by putting down a deposit, before anyone picksup the phone.


---

## Context & Role

| Question | Answer |
|---|---|
| What is this system? | Digital transaction platform for both customers and dealers. Customers see full estimation of trade-in values, fees, financing, and can hold a car by putting down a deposit. Dealers get enhanced customer information and a more confirmed lead when customers come to the store for a test drive. |
| Why was it needed? | Introduced during pandemic — consumers couldn't come to the store. We close the gap: give consumers more confidence before entering a dealership, give dealers more information about consumers to push forward with the deal. |
| What was your role? | Sole backend architect + primary implementer. All architecture decisions mine. Started with 2 backend engineers. Got promoted to Principal on this project. |
| What's the hard part? | Three things: (1) Figuring out product ambiguities — fast iterations across teams to find better product designs. (2) Product vs engineering tradeoff judgment — knowing when to ship fast vs invest in correctness. (3) Strong correctness and robustness for the payment/financial system — can't lose state, can't double-charge, must handle money safely. |

---

## Architecture — Key Decisions

| Component | WHY this design |
|---|---|
| **Per-step service calls** (not a chain) | Each step is a separate customer action → one downstream call. State machine enforces dependency order (can't calc fees without trade-in). Not one long-running request chaining through services. |
| **Eventual consistency for leads/notifications** | Dealer notification can lag seconds. Not critical path. Decoupled via Kafka. |
| **Single DB (Postgres)** | 100-200 writes/min. Doesn't justify separate DBs. Config + transactional in same DB, different tables. |
| **Redis cache (write-through)** | Improves read performance. Write to DB first, then update Redis. No race condition concern — one customer updates one transaction at a time. |
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
| **Idempotency** | Customer_id + vehicle_id is compound key for the transaction. Transaction ID attached as idempotency key on Stripe calls. Only two calls touch the card: auth (transaction ID as key — Stripe won't create two holds) and capture (auth ID — can only capture a hold once). Redis lock on transaction ID dedupes concurrent requests before hitting Stripe — reduces server load and protects Stripe rate limits. |
| **Audit trail** | Append-only action log in DB for all transaction actions with full details. Never mutate — only append. Full history for disputes, compliance, and reconciliation. |
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
| **Hold expires (7 days)** | Daily reconciliation job detects expired holds and updates our records. Webhook is another trigger. Re-auth available if deal still active. |
| **Cancel-capture race** | Stripe is authority. Only one succeeds. Poll-before-action ensures we check latest state. |
| **Customer clicks pay twice** | Three layers: (1) API dedup by transaction compound key (customer + vehicle), (2) Redis lock on transaction ID in payment service blocks concurrent/retry requests, (3) Transaction ID as Stripe's idempotency key on auth call — even if two requests reach Stripe, only one auth created. |
| **Fee/Tax service slow** | Cached by dealer. If cache miss + slow: return partial data with error. Customer fixes before deposit. |
| **Loan service down** | Non-blocking. Customer proceeds without estimate. Can add later. |
| **Refund after capture** | Separate flow, requires support review (we lose processing fee on refunds). |

---

## Orchestration & Architecture Deep Dive

| Question | Answer |
|---|---|
| **Config vs transactional data?** | Same DB, different tables. Config: read-heavy, cached aggressively, long TTL. Transactional: write-heavy, strongly consistent, no cache for active records. |
| **Configurable flows (not all dealers offer trade-in)?** | Config-driven. If feature not configured, skip in UI. Backend validates config before each step. |
| **Adding a new service (e.g., insurance)?** | Add as optional step in backend. Plug in integration, test. Release in UI via feature flag. |

---

## Scale & Performance

| Metric | Value | Implication |
|---|---|---|
| Config/consumer reads | 10-15K rpm | Cached in Redis (write-through) |
| Transaction reads | ~2K rpm | Moderate, strong consistency |
| Transaction creates | 100-200/min | Single DB handles fine |
| Read:write ratio | ~10:1 | Cache-first architecture |
| Why no sharding? | Two reasons | (1) Volume is low (100-200 writes/min). (2) Transactions older than 6 months moved to separate reporting DB — active table stays small. |

**Key line:** "I sized for actual load. Didn't over-engineer. That's judgment."

---

## Operational Excellence

| Question | Answer |
|---|---|
| **What do you monitor?** | Engineering: 200/500 rates, RPM, p50/p99, cache miss rate, DB pool, payment auth errors by code, webhook lag, reconciliation mismatches. Product: funnel conversion, drop-off rates. |
| **On-call at 3 AM — payment auth fails?** | Honestly never happens — payment service is low traffic and not the source of truth. If service is unhealthy, SRE on-call bounces it. No eng investigation needed. If Stripe is down, customers just can't deposit until it's back — transaction data is safe, no money at risk because nothing gets authorized. |
| **How to deploy safely?** | Canary deploys. Spring Boot graceful shutdown (finish active requests). Risky changes wrapped in feature flags — new transactions use new path, existing ones finish on old path. |
| **How to test end-to-end?** | Staging with real payment provider in test mode (test cards, real API calls, real webhooks, prod DB copy). No mocking the provider — too critical to fake. |

---

## Key Principles (weave naturally)

- **"Auth is not the charge"** — same as "hold is not the trade"
- **"Provider is the source of truth"** — always poll before acting
- **"Append-only, never mutate"** — audit trail for financial compliance
- **"Reconciliation runs always"** — not error handling, permanent safety net
- **"Strong consistency for money, eventual for everything else"**
- **"Sized for actual load — didn't over-engineer"**
- **"Correctness over performance"** — redundant validation at every step
