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

## Applications — Active

### Applied

| Company | Role | Status | Resume Used |
|---|---|---|---|
| **Netflix** | L5 Distributed Systems, Membership & Monetization Platform (Remote) | Applied May 30 | Coinbase |
| **Stripe** | Backend/API Engineer, Money as a Service (Remote) | Applied May 30 | Coinbase |
| **Affirm** | Senior SWE, Backend - Merchant Advocacy (Remote) | Applied May 30 | Coinbase |
| **Reddit** | Staff SWE, Community Builders (Remote) | Applied May 30 | Coinbase |
| **Dropbox** | Staff Backend, Commerce Platform (Remote) | Applied May 26 | Coinbase |
| **Airbnb** | Senior SWE, Guest & Host - Partner Integrations (Remote) | Applied May 31 | Coinbase |
| **GitHub** | Staff SWE, Code Search (Remote — stretch) | Applied May 30 | Coinbase |

### Apply Now (strong product-backend fits)

| Company | Role | Why It Fits | URL | Resume |
|---|---|---|---|---|
| **Affirm** | Senior SWE, Backend (Merchant Advocacy) - Remote US | Checkout/payment flows. Your exact domain. | https://job-boards.greenhouse.io/affirm/jobs/7636414003 | Coinbase |
| **Affirm** | Senior SWE, Full Stack (Zero to One Labs) - Remote US | 0→1 product building. Your Digital Shopping story. | https://job-boards.greenhouse.io/affirm/jobs/7686804003 | Cherry |
| **Reddit** | Senior SWE, GraphQL - Remote US | Your DGS/federation experience directly. | https://job-boards.greenhouse.io/reddit/jobs/7309137 | Coinbase |
| **Reddit** | Staff SWE, Community Builders - Remote US | Staff product backend, remote. | https://job-boards.greenhouse.io/reddit/jobs/7875645 | Coinbase |

### Browse Later (manual check needed)

| Company | Why | Notes |
|---|---|---|
| **Netflix** | L5 = $400-700K all cash. Java shop. | Workday API blocked — browse jobs.netflix.com manually. Referral-driven. |
| **LinkedIn** | Java, distributed systems, remote. | Browse careers.linkedin.com for Senior Backend. |
| **Square/Block** | Payment infra at scale. | No remote roles currently — monitor. |

---

## Lane Definition (what to apply for vs skip)

**✅ Target (product backend):**
- Payments, commerce, transactions, checkout
- User-facing APIs, order systems, state machines
- Marketplace backends, merchant integrations
- Financial systems, BNPL, lending platforms
- GraphQL/API layers serving product features
- 0→1 product building

**❌ Skip:**
- Pure infra (compute platform, networking, containers, K8s internals)
- Security / IAM / identity (HMs don't see enough recent depth)
- Database / storage internals
- Search engine internals
- Developer tools / CI/CD
- ML/AI research (not ML platform)

---

## What I Learned — Why Coinbase Rejected + How to Fix

### The Root Cause

I prepared TOO well. I knew all the patterns by heart and jumped to solutions immediately without showing the reasoning journey. The interviewer couldn't tell if I was THINKING or RECITING.

**What the interviewer experienced:** "This candidate jumped to a solution in 2 minutes. Did they actually think about this problem, or did they memorize an architecture?"

**The Coinbase feedback ("more proactive on requirements" + "better tradeoff clarification") actually means:**
- I didn't explore the problem's UNIQUE constraints before designing
- I didn't show WHY my choices were right for THIS specific problem
- I didn't demonstrate the design space (alternatives considered, tradeoffs made)
- I arrived at the correct answer too fast — without bringing the interviewer along

**Same problem showed up at NVIDIA coding:** I said "this is topological sort" immediately. The interviewer was shocked and had to ask "WHY do you think that?" — because I didn't show the reasoning that led me there.

### The Senior vs Staff+ Gap

| Level | What they demonstrate |
|---|---|
| **Senior** | "I know the right answer and can implement it" |
| **Staff+** | "I know WHY it's right, WHEN it's wrong, and WHAT would change my mind" |

**I have the Senior signal down cold.** The Staff+ signal requires showing:
- Why THIS solution and not the alternatives
- When this solution would be the WRONG choice
- What constraint in this specific problem makes it the winner
- If that constraint changed, would my answer change

### The Fix — Three Habits to Build

**Habit 1: Don't name the solution for 3-5 minutes.**

Even when you recognize the pattern instantly, spend time on:
1. "What's the core constraint/unique thing about THIS problem?"
2. "What would a naive approach be and why doesn't it work?"
3. "What property of the problem points toward [solution]?"
THEN name the pattern.

**Habit 2: The 4-sentence tradeoff at every decision.**

1. "I need [what]"
2. "Options are [A vs B vs C]"
3. "I'm picking [A] because [specific constraint in this problem]"
4. "Tradeoff: [what I give up]. If [constraint X changed], I'd reconsider."

**Habit 3: Know the WHY depth for every technology.**

For each technology I commonly pick, know:
- When it's the RIGHT choice (the constraint that makes it win)
- When it's the WRONG choice (the constraint that makes it lose)
- The 2 alternatives and what they trade differently
- The failure modes (what breaks at scale or in edge cases)

### The Doctor Analogy

- Bad doctor: "I don't know what's wrong"
- Okay doctor: "It's pneumonia. Here's antibiotics." ← THIS IS ME RIGHT NOW
- Great doctor: "Symptoms suggest respiratory infection. Could be viral or bacterial. Fever duration + chest X-ray point toward bacterial. Prescribing antibiotics because [reason]. If no improvement in 48h, reconsider because [alternative]." ← THIS IS STAFF+

Same diagnosis. Same treatment. But the great doctor showed the differential reasoning.

### The Pacing Problem

| My instinct | What the interviewer values |
|---|---|
| Finish early = looks strong | Thoughtful pace = looks senior |
| Fast answer = confidence | Explored answer = judgment |
| No wasted time | Time on reasoning IS the evaluation |

**Finishing early ≠ impressing them. It means I left signal on the table.**

Rules:
- Coding: 3-5 min talking before writing ANY code
- System Design: 5-8 min on requirements/constraints before drawing ANY boxes
- If I finish early: discuss alternatives, edge cases, production concerns

### It's NOT That I'm Not Good Enough

The knowledge is there. The experience is there. The correct answers are there. What's missing is the PERFORMANCE of arriving at the answer through visible reasoning — not the knowledge itself.

**The skill to build:** Narrating the journey to a known destination. I know where I'm going — just bring the interviewer along for the ride.

---

### Quick Tradeoff Reference (have these ready)

| Decision | Pick A | Pick B | Deciding factor |
|---|---|---|---|
| Postgres vs Mongo | ACID, joins, constraints | Flexible schema, high write, document-shaped | Need transactions? → Postgres. Document-shaped + no joins? → Mongo. |
| Redis vs in-memory | Shared across instances, survives restart | Zero latency, no serde cost | Multiple instances need same data? → Redis. Single service, hot path? → In-memory. |
| Kafka vs SQS | Replay, ordering, multi-consumer | Managed, simple, cheap | Need replay or multiple consumers? → Kafka. Simple work queue? → SQS. |
| REST vs gRPC | Human-readable, browser-compatible, universal | Binary, fast, typed, streaming | External/public API? → REST. Internal service-to-service? → gRPC. |
| Sync vs async | Simple, immediate consistency | Decoupled, handles burst, eventual consistency | Critical path + user waiting? → Sync. Background processing + can lag? → Async. |
| Monolith vs microservice | Simple ops, fast iteration, one deploy | Independent scaling, separate ownership, fault isolation | Early stage / low traffic? → Monolith. Clear domain boundaries + team ownership? → Extract. |

### WHY Depth Reference (build this out for each technology)

**Template for each technology:**

```
[Technology X]
✅ RIGHT choice when: [constraint that makes it win]
❌ WRONG choice when: [constraint that makes it lose]
🔄 Alternatives: [A] trades [X], [B] trades [Y]
💥 Failure modes: [what breaks at scale/edge cases]
🔑 The deciding question: "[one question that determines if this is right]"
```

**Example — Kafka:**
- ✅ RIGHT: Need replay for crash recovery, multiple consumers, ordering guarantees, high throughput
- ❌ WRONG: Single consumer, simple work queue, low volume, don't need replay. Kafka is operational overhead you don't need.
- 🔄 Alternatives: SQS (managed, cheap, no replay), direct HTTP (simple, coupled, no buffer), Redis pub/sub (fast but no persistence)
- 💥 Failure modes: Consumer lag grows unbounded, partition rebalancing storms, offset management bugs lose messages
- 🔑 Deciding question: "Do I need replay OR multiple consumers? If no to both → SQS is simpler."

(TODO: Build this for Postgres, Mongo, Redis, Elasticsearch, REST, gRPC, WebSocket, in-memory cache, CDN, etc.)

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
