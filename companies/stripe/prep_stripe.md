# Stripe — Staff Engineer, Workflow Engine (Service Platform)

> **Full prep doc.** Read before recruiter screen, hiring manager call, and on-site.
> Last updated: March 2026

---

## 1. Company Overview

**What they do:** Financial infrastructure / payments platform for the internet. APIs for accepting payments, managing subscriptions, handling payouts, fraud detection, and financial operations. Powers millions of businesses from startups to Fortune 500.

**Mission:** "Increase the GDP of the internet."

**Scale:** ~$1T+ in annual payment volume. Thousands of engineers. Billions of API calls daily.

**Recent news worth mentioning:**
- Continued push beyond payments into financial services (Treasury, Issuing, Revenue Recognition, Tax)
- Stripe's valuation recovery and potential IPO timeline
- Heavy investment in developer experience and API quality
- Growing enterprise adoption and international expansion

---

## 2. Engineering Culture & Values

- **Engineering-driven:** Engineers have significant product influence. Technical quality is a competitive advantage.
- **Strong writing culture:** Design docs, RFCs, and written proposals are the norm. Decisions are made through written artifacts, not hallway conversations.
- **Rigor over speed:** Values craftsmanship and long-term thinking. "We'd rather get it right than get it fast."
- **Languages:** Ruby (legacy) + Java + Go. Moving toward more service-oriented architecture.
- **Operational excellence:** Deep investment in observability, reliability, and incident response for financial-grade systems.

**What this means for your interview:**
- Write clearly and structure your answers. They value articulation.
- Show you think about long-term maintenance, not just shipping.
- Demonstrate that you care about correctness before performance.

---

## 3. Team Context — Service Platform / Workflow Engine

- Builds the **orchestration and workflow infrastructure** that other Stripe teams consume
- Critical path for payment flows, subscription lifecycle, disbursements
- Reliability and correctness are paramount — these workflows move real money
- Think of it as building the "Temporal/Cadence" equivalent inside Stripe, purpose-built for financial transactions

**Likely technical challenges:**
- Workflow state machine persistence and recovery after failures
- Exactly-once execution guarantees in distributed workflow steps
- Backward-compatible workflow definition evolution (adding steps to live workflows)
- Multi-region workflow execution with consistent state
- Observability into workflow execution (tracing, debugging stuck workflows)

---

## 4. Why You're a Strong Fit

| Their Need | Your Evidence |
|---|---|
| Orchestration architecture | Built orchestration service consolidating 12→5 downstream integrations |
| Workflow reliability | Parity-testing framework for zero-regression migration of highest-traffic API |
| Cross-org platform adoption | Architecture standards adopted across 10+ teams, 3 departments |
| API design at scale | GraphQL federation gateway, API design standards via RFCs |
| Writing and communication | Authored design docs, RFCs, decision records driving org-wide consensus |
| 0→1 platform building | MCP server (from scratch under ambiguity), GenAI decision engine |
| Financial system thinking | Event-driven transactional pipelines for commerce workflows |

---

## 5. Interview Mindset — Financial Category

**Core philosophy to project:** *"Correctness above all. We'd rather be slow and correct than fast and wrong."*

**System design framing (say this early):**
> "Before I start, the key invariant here is that money is never lost or double-counted. I'll design for correctness first, then optimize for latency."

**Key concepts to weave into every answer:**
- **Idempotency** — every operation must be safe to retry. Idempotency keys, deduplication at every layer.
- **Strong consistency** — lean CP in CAP for money movement. Eventual consistency only where explicitly safe.
- **Reconciliation** — "How do you know the system is correct?" Async reconciliation jobs, double-entry ledger, audit trails.
- **Failure enumeration** — don't just describe the happy path. Enumerate what happens when each component fails.
- **Schema evolution** — Protobuf/Avro with schema registry for event contracts between services.

**System design topics likely asked:**
- Payment processing pipeline (idempotency, PSP integration, reconciliation)
- Workflow engine / distributed state machine
- Distributed transactions (Saga pattern, compensating transactions)
- Rate limiter for API gateway
- Event-driven architecture for financial operations

---

## 6. STAR Stories to Prepare (Ranked by Relevance)

| Priority | # | Story | Why It Fits |
|---|---|---|---|
| **Must tell** | 1 | API Modernization — Cross-Org Migration | Orchestration, cross-team leadership, safe migration |
| **Must tell** | 3 | Parity Testing Framework | Correctness verification — directly relevant to financial systems |
| **Must tell** | 5 | MCP Server — 0→1 Under Ambiguity | Platform building, independence, technical judgment |
| **Strong** | 4 | Architectural Standards Adoption | Writing culture, RFC process, earning trust |
| **Strong** | 9 | Digital Shopping — 0→1 Under Pressure | Event-driven commerce, fast delivery under constraints |
| **Strong** | 10 | Safe Experiment Retirement | Safe feature lifecycle — relevant to workflow deprecation |
| **Strong** | 12 | Driving Consensus via RFCs | Writing culture fit, cross-org alignment |
| **Good** | 7 | DGS Subgraph — Federation Migration | Schema federation, API consolidation |
| **Good** | 14 | Applause — Event Sourcing / CQRS | Distributed systems patterns |
| **Good** | 17 | GenAI Engine — Hybrid Architecture | 0→1 independent thinking, novel system design |
| **Wildcard** | 19 | Disagree and Commit | Behavioral signal for healthy conflict |
| **Wildcard** | 20 | Failure & Learning | Self-awareness, growth mindset |

**Story selection strategy per round:**
- **Behavioral (leadership):** Stories 1, 12, 19
- **Behavioral (technical depth):** Stories 3, 5, 14
- **Behavioral (mentoring/people):** Stories 11, 6
- **System design follow-up ("tell me about a time..."):** Stories 1, 10

---

## 7. Questions to Ask Interviewers

### Recruiter Screen
- What does the interview process look like, and what's the expected timeline?
- How does the Service Platform team interact with product teams that consume the workflow engine?
- What's the team size and composition for the Workflow Engine group specifically?
- Is this a backfill or a new headcount? What's driving the hire?

### Hiring Manager
- What are the biggest reliability or scalability challenges the workflow engine faces today?
- How does the workflow engine handle failure modes — retries, dead letters, human intervention?
- What's the migration story for teams currently on older orchestration patterns?
- How much of the workflow engine is Stripe-proprietary vs. built on open-source foundations (e.g., Temporal)?
- How much autonomy does this role have in setting technical direction vs. executing a defined roadmap?
- How do you measure success for this role in the first 6-12 months?

### Team Match / Technical
- What does a typical workflow definition look like — code-based, config-based, DSL?
- How does the team think about backward compatibility when evolving the workflow API?
- What's the deployment cadence? How do you handle rollouts for infrastructure that sits in the critical payment path?
- What's a recent project you're proud of, and what made it successful?
- How does the team handle disagreements on technical direction?

---

## 8. "Why Stripe?" Answer

> "Two reasons. First, the problem space — building reliable orchestration infrastructure for financial transactions is exactly the kind of high-leverage platform work I find most rewarding. At CarGurus, I built an orchestration layer that consolidated 12 downstream services into 5, and I've seen firsthand how good workflow infrastructure multiplies every team's velocity. Second, Stripe's engineering culture — the emphasis on writing, rigor, and long-term thinking over speed hacks matches how I naturally work. I authored RFCs and architecture standards that were adopted across 10+ teams, and that kind of written-decision-making culture is where I do my best work."

---

## 9. Red Flags to Watch For

- If the workflow engine is primarily maintenance work with no architectural evolution
- If the "Staff" scope is really just senior IC work without cross-team influence
- If the team is siloed from the teams consuming the workflows (platform without customer feedback loop)
- If on-call is punishing and unaddressed (financial systems can be brutal)

---

## 10. Pre-Interview Checklist

- [ ] Re-read this doc
- [ ] Re-read resume_stripe.html
- [ ] Practice Stories 1, 3, 5, 12 aloud (2 min each)
- [ ] Review system_design_playbook.md: Payment System, Rate Limiter, Distributed Message Queue
- [ ] Review technical_playbook.md: concurrency, distributed transactions
- [ ] Have "Why Stripe?" answer ready
- [ ] Prepare 3 questions per interviewer
