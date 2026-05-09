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

#### Context & Judgment Arc (0:00–3:00)

**Script:**

> "I'm going to walk you through a digital shopping platform I built from scratch. The context: pandemic hit, consumers couldn't visit dealerships, and we needed to enable online transactions — browsing, expressing purchase intent, and eventually putting down deposits. There was enormous business pressure, but no spec — nobody at the company had done this before.
>
> My first job wasn't writing code. It was translating ambiguity into priorities. I worked with product to break 'digital shopping' into concrete features. Lead capture was the critical business path — that's money flowing to dealers — so it went first with strong consistency guarantees. Inventory display could be eventually consistent because the data was already slightly stale from dealer feeds. Merchandising and pricing experiments were explicitly deferred — not because they weren't important, but because we didn't have enough signal on what would work.
>
> The key judgment: ship the minimum that proves the business model works, with enough architectural room to grow without rewriting."

**[Draw on Miro: Stage 1 — monolith with modules]**

#### Architecture Evolution (3:00–8:00)

**Script:**

> "I started simple. A few helper modules inside the monolith — lead capture, inventory display, dealer config. Single DB, single deploy, zero operational overhead. The team was small, we co-located, and it let us iterate daily.
>
> [Draw Stage 2] As the product grew and we understood the domain better, I extracted services one at a time. Lead capture came out first — it needed an independent SLA because that's revenue. It got its own DB with strong write consistency. Inventory sync moved to event-driven because it tolerates eventual consistency — the data is already stale from dealer feeds. I added feature flags at this point because I knew product would want to experiment.
>
> [Draw Stage 3] The mature state: independent services connected via event bus. Lead Service, Inventory Service, Merchandising Service — each with its own data store, independent deployment, clean boundaries. Notification and analytics services subscribe to events. Experiments can be safely retired without touching core services.
>
> Each extraction was triggered by real pain — deploy coupling, SLA requirements, or team ownership boundaries — not by theory."

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

### Part 3: Wrap-Up (16:00–18:00)

**Script:**

> "To summarize the key decisions and tradeoffs:
>
> - Started simple (monolith), extracted when complexity justified — never pre-optimized
> - Consistency matched to domain: strong for money flows, eventual for display data
> - Auth-then-capture for safe payment lifecycle — cancel is free before capture
> - Event-sourced audit trail for compliance and reconciliation
> - Feature flags from day one — experiments retired safely, zero incidents
>
> Results: launched on timeline, captured meaningful revenue during a business-critical period, architecture grew organically, and multiple experiments were safely retired using the playbook I created.
>
> Happy to go deeper on any part — payments, the event architecture, scaling concerns, or how I'd improve this with AI today."

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
