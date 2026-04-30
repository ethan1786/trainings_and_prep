# System Design Round (60 min, Excalidraw on CoderPad)

**Format:** Whiteboarding, infrastructure-focused, no AI allowed
**Tool:** Excalidraw (practice drawing in it beforehand)
**Topics mentioned:** Load balancers, inter-service communication, scaling

---

## What They're Evaluating

From the interview doc: "infrastructure and high-level system design... exploring details in depth, discussing tradeoffs, and defending your design decisions."

---

## Framework (use every time)

### 1. Requirements (5-7 min)
- Functional: what does the system do?
- Non-functional: scale (users, requests/sec), latency, availability, consistency
- Clarify: read-heavy vs write-heavy? Real-time vs batch? Global vs single region?

### 2. High-Level Design (10-15 min)
- Draw the end-to-end flow: client → load balancer → services → data stores
- Identify core services (2-4 max)
- Show data flow direction with arrows
- Label protocols (REST, gRPC, async/queue)

### 3. Deep Dive (20-25 min)
- Interviewer will pick 1-2 areas to go deep on
- Be ready to discuss: database schema, caching strategy, queue design, consistency model
- Draw sequence diagrams if helpful

### 4. Scaling & Tradeoffs (10 min)
- How does this handle 10x traffic?
- What breaks first? How do you fix it?
- What tradeoffs did you make and why?

---

## Cherry-Relevant System Design Topics

Since Cherry is BNPL for healthcare:

**Payment processing system:**
- Loan application → approval → disbursement → repayment
- Idempotency for payment operations
- Event-driven architecture for state changes
- Audit logging for compliance

**Healthcare provider portal:**
- Multi-tenant system (many clinics, one platform)
- Real-time payment status
- Notification system (email, SMS)

**General topics (always relevant):**
- API gateway + authentication (your Kong/Keycloak experience)
- Rate limiting (your Nginx/Lua experience)
- Event-driven architecture (your SQS/SNS/Kafka experience)
- Database scaling (read replicas, sharding, caching)

---

## Building Blocks (draw from memory)

| Component | When to use | Cherry context |
|---|---|---|
| Load balancer (ALB/NLB) | Multiple service instances | Frontend → API |
| API Gateway | Auth, rate limiting, routing | You built this at Toast and Applause |
| Message queue (SQS/Kafka) | Async processing, decoupling | Payment state transitions |
| Cache (Redis) | Read-heavy data, session state | Provider/plan lookup |
| SQL (PostgreSQL) | Transactional data, relationships | Loans, payments, users |
| NoSQL (DynamoDB) | High-write, simple access patterns | Audit logs, events |
| CDN | Static assets | Provider portal frontend |
| Pub/Sub (SNS) | Fan-out notifications | Payment status updates |

---

## Tradeoffs to Proactively Mention

- **Sync vs async:** "Payment creation is synchronous (user needs confirmation), but downstream processing (credit check, disbursement) is async via queue."
- **SQL vs NoSQL:** "Core financial data in PostgreSQL for ACID guarantees. Audit logs in DynamoDB for high-write throughput."
- **Consistency vs availability:** "For payments, we need strong consistency — a user should never see a stale balance. For provider search, eventual consistency is fine."
- **Monolith vs microservices:** "At Cherry's stage, I'd start with a modular monolith and extract services when the team grows or a clear scaling boundary emerges."

---

## Tips

- **Start simple.** Draw 3-4 boxes and arrows first. Don't open with "let me draw the Kafka cluster topology."
- **Label everything.** Protocol, data format, sync/async on every arrow.
- **Talk while drawing.** Silent drawing is a red flag. Narrate your decisions.
- **Ask "does this match what you had in mind?"** after the high-level design. Course-correct early.
- **Practice Excalidraw** for 10 minutes before the interview. Know how to draw boxes, arrows, and text quickly.
