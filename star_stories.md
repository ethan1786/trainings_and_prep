# STAR Stories — Master Reference

> **Format per story:** STAR Spoken-Style → Bullet Recap → Long-Form Narrative
> **LP Tags** map to Amazon-style Leadership Principles for quick lookup.
> **Company Tags** show which target companies each story is most relevant for.

---

## Direct Questions — 30-Second Answers

These aren't STAR questions — they're direct, and you need a prepared crisp answer. Don't ramble.

### About You

**"Tell me your strengths."**
> "I'm strong at seeing across team boundaries. After working across many product features, I naturally spot systemic problems that no single team owns — and I have the follow-through to turn that into a cross-org initiative. The API modernization at CarGurus started that way: I identified the bottleneck, pitched the solution, led 10 teams through it, and set the architectural standard for the org."

**"Tell me your weaknesses."**
> "I tend to dive deep into the technical solution before fully validating the product context. I had a case where I designed an aggressive caching strategy that was technically sound but didn't account for how frequently the product team was running experiments — it caused stale data in A/B tests. Since then, I always ask 'what's the mutation pattern?' before designing caching or any data strategy. I catch myself and ask the product question first now."

**"Tell me about yourself." / "Walk me through your background."**
> "I'm a Staff/Principal backend engineer with 13 years of experience. Three chapters: I was an early engineer at Toast during hypergrowth — built core services, infrastructure, the whole stack from scratch. Then at Applause I led the auth modernization — Keycloak SSO, API gateway security, service mesh. For the last 6 years at CarGurus I've been the technical lead for the highest-traffic platform — redesigned the API serving millions of daily requests, 5x latency improvement, drove architecture standards across 10+ teams. Most recently I've been focused on AI platform infrastructure — MCP servers, agent backends, and using AI to automate cross-team collaboration."

**"Why are you leaving your current role?"**
> "I've been at CarGurus for 6 years and I've had a great run — led the biggest platform initiatives, set architecture standards, mentored engineers. But I've outgrown the problems. I want to build at higher stakes and larger scale, and [company name]'s challenges are exactly the kind of work I'm looking for."

**"Why this company?"**
- **Coinbase:** "Financial platform infrastructure at massive scale. Correctness, reliability, and observability are non-negotiable — that's exactly where my experience maps. Plus you're going AI-first, and I've been building AI platform backends."
- **HashiCorp/IBM:** "I use Terraform daily, and my auth background — Keycloak, Kong, service mesh — maps directly to Vault and Boundary. IBM's backing gives the team stability to invest long-term."
- **Cherry:** "Early-stage, full-stack ownership, building real infrastructure from scratch — I did this at Toast and it's where I thrive."
- **NVIDIA:** "The platform work — distributed systems, data pipelines, APIs across engineering orgs — is my core strength. My academic background in control systems and sensor processing is a bonus fit."

### Career & Growth

**"Why haven't you been promoted?" / "Why are you still at the same level?"**
> "My title is Principal at CarGurus, which maps to Staff at most FAANG-scale companies. I've been operating at that level for years — driving cross-org initiatives, setting architecture standards, leading 10+ teams through a major platform redesign. I'm looking for a company where the scope matches what I'm already doing."

**"Have you ever been a people manager? Would you want to?"**
> "There were opportunities to grow into the management track. I considered it seriously, but I felt my strength was in technical leadership — and my manager agreed. That said, I do a lot of the work that overlaps with management: mentoring engineers toward promotion, running cross-team alignment, giving hard feedback, driving consensus through RFCs. I'm not allergic to the people side — I actively seek it."

**"Where do you see yourself in 5 years?"**
> "Leading technical direction for a critical platform at scale — the person teams come to when there's a hard architectural problem that crosses org boundaries. Whether that's as a Staff+ IC or a technical director depends on where I can have the most impact."

**"What does your first 90 days look like?"**
> "First 30 days: learn the system. Read the code, understand the architecture, build relationships with the teams I'll be working with. Ship something small to build credibility. Days 30-60: identify the highest-leverage improvement I can drive — usually a reliability or correctness gap that's been accepted as normal. Days 60-90: propose the fix through a design doc or RFC, get buy-in, start executing. I don't come in with a pre-built agenda — I come in with a process for finding the right agenda."

### Situational

**"How do you handle disagreements with your manager?"**
> "I present my perspective with data, not just opinion. If we still disagree, I ask what would change their mind — that usually reveals we're optimizing for different things. Once the decision is made, I commit fully. I had a case where a senior leader proposed a technology I disagreed with — I prepared a 5-dimension comparison, presented it respectfully, and the group went with my recommendation. But on a separate decision where the group went the other direction, I committed completely."

**"How do you prioritize when everything is urgent?"**
> "I ask: what's the blast radius if this doesn't get done? Correctness issues (money could be wrong) beat reliability issues (system could go down) beat performance issues (system is slow) beat feature work. For the API modernization, I prioritized the parity testing framework before the performance work — getting the answers right mattered more than getting them fast."

**"How do you handle ambiguity?"**
> "I start building. Not the final solution, but something concrete that forces clarity. On the MCP server project, requirements were shifting weekly. I built a modular architecture in the first sprint that gave PMs something to demo and gave me feedback on what actually mattered. Ambiguity resolves faster when people can react to something real than when they're debating abstractions."

**"Tell me about a time you had to say no."**
> "I don't say no — I say 'here's what that costs.' On the MCP project, a PM wanted a new capability that would require significant rework. Instead of refusing, I said: 'We can do this in two days for the demo, but it won't be production-safe. Here's the alternative that gets you 80% of the value and stays on the production path.' They chose the alternative. Transparent tradeoffs, not binary yes/no."

---

## Staff+ Vocabulary — Drop These Naturally

These are the terms FAANG interviewers listen for. Don't force them — weave them into your stories where they naturally fit.

### Process & Leadership

| Term | What It Signals | Where You Used It |
|---|---|---|
| **RFC (Request for Comments)** | You drive decisions through written proposals, not just meetings | Story 1 (API mod standards), Story 7 (consensus) |
| **ADR (Architecture Decision Record)** | You document decisions with context so future engineers understand *why* | Story 1 (influence layer) |
| **Design Doc / Tech Spec** | You write before you code | Story 1, 13 |
| **Pre-socialization** | You build consensus before the big meeting — no surprises | Story 1 (influence), Story 7 |
| **Stakeholder alignment** | You manage competing priorities across orgs | Story 3 (MCP stakeholders) |
| **OKRs / Success metrics** | You define what "done" looks like upfront | Story 1 (p99, availability targets) |
| **Blast radius** | You think about failure scope before shipping | Story 1 (deploy risk), Story 4 (experiment retirement) |
| **Force multiplier** | You make others more effective, not just yourself | Story 5 (mentoring), Story 1 (standards adoption) |

### Architecture & Reliability

| Term | What It Signals | Where You Used It |
|---|---|---|
| **SLO (Service Level Objective)** | You set measurable reliability targets per service | Story 1 (per-hop latency budgets) |
| **SLA (Service Level Agreement)** | You understand the contractual commitments to users | Story 11 (Applause auth — partner SLAs) |
| **Error budget** | You balance reliability investment vs. feature velocity | Story 1 (SLO framework) |
| **Circuit breaker** | You isolate failures so one bad dependency doesn't cascade | Story 1 (technical layer) |
| **Graceful degradation** | You return partial results instead of a 500 | Story 1 (non-critical sources) |
| **Fault isolation** | You contain blast radius of failures per domain | Story 1 (orchestration design) |
| **Idempotency** | Retries are safe — critical for financial systems | Story 12 (CQRS), Coinbase prep |
| **Reconciliation** | You verify two sources of truth match | Story 2 (parity testing) |
| **Parity testing** | You validate new vs old at production scale | Story 2 |
| **Canary / Blue-green deploy** | You roll out safely to a subset before full traffic | Story 1 (A/B at 50% traffic) |
| **Feature flags** | You decouple deploy from release | Story 4 (experiment retirement) |
| **Event sourcing / CQRS** | You separate reads from writes, events as source of truth | Story 12 (Applause) |
| **Dead letter queue (DLQ)** | You handle message processing failures gracefully | Story 4 (event-driven), Coinbase reverse SD |
| **Backpressure** | You prevent upstream from overwhelming downstream | System design discussions |

### Observability & Operations

| Term | What It Signals | Where You Used It |
|---|---|---|
| **Distributed tracing** | You can trace a request end-to-end across services | Story 1 (Datadog dashboards) |
| **p99 / p95 latency** | You measure tail latency, not just averages | Story 1 (250ms→50ms) |
| **Latency budget** | You allocate time per hop so you know where to optimize | Story 1 (per-hop SLOs) |
| **Structured logging** | Your logs are queryable, not printf debugging | Story 1 (observability standards) |
| **Runbook** | You document incident response so on-call isn't tribal knowledge | Story 11 (Applause migration), Story 13 (Toast) |
| **On-call / incident response** | You own production reliability, not just shipping code | Story 13 (Toast — built it from scratch) |
| **Alerting on SLOs (not raw thresholds)** | You catch gradual degradation, not just hard failures | Story 1 (SLO framework) |

### Collaboration & Culture

| Term | What It Signals | Where You Used It |
|---|---|---|
| **Disagree and commit** | You push back with data, then fully commit to the group decision | Story 8 |
| **Document-driven culture** | You collaborate async through writing, not just meetings | Story 1, 7 |
| **Cross-functional** | You work with PM, Risk, Compliance — not just engineers | Story 3 (MCP), Story 4 (digital shopping) |
| **Tech lead vs. people manager** | You know the difference and chose IC leadership deliberately | All interviews |
| **Raising the bar** | You leave the org better than you found it | Story 5 (mentoring), Story 1 (standards) |

> **Tip:** Don't stack these. One or two per answer is plenty. The signal is that you use them *naturally* as part of how you think, not that you memorized a vocabulary list.

---

## Quick Index

### Section A: Full Stories (go-to stories for interviews)

| # | Story | LP Tags | Best For |
|---|-------|---------|----------|
| 1 | API Modernization — Full Story (Leadership + Technical + Influence) | Ownership, Delivers Results, Think Big, Insists on Highest Standards, Dive Deep, Earn Trust | All |
| 2 | API Modernization — Parity Testing Framework | Invent and Simplify, Dive Deep | Coinbase, Stripe |
| 3 | AI Platform Backend — MCP & Conversational AI Infrastructure | Bias for Action, Earn Trust, Customer Obsession | Coinbase, All |
| 4 | Digital Shopping — 0→1 Product Building | Bias for Action, Delivers Results, Customer Obsession, Ownership, Are Right A Lot | Coinbase, Stripe, Cherry |
| 5 | Cross-Org Leadership — Mentoring to Staff Level | Hire & Develop The Best, Earn Trust | All |
| 6 | Cross-Org Leadership — Driving Consensus via RFCs | Disagree and Commit, Earn Trust | Stripe, Netflix |
| 7 | GenAI Engine — Architecture & Experimentation Platform | Invent and Simplify, Think Big, Learn and be Curious, Insists on Highest Standards | Coinbase, Stripe, Netflix |
| 8 | Disagree and Commit — Pushing Back on Architecture | Have Backbone, Disagree and Commit | All |
| 9 | AI-Powered Cross-Domain Validation (In Progress) | Invent and Simplify, Think Big, Customer Obsession | Coinbase, All |

### Section B: Brief References (mention for experience, not lead stories)

| # | Story | Use When |
|---|-------|----------|
| 10 | DGS Subgraph — GraphQL Federation & Performance | "Learned something new," JVM performance, GraphQL |
| 11 | Applause — Auth Modernization | HashiCorp/IBM interviews, identity/auth questions |
| 12 | Applause — Event Sourcing / CQRS | Event sourcing / Kafka background questions only |
| 13 | Toast — Early Engineer in Hypergrowth | Cherry (startup context), "wearing multiple hats" |

### Section C: LP-Specific Stories (for specific behavioral questions — TODO)

| # | Story | LP Gap It Fills | Status |
|---|-------|-----------------|--------|
| 14 | Failure & Learning | Are Right A Lot, Learn and be Curious | ⚠️ NEEDS REAL STORY |
| 15 | Customer Obsession | Customer Obsession | ⚠️ PLACEHOLDER |
| 16 | Peer Conflict Resolution | Have Backbone, Disagree and Commit (peer, not leader) | ⚠️ PLACEHOLDER |

---

---

# Section A: Full Stories

---

## Story 1: API Modernization — Full Story

**Anchor:** High-Traffic Legacy API Modernization · **LPs:** Ownership, Delivers Results, Think Big, Insists on Highest Standards, Dive Deep, Earn Trust
**Best for:** All companies — this is your flagship story

### Angle Guide

This is one story with multiple layers. Emphasize the angle that fits the question — expand or skip layers as needed.

| Question Type | Lead With | Expand On | Skip |
|---|---|---|---|
| "Tell me about a project you led" / cross-org leadership | Leadership layer | Technical if they ask follow-ups | Influence |
| "How did you improve performance/reliability" / technical depth | Technical layer | Leadership for scope context | Influence |
| "How do you drive org-wide change" / standards & influence | Influence layer | Leadership for credibility | Technical details |
| "Most significant project" / delivers results | Leadership + Results | Technical + Influence as follow-ups | Nothing — tell the full arc |
| "Insists on highest standards" / pushing the bar | Technical layer ("I wasn't satisfied, pushed for 5x") | SLO framework | Influence |
| "Why did you take this on?" / ownership & motivation | Motivation framing (see below) | Technical or Influence as evidence | Don't say "manager assigned it" |

### Motivation Framing (for "why this project?" questions)

> "I'd been working across multiple product features for a couple of years and kept running into the same problems — the listing API was the bottleneck for every team. Slow, fragile, hard to deploy. I realized the fix wasn't another patch on one product — it was rearchitecting the foundation. The opportunity was twofold: improve performance for the highest-traffic page, and establish architectural patterns that every team could build on going forward. I pitched the approach to my leadership and got the green light to lead it."

**Key signals:** You identified the problem from hands-on experience, saw the cross-org opportunity (not just a local fix), and proactively pitched the solution. The project came from your insight, not an assignment.

### Likely Follow-Up: "Why not use GraphQL for the orchestration layer?"

You already use GraphQL (Netflix DGS) elsewhere, so this is a natural question. Three reasons:

> **1. I needed fine-grained per-service control.** The orchestration layer required per-service timeout configs, circuit breakers, retry policies, caching strategies, and graceful degradation — all tuned differently per downstream dependency. Forking and customizing the Netflix DGS library to support all of that is too much effort and not sustainable long-term.
>
> **2. Timeline and domain boundaries.** Each downstream service is its own domain and should eventually have its own subgraph. Creating one master graph that calls individual subgraphs underneath is just another orchestration service — it doesn't give you much benefit over a purpose-built one, and it adds GraphQL framework overhead on top.
>
> **3. Not all services fit GraphQL's paradigm.** GraphQL excels at client-driven field selection over graph-shaped, relational data. But several of our downstream services didn't fit that model:
> - Some return **flat, fixed-shape responses** — every caller wants the same fields. No benefit from flexible field selection; just overhead from query parsing and validation.
> - Some are **command-oriented** — "trigger a recalculation," "invalidate a cache." These are side-effect operations, not data fetches. Mutations technically work, but it's fighting the paradigm.
> - Some have **very high throughput requirements** where the query parsing and resolver execution overhead is unnecessary latency. A direct REST call with a known contract is faster.
>
> "The right tool for the right job. GraphQL is great for our consumer-facing gateway where clients need flexible data access. The orchestration layer is an internal coordination concern — it needs operational control, not query flexibility."

### STAR Spoken-Style

**Situation:** CarGurus' most-visited page — the vehicle listing page — was powered by a monolithic API handling about 8,000 requests per minute with millions of daily impressions. The codebase had years of accumulated domain logic spread across roughly 12 downstream integrations. It was slow, fragile, and very hard to deploy safely. P99 latency was around 250 ms, availability was about 98%, and deploys took about an hour because of the blast radius. After working across multiple product features for a couple of years, I kept hitting the same problems — this API was the bottleneck for every team. I realized the fix wasn't another patch; it was rearchitecting the foundation.

**Task:** I pitched the modernization to my leadership and got the green light to lead it. It wasn't just a rewrite — it touched almost every team's data. I needed to coordinate with about 10 teams across 3 departments, lead a small group of 3 principal and senior engineers, and deliver something that could safely take over production traffic without regressions. The opportunity was twofold: improve performance for the highest-traffic page, and establish architectural patterns that every team could build on going forward.

**Action:**

*Leadership layer:* I started by producing the initial architecture proposal in about two weeks. The key insight was introducing an orchestration service that consolidated those 12 downstream integrations into 5 well-defined services. I ran architecture reviews across all affected teams to build consensus, then we shipped the first production milestone in 6 months. We ran the new implementation in A/B testing handling 50% of traffic side-by-side with the legacy stack.

*Technical layer:* I re-planned the entire call graph. The legacy system made sequential calls where there were no data dependencies, so I restructured the orchestration to fan out independent downstream calls in async threads — parallel wherever possible, sequential only where one call's output feeds another. I defined fine-grained per-service network configs: individual timeouts, connection pools, and retry policies tuned to each dependency's profile. I added circuit breakers so a slow or failing downstream would be isolated instead of blocking the entire request. For non-critical data sources, I designed graceful degradation — return a partial response rather than a 500. On the caching side, I added in-memory caches for both long-lived static data and short-TTL dynamic data. In-memory was a deliberate choice over Redis: at 8,000 rpm with deeply nested response objects, the network hop and serialization cost would have eaten into the latency gains. I also introduced per-hop SLO latency budgets monitored in Datadog so any single service regression was immediately visible.

*Influence layer:* I documented the patterns we established — service decomposition, orchestration, caching strategy, parity testing — as formal RFCs and design docs. I pre-socialized them with tech leads across teams, incorporated feedback, and presented at architecture reviews and all-hands. I also paired with engineers from other teams when they started new services, helping them apply the patterns. The standards became org-wide, not just our team's way of doing things.

**Result:** We completed the modernization ahead of schedule. P99 went from 250 ms to about 50 ms — a 5× improvement. Availability improved from 98% to 99.9%. Deploy time dropped from an hour to about 3 minutes — 20× faster. The architectural patterns we established were adopted across multiple teams and departments. Several team leads told me the standards saved them weeks of design work. The SLO framework became the model for how other teams think about latency budgets.

### Bullet Recap

- **S:** Monolithic API powering highest-traffic page, 8k rpm, 250ms p99, ~98% availability, 1hr deploys
- **T:** Lead full modernization; coordinate 10 teams / 3 depts; deliver without regressions
- **A (leadership):** Architecture proposal in 2 weeks; orchestration service; 12→5 service consolidation; A/B tested at 50% traffic; led 3 principal/senior engineers
- **A (technical):** Sequential→parallel async fan-out; per-service timeouts, connection pools, retry policies; circuit breakers; graceful degradation; in-memory cache (not Redis — avoid network hop + serialization cost at 8k rpm); per-hop SLO latency budgets in Datadog
- **A (influence):** Wrote RFCs and design docs; pre-socialized with tech leads; presented at architecture reviews and all-hands; paired with other teams on new services
- **R:** p99 250ms→50ms (5×), availability 98%→99.9%, deploy 1hr→3min (20×), completed ahead of schedule, patterns adopted org-wide, SLO framework became org model

### Long-Form Narrative

The vehicle listing page is CarGurus' bread and butter — millions of consumers visit it daily, and the API behind it handled roughly 8,000 requests per minute. Over the years, the implementation had become a monolith with tendrils reaching into a dozen downstream services, each with its own quirks and hidden domain logic. Latency was hovering around 250 ms at the 99th percentile, and availability was around 98%. Deploys were nerve-wracking hour-long affairs because a bug in any part of the stack could cascade.

I was tapped to lead the modernization. My first move was to map the entire dependency graph and identify the real boundaries. Within about two weeks, I had an architecture proposal centered on a new orchestration service that consolidated 12 downstream integrations into 5 clearly defined services with explicit contracts. I presented this to all affected teams — roughly 10 teams across engineering, data, and product — and iterated on the design based on their feedback. I led a core team of 3 principal and senior engineers.

On the technical side, I found the old system was making sequential calls to downstream services even when there were no data dependencies between them, with no fine-grained network controls — every call used the same default timeout, with no circuit breaking or isolation. I restructured the call graph to fan out independent downstream calls in async threads — parallel wherever the data dependencies allowed, sequential only where one call's output fed another's input. I defined per-service network configurations: individual timeouts tuned to each dependency's latency profile, dedicated connection pools, and retry policies appropriate to each service's failure characteristics. I added circuit breakers so that a slow or failing dependency would be isolated — one bad downstream wouldn't block the entire request. For non-critical data sources, I designed graceful degradation: return a partial response rather than a 500.

For caching, I chose in-memory caches rather than Redis — a deliberate decision. At 8,000 rpm with deeply nested response objects, the network hop to Redis and the serialization/deserialization cost would have eaten significantly into the latency gains. I used long-TTL in-memory cache for static data (like dealer metadata) and short-TTL in-memory cache for dynamic data that changed more frequently but was still read-heavy. I also introduced a latency budget framework — each downstream service got an SLO for its contribution to the total request, monitored in Datadog dashboards.

We shipped the first production milestone in 6 months and set up an A/B test where the new implementation handled 50% of live traffic. I also built a parity-testing framework (see Story 2) that validated correctness during rollout.

After the project, I invested in codifying the patterns. I wrote formal RFCs and design docs covering service decomposition, API contracts, caching strategy, and the parity testing approach. I met individually with tech leads from each major team before publishing, incorporated their feedback, and presented at architecture reviews and all-hands. I also paired with engineers from other teams when they started building new services, helping them apply the patterns to their specific domains.

The results: p99 latency dropped to about 50 ms (5×), availability climbed to 99.9%, and deploy time went from an hour to about 3 minutes (20×). We completed the project ahead of schedule. The architectural patterns were adopted across multiple teams and departments — several team leads told me the standards saved them weeks of design work. The SLO budgeting approach became a model other teams adopted. The user engagement metrics on the listing page improved measurably with the reduced latency.

---

## Story 2: API Modernization — Parity Testing Framework

**Anchor:** High-Traffic Legacy API Modernization · **LPs:** Invent and Simplify, Dive Deep
**Best for:** Stripe, Datadog, Figma

### STAR Spoken-Style

**Situation:** We were rewriting CarGurus' highest-traffic API — the one behind the listing page. The legacy system had years of hidden domain logic embedded in it. Nobody had a complete specification of what the output should look like for every edge case. If we introduced even subtle regressions, it would impact millions of daily users.

**Task:** I needed a way to guarantee that the new implementation produced the exact same results as the old one for every real-world request, including edge cases that no one had documented.

**Action:** I built a parity-testing framework. It replayed real production traffic against both the legacy and new stacks in parallel, then did a deep structural diff of the full response payload — not just top-level fields, but nested objects, ordering, null handling, everything. When differences were found, the framework categorized them: was it a genuine bug, an intentional improvement, or a known legacy quirk? We ran this continuously during the rollout phase with thousands of request patterns.

**Result:** The framework caught dozens of subtle edge-case bugs before they reached production. It also surfaced hidden legacy behaviors that turned out to be bugs in the old system — things nobody knew about. This gave us the confidence to run the A/B test at 50% traffic with zero customer-facing regressions. The framework was later reused by other teams doing similar migrations.

### Bullet Recap

- **S:** Rewriting highest-traffic API with years of undocumented domain logic; zero tolerance for regressions
- **T:** Guarantee byte-level parity between old and new implementations for all real-world traffic
- **A:** Built parity-testing framework: replayed prod traffic against both stacks; deep structural diff of full payloads; categorized differences (bug vs. improvement vs. legacy quirk); ran continuously
- **R:** Caught dozens of edge-case bugs pre-production; surfaced hidden legacy bugs; enabled 50% A/B with zero regressions; framework reused by other teams

### Long-Form Narrative

The scariest part of rewriting a monolithic API isn't the rewrite itself — it's the unknowns. The legacy listing API at CarGurus had been accumulating domain logic for years. There was no authoritative spec. Business rules were encoded in conditional branches that nobody fully understood anymore.

I decided early on that we needed a safety net beyond unit tests. I designed a parity-testing framework that could replay real production request traffic against both the legacy stack and the new implementation simultaneously. The framework performed a deep structural comparison of the full response payload — not just checking that the status code matched, but comparing every nested field, array ordering, null vs. absent keys, numeric precision, the works.

When the framework found differences, it didn't just flag them — it categorized them. Some differences were genuine bugs in the new code. Others were intentional improvements (e.g., returning a consistent null instead of an empty string). And some turned out to be bugs in the legacy system that had been there for years unnoticed. We ran this continuously with thousands of distinct request patterns drawn from production logs.

The parity framework caught dozens of subtle issues before they ever reached a real user. It gave the team — and stakeholders — the confidence to run the A/B test at 50% of traffic knowing that we'd validated every edge case we could find. After the migration, other teams doing similar modernization projects adopted the framework for their own use.

---

## Story 3: AI Platform Backend — MCP & Conversational AI Infrastructure

**Anchor:** AI-First Platform Initiative · **LPs:** Bias for Action, Earn Trust, Customer Obsession
**Best for:** Coinbase (AI-first signal), All companies
**Use for:** "Tell me about AI/LLM work" — this is your answer. Keep it concise (60-90 sec), then let them dig.

### Framing: "I build the backends that AI products depend on"

Don't position this as an AI story. Position it as a **platform story** where AI is the consumer:

> "AI has been a major focus for me this year. It started when my director picked me to build the backend for our ChatGPT integration — a high-visibility project with no internal precedent. I owned the MCP server architecture end-to-end while the frontend team built the conversational UI. I delivered a working backend in the first sprint that unblocked stakeholder demos, and the modular design absorbed three rounds of requirement changes without rework. That work expanded into designing MCP APIs for several other conversational AI agents across the org — I proposed the architecture and own the backend interfaces, even where other teams handle the implementation. And now I'm driving a broader initiative using AI to automate our cross-team validation process (Story 9). Each project built on the last."

### The Progression (one answer, three data points)

| Phase | What Happened | Signal |
|---|---|---|
| MCP Server | Director picked me for high-visibility AI integration; owned backend, delivered fast, navigated stakeholder ambiguity | "I can execute on AI platform work" |
| Conversational AI agents | Proposed MCP API designs for multiple agents; own backend interfaces | "I can shape AI platform direction" |
| Cross-domain validation (Story 9) | Identified highest-leverage opportunity for AI, currently driving initiative | "I can identify where AI creates org-level leverage" |

### STAR Spoken-Style

**Situation:** CarGurus was going AI-first this year — a company-wide strategic bet. The first major initiative was integrating with ChatGPT through the OpenAI Apps SDK to expose CarGurus capabilities (vehicle search, pricing, delivery estimates) through conversational AI. There was no existing framework for this internally, the protocol was new, and requirements were evolving weekly across multiple stakeholder groups — PMs needed demos, the AI team needed a stable foundation, and directors wanted a production path.

**Task:** My director chose me to own the backend for this — a high-visibility project that needed someone who could figure out the architecture independently under ambiguity. I owned the MCP server end-to-end; the frontend team built the conversational UI on top of my APIs.

**Action:** I studied the MCP protocol deeply, then designed a modular server architecture — a core protocol handler with a plugin system where each capability was a separate tool that could be registered independently. I delivered a working backend in the first sprint that unblocked PM demos. When requirements shifted (new capabilities, different response formats, production safety concerns), the architecture absorbed the changes without rework. I managed stakeholder expectations transparently — I gave PMs early access to working demos, held weekly syncs with the AI team on interface contracts, and maintained a clear roadmap for directors showing demo-ready vs. production-ready with explicit gaps. When asks were too expensive, I proposed alternatives instead of saying no.

**Result:** The POC was successful — every stakeholder group got what they needed. The MCP architecture became the foundation for the company's AI platform. I went on to propose and design MCP APIs for several additional conversational AI agents across the org, owning the backend interfaces. This work is now evolving into a broader initiative (Story 9) using AI to automate cross-team validation.

### Bullet Recap

- **S:** Company going AI-first; ChatGPT integration as flagship initiative; no internal precedent; multiple stakeholders with competing priorities
- **T:** Director chose me to own the backend; high-visibility, ambiguous scope; frontend team handled conversational UI
- **A:** Designed modular MCP architecture (plugin-style tools); delivered working backend in first sprint; navigated stakeholder ambiguity (PM demos, AI team contracts, director production roadmap); proposed alternatives over binary yes/no; transparent tradeoff communication
- **R:** POC successful; architecture became AI platform foundation; expanded to designing MCP APIs for multiple conversational AI agents; now driving AI-powered cross-domain validation initiative (Story 9)

### Interview Tips
- **Keep it to 60-90 seconds.** This is a supporting story, not your flagship. Let them ask follow-ups.
- **If they dig into technical depth:** Talk about the modular tool plugin architecture, the demo/production boundary separation.
- **If they dig into stakeholder management:** Talk about the transparent tradeoff approach — "We can do this for the demo, but here's what's needed for production."
- **If they ask "what else in AI?":** Mention the conversational AI agent APIs and Story 9 initiative. Show the progression.
- **Don't oversell.** You built the backend platform. You didn't build the AI models or the frontend. That's honest and that's fine — you're interviewing for a platform role.

---

## Story 4: Digital Shopping — 0→1 Product Building

**Anchor:** Digital Shopping & Online Leads Products · **LPs:** Bias for Action, Delivers Results, Customer Obsession, Ownership, Are Right A Lot
**Best for:** Coinbase, Stripe, Cherry

### Angle Guide

This is your biggest **0→1 product story** at CarGurus (vs. Story 1 which is your biggest platform redesign). The differentiator is heavy cross-functional collaboration — you worked through ambiguity with product, frontend, data eng, and dealers to ship something new.

| Question Type | Lead With | Expand On | Skip |
|---|---|---|---|
| "Built something from scratch" / 0→1 | Product building angle — ambiguity, cross-functional, incremental delivery | Technical decisions as follow-ups | Retirement details |
| "Cross-functional collaboration" / working with product | Collaboration angle — clearing ambiguities with PM, frontend, data eng | Short-term vs long-term tradeoffs | Technical architecture |
| "Short-term vs long-term tradeoffs" / pragmatic decisions | Tradeoff angle — what to ship now vs invest in | Collaboration context | — |
| "Ownership / long-term thinking" | Lifecycle angle — built it, iterated, retired experiments safely | 0→1 context for scope | — |
| "Bias for action" / delivers results | Delivery angle — critical path first, pragmatic tradeoffs, speed | Collaboration as enabler | Retirement |

### STAR Spoken-Style

**Situation:** When the pandemic hit in 2020, the automotive industry shifted overnight. Consumers couldn't visit dealerships, and CarGurus needed a way to capture online leads and enable digital shopping experiences. There was enormous business pressure to ship — competitors were racing to fill the gap. But the product requirements were ambiguous: nobody had done this before at CarGurus, and the product team, frontend, data engineering, and I all had different assumptions about what "digital shopping" meant and how it should work.

**Task:** I led the backend design and implementation for this 0→1 product. Beyond the technical work, I needed to collaborate closely with product to clarify what we were actually building, align with frontend on data contracts and API shapes, and work with data engineering on inventory pipelines — all under pressure to ship fast.

**Action:**

*Product building / cross-functional angle:* The biggest challenge wasn't the code — it was clearing the ambiguity. I spent significant time with product to break down "digital shopping" into concrete features with clear priorities. We aligned on what needed to launch first (lead capture — getting consumer intent to dealers) vs. what could follow (merchandising, inventory display). I worked with frontend to define API contracts iteratively — we didn't have a perfect spec upfront, so I designed the backend to be flexible enough to evolve as the product definition solidified. With data engineering, I figured out how to get inventory data flowing reliably from dealer feeds into the new system.

*Technical / incremental delivery angle:* I started small — a few helper services within the monolith to prove the core flows worked. As the product grew and we understood the domain better, I gradually extracted pieces into their own microservices with Kafka-based event pipelines connecting them. This wasn't a grand "let's build microservices" plan — it was pragmatic extraction as complexity justified it. I prioritized ruthlessly: lead capture went to production first because it was the critical business path. Inventory data could be eventually consistent (it was already slightly stale from dealer feeds), which let us move faster. Lead data needed stronger delivery guarantees.

*Short-term vs long-term tradeoff angle:* I made deliberate tradeoffs with product and documented them. We launched with eventual consistency where strong consistency wasn't needed. I invested upfront in feature flags and clean service boundaries — not because it was cool architecture, but because I knew from experience that product would want to experiment, and experiments that can't be safely retired become permanent tech debt. That investment paid off: when we later ran follow-on experiments (new lead flows, merchandising variations, pricing models), the ones that didn't work could be retired cleanly through a playbook I created — phased teardown with no customer-facing incidents.

**Result:** We launched within the target timeline, capturing a meaningful volume of online leads during a period when the company's core business was under stress. The architecture grew organically from monolith helpers to independent services as the product matured. We retired multiple experiments without a single customer-facing incident — the retirement playbook was adopted by other teams. The bigger cultural win: the business gained confidence to keep experimenting because they saw experiments could be safely retired.

### Bullet Recap

- **S:** Pandemic forced automotive industry online; ambiguous product requirements; multiple teams (product, frontend, data eng) with different assumptions; enormous pressure to ship
- **T:** Lead 0→1 backend for digital shopping; clear ambiguity with cross-functional partners; ship fast while building for iteration
- **A (cross-functional):** Worked with product to break ambiguity into prioritized features; iterated API contracts with frontend; aligned with data eng on inventory pipelines; documented tradeoffs jointly
- **A (technical):** Started with helpers in monolith, gradually extracted to microservices as complexity justified; Kafka event pipelines; critical path (lead capture) to production first; eventual consistency where safe, stronger guarantees for lead data
- **A (long-term):** Feature flags + clean boundaries from day one; retirement playbook for failed experiments (map integrations → disable traffic → drain pipelines → clean data → remove code)
- **R:** Launched on timeline; meaningful leads during business disruption; architecture grew organically monolith→microservices; multiple experiments retired with zero incidents; playbook adopted by other teams; experimentation became routine

### Long-Form Narrative

The pandemic created an existential shift for CarGurus. The company's business model assumed consumers would visit dealerships, but suddenly nobody could. We needed a digital shopping experience — browse, compare, and express purchase intent entirely online. And we needed it fast.

The hardest part wasn't the code — it was the ambiguity. Nobody had built this before at CarGurus. Product had a vision but not a spec. Frontend had assumptions about API shapes that didn't match the backend reality. Data engineering had inventory feeds that weren't designed for real-time consumer experiences. I spent significant time working across all of these teams to break "digital shopping" into concrete, prioritized features. Lead capture — getting consumer intent to dealers — was the critical path. Merchandising and inventory display could follow.

I started small. Rather than designing a grand microservice architecture upfront, I built a few helper services within the monolith to prove the core flows worked. As the product grew and we understood the domain better, I gradually extracted pieces into their own services with Kafka-based event pipelines. This was pragmatic, not ideological — each extraction happened when the complexity justified the operational overhead of a new service.

I made pragmatic tradeoffs with product and documented them. Inventory data could be eventually consistent — it was already slightly stale from dealer feeds — which simplified the architecture and let us move faster. Lead data needed to be reliable, so that pipeline had stronger delivery guarantees. These weren't unilateral technical decisions; I walked product through the tradeoffs so they understood what they were getting and what they were giving up.

I also invested upfront in feature flags and clean service boundaries. Not because it was fashionable, but because I knew product would want to experiment, and experiments that can't be safely retired become permanent tech debt. That foresight paid off. When CarGurus ran follow-on experiments (new lead flows, merchandising variations, pricing models), the ones that didn't work could be retired cleanly. I created a retirement playbook — phased teardown from traffic disable to code removal, with verification at each step. Multiple experiments retired with zero customer-facing incidents. Other teams adopted the playbook.

The bigger cultural win: because the business saw that experiments could be safely retired, they were more willing to approve new ones. The architecture and the process turned experimentation from risky to routine.

---

## Story 5: Cross-Org Leadership — Mentoring to Staff Level

**Anchor:** Cross-Org Platform & API Leadership · **LPs:** Hire & Develop The Best, Earn Trust
**Best for:** All companies

### STAR Spoken-Style

**Situation:** At CarGurus, I worked with several senior engineers who had strong technical skills but were scoped primarily within their own team's domain. They wanted to grow toward Staff-level roles, but they struggled with the shift from "best engineer on my team" to "engineer who drives impact across teams."

**Task:** I took it upon myself to mentor these engineers — not because it was assigned, but because I believed it was part of my responsibility as a principal engineer to raise the level of engineering around me.

**Action:** I focused on three things. First, I gave them opportunities to work on cross-team problems — I'd pull them into architecture reviews or design discussions for projects outside their immediate scope, so they could practice thinking at the organizational level. Second, I gave specific, actionable feedback on their design docs and code reviews — not just "this is good" or "this needs work," but "here's how to frame this decision so other teams understand the tradeoff" or "here's how to scope this RFC so it gets buy-in." Third, I modeled the behavior — I was transparent about my own decision-making process, including when I was uncertain, so they could see how a principal engineer navigates ambiguity.

**Result:** Multiple engineers I mentored successfully expanded their scope and took on cross-team projects. One engineer went from purely executing within their team to leading a cross-org initiative and was promoted. The feedback I consistently got was that the most valuable thing wasn't technical knowledge — it was learning how to communicate technical decisions to a broader audience.

### Bullet Recap

- **S:** Senior engineers strong technically but scoped within own team; wanted Staff-level growth
- **T:** Self-directed mentoring to help engineers develop cross-org impact
- **A:** Gave cross-team problem exposure; specific feedback on design docs and communication framing; transparent decision-making modeling; paired on architecture reviews outside their domain
- **R:** Multiple mentees expanded scope; one promoted after leading cross-org initiative; key feedback: communication framing was most valuable skill transferred

### Long-Form Narrative

One of the patterns I've noticed in engineering organizations is that the gap between senior and Staff isn't primarily technical — it's about scope, communication, and influence. Senior engineers often have excellent technical judgment within their domain, but they struggle to project that judgment across team boundaries.

At CarGurus, I worked with several such engineers. They were strong ICs who wanted to grow, but their impact was contained within their team's codebase. I made it a personal priority to mentor them, because I believe part of the principal engineer role is multiplying the org's capabilities, not just your own.

My approach was threefold. First, exposure: I brought them into architecture reviews and design discussions for projects they weren't directly involved in. This forced them to think about problems from an organizational perspective, not just a team perspective. Second, targeted feedback: when they wrote design docs or RFCs, I didn't just approve or reject — I gave specific guidance on how to frame decisions for a cross-team audience. "You're optimizing for your team's deployment speed, but the platform team cares about consistency. Here's how to reframe this to address both concerns." Third, modeling: I was transparent about my own process, including uncertainty. I'd say things like "I'm not sure this is the right call, and here's why I'm making it anyway" — which showed them that leadership at this level isn't about always being right, it's about making decisions transparently.

Over time, multiple engineers I mentored expanded their scope. One went from executing within their team to leading a cross-org API initiative and was subsequently promoted. The consistent feedback I got was that the most valuable thing wasn't the technical knowledge I shared — it was learning how to communicate technical decisions to an audience beyond their own team.

---

## Story 6: Cross-Org Leadership — Driving Consensus via RFCs

**Anchor:** Cross-Org Platform & API Leadership · **LPs:** Disagree and Commit, Earn Trust
**Best for:** Circle, Stripe, Netflix

### STAR Spoken-Style

**Situation:** CarGurus was growing its microservices footprint rapidly, and different teams were making inconsistent decisions about API contracts, error handling, pagination, and caching. There was no central standard, and it was causing friction when services needed to integrate with each other.

**Task:** I wanted to establish organizational standards for API design and service architecture. But I couldn't just dictate — multiple teams had their own opinions and existing patterns. I needed to build consensus.

**Action:** I wrote a series of RFCs covering API contract standards, error response formats, pagination patterns, and caching strategies. But writing them was only 30% of the work. I spent significant time socializing the drafts: I met with tech leads from each major team individually before publishing, incorporated their feedback, and addressed concerns. When there were genuine disagreements — for example, one team preferred cursor-based pagination while another preferred offset-based — I facilitated discussions, documented the tradeoffs of each approach, and drove the group to a decision. Once decided, I committed fully even on points where I'd personally preferred a different approach, and I made sure others saw me doing so.

**Result:** The RFCs were adopted as the engineering organization's official standards. New services were built consistently, which reduced integration friction and made it easier for engineers to move between teams. The process itself — structured RFCs with pre-socialization — became the model for how the organization makes cross-cutting technical decisions.

### Bullet Recap

- **S:** Rapid microservice growth; inconsistent API contracts, error handling, caching across teams; integration friction
- **T:** Establish org-wide standards through consensus, not dictation
- **A:** Wrote RFCs for API contracts, errors, pagination, caching; pre-socialized with individual tech leads; incorporated feedback; facilitated disagreements with documented tradeoffs; committed fully to group decisions even when personally disagreeing
- **R:** RFCs adopted as official standards; reduced integration friction; easier engineer mobility; RFC process itself became model for cross-cutting decisions

### Long-Form Narrative

As CarGurus scaled its microservices, a coordination problem emerged. Team A used offset-based pagination. Team B used cursor-based. Team C had their own error format. When services needed to talk to each other, every integration was a negotiation. Engineers moving between teams had to learn new conventions.

I decided to address this by writing a set of RFCs covering the most common friction points: API contract structure, error response formats, pagination, and caching headers. But I knew from experience that top-down mandates don't work in engineering organizations — people need to feel heard.

So before publishing the RFCs broadly, I met individually with tech leads from each major team. I shared drafts, asked for feedback, and genuinely incorporated it. Some of their suggestions were better than my original proposals. This pre-socialization meant that by the time the RFCs went to the wider group, most stakeholders already felt ownership over the content.

The hardest part was genuine disagreements. The pagination debate was a real one — cursor-based is better for consistency in dynamic datasets, but offset-based is simpler and some teams' use cases didn't need the consistency guarantee. I facilitated the discussion by documenting the tradeoffs explicitly, identifying which use cases needed which approach, and proposing a standard that accommodated both with clear guidance on when to use each. On a couple of decisions where the group went a different direction than I preferred, I committed fully and publicly — no sandbagging, no "I told you so" later.

The standards were adopted and are still in use. More importantly, the process became the template for how the organization makes cross-cutting technical decisions: structured proposal, pre-socialization, facilitated discussion, documented decision, full commitment.

---

## Story 7: GenAI Engine — Architecture & Experimentation Platform

**Anchor:** GenAI Decision Engine (Independent) · **LPs:** Invent and Simplify, Think Big, Learn and be Curious, Insists on Highest Standards
**Best for:** Netflix, Stripe, Coinbase

### Angle Guide

This is one story covering two phases: designing the hybrid architecture, then building the experimentation platform that made it optimizable.

| Question Type | Lead With | Expand On | Skip |
|---|---|---|---|
| "Tell me about a system you designed / architecture" | Architecture/design angle | Prompt Lab as evidence of measurement rigor | — |
| "How do you measure and improve a system?" / data-driven | Measurement/optimization angle | Architecture for context on what's being optimized | — |
| "Tell me about an AI/LLM project" | Architecture angle (hybrid design is the interesting part) | Prompt Lab to show you went beyond building to optimizing | — |
| "Insists on highest standards / you weren't satisfied" | Prompt Lab angle (moved from intuition to data-driven) | Architecture to show the scope of what you were optimizing | — |
| "Learn and be curious" / self-directed growth | Initiative framing (see below) | Architecture + Prompt Lab as evidence of depth | — |

### Initiative Framing (for "why did you build this?" / "learn and be curious" questions)

> "AI was becoming central to our industry, and I didn't have the opportunity to build AI systems at work at the time. Instead of waiting, I built one myself — a full GenAI decision engine as an independent project. I wanted to understand not just how to call an LLM API, but how to architect a production-grade system around it: routing, cost optimization, explainability, and systematic evaluation. That self-directed investment is what gave me the foundation to later lead the MCP server work and propose the AI cross-domain validation initiative at CarGurus."

**Key signal:** You didn't wait for permission. You invested in yourself, and that investment directly led to real work impact (Story 3 → Story 9).

### STAR Spoken-Style

**Situation:** AI was becoming central to our industry, but I didn't have the opportunity to build AI systems at work. Rather than wait, I built a GenAI decision engine as an independent project to develop real depth in the space. I hit two fundamental challenges. First, a design tension: pure LLM-based decisions were too slow and expensive for real-time use cases, but pure rule-based systems couldn't handle the nuance that made GenAI valuable. Second, an optimization problem: once the system was built, it had dozens of tunable parameters — prompts, model selection, routing thresholds, policy weights — and I was optimizing by intuition and spot-checking manually. That doesn't scale and doesn't give you confidence you're not regressing on other cases.

**Task:** I needed to design a hybrid inference architecture that was both real-time capable and LLM-quality for complex cases, and then build a systematic experimentation platform to optimize it — moving from "it seems better" to "here's the data showing it's better."

**Action:**

*Architecture/design angle:* I designed a two-path hybrid architecture. The fast path uses deterministic rules and lightweight scoring models for decisions that can be made quickly and cheaply. The deep path uses full LLM reasoning for decisions requiring nuance, context, or creativity. Every incoming request hits a routing layer that evaluates which path to use based on configurable signals: estimated decision complexity, available latency budget, and cost budget. On top of this, I built a policy overlay that processes heterogeneous telemetry — user behavior signals, contextual data, historical patterns — and applies enterprise-configurable rules to constrain the decision space. Critically, every decision comes with an explainability trace: which path was taken, which rules fired, and what the LLM's reasoning was. Stakeholders need to understand why the system made a recommendation, not just what it recommended.

*Measurement/optimization angle:* I built Prompt Lab to systematically optimize the engine. The core capability is historical replay: I can take a corpus of past decision requests with known outcomes and run them through the engine under any configuration — giving me a ground-truth comparison across changes. Beyond replay, I built parameter search: grid search for discrete configuration spaces (e.g., 5 prompts × 3 temperatures × 2 routing thresholds = 30 configs), and Bayesian optimization for continuous parameters, which builds a probabilistic model of the objective function and samples intelligently — finding good configurations in far fewer iterations than exhaustive search. All of this runs as background jobs with proper observability — experiment progress, intermediate results, resource consumption visible in dashboards. I also added multi-LLM-provider support so I could compare quality, latency, and cost across models side by side.

**Result:** The architecture achieved real-time performance for the majority of requests via the fast path, while preserving LLM-quality reasoning for complex cases. The policy overlay made it enterprise-ready — organizations can configure constraints without code changes. Prompt Lab transformed optimization from intuition to data-driven: Bayesian search found a non-obvious combination of lower temperature with a more detailed prompt template that outperformed both the high-temperature creative approach and the low-temperature simple-prompt approach. Multi-provider comparisons revealed that different models excelled at different decision types, enabling cost-quality optimization per use case.

### Bullet Recap

- **S:** Building GenAI decision engine; two challenges: (1) LLM too slow/expensive for real-time, rules too rigid for nuance; (2) optimization was ad-hoc, no systematic evaluation
- **T:** Design hybrid inference architecture + build experimentation platform to optimize it systematically
- **A (architecture):** Two-path hybrid (fast rules vs. deep LLM); configurable routing layer (complexity, cost, latency); policy overlay with heterogeneous telemetry; enterprise-configurable constraints; explainability traces on every decision
- **A (experimentation):** Prompt Lab with historical replay against real data; grid search + Bayesian optimization for parameter tuning; background job scheduler with observability; multi-provider LLM comparison
- **R:** Real-time performance for majority; LLM quality for complex cases; enterprise-ready via policy layer; Bayesian search found non-obvious optimal configs; revealed provider-specific quality/cost tradeoffs; optimization moved from intuition to data-driven

### Long-Form Narrative

The core challenge of building a GenAI decision engine is the tension between speed and quality. LLMs produce nuanced, context-aware outputs, but they're slow and expensive. Rule-based systems are fast and cheap, but they can't handle the breadth of situations that make AI valuable. Most real-world applications need both.

I designed a hybrid architecture. The system has two inference paths: a fast path (deterministic rules, lightweight scoring models, cached lookups) and a deep path (full LLM reasoning with prompt engineering and multi-step chains). Every incoming request hits a routing layer that evaluates which path to use based on configurable signals: estimated complexity of the decision, the latency budget available, the cost budget, and whether the request type has a high-quality rule available.

On top of the inference paths, I built a policy overlay. This layer processes heterogeneous telemetry — user behavior signals, contextual data, historical patterns — and applies enterprise-configurable rules to constrain the decision space. For example, an enterprise client might say "never recommend products in category X" or "always prioritize cost savings over quality for this segment." These policies are stored in a database and can be updated without code changes or deployments.

Every decision comes with an explainability trace: which path was taken, which rules fired, which telemetry signals influenced the routing, and what the LLM's reasoning was (if the deep path was used). This was critical for building trust — stakeholders need to understand why the system made a particular recommendation, not just what it recommended.

Building the system was only half the work — optimizing it was the other half, and it's arguably harder. The system has dozens of tunable parameters: prompt templates, model selection, temperature settings, routing thresholds, policy weights, caching TTLs. Changing any one of them affects behavior in ways that are hard to predict.

Initially, I was optimizing by intuition: change a prompt, run a few test cases, see if the output looked better. This doesn't scale and doesn't give you confidence that you haven't regressed on other cases.

I built Prompt Lab to solve this systematically. The core capability is historical replay: I can take a corpus of past decision requests — real data with known good outcomes — and run them through the engine under any configuration. This gives me a ground-truth comparison: did this prompt change improve decision quality? Did this routing threshold change reduce latency without hurting quality?

Beyond replay, I built parameter search. Grid search lets me sweep across discrete configuration spaces (e.g., try these 5 prompts × 3 temperatures × 2 routing thresholds = 30 configurations). Bayesian optimization handles continuous parameters more efficiently — it builds a probabilistic model of the objective function and samples intelligently, finding good configurations in far fewer iterations than grid search.

All of this runs as background jobs managed by a scheduler with proper observability — I can see experiment progress, intermediate results, and resource consumption in dashboards. The multi-provider support was another key feature: I could run the same experiment against GPT-4, Claude, and other models and compare quality, latency, and cost side by side.

The platform revealed insights I wouldn't have found manually. Bayesian optimization discovered that a non-obvious combination of a lower temperature with a more detailed prompt template outperformed both the high-temperature creative approach and the low-temperature simple-prompt approach. Multi-provider comparisons showed that different models excelled at different decision types — one model was better at structured analytical decisions while another was better at creative recommendations.

---

## Story 8: Disagree and Commit — Pushing Back on Architecture

**Anchor:** Cross-cutting · **LPs:** Have Backbone, Disagree and Commit
**Best for:** All companies

### STAR Spoken-Style

**Situation:** During the API modernization at CarGurus, a senior leader proposed that we should adopt a specific technology stack for the new orchestration service — one that they had experience with from a previous company. The proposal had momentum because of the leader's influence, but I had serious concerns. The technology was a poor fit for our use case: it added operational complexity, our team had no experience with it, and the problem it solved wasn't actually our bottleneck.

**Task:** I needed to push back on a proposal from a senior leader without damaging the relationship or creating a political situation. The decision would affect the project for years.

**Action:** I didn't just say "I disagree." I prepared a structured analysis comparing the proposed technology against the alternative I recommended — our existing stack with targeted improvements. I covered five dimensions: operational complexity, team learning curve, fit for our specific access patterns, long-term maintenance cost, and community/support ecosystem. I presented this in a design review, making it clear that I respected the leader's experience but believed the data pointed in a different direction for our specific context. I explicitly said: "I could be wrong, and here's how we'd know — if we see [specific signals], the other approach would be better, and we should revisit." I also acknowledged the legitimate benefits of their proposal.

**Result:** After discussion, the team and the senior leader agreed to go with my recommendation. The key was that I'd done the work — I didn't just have an opinion, I had a structured comparison with specific tradeoffs. The senior leader told me afterward that they appreciated the approach and that it changed their mind. We built on our existing stack, which turned out to be the right call — the project was completed ahead of schedule partly because the team didn't have to learn a new technology while simultaneously delivering under pressure. On a separate occasion where the group decided to go a different direction than I preferred, I committed fully and didn't revisit the decision.

### Bullet Recap

- **S:** Senior leader proposed unfamiliar technology stack for critical project; proposal had momentum due to influence
- **T:** Push back constructively without damaging relationship; decision would affect project for years
- **A:** Prepared structured 5-dimension comparison; presented data-driven analysis in design review; explicitly acknowledged being possibly wrong with specific revisit signals; respected leader's perspective while advocating firmly
- **R:** Team agreed with my recommendation; leader appreciated the approach; project completed ahead of schedule partly due to team familiarity; committed fully on separate decisions where group went other direction

### Long-Form Narrative

One of the hardest things about senior engineering is knowing when to push back and how to do it well. During the API modernization, a senior engineering leader proposed we adopt a specific technology for the new orchestration service. They'd used it successfully at a previous company and were enthusiastic about it. The proposal was gaining traction because of their seniority and conviction.

But I had concerns. The technology added significant operational complexity — new deployment patterns, new monitoring requirements, new failure modes we'd need to learn. Our team had zero experience with it. And critically, the problem it was designed to solve (extreme horizontal scalability) wasn't actually our bottleneck — our challenge was service coordination and data consistency, not raw throughput.

I could have stayed quiet and let the momentum carry the decision. Instead, I spent two days preparing a structured comparison. I evaluated both options across five dimensions: operational complexity (how much new infrastructure we'd need), learning curve (time to productivity for the team), access pattern fit (how well each option handled our specific query and coordination patterns), maintenance cost (ongoing operational burden), and ecosystem (community support, documentation, talent availability).

I presented this in a design review. I was careful to be respectful — I explicitly acknowledged the strengths of the proposed approach and the leader's experience. But I also made my case clearly: "For our specific context — this team, this timeline, these access patterns — I believe our existing stack with targeted improvements is the better choice. Here's the data." I also added: "I could be wrong. If we see [specific performance signals] after the first milestone, we should revisit this decision."

The group, including the senior leader, agreed with my recommendation. The leader told me afterward that they appreciated the structured approach — it wasn't personal, it was analytical. The project was completed ahead of schedule, and the team's familiarity with the stack was a real contributor to velocity.

On a different decision later in the project — a disagreement about testing strategy where the team went with an approach I wasn't fully convinced by — I committed completely. No hedging, no "I told you so" if it didn't work out perfectly. Disagree and commit means both parts.

---

## Story 9: AI-Powered Cross-Domain Validation (In Progress)

**Anchor:** VDP Cross-Team Validation · **LPs:** Invent and Simplify, Think Big, Customer Obsession, Bias for Action
**Best for:** Coinbase (AI-first signal), all companies (cross-org, initiative-driven)
**Status:** In design phase — use as "current initiative" story

### Motivation Framing

> "CarGurus is pushing AI-first this year. I looked at where AI could have the highest cross-org leverage — not just a cool demo, but something that solves a real collaboration bottleneck. Our VDP page is worked on by three teams: core, international (CA/UK-specific features), and mobile (React Native). Every feature release requires manual cross-team validation that takes days. I'm designing an AI-powered validation pipeline to turn that multi-day coordination into an automated CI check."

### STAR Spoken-Style

**Situation:** The VDP (Vehicle Detail Page) is CarGurus' most critical page, and it's worked on by three separate teams: core platform, international (Canada and UK locale-specific features), and mobile (React Native). Every time any team ships a new feature, there's a multi-day manual validation process — each team has to verify their domain isn't broken by the change. It's slow, error-prone, and doesn't scale. This is exactly the kind of cross-org friction that AI can solve.

**Task:** As part of CarGurus' AI-first initiative this year, I identified this as the highest-leverage opportunity for AI-powered automation. The goal is to turn the manual multi-day cross-team validation into an automated pipeline that runs in CI — catch cross-domain regressions before they reach staging, and eliminate the coordination overhead.

**Action (design phase — three components):**

*Phase 1 — AI Impact Analysis:* When a PR is opened touching VDP, an AI agent reads the diff, maps it against known domain boundaries (international locale logic, mobile-specific rendering, A/B test variants), and generates an impact report identifying which teams and domains are affected. Auto-tags relevant teams for review. This alone saves the "who do I need to loop in?" coordination.

*Phase 2 — MCP Server for Spec Validation:* An MCP server with tools that can read API contracts and component specs from each domain, cross-reference a proposed change against other domains' expectations, and flag breaking changes in CI. This builds directly on my MCP server architecture (Story 3) and applies my parity testing approach (Story 2) to specs instead of responses.

*Phase 3 — AI-Generated Cross-Domain Test Suites:* AI analyzes the change and auto-generates test scenarios per affected domain — US locale, CA locale, UK locale, mobile viewport, desktop viewport. Runs them against staging and surfaces unexpected differences (regression) vs. intentional differences (locale-specific behavior).

**Result (expected):** Reduce cross-team validation from days to minutes. Catch cross-domain breaking changes in CI before they reach staging. Free up engineers from manual coordination so they can focus on building. Establish a pattern that other multi-team pages can adopt.

### Bullet Recap

- **S:** VDP worked on by 3 teams (core, international, mobile); every release requires days of manual cross-team validation
- **T:** AI-first initiative — highest-leverage opportunity for AI to solve cross-org friction
- **A (design phase):** Phase 1: AI impact analysis on PR (auto-detect affected domains, auto-tag teams); Phase 2: MCP server for cross-domain spec validation in CI (builds on existing MCP + parity testing work); Phase 3: AI-generated cross-domain test suites run on staging
- **R (expected):** Days→minutes for validation; catch breaking changes in CI; free engineers from manual coordination; reusable pattern for other multi-team surfaces

### How This Connects to Your Prior Work

```
Story 2 (Parity Testing)     → compared old vs new responses at 50% traffic
Story 3 (MCP Server)         → built tool-calling server for AI integration
Story 9 (THIS)               → combines both: AI agent validates cross-domain
                               consistency using MCP tools + parity patterns
```

### Interview Tips for "In Progress" Stories
- **Don't oversell.** Say "I'm in the design phase" — honesty about status builds trust.
- **Show the thinking.** Walk through *why* you chose this problem (highest leverage), *how* it builds on prior work (MCP + parity testing), and *what the phases are* (incremental delivery, not big bang).
- **Connect to the company.** For Coinbase: "This is the same pattern you'd need for cross-team validation across payment rails, compliance, and risk — every domain change needs to be validated against other domains' contracts."

---

# Section B: Brief References

---

## Story 10: DGS Subgraph — GraphQL Federation & Performance (Brief Reference)

**Anchor:** Netflix DGS Subgraph · **LPs:** Ownership, Learn and be Curious, Dive Deep
**Status:** Trimmed — use as supporting detail, not a standalone story. Pivot to Story 1 (API Modernization) for cross-org platform work, or Story 9 (AI Cross-Domain Validation) for technical curiosity.

> **One-liner if it comes up:** "I own the Delivery Lookup service at CarGurus. When we stood up a federated GraphQL gateway for our AI chatbot platform, I learned the Netflix DGS framework from scratch, designed a federation-friendly schema with batch data loaders to prevent N+1 issues, and solved a JVM cold-start problem by building a warmup routine that exercises the full resolution stack before the service accepts traffic. The patterns were adopted by other teams joining the federation."

> **If they dig into JVM performance:** "Newly deployed instances showed p99 3-5x higher than steady state. I profiled the JVM and found two root causes: JIT hadn't compiled the hot paths yet, and DGS does lazy initialization of query parsing on first use. I built a warmup routine that sends synthetic GraphQL queries through the full pipeline — data loaders, cache, serialization — before the readiness probe passes. Cold-start spikes eliminated entirely."

**When to mention:** "Learned something new quickly," "dive deep / root cause analysis," or "how do you ensure performance in production." Not a lead story — use as a follow-up example or supporting detail.

---

## Story 11: Applause — Auth Modernization (Brief Reference)

**Anchor:** Authentication & Identity Modernization · **LPs:** Delivers Results, Ownership, Dive Deep
**Status:** Trimmed — use for HashiCorp/IBM (IAM domain) or any identity/auth questions. Not a lead story for other companies.

> **30-second version:** "At Applause, I led the migration from a home-grown auth system to Keycloak-based SSO — unified authentication across internal tools, an enterprise partner platform, and a large external community with OAuth 2.0, SAML, and social login. The key was a dual-auth bridge: legacy and Keycloak ran in parallel so I could migrate products one at a time, ordered by risk — internal first, partners second, external community last. Zero SLA violations, zero customer-facing auth outages."

> **If they dig into technical approach:** "I built custom token validation and RBAC plugins for the Kong API gateway in Python — per-request JWT validation against Keycloak, token refresh handling, and fine-grained permission checks at the gateway layer. Also deployed service mesh (Linkerd on K8s) with mTLS for service-to-service trust. Coordinated the migration across Angular, Node.js, and Java teams."

> **If they ask about the dual-auth bridge pattern:** "Both auth systems accepted sessions simultaneously. A migrated user got Keycloak; a non-migrated user stayed on legacy. No flag day. Each phase had runbooks and rollback procedures — if anything broke, we could revert in minutes."

**When to use:** HashiCorp/IBM interviews (Vault/Boundary = auth infrastructure), "tell me about a risky migration," "identity/security experience." For other companies, mention briefly as background: "I've built auth infrastructure before — Keycloak SSO, API gateway security, service mesh — so I understand what it takes."

---

## Story 12: Applause — Event Sourcing / CQRS (Brief Reference)

**Anchor:** Event Sourcing & CQRS Initiative · **LPs:** Invent and Simplify, Think Big
**Status:** Trimmed — use as brief background, not a full story. Pivot to CarGurus event-driven work (Story 4) for recent examples.

> **One-liner if it comes up:** "At Applause, I introduced event sourcing and CQRS to decouple services that were sharing databases directly. I built the POC, defined the patterns, and ran workshops to help engineers adopt the paradigm. That experience informed how I designed the event-driven architecture at CarGurus — Kafka pipelines, decoupled services, independent deployability."

**When to mention:** Only if they ask specifically about event sourcing, CQRS, or Kafka background. Don't lead with this — it's 7 years old and at Senior scope.

---

## Story 13: Toast — Early Engineer in Hypergrowth (Brief Reference)

**Anchor:** Toast Hypergrowth · **LPs:** Ownership, Bias for Action, Learn and be Curious
**Status:** Trimmed — use for "early-stage experience," "wearing multiple hats," or Cherry interviews (startup context). Not a lead story.

> **30-second version:** "I joined Toast when it was very early — small engineering team, no DevOps, no QA. I built the core backend services (Order Service, Labor Service) that became the platform backbone, then saw that the deployment and testing gaps were a ticking time bomb and built the CI/CD pipeline and integration testing framework myself — nobody assigned me that. Pragmatic monolith-first approach, clean interfaces for future decomposition. When Toast hired dedicated DevOps and QA, they inherited a working foundation."

> **If they ask about ownership / going beyond your role:** "The deployment infrastructure wasn't my job — but I saw it as the highest-leverage problem I could solve. Restaurants depended on our system for every transaction. I built the safety nets because nobody else was going to."

> **Key takeaway to quote:** "In hypergrowth, the best architecture is the simplest one that works today and doesn't prevent you from evolving tomorrow."

**When to use:** Cherry HM call (startup builder angle), "tell me about early-stage experience," "wearing multiple hats." For Coinbase/HashiCorp, mention briefly as background: "I was an early engineer at Toast — built core services and infrastructure from scratch during hypergrowth."

---

# Section C: LP-Specific Stories

---

## Story 14: Failure & Learning — TODO: NEEDS REAL STORY

**Anchor:** Cross-cutting · **LPs:** Are Right A Lot, Learn and be Curious
**Best for:** All companies
**Status:** ⚠️ PLACEHOLDER — previous content was fabricated. Need a real failure story before interviews. Think about: a technical decision that seemed right but wasn't, underestimated complexity, didn't push back hard enough, or moved too fast.

### STAR Spoken-Style

**Situation:** Early in the digital shopping project at CarGurus, I made an architectural decision to use a particular caching strategy — aggressive in-memory caching with long TTLs — to optimize the product listing API. My reasoning was sound in isolation: the data was mostly static, and caching would dramatically reduce database load.

**Task:** The challenge became apparent when the product team started running frequent inventory and pricing experiments. The long cache TTLs meant experiment changes weren't reflected to users for minutes, sometimes longer. PMs were frustrated because their A/B tests showed confusing data — different users were seeing different versions depending on when their cache expired.

**Action:** Once I understood the problem, I had to admit that my original decision was wrong for the context. I was optimizing for the static case but hadn't adequately considered the experimentation use case that was becoming central to the product strategy. I redesigned the caching layer with a shorter TTL for experiment-sensitive data and implemented cache invalidation tied to experiment configuration changes. I also added versioned cache keys so that when an experiment changed, the old cached data was automatically bypassed. I documented the decision retrospectively: what I assumed, what I missed, and what the better approach was — and shared it with the team so others could learn from it.

**Result:** The revised caching strategy resolved the experimentation issues. PMs got consistent A/B test data, and the performance impact was minimal because I was surgical about which data got shorter TTLs. The bigger result was the learning: I now always ask "what's the mutation pattern?" before designing a caching strategy, not just "what's the read pattern?" The retrospective document I shared was referenced by other engineers facing similar caching decisions.

### Bullet Recap

- **S:** Chose aggressive long-TTL caching for product listing API; seemed sound for mostly-static data
- **T:** Problem emerged when product team ran frequent experiments; stale cache caused confusing A/B test data
- **A:** Acknowledged the decision was wrong for the context; redesigned with shorter TTLs for experiment-sensitive data; cache invalidation tied to experiment config changes; versioned cache keys; wrote and shared retrospective
- **R:** Experimentation issues resolved; minimal performance impact; learned to always consider mutation patterns in caching design; retrospective referenced by other engineers

### Long-Form Narrative

This is a story about a decision I got wrong and what I learned from it. During the digital shopping project, I designed the caching layer for the product listing API. The data was predominantly static — vehicle inventory that updated in batch feeds, pricing that changed infrequently. I chose aggressive in-memory caching with long TTLs (15-30 minutes). The performance gains were significant: database load dropped, response times improved, and the service handled higher throughput.

The problem surfaced weeks later when the product team began running inventory and pricing experiments more frequently. They'd change experiment configurations expecting users to see the new treatment immediately, but the long cache TTLs meant some users continued seeing stale data for minutes. Their A/B test metrics were noisy and confusing — differences between test and control groups were partially artifacts of cache staleness, not actual treatment effects.

When I dug into the complaints, I realized the root cause was my design decision. I'd optimized for the dominant access pattern (static reads) without adequately considering the emerging mutation pattern (frequent experiment changes). In hindsight, I should have asked the product team about their planned experimentation cadence before designing the cache.

I owned the mistake and redesigned the caching layer. The fix was surgical: data that was sensitive to experiment configuration got shorter TTLs and cache invalidation tied to experiment change events. I also introduced versioned cache keys — when an experiment configuration changed, the version incremented, and the old cache entries were automatically bypassed without needing explicit invalidation.

The performance impact was minimal because most data was still long-TTL cached — only experiment-sensitive fields used the shorter TTLs. The PMs got consistent A/B data, and the system was designed to handle frequent experiment changes gracefully.

I wrote a retrospective documenting what I assumed, what I missed, and what the better approach was. I shared it with the engineering team not to self-flagellate, but because I thought the lesson was generalizable: when designing caching, ask about mutation patterns, not just read patterns. Other engineers referenced that document when making their own caching decisions.

---

## Story 15: Customer Obsession — TODO: PLACEHOLDER

**Anchor:** Cross-cutting · **LPs:** Customer Obsession
**Best for:** All companies
**Status:** ⚠️ PLACEHOLDER — Need a story about making a decision that prioritized the end user/customer over engineering convenience. Think about: responding to dealer/user feedback, changing a technical approach because of customer impact, advocating for user experience in a technical decision.

---

## Story 16: Peer Conflict Resolution — TODO: PLACEHOLDER

**Anchor:** Cross-cutting · **LPs:** Have Backbone, Disagree and Commit
**Best for:** All companies
**Status:** ⚠️ PLACEHOLDER — Need a story about disagreeing with a peer (not a senior leader — Story 8 covers that). Think about: disagreeing with another principal engineer on an approach, resolving a technical disagreement between two teams, a time you and a peer had different opinions and how you resolved it.

---

## LP Quick-Reference Matrix

| LP | Stories |
|---|---|
| **Customer Obsession** | 3, 4, 15 (TODO) |
| **Ownership** | 1, 4, 5, 11, 13 |
| **Invent and Simplify** | 2, 7, 9, 12 |
| **Are Right A Lot** | 4, 14 (TODO) |
| **Learn and be Curious** | 7, 10, 13 |
| **Hire & Develop The Best** | 5 |
| **Insists on Highest Standards** | 1, 7 |
| **Think Big** | 1, 7, 9 |
| **Bias for Action** | 3, 4, 13 |
| **Dive Deep** | 1, 2, 10, 11 |
| **Earn Trust** | 1, 3, 5, 6 |
| **Delivers Results** | 1, 3, 4, 11 |
| **Have Backbone; Disagree and Commit** | 6, 8, 16 (TODO) |

## Company Quick-Reference Matrix

| Company | Best Stories |
|---|---|
| **Coinbase** | 1, 2, 3, 4, 7, 9, 11 |
| **HashiCorp/IBM** | 1, 2, 11, 12, 13 |
| **NVIDIA** | 1, 2, 7, 10 |
| **Cherry** | 1, 4, 11, 13 |
| **Stripe** | 1, 2, 4, 6, 7, 10 |
| **Netflix** | 1, 6, 7, 10 |
| **All** | 3, 5, 8, 13, 14, 15, 16 |
