# Domain Interview Prep — Digital Shopping System

> For Coinbase VO Round 3 (Domain Interview). You present a system YOU designed on a whiteboard.
> Goal: Walk through architecture, key decisions, tradeoffs, and results in ~10 min, then handle 20 min of Q&A.

---

## Questions to Answer (fill in to build the whiteboard diagram)

### 1. High-Level Architecture
- What were the main services/components? (list all of them)
- How did they connect — REST, Kafka, shared DB?
- What was the monolith vs. new services boundary? (what stayed in monolith, what got extracted?)
- Was there an API gateway or BFF in front?

### 2. Data Flow — End to End
- How did dealer inventory data get into the system? (batch feeds? real-time? what format?)
- How did a consumer's action (browse, express interest, submit lead) flow through the services?
- How did lead data get to the dealer? (email? dashboard? CRM integration?)
- Where did merchandising/pricing data come from?

### 3. Kafka / Event-Driven Details
- What Kafka topics existed? (name them if you remember)
- What events flowed through them? (e.g., InventoryUpdated, LeadCaptured, etc.)
- Who produced and who consumed each topic?
- What delivery guarantees did you use? (at-least-once? exactly-once? per topic?)
- Did you use consumer groups? Partitioning strategy?

### 4. Data Stores
- What databases did each service use? (Postgres? DynamoDB? Redis?)
- What was the source of truth for inventory? For leads? For merchandising?
- Any caching layer? What was cached and with what TTL?
- Any shared databases between services, or fully isolated?

### 5. Monolith → Microservice Extraction
- What were the "helpers in the monolith" you started with?
- What triggered the decision to extract each service?
- How did you handle the migration? (strangler fig? dual-write? flag-based routing?)
- What was the order of extraction? (what came out first, last?)

### 6. Consistency & Reliability
- Where did you choose eventual consistency? Why was it safe there?
- Where did you require strong consistency? How did you enforce it?
- What happens if Kafka is down? (backpressure? fallback? DLQ?)
- What failure modes did you design for?
- Did you have circuit breakers, retries, or DLQs?

### 7. Feature Flags & Experiments
- How were feature flags implemented? (which tool? config service? LaunchDarkly?)
- How did you isolate experimental code paths from the core?
- What did the experiment retirement process look like technically? (not the playbook — the actual system behavior)

### 8. Scale & Performance
- What was the traffic volume? (requests/sec, events/sec)
- What were the latency requirements?
- Any hot spots or bottlenecks you discovered?
- How did you monitor the system? (metrics, dashboards, alerting)

### 9. Team & Collaboration (for follow-up questions)
- How many engineers worked on this?
- How did you split ownership across sub-teams?
- How did you align with product on what to build first?
- How did you define API contracts with frontend?

### 10. The AI Question — "How would you build this differently with AI tools?"
- Think about: AI for inventory data quality (detect stale/wrong listings)
- Think about: AI for lead scoring (which leads are high-intent?)
- Think about: AI for merchandising (personalized pricing/display)
- Think about: AI for testing (auto-generated integration tests across services)
- Think about: AI for monitoring (anomaly detection on lead volume, inventory freshness)

---

## Whiteboard Structure (suggested layout for the interview)

```
[Draw this on CodeSignal whiteboard — practice beforehand]

┌─────────────────────────────────────────────────────┐
│                   Consumer Layer                       │
│   (Web/Mobile frontend → BFF or API Gateway)          │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────────┐
        ▼              ▼                  ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│ Lead Capture │ │Merchandising│ │ Inventory Sync  │
│   Service    │ │   Service   │ │    Service      │
└──────┬──────┘ └──────┬──────┘ └────────┬────────┘
       │               │                  │
       ▼               ▼                  ▼
┌──────────────────────────────────────────────────────┐
│              Kafka Event Bus                           │
│  (topics: leads.captured, inventory.updated, etc.)    │
└──────────────────────────────────────────────────────┘
       │               │                  │
       ▼               ▼                  ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│  Lead DB     │ │  Config /   │ │  Inventory DB   │
│  (strong     │ │  Feature    │ │  (eventual      │
│  consistency)│ │  Flags      │ │  consistency)   │
└─────────────┘ └─────────────┘ └─────────────────┘
                                          ▲
                                          │
                                 ┌─────────────────┐
                                 │  Dealer Feeds    │
                                 │  (batch/periodic)│
                                 └─────────────────┘
```

---

## Presentation Plan (1-hour Domain Interview)

**Format:** ~18 min presentation + ~40 min Q&A from interviewer

---

### Part 1: System Overview (0:00–8:00)

#### Opening Hook + Context (0:00–3:00)

**Script:**

> "I designed and shipped a digital transaction platform that processes deposits on vehicles — real money, strong consistency, payment state machine with auth-then-capture. This is the project that got me promoted to Principal — I'll show you why.
>
> **My role:** I was the sole backend architect and primary implementer. I worked with product on requirements, defined all API contracts with frontend, made all the architecture decisions, and wrote the majority of the backend code. Started with 2 backend engineers — myself and one other. I was the architectural constant from day one through every evolution, even as the team grew and went through re-orgs.
>
> **Context:** Pandemic hit, consumers couldn't visit dealerships, we needed to enable online transactions. Enormous business pressure, but no spec — nobody at the company had done this before.
>
> **My approach:** My first job wasn't writing code. It was working with product and management to drive the design through ambiguity — translate a vague vision into concrete priorities. I had a head start: at Toast I'd designed a similar order management system, so the foundational patterns — configurational vs transactional data separation, state machine design for order lifecycles, DB structure — translated directly.
>
> **Key early decisions:** Lead processing is eventually consistent (acceptable latency). Transaction state transitions are strongly consistent (money — no stale state). Payments deferred to phase 2 — ship lead capture first to prove the business model. Everything started inside the monolith — no premature extraction. This let us ship 3 weeks earlier and start generating revenue while competitors were still building their microservice architectures.
>
> **The technical complexity isn't in the scale** — it's in the correctness requirements. When money is involved, you can't have stale state, you can't lose a transaction, and you can't double-charge. The patterns — state machine, idempotency, reconciliation, event sourcing — matter more than the throughput numbers."

**[Draw on Miro: Stage 1 — monolith with modules]**

#### Architecture Evolution (3:00–8:00)

**Script:**

> "I started simple. A few service and repository classes inside the monolith — transaction CRUD, a lead processing path for digital transactions, dealer and customer configuration management. Single DB, single deploy, zero operational overhead. The team was small, we co-located, and it let us iterate daily.
>
> [Draw Stage 2] As the product grew, the core app remained the transaction CRUD engine with dealer and customer config management — that's the strongly consistent path. What I extracted to event-driven was the lead processing: after a transaction commits, an event is published. A downstream consumer picks it up, saves a lead record, then notifies the dealer — either via email or an external API call. This decoupling was deliberate: the transaction commit is the critical path (strong consistency, must not fail), but lead notification is eventually consistent (dealer gets notified within seconds, not in the same DB transaction). I added feature flags at this point because I knew product would want to experiment.
>
> [Draw Stage 3] The mature state: the core app evolved into a transaction state machine AND orchestrator. It manages the transaction lifecycle and coordinates downstream services via sync HTTP calls: a fee/tax service (calls 3rd party for dealer fees and regional taxes), a trade-in service (3rd party estimate), a loan service (3rd party rate estimate), and a payment service for deposits.
>
> The payment service is interesting because it has a dual communication pattern: the core app calls it synchronously to create and update payments, but the payment provider sends webhook events back asynchronously. The payment service listens to those webhooks, then publishes events to the event bus — which the core app consumes to update the transaction state and notify the customer of payment status changes. So it's sync outbound, async inbound.
>
> The lead processor and notification service remain as async consumers from the event bus — same as Stage 2 but now with richer events flowing from the expanded system.
>
> Each service extraction was triggered by real need — different ownership, different deployment cadence, or different reliability requirements — not by theory."

**[Three-panel evolution diagram on Miro]**

---

### Part 2: Payment/Reservation Deep Dive (8:00–16:00)

**Transition script:**

> "Now I want to zoom into the most technically interesting subsystem — the payment and reservation flow. This is where consistency, audit trails, and failure handling matter most, and I think it connects directly to your domain at Coinbase."

#### Payment Architecture (8:00–11:00)

**Script:**

> "When we added deposits — consumers putting real money down on a vehicle — I needed to design a payment flow that was safe, auditable, and resilient to failures. The key decision was auth-then-capture: we authorize the card immediately to hold funds, but don't actually charge until the dealer confirms the deal. This means cancellation before confirmation is free — no refund needed, just release the hold.
>
> [Draw on Miro: Client → Transaction Service → Payment Provider, showing auth-then-capture split]
>
> The async piece: the payment provider confirms out-of-band via webhook. I don't block the user on settlement — they get a 'reservation confirmed' immediately after auth succeeds. The capture happens later when the dealer takes action."

#### State Machine & Audit Trail (11:00–14:00)

**Script:**

> "The reservation lifecycle is a formal state machine: STARTED → CONFIRMED → CAPTURED → PAID OUT. With branches for CANCELLED (from STARTED or CONFIRMED) and REFUNDED (from CAPTURED).
>
> [Draw state machine on Miro]
>
> For auditability — because this is real money — I event-sourced the state transitions. Each state change is an Action record in a linked list: it stores the payment intent ID, the transition type, and a pointer to the previous action. This gives a full audit trail: I can reconstruct exactly what happened to any reservation, in what order, and reconcile against the payment provider's records.
>
> The linked-list design means I never mutate state — I only append. That's critical for dispute resolution and compliance."

#### Failure Handling & Durability (14:00–16:00)

**Script:**

> "Because this is real money, durability and availability were primary design constraints — not addons.
>
> For durability: every state transition is written to a WAL-backed Postgres with synchronous replication to a standby before we acknowledge to the user. No in-memory-only or cache-only storage for payment state. The event-sourced action log means I never mutate — only append. If anything goes wrong, I can replay the entire history of a reservation and reconcile against the payment provider's records. Zero data loss even on node crash.
>
> For availability: the payment flow has no single point of failure. The transaction service runs multi-AZ. If the primary DB fails, automatic failover to the sync standby — same data, no loss. The reconciliation worker is the safety net: even if a webhook is lost or the service is briefly unavailable, the worker catches up by polling the provider for any stuck reservations.
>
> Three failure patterns I designed for:
>
> First, synchronous failures: payment provider returns an error during auth. The transaction service rolls back the reservation to STARTED state and returns the error to the user. Compensating transaction — no partial state left behind.
>
> Second, async failures: webhook never arrives (provider timeout). I have a reconciliation job that polls the payment provider for any reservations stuck in CONFIRMED for longer than a threshold. If the provider says it failed, I cancel. If it succeeded, I advance the state.
>
> Third, idempotency: webhooks can arrive multiple times. Each action is idempotent — if I receive a 'confirmed' webhook but the reservation is already CONFIRMED or beyond, I no-op. The action linked list makes this check trivial."

#### Tips: Durability & Availability Talking Points (say these out loud)

When presenting or answering Q&A, drop these naturally:

- **"WAL before acknowledge"** — "We write to the WAL before confirming to the client. Even if the node crashes mid-write, we replay the log on restart. Zero data loss."
- **"Sync replication"** — "The standby confirms it received the write before the primary acknowledges to the client. If the primary dies, the standby has everything."
- **"Append-only / never mutate"** — "For financial data, I never update in place. Every state change is a new record. This gives me a full audit trail and makes reconciliation trivial."
- **"Reconciliation as safety net"** — "Even with all these guarantees, I run a nightly reconciliation comparing our internal ledger against the payment provider's settlement file. Belt and suspenders."
- **"No single point of failure"** — "Every component in the payment path has a fallback: multi-AZ DB, reconciliation worker as webhook backup, idempotent operations for safe retries."
- **"Graceful degradation outside the money path"** — "For non-payment features (inventory display, notifications), I accept eventual consistency and cache staleness. But for anything touching money: strong consistency, sync replication, no shortcuts."

**Connection to Coinbase:** "This is the same principle you use for trading — you can't lose a trade, you can't double-execute an order, and you need to reconcile against the blockchain. The durability and consistency requirements are identical."

---

### Part 3: Wrap-Up + Coinbase Bridge (16:00–18:00)

**Script:**

> "To summarize the key decisions and tradeoffs:
>
> - Started simple (monolith), extracted when complexity justified — never pre-optimized
> - Consistency matched to domain: strong for money flows, eventual for display/lead data
> - Auth-then-capture for safe payment lifecycle — cancel is free before capture
> - Event-sourced audit trail for compliance and reconciliation
> - Feature flags from day one — experiments retired safely, zero incidents
> - Sized correctly for actual load — no over-engineering (10:1 read-write, in-memory cache, single DB handles writes fine)
>
> Results: launched on timeline, captured meaningful revenue during a business-critical period, architecture grew organically. This project got me promoted to Principal.
>
> **Connection to your domain:** This maps directly to Coinbase. Auth-then-capture is like placing a limit order — intent committed but not settled. The payment state machine mirrors your order states (PENDING → OPEN → FILLED). Event-sourced audit trail is essential for any regulated financial system. The webhook reconciliation pattern applies to any external settlement — whether it's a payment provider or the blockchain. And the correctness requirements are identical: can't lose a transaction, can't double-charge, can't have stale state when money is involved.
>
> Happy to go deeper on any part — payments, orchestration patterns, scaling concerns, or how I'd improve this with AI today."

---

### Part 4: Q&A (~40 minutes)

This is where you prove depth. The interviewer will dig into specifics.

---

## Likely Follow-Up Questions (prepare answers)

**Architecture & Tradeoffs:**
- "Why Kafka instead of [SQS / direct HTTP / etc.]?"
- "What would break first at 10x scale?"
- "How do you handle out-of-order events?"
- "Why event sourcing for the actions? Why not just update in place?"
- "How do you handle schema evolution on the event bus?"

**Payments & Reliability:**
- "What if a lead is captured but the downstream dealer notification fails?"
- "What if the webhook never arrives?"
- "How do you reconcile with the payment provider?"
- "What if two webhooks arrive at the same time for the same reservation?"
- "How do you handle partial failures in a multi-step checkout?"

**Testing & Operations:**
- "How do you test this end-to-end?"
- "How did you validate payments in staging without real money?"
- "What monitoring/alerting did you have?"
- "How did you handle deployments with active reservations in flight?"

**Evolution & AI:**
- "What would you do differently if you rebuilt it today?"
- "How would you use AI tools to build or improve this?" ← EXPECT THIS ONE
- "What was the hardest part to get right?"
- "What's the next thing you'd extract or rebuild?"

---

## Talking Points (keep in back pocket)

### Technical Judgment Under Ambiguity

> "Nobody had built digital shopping before at my company. Product had a vision, not a spec. My first job wasn't writing code — it was translating ambiguity into scope. Lead capture went first because it's the revenue path. Inventory was deferred to eventual consistency because the data is already stale from dealer feeds. Merchandising was explicitly scoped out — not because it wasn't important, but because we didn't have signal yet."

**Why this works for Staff+:** You're showing *judgment*, not architecture. The architecture is evidence.

### Why Auth-Then-Capture

> "We authorize immediately to hold funds, but don't charge until the dealer confirms. Cancellation before capture is free — just release the hold, no refund. This reduces friction for consumers and eliminates refund disputes for dealers. It's the same pattern used in hotel bookings and ride-sharing holds."

### Why Event-Sourced Actions

> "For anything involving money, I need a full audit trail. I never mutate state — I append an action record. This gives me: (1) complete history for dispute resolution, (2) ability to reconcile with the payment provider by replaying actions, (3) idempotent webhook processing — if I've already seen a transition, I no-op."

### Connection to Coinbase

> "This maps directly to your domain. Auth-then-capture is like placing a limit order — you've committed intent but the trade hasn't settled. The state machine (STARTED → CONFIRMED → CAPTURED) is like your order states (PENDING → OPEN → FILLED). Event-sourced audit trail is essential for any regulated financial system. And the webhook reconciliation pattern applies to any external settlement system."

---

## Numbers to Mention (quantify during presentation)

| Metric | Value | Implication |
|---|---|---|
| Config/consumer reads | 10-15K rpm | Read-heavy, cached in-memory |
| Transaction reads | ~2K rpm | Moderate, strong consistency |
| Transaction creates | 100-200/min | Low write volume — single DB is fine |
| Read:write ratio | ~10:1 | Cache-first architecture, invalidate via Kafka |
| Caching strategy | In-memory, Kafka-driven invalidation | No TTL staleness — events keep cache consistent |

**How to drop these naturally:**

> "Traffic-wise, we're looking at about 10-15K rpm for config and consumer data reads — heavily cached in-memory. Transaction creation is much lower, about 100-200 per minute. So it's a 10:1 read-write ratio. The single DB handles writes fine; the read path is served almost entirely from in-memory cache kept consistent via Kafka events. We didn't need sharding or read replicas — the cache does the heavy lifting."

**Why this matters for the interview:** Shows you sized the system correctly — you DIDN'T over-engineer (no sharding, no Redis, no read replicas needed) because you understood the actual load. That's judgment.

---

## "What Was the Hardest Part?" (prepare this — it'll be asked)

> "Honestly, the technical architecture wasn't the hard part — the load is moderate and the patterns are well-known. The hard part was driving alignment across product, frontend, data engineering, and dealers when nobody had done this before and requirements were shifting weekly. The system I designed needed to be flexible enough to absorb those changes without rework — that's why I invested in configurable flows, feature flags, and a non-linear transaction model where steps are optional and order-independent. The architecture's job was to absorb organizational uncertainty, not just handle traffic."

**Why this answer works for Staff+:** You're not pretending 200 writes/min is a scaling challenge. You're naming the REAL difficulty — organizational alignment under ambiguity — which is where Staff+ engineers actually spend their time. The technical decisions (configurable flows, feature flags, flexible state model) are the evidence that you solved the real problem.

---

## Deep-Dive Expansion — Questions to Answer (fill in offline)

These expand the presentation from ~18 min to ~25 min and prepare for 35+ min of Q&A depth. Answer each in 2-4 sentences — enough to speak fluently when asked.

---

### A. Payment Service — Failure Handling & Edge Cases

1. **Partial failure: auth succeeds but DB write fails.** What happens? Does the customer get charged without a record? How do you recover?
the 3rd service is always treated as the source of truth. Normally db txn is only committed on a 200 API response. If the db txn fails, it can be corrected by two methods: 1. on a successful auth, there is a webhook event listened by the system to validate or correct the db records. 2. Before making any payment updates, I always query the 3rd service for the latest status, and only process when the state matches. If db is behind, it is allowed to update programmatically, otherwise it will prompt support to review and manually override.

2. **Webhook idempotency:** Same webhook arrives twice (provider retries). How does the payment service handle it? What's the dedup mechanism?
Webhook events have ideompotency key and the key is saved in db after processed.

3. **Webhook ordering:** What if "captured" webhook arrives before "confirmed"? Does order matter? How do you handle out-of-order?
There are different out-of-order tolenrance setup in the state machine. Some out of order events are allowed, some are not. When an out of order event occors, it will prompt to support to review.

4. **Webhook never arrives (provider timeout).** How long do you wait? What's the reconciliation strategy? Polling? Alert threshold?
We don't wait for failed webhooks, as we actively poll in the next action, and in a reconsiliation job that runs daily to batch validate active payments.

5. **Hold expiration:** Auth hold typically expires in 7 days. What if the dealer doesn't confirm in time? Who handles the expiry — your system or the provider?
If the dealer does not handle it, it will expire in the 3rd service, and core app will update the record on the expired webhook event. However we still provide a re-auth-and-capture function if the deal is made after the payment is expired.

6. **Refund after capture:** Dealer cancels after money moved. What's the refund flow? State machine transition? Who initiates?
There is a separate refund flow, that is not directly allowed and needs support to review. It is because we lose the processing fee on each refund, so it does not come for free.

7. **Duplicate payment attempts:** Customer clicks "pay" twice. How do you prevent double-charging? Idempotency key design?
There is idempotency key for each payment, simply using the customer id and vehicle id, because there is only one payment allowed per customer for each vehicle. The key is posted in Redis as a dedup key when request is received, and checked before making auth service calls to prevent concurrent payments.

---

### B. Orchestration Patterns — Core App as Orchestrator

8. **Call ordering and parallelism:** Which downstream calls are independent (can run in parallel) and which have dependencies (must be sequential)? Draw the dependency graph.
The downstream calls are sequential because they have real data dependencies — trade-in value affects fee/tax calculation, and fee/tax totals affect the final deposit amount. There's nothing that can run in parallel here. Each step is triggered by a customer action, and the next step depends on the previous one's output.

9. **Timeout and circuit breaker strategy:** Fee/Tax service is slow — what happens? Do you block the whole transaction or return partial data? What are the per-service timeouts?
Static fee-tax data are cached by dealer, and calculations are done in memory for specific vehicle and trade in. If there is a cache miss and the service is slow, it will return partial data with errors, to notify the customer missing data, and is polled/fixed before the final deposit.

10. **Graceful degradation:** If loan service is down, does the transaction fail? Or can the customer proceed without a loan estimate and add it later?
If loan service is done, we also return the error to customer but allow customer to proceed without an estimate. Customer can see the fix this error any time afterwards before the deposit.

11. **Configurable transaction flows:** Not all dealers offer trade-in or loan. How do you handle configurable flows — skip services that don't apply? Is this config-driven or code-driven?
If trade-in or loan is not configured, it will skip the flow in UI, and the actual code path should not be triggered (with config validation before each txn).

12. **Adding a new service:** Product wants to add an insurance quote service. How do you add it without changing the core app's state machine? Is the orchestrator extensible?
I will add it in backend flow as an optional state first, have all the integration plugged in and tested. Then gradually release in UI by a feature flag.

13. **Why orchestration over choreography?** Each service called by the core app doesn't know about the others. Why not have each service publish events and let the next one react?
Orchestration gives us full visibility into the transaction flow — I can trace exactly where a transaction is, what failed, and what to retry. With choreography, debugging becomes "which event got lost between which services?" — much harder. The data dependencies between steps also make choreography awkward: trade-in → fee/tax → deposit is a natural pipeline, not independent reactions. At our scale, the operational complexity of choreography isn't justified.

---

### C. Transaction State Machine — States & Transitions

14. **What are all the states?** List them (e.g., CREATED, FINANCE_PENDING, READY, RESERVED, CONFIRMED, COMPLETED, CANCELLED...). Which are terminal?
The payment has its own state machine: CREATED, CONFIRMED, CAPTURED, CANCELLED, DECLINED, PAID_OUT. But the transaction itself isn't a rigid state machine — it's a data processing flow. Steps are optional and can be done in any order. The only terminal states are "deposit placed" or "appointment made." If anything changes mid-flow (e.g., trade-in added after initially skipped), it triggers cascading recalculation through dependent processors in order: trade-in → fee/tax → loan. This is more flexible than a strict state machine — the customer can go back and change things, and the system recomputes downstream automatically.

15. **What triggers each transition?** User action? System event? Timer? Dealer action?
Mostly customer of dealer trigger the action, and some states can be triggered by webhooks

16. **Invalid transitions:** What happens if a "capture" event arrives for a transaction in CREATED state? How do you guard against invalid state transitions?
There are critical events and non critical ones. If critical ones arrives out of order, we usually needs to bring support to review.

17. **Concurrent state mutations:** Two requests try to update the same transaction simultaneously (e.g., customer cancels while dealer confirms). How do you handle the race?
We don't need complex distributed locking because the 3rd party payment service is the source of truth. Whoever gets a 200 from the provider first wins — that's the committed state, and we update our DB to match. If customer cancels and dealer captures simultaneously, the provider will only accept one (you can't capture a cancelled payment). Our poll-before-action pattern also helps: before any state-changing call, we query the provider for the latest status, so we never act on stale local state. The daily reconciliation job catches any edge cases that slip through.

18. **State machine persistence:** Is the state machine in application code only, or is it enforced at the DB level too (e.g., CHECK constraints, triggers)?
It is application code for simplicity, and is checked before update in db.

---

### D. Staff+ Design Judgment — Why You Made These Choices

19. **Why orchestration over choreography?** What would choreography look like here? What breaks?
Same as #13. With choreography, each service publishes events and the next one reacts — trade-in publishes "estimate ready," fee/tax consumes it and recalculates, then publishes "fees ready," loan consumes that. The problems: (1) debugging is a nightmare — "where did the transaction stall?" requires correlating events across 4 services. (2) The data dependency chain (trade-in → fee/tax → loan → deposit) is a natural pipeline, not independent reactions. (3) Error handling becomes "who compensates?" instead of one orchestrator knowing the full picture. Orchestration trades some coupling for visibility and control — at our scale, that's the right call.

20. **Why monolith-first then extract?** What if you'd started with microservices from day one? What would have gone wrong?
Simply not needed. This was a new product with no traffic — microservices would have added operational overhead for zero benefit. Adding to the existing monolith was the lowest-cost way to ship and validate the business model. We also didn't know the domain boundaries yet — product requirements were ambiguous, features might get cut. Once the product proved itself and we understood the real fault lines, we extracted where it made sense. Starting with microservices would have meant guessing boundaries wrong, paying cross-service refactoring costs, and moving slower when speed mattered most.

21. **How did you decide what to extract vs. keep in the monolith?** What's your extraction criteria?
Extraction isn't needed until traffic or complexity forces it. When the time comes, the real criteria are operational: (1) CI/CD pipeline is ready to support another service, (2) team has bandwidth for the extra operational cost, (3) product and management agree on the investment. On the technical side, it's straightforward — different deployment cadence, different ownership, or different reliability requirements. But the organizational readiness gates matter more than the technical justification. You can always justify extraction technically; the question is whether you can afford it operationally.

22. **How do you handle the config vs. transactional data split in the DB?** Same schema? Same DB? Different tables? Read replicas for config?
Same DB, different tables. Config data (dealer settings, product eligibility, fee schedules) is read-heavy, changes rarely, and is cached aggressively in-memory with long TTL. Transactional data (transactions, payments, leads) is write-heavy, strongly consistent, no caching for active records. The split is logical (table separation + different access patterns) not physical (separate DB) — at our scale, one DB handles both fine. If config reads ever became a bottleneck, I'd add a read replica or promote the cache to the primary read path.

23. **What would you redesign today?** With everything you know now, what's the one thing you'd architect differently? Why?
I'd keep most of the system the same — it's been proven to work well with customers and the market. The core architecture (orchestrator + state machine + event-driven lead processing) is sound. What I'd add from the beginning: (1) more integrations upfront — customer management system (CRM) as a first-class integration rather than bolted on later, (2) GraphQL as the data serving layer from day one — we added it later and had to migrate consumers, would have been cheaper to start there, (3) AI-powered features (fraud detection, conversational shopping agent) baked into the architecture rather than retrofitted. The system design was right; what I'd change is scope of integration — I was too conservative about external touchpoints early on.

24. **How would you use AI to improve this system?** Think: anomaly detection on payment failures, AI-powered fraud scoring on transactions, LLM-based test generation for state machine edge cases, AI for dealer config validation.
Three areas: (1) AI-powered fraud detection and personal verification — flag suspicious payment patterns (unusual deposit amounts, rapid create-cancel cycles, mismatched identity signals) before they reach the payment provider. Use ML models trained on historical fraud data to score transactions in real-time. (2) Integrate conversational AI shopping agents with the digital transaction flow — instead of a multi-step form UI, the customer interacts with an AI agent that guides them through configuration (trade-in, financing, add-ons) conversationally. One smart unified entrance that understands context, answers questions, and drives toward deposit. The backend MCP APIs I built (Story 3/15) are exactly the foundation for this. (3) Anomaly detection on operational metrics — if payment auth rates drop, webhook latency spikes, or transaction funnel conversion changes unexpectedly, AI alerts before customers or product notice.

---

### E. Operational Excellence — Day 2

25. **What metrics/dashboards do you monitor?** Transaction success rate? Payment auth success rate? State machine stuck-in-state alerts? Lead delivery latency?
Two levels. Product/BI dashboards track transaction funnel conversion and drop-off — that's how product measures whether the feature is working for customers. Engineering dashboards are what I own: (1) 200/500 rates per endpoint, (2) RPM and response time (p50/p99), (3) cache miss rate, (4) DB connection pool, memory, CPU, (5) payment auth errors broken down by error code and provider, (6) webhook delivery errors and processing lag, (7) reconciliation job mismatches per run. I care about both — if the product funnel drops, it's often an engineering issue (slow response, payment failure spike) that shows up in my dashboards first.

26. **What's your on-call playbook?** If payment auth rate drops at 3 AM, what do you check first? What levers can you pull?
First check: is it one dealer or all dealers? If one dealer, likely their account config or a card issue — notify them, not our emergency. If all dealers: check the payment provider's status page — is it their outage? If provider is healthy: check our recent deploys (rollback if recent), check connection pool / timeout metrics, check if we're sending malformed requests (bad API version, expired credentials). Emergency lever: disable payments via feature flag until morning. Customers can still browse and configure their transaction — they just can't submit the deposit until we restore. We don't have a backup payment provider, and we can't queue payments for later retry — payment data is PII and holding it in a queue violates compliance. So the only safe option is disable and investigate in the morning.

27. **How do you deploy without affecting in-flight transactions?** Blue-green? Feature flags? State machine versioning?
Canary deploys — new version goes to a small percentage of traffic first, we watch metrics, then roll out fully. For in-flight transactions: Spring Boot handles graceful shutdown — it finishes processing any active requests/transactions before killing the application and booting the new version. So no transaction is ever interrupted mid-processing. For risky changes (e.g., new payment flow), we also wrap them in a feature flag so new transactions use the new path while existing ones continue on the old path until they reach a terminal state.

28. **How do you test the full flow end-to-end?** Staging with real payment provider (test mode)? Mock services? Contract tests?
Staging environment connects to the real payment provider in test mode (test card numbers, real API calls, real webhooks) with a production database copy. This gives us the closest-to-real environment possible — real data shapes, real provider behavior, real webhook timing. We test the full customer journey: transaction creation → fee/tax → trade-in → loan → deposit auth → webhook confirm → state transitions. No mocking the payment provider — it's too critical to fake.
