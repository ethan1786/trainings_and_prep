# Airbnb — Senior Staff Engineer, Performance

> **Full prep doc.** Read before recruiter screen, hiring manager call, and on-site.
> Last updated: March 2026

---

## 1. Company Overview

**What they do:** Online marketplace for lodging, experiences, and travel. Connects hosts and guests globally. 7M+ active listings in 220+ countries.

**Mission:** "Belong anywhere."

**Scale:** 400M+ guest arrivals since founding, ~$10B annual revenue, hundreds of millions of monthly active users. Every millisecond of latency affects booking conversion.

**Recent news worth mentioning:**
- Strong profitability focus under Brian Chesky's leadership (2022 restructuring paying off)
- Expansion into Experiences and Services (beyond stays)
- Major app redesign — "Rooms," "Experiences," simplified booking flow
- AI-powered features for hosts (smart pricing, automated messaging) and guests (trip planning)
- Investment in internal developer productivity and platform infrastructure
- Continued growth in international markets (Asia-Pacific, Latin America)

---

## 2. Engineering Culture & Values

- **Design-driven company with strong engineering collaboration:** Product, design, and engineering work closely. Engineers have strong product voice, but design sensibility matters.
- **Performance is a business metric:** Latency directly impacts booking conversion. This isn't abstract — there are dashboards showing revenue impact of P99 changes.
- **Significant investment in internal tools:** Developer productivity, build systems, and internal platforms are first-class concerns.
- **Languages:** Java, Kotlin backend; Ruby (legacy); strong GraphQL adoption; React frontend.
- **Experiment-driven:** Heavy A/B testing culture. Features are measured, not just shipped.
- **Cross-functional roles:** Performance team works across many product teams — high influence, high visibility.

**What this means for your interview:**
- Connect performance to business outcomes. "P99 dropped 50ms" isn't enough — say "which improved page engagement by X%."
- Show you can work cross-functionally without authority. The performance team influences, it doesn't own the codebase.
- Demonstrate profiling depth — you should be able to talk about flame graphs, allocation profiling, GC analysis.
- Show experimentation awareness — how do you measure the impact of a performance change?

---

## 3. Team Context — Performance Engineering

- **Cross-cutting platform role** — not embedded in one product team. Works across search, booking, listing pages, checkout.
- **Direct business impact:** Performance → conversion → revenue. The team has quantified this relationship.
- **Core responsibilities:** Page load optimization, API latency reduction, continuous regression detection, performance budgets, JVM tuning.
- **Both backend and client-side:** Backend API latency + frontend rendering + network optimization. The role may lean backend-heavy given your profile.

**Likely technical challenges:**
- Identifying and eliminating latency bottlenecks across a deep microservice call graph
- Building continuous performance regression detection (automated, in CI/CD pipeline)
- JVM tuning for large Java services (GC policy selection, heap sizing, JIT optimization)
- Caching strategy optimization (multi-tier: local → Redis → DB, cache invalidation at scale)
- Performance budgets per service/page — how to enforce without blocking product velocity
- Search/ranking system performance (complex queries with personalization, geo-filtering, availability)

---

## 4. Why You're a Strong Fit

| Their Need | Your Evidence |
|---|---|
| Latency reduction at scale | 5× P99 improvement (250ms → 50ms) on highest-traffic API |
| SLO-based performance management | Introduced per-hop SLO latency budgets across downstream services |
| JVM depth | JVM warmup strategies, JIT profiling, cold-start elimination for DGS subgraph |
| Caching strategy | Two-tier caching (local + Redis), cache invalidation design |
| Cross-org influence | Performance/architecture standards adopted across 10+ teams, 3 departments |
| Profiling-driven optimization | Deep profiling, call graph optimization, batched data fetching |
| Experimentation | A/B testing with 50% traffic split during API migration |

**Your unique differentiator:** You have a **quantified story** of latency reduction that directly moved user engagement metrics — exactly what this team does every day. Most candidates talk about performance abstractly; you have concrete numbers and a cross-org adoption story.

---

## 5. Interview Mindset — B2C Category

**Core philosophy to project:** *"Latency is a business metric. Every millisecond matters because it directly impacts user engagement and booking conversion."*

**System design framing (say this early):**
> "The most important non-functional requirement here is P99 latency. I'll design with a latency budget — allocating time to each service in the call graph — and make sure we degrade gracefully rather than fail when any component is slow."

**Key concepts to weave into every answer:**
- **Latency budgets** — allocate a time budget per service in the call graph. If service A has 200ms total, and calls B (50ms), C (30ms), D (40ms), you have 80ms for orchestration + processing.
- **Tail latency amplification** — at fan-out, P99 of the overall request is dominated by the slowest downstream call. Mitigate with hedged requests, timeouts, and caching.
- **Graceful degradation** — "If the personalization service is slow, serve non-personalized results rather than timing out."
- **Caching tiers** — L1 local (Caffeine/Guava) → L2 distributed (Redis) → L3 DB. Each tier has different latency, consistency, and invalidation characteristics.
- **Profiling methodology** — CPU profiling (flame graphs), allocation profiling (GC pressure), lock contention analysis, async profiler for JVM.
- **Regression detection** — continuous benchmarking in CI/CD, automated alerts on P99 drift.

**System design topics likely asked:**
- Search/listing page with low-latency requirements (geo-search, availability, pricing, personalization)
- Booking system (availability checking, payment, confirmation — with performance constraints)
- Notification system (push, email, SMS at scale)
- Real-time pricing engine (dynamic pricing based on supply/demand)
- CDN and edge optimization for a global audience

---

## 6. STAR Stories to Prepare (Ranked by Relevance)

| Priority | # | Story | Why It Fits |
|---|---|---|---|
| **Must tell** | 2 | API Modernization — 5× Latency Reduction | THE story. Your strongest differentiator. |
| **Must tell** | 1 | API Modernization — Cross-Org Migration | Shows cross-org leadership on performance initiative |
| **Must tell** | 8 | DGS Subgraph — JVM Warmup & Performance | JVM depth, profiling, performance engineering |
| **Strong** | 3 | Parity Testing Framework | Testing rigor, regression prevention |
| **Strong** | 18 | GenAI Engine — Prompt Lab & Experimentation | Experimentation thinking, measuring outcomes |
| **Strong** | 4 | Architectural Standards Adoption | Cross-org standards for performance |
| **Good** | 11 | Mentoring to Principal Level | People development |
| **Good** | 15 | Toast — Early Engineer in Hypergrowth | Scaling systems under rapid growth |
| **Good** | 6 | MCP Server — Stakeholder Management | Cross-functional collaboration |
| **Wildcard** | 19 | Disagree and Commit | Technical pushback |
| **Wildcard** | 20 | Failure & Learning | Growth mindset |

**Story selection strategy per round:**
- **Behavioral (performance depth):** Stories 2, 8, 3
- **Behavioral (leadership/influence):** Stories 1, 4, 11
- **Behavioral (experimentation):** Stories 18, 3
- **System design follow-up:** Stories 2 (latency reduction approach), 8 (JVM optimization)

---

## 7. Questions to Ask Interviewers

### Recruiter Screen
- Is this role embedded in a specific product area, or is it a cross-cutting platform role?
- How does Airbnb measure performance impact on business metrics?
- What does the interview process look like, and what's the expected timeline?
- Is this a backfill or a new headcount? What's driving the hire?

### Hiring Manager
- What's the current performance profile — what are the main latency bottlenecks today?
- How does the performance team prioritize work — top-down business metrics vs. bottom-up profiling discoveries?
- What tools and infrastructure does the team use for continuous performance monitoring and regression detection?
- How much of the performance work is JVM/backend vs. client-side/rendering?
- How does the team handle performance regressions introduced by product feature work? Is there a performance budget system?
- How do you measure success for this role in the first 6-12 months?

### Team Match / Technical
- What's a recent performance win the team shipped, and what was the approach?
- What's the typical call graph depth for a search or listing page? How many services are in the critical path?
- How does the team handle performance regressions introduced by product feature work?
- What does the on-call rotation look like? What causes most performance incidents?
- What's the most frustrating infrastructure or tooling gap on the team right now?

---

## 8. "Why Airbnb?" Answer

> "Performance engineering at Airbnb's scale — where latency directly impacts booking conversion and millions of travelers' experiences — is exactly the kind of high-impact, deeply technical work I'm most passionate about. I led a 5× P99 latency reduction on CarGurus' highest-traffic API through deep profiling, call graph optimization, and SLO-based latency budgets, and the performance improvements directly moved user engagement metrics. That experience of connecting milliseconds to business outcomes is what I want to do at a much larger scale. Airbnb's investment in performance as a first-class engineering discipline — not just a reactive fix when things get slow — is what excites me about this role."

---

## 9. Performance Engineering Deep-Dive Preparation

Expect them to go deep on profiling and optimization techniques. Be ready:

### JVM Performance Arsenal
- **GC tuning:** G1 vs. ZGC vs. Shenandoah. When to use each. How to diagnose GC pressure (GC logs, allocation rate, promotion rate).
- **JIT compilation:** C1 vs. C2 compiler, tiered compilation, warmup effects. Your DGS warmup story is gold here.
- **Flame graphs:** async-profiler for CPU profiling. How to read a flame graph. Identifying hot methods.
- **Allocation profiling:** Finding objects that create GC pressure. Escape analysis, scalar replacement.
- **Thread contention:** Lock profiling, synchronized vs. ReentrantLock, lock-free data structures.

### Caching Strategy Deep-Dive
- **L1 (local):** Caffeine cache. Bounded by JVM heap. Microsecond access. Stale on multi-instance deployments.
- **L2 (distributed):** Redis. ~1ms access. Consistent across instances. Network overhead.
- **Invalidation:** TTL-based (simple, stale-tolerant), event-driven (Kafka/Redis Pub/Sub for immediate invalidation), hybrid.
- **Cache stampede:** Lock-based refresh, probabilistic early expiration, stale-while-revalidate.

### Latency Analysis Framework
- **Waterfall decomposition:** Break request into phases. Network → routing → auth → orchestration → downstream calls → serialization → response.
- **Amdahl's Law applied to latency:** Optimizing a phase that's 5% of total time gives you at most 5% improvement. Focus on the biggest phase first.
- **Fan-out amplification:** P99 of N parallel calls ≈ 1 - (1 - P99_single)^N. At fan-out of 10, even 99th percentile of individual services compounds badly.

---

## 10. Red Flags to Watch For

- If the "Senior Staff" scope is really just hands-on optimization without strategic influence
- If performance work is reactive (firefighting) rather than proactive (budgets, regression detection, standards)
- If the team is small and siloed without cross-org mandate
- If performance improvements are made but not measured for business impact (disconnected from product)

---

## 11. Pre-Interview Checklist

- [ ] Re-read this doc
- [ ] Re-read resume_airbnb.html
- [ ] Practice Stories 2, 1, 8 aloud (2 min each)
- [ ] Practice explaining your latency reduction approach end-to-end (5 min narrative)
- [ ] Review system_design_playbook.md: Rate Limiter, Caching Strategies, Proximity (geo-search)
- [ ] Review technical_playbook.md: JVM internals, concurrency, data structures
- [ ] Brush up on async-profiler, flame graph reading, GC tuning flags
- [ ] Have "Why Airbnb?" answer ready
- [ ] Prepare 3 questions per interviewer
