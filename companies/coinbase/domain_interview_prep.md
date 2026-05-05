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

## Presentation Flow (10 min walkthrough)

1. **Context** (1 min): Pandemic, automotive went online, 0→1 product, business pressure
2. **High-level architecture** (2 min): Draw the main components, show data flows
3. **Key decision: monolith→microservices extraction** (2 min): Started simple, extracted as complexity justified. Show the evolution.
4. **Key decision: consistency tradeoffs** (2 min): Eventual for inventory (already stale from feeds), strong for leads (money). Explain WHY.
5. **Key decision: feature flags + experiment isolation** (2 min): How you designed for iteration from day one
6. **Results** (1 min): Launched on timeline, meaningful leads, architecture enabled safe experimentation

---

## Likely Follow-Up Questions (prepare answers)

- "Why Kafka instead of [SQS / direct HTTP / etc.]?"
- "What would break first at 10x scale?"
- "How do you handle out-of-order events?"
- "What if a lead is captured but the downstream dealer notification fails?"
- "How do you test this end-to-end?"
- "What would you do differently if you rebuilt it today?"
- "How would you use AI tools to build or improve this?" ← EXPECT THIS ONE
