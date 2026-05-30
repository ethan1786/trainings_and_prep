# Job Search — Round 2

> Last updated: May 30, 2026
> Strategy shift: Senior roles at higher-bar companies for growth + comp.

---

## Strategy

**Target level:** Senior (at companies where Senior = Staff-level scope/comp elsewhere)
**Target roles:** Backend platform, payments/financial systems, distributed systems, infrastructure
**Target comp:** $300-450K+ TC
**Approach:** Cast wider net, don't over-invest in any single application. Apply in batches.
**Key lesson from Round 1:** Narrate tradeoffs out loud. State alternatives before picking. Spend 2 more minutes on "what do we need" before "here's what I'd use."

---

## Pending from Round 1

| Company | Status | Expected Response |
|---|---|---|
| **NVIDIA** | All 4 rounds done | Days to 1 week |
| **Cherry** | All 3 tech rounds done | Days to 1 week |
| **Dropbox** | Cold app (Commerce Platform) | 1-2 weeks |
| **GitHub** | Cold app (Code Search - stretch) | 1-2 weeks |
| **HashiCorp/IBM** | Coding round done, low priority | Whenever |

---

## New Target Companies — Priority Order

### Tier 1: Strong fit + high comp (apply first)

| Company | Role Focus | Why It Fits | Status |
|---|---|---|---|
| **Netflix** | L5 Senior, Platform/Backend | Java shop, $400-700K all cash, massive scale. | Check cooldown from previous app |
| **Stripe** | Senior, Payments/Identity | Your exact domain. Already applied Commerce Platform. | Check for new roles / follow up |
| **LinkedIn** | Senior, Backend/Platform | Java, distributed systems, Microsoft-owned, stable, remote. | Browse careers page |
| **Databricks** | Senior, Platform/Infra | Distributed systems, data platform, high comp. | Browse careers page |
| **Uber** | Senior, Platform/Payments | Java backend, payment systems, huge platform org. | Browse careers page |
| **Square/Block** | Senior, Payment Infrastructure | Literally your payment system domain at scale. | Browse careers page |
| **Affirm** | Senior, Backend/Platform | BNPL at scale — Cherry's domain but bigger company. | Browse careers page |

### Tier 2: Good fit (apply after Tier 1)

| Company | Role Focus | Why It Fits | Status |
|---|---|---|---|
| **Lyft** | Senior, Platform/Payments | Same domain as Uber, smaller. Tim (Cherry HM) came from here. | Browse |
| **Shopify** | Senior, Commerce Platform | Payments, commerce, remote-first. | Browse |
| **DoorDash** | Senior, Platform (non-security) | Strong eng org, check platform/payments teams. | Browse |
| **Instacart** | Senior, Marketplace/Payments | Similar patterns (marketplace + payment flows). | Browse |
| **Klarna** | Senior, Backend/Payments | BNPL competitor to Cherry/Affirm. European HQ, US remote. | Browse |
| **Twilio** | Senior (if available) | Already applied Principal — check if Senior roles exist. | Check |

### Tier 3: Stretch / high reward

| Company | Role Focus | Notes |
|---|---|---|
| **Amazon** | L6 Senior SDE | LC Heavy + LP stories (prepped). High comp. |
| **Snowflake** | Senior, Distributed Systems | Cloud platform, high bar, high comp. |
| **Apple** | Senior, Backend Services | Apple Pay, iCloud. Less remote-friendly. |
| **Confluent** | Senior, Platform | Kafka experts. Tried before, no response. Try new role. |

---

## What to Fix (Coinbase Feedback)

**Problem:** Jumped to solutions without narrating reasoning.
**Fix:** At every design decision, say 4 sentences:

1. "I need [what]"
2. "Options are [A vs B vs C]"
3. "I'm picking [A] because [reason]"
4. "Tradeoff: [what I give up]"

**Practice this as a reflex.** Before any technology choice — pause 10 seconds and say the 4 sentences.

### Quick Tradeoff Reference (have these ready)

| Decision | Pick A | Pick B | Deciding factor |
|---|---|---|---|
| Postgres vs Mongo | ACID, joins, constraints | Flexible schema, high write, document-shaped | Need transactions? → Postgres. Document-shaped + no joins? → Mongo. |
| Redis vs in-memory | Shared across instances, survives restart | Zero latency, no serde cost | Multiple instances need same data? → Redis. Single service, hot path? → In-memory. |
| Kafka vs SQS | Replay, ordering, multi-consumer | Managed, simple, cheap | Need replay or multiple consumers? → Kafka. Simple work queue? → SQS. |
| REST vs gRPC | Human-readable, browser-compatible, universal | Binary, fast, typed, streaming | External/public API? → REST. Internal service-to-service? → gRPC. |
| Sync vs async | Simple, immediate consistency | Decoupled, handles burst, eventual consistency | Critical path + user waiting? → Sync. Background processing + can lag? → Async. |
| Monolith vs microservice | Simple ops, fast iteration, one deploy | Independent scaling, separate ownership, fault isolation | Early stage / low traffic? → Monolith. Clear domain boundaries + team ownership? → Extract. |

---

## Interview Prep Adjustments

**What's already strong (keep):**
- System design mental model (product reqs → facts → constraints → trace path → failure modes)
- Behavioral stories (STAR format, leadership + technical angles)
- Domain interview (payment system walkthrough)
- Java depth (concurrency, caching, connection pools)

**What to add for FAANG-tier:**
- [ ] More LC practice — expect Medium-Hard at Netflix/Uber/Amazon
- [ ] Sharper tradeoff articulation — practice saying "I considered X but chose Y because..."
- [ ] Deeper system design — Netflix/Amazon expect 60-min SD with more depth than Coinbase
- [ ] Amazon LP stories (if applying) — you already have the LP playbook

---

## This Week — Action Items

- [ ] Wait for NVIDIA + Cherry results
- [ ] Browse: Netflix, LinkedIn, Square/Block, Affirm, Uber careers pages
- [ ] Apply to any matching roles found (use Coinbase resume for platform, HashiCorp resume for infra/security)
- [ ] Light LC practice — 2-3 mediums per day to stay sharp
- [ ] Practice tradeoff narration — pick any past design decision, explain it with the 4-sentence framework

---

## Resume Strategy

| Company Type | Resume to Use |
|---|---|
| Platform / payments / fintech | `resume_coinbase.html` (platform + financial systems) |
| Security / identity / infra | `resume_hashicorp.html` (IAM + security focus) |
| Full-stack / startup | `resume_cherry.html` (full-stack generalist) |
| AI / ML platform | `resume_twilio.html` (platform + AI emphasis) |
