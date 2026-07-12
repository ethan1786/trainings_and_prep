# Questions to Ask Interviewers

> Organized by interview stage.
> Pick 2-3 per round. Don't ask things easily Googleable.
> **New: includes manager/culture screening questions based on 3 months of interview experience.**

---

## Universal Questions (Any Company, Any Stage)

### Recruiter Screen
- What does the interview process look like, and what's the expected timeline?
- Is this a backfill or a new headcount? What's driving the hire?
- How is the team structured? How many engineers, and what's the seniority distribution?
- What does remote collaboration look like day-to-day for this team?
- Is there flexibility on level, or is this firmly scoped to [Staff/L6/etc.]?
- What's the total compensation range for this role (base + bonus + equity)?

### Hiring Manager
- What's the biggest technical challenge the team is facing right now?
- How do you measure success for this role in the first 6-12 months?
- What does the on-call rotation look like? What's the incident frequency?
- How much autonomy does this role have in setting technical direction vs. executing a defined roadmap?
- What's the team's relationship with product? How are priorities set?

### Team Match / Cross-functional
- What's a recent project you're proud of, and what made it successful?
- What's the most frustrating infrastructure or tooling gap on the team right now?
- How do design decisions get made here — RFCs, design reviews, informal discussion?
- How does the team handle disagreements on technical direction?
- What's something you wish you'd known before joining?

---

## Manager & Culture Screening Questions

> **Purpose:** Detect anxiety-driven management, lack of autonomy, and dysfunction before you accept.
> Ask these to the HM, skip-level, or team match interviewer. Frame them as curiosity, not interrogation.

### Autonomy & Trust

| Question | What you're listening for |
|---|---|
| "How do you like to stay informed on projects — standups, async updates, something else?" | Good: "I trust the team to escalate." Red flag: "I like daily syncs and to be looped in on everything." |
| "How much autonomy do Staff engineers have in technical decisions?" | Good: "They own the decision, I'm a sounding board." Red flag: "I like to be involved in all major decisions." |
| "If a Staff engineer disagrees with a technical direction, how does that get resolved?" | Good: "We discuss, data wins, then commit." Red flag: "I make the final call." / vague non-answer. |
| "How do you balance being informed vs. giving the team space to execute?" | Good: specific process (weekly update, escalation path). Red flag: "I just like to know what's going on" (= constant check-ins). |

### Decision-Making & Technical Direction

| Question | What you're listening for |
|---|---|
| "When technical decisions get made, who has final say — the IC closest to the problem, the manager, or a committee?" | Good: "The IC owns it, I help remove blockers." Red flag: "We discuss as a team" (= no one owns it, loudest voice wins). |
| "Can you tell me about a recent technical decision that changed direction mid-project? What drove that?" | Good: new data, customer feedback, constraint changed. Red flag: vague "leadership decided" or "priorities shifted" with no clear reason. |
| "How does the team handle situations where an engineer recommends one approach but leadership wants something different?" | Good: transparent tradeoff discussion, engineer's voice matters. Red flag: "We align with leadership's vision" (= you'll be overruled without discussion). |

### Workload & Scope

| Question | What you're listening for |
|---|---|
| "What does a typical week look like for a Staff engineer here — ratio of meetings vs. deep work?" | Good: "Protected maker time, meetings clustered." Red flag: "It varies, we have a lot of alignment meetings." |
| "How does the team handle scope creep — when a Staff engineer is asked to be involved in things outside their domain?" | Good: "We're explicit about ownership boundaries." Red flag: "We expect Staff engineers to be involved across the board." |
| "What does 'being proactive' look like for this role?" | Good: "Identify problems, propose solutions, drive them." Red flag: "Stay on top of everything, be involved everywhere." (= surveillance expectation) |

### Culture & Growth

| Question | What you're listening for |
|---|---|
| "What's the most common reason engineers leave this team?" | Honest answer = trust. Deflection = red flag. |
| "How does the team celebrate wins vs. handle failures?" | Good: blameless retros, public recognition. Red flag: "We do post-mortems" (only failure-focused). |
| "What does the path from Staff to Senior Staff / Principal look like here?" | Good: clear criteria, examples of recent promotions. Red flag: vague "keep doing great work." |
| "How has the team changed in the last year?" | Listen for: reorgs, layoffs, direction changes, manager turnover. Stability matters. |

### The Meta-Question (ask yourself after the interview)

> **Did the HM talk more about PROCESS (meetings, visibility, updates, alignment) or OUTCOMES (what you'll build, what problems you'll solve)?**
> 
> Process-heavy = anxiety-driven manager who manages by presence, not results.
> Outcome-heavy = trusts you to figure out the HOW, cares about the WHAT.

---

## Red Flag Checklist (Ask Yourself After Each Interview)

### About the Role
- [ ] Did they struggle to articulate the team's biggest challenge? (unclear direction)
- [ ] Did they dodge questions about on-call or work-life balance? (burnout culture)
- [ ] Did the team match interviewer seem disengaged or negative? (retention issues)
- [ ] Did they oversell the role without specifics? (role isn't well-defined)
- [ ] Did they seem surprised by technical depth questions? (role is less technical than posted)

### About the Manager
- [ ] Did the HM mention "visibility" or "alignment" more than "building" or "shipping"? (process over substance)
- [ ] Did they describe Staff+ expectations as "be involved in everything"? (no scope boundaries)
- [ ] Did they avoid answering who has final say on technical decisions? (politics over engineering)
- [ ] Did they talk about what THEY want to see rather than what YOU'LL own? (you're an extension of them, not autonomous)
- [ ] Did they mention other teams or people making decisions that affect your scope? (you'll be overruled regularly)

### About the Culture
- [ ] Did they recently have layoffs or reorgs without clear explanation? (instability)
- [ ] Is the team mostly junior with you as the only senior? (you'll be doing all the heavy lifting + mentoring with no peers)
- [ ] Did they dodge the "why do people leave" question? (they know the answer and it's bad)
- [ ] Did they emphasize "fast pace" repeatedly? (may mean chaotic, not productive)
- [ ] Did multiple interviewers give conflicting descriptions of the role? (role isn't defined)

---

## Company-Specific Questions

### Coinbase — Staff SWE (November re-apply)

**Recruiter:**
- How does the team I'm matched to relate to the broader backend infrastructure?
- What's the regulatory environment like — do engineers interact directly with compliance?

**Hiring Manager:**
- What does the transaction processing pipeline look like end-to-end — from user intent to settlement?
- How does the team handle idempotency and exactly-once semantics in financial flows?
- What's the biggest reliability or correctness challenge the team faces today?
- How does the team think about auditability and regulatory compliance in the architecture?

**Team Match:**
- What's the testing strategy for financial correctness — property-based testing, chaos engineering, reconciliation?
- How does the on-call experience compare to a non-financial engineering team?

---

### Affirm — Staff SWE, Backend

**Hiring Manager:**
- What does the merchant lifecycle orchestration look like end-to-end — onboarding through active management?
- How does the team handle peak traffic events (Black Friday/Cyber Monday) — capacity planning, load shedding?
- What's the biggest architectural challenge the team is tackling right now?
- How does the team balance reliability investment vs. feature velocity?

**Team Match:**
- How do services communicate — sync REST/gRPC, async events, or a mix?
- What does the deploy and rollback process look like? How often do you ship?

---

### Circle — Staff SWE

**Hiring Manager:**
- What's the current architecture of the payment/stablecoin infrastructure — monolithic, microservices, event-driven?
- What's the biggest platform-level technical debt or architectural challenge right now?
- How does the team handle the tension between moving fast and maintaining financial-grade reliability?
- What does "transfer value across blockchain and traditional banking protocols" look like day-to-day for engineers?

**Team Match:**
- What's the security and compliance review process for architectural changes?
- How does the team test blockchain interactions — testnets, simulation, or something else?

---

### Meta — E6 Backend/Infrastructure

**Hiring Manager:**
- What team would I likely be matched to, and what's their current biggest challenge?
- How does the team balance shipping new capabilities vs. scaling/reliability of existing systems?
- What does technical leadership look like at E6 — setting direction for your team, or influence across teams?

**Team Match:**
- What's the deploy cadence? How does the team handle rollouts at Meta's scale?
- How do design decisions get made — design docs, diff reviews, architecture councils?
- What's the on-call experience like for this team?

---

### Spotify — Staff SWE, Content Intelligence

**Hiring Manager:**
- What does the content processing pipeline look like end-to-end — from raw content to enriched metadata?
- How does the team handle multimodal processing at scale — batch, streaming, or hybrid?
- What's the relationship between this platform team and the product teams consuming the intelligence?
- What are the biggest reliability or latency challenges in the current system?

**Team Match:**
- How does the team integrate AI/LLM capabilities into the pipeline — synchronous inference, batch enrichment, or both?
- What does the development experience look like — local testing, staging, canary deploys?

---

### NVIDIA — Cloud Platform (when role appears)

**Hiring Manager:**
- What's the architecture of the cloud service platform — multi-tenant, per-customer isolation, or hybrid?
- What are the biggest scaling challenges as GPU cloud demand grows?
- How does the team handle resource scheduling and multi-tenancy at GPU-cluster scale?

**Team Match:**
- What does the development and deployment cycle look like for cloud services?
- How does the team monitor and maintain SLOs across the platform?

---

### Klaviyo — Staff/Principal (safety net)

**Hiring Manager:**
- What's the event processing architecture — volume, latency requirements, storage?
- What are the biggest scaling challenges as customer count grows?
- How does the team handle noisy neighbor problems across tenants?
- What does technical leadership look like at Staff/Principal level here — scope, autonomy, influence?

**Team Match:**
- How does the platform handle per-customer data isolation and processing fairness?
- What's the ratio of feature work vs. infrastructure/reliability investment?
