# Netflix — L6 Software Engineer, Technical Catalog (Data Platform)

> **Full prep doc.** Read before recruiter screen, hiring manager call, and on-site.
> Last updated: March 2026

---

## 1. Company Overview

**What they do:** Streaming entertainment — content creation, delivery, and discovery platform serving 200M+ subscribers globally across every device (web, mobile, TV, game consoles).

**Mission:** Entertain the world.

**Scale:** 200M+ subscribers, 190+ countries, thousands of titles, billions of hours streamed monthly. Content catalog metadata powers every surface — from the homepage to search to ML recommendation pipelines.

**Recent news worth mentioning:**
- Investment in live events (NFL games on Christmas, live comedy specials, WWE Raw)
- Ad-supported tier growth and international expansion
- Continued open-source contributions (DGS framework, Conductor, Zuul, Eureka)
- Crackdown on password sharing driving subscriber growth
- Heavy AI/ML investment for content recommendations and personalization

---

## 2. Engineering Culture & Values

- **"Freedom and Responsibility"** — high autonomy, high expectations. You're trusted to make decisions, but expected to own outcomes fully.
- **Keeper test:** "Would I fight to keep this person?" If not, generous severance. This means high performance density.
- **All-cash compensation** — no equity vesting games, no golden handcuffs. They want people who stay because of the work.
- **Candor culture** — direct, honest feedback is expected. Sugarcoating is seen as disrespectful.
- **Data-driven decisions** — heavy A/B testing, experimentation, and metrics-driven development.
- **Strong Java ecosystem** — Netflix OSS (Zuul, Eureka, DGS, Conductor). JVM performance matters deeply.

**What this means for your interview:**
- Show independent judgment. They want to hear "I decided X because..." not "I was told to do X."
- Be direct in your communication. Don't hedge excessively.
- Demonstrate intellectual curiosity — they value engineers who explore beyond their immediate scope.
- Culture fit is heavily weighted. Autonomy + judgment + candor are screened explicitly.

---

## 3. Team Contexts

### 3a. Technical Catalog / Data Platform (L6 — applied directly)

- **Manages metadata** about Netflix's entire content catalog — titles, episodes, seasons, images, localization, relationships, content attributes
- **Powers content discovery** — search, recommendations, browse, "because you watched...", and operational workflows
- **GraphQL federation is central** — Netflix DGS is their own open-source framework, and the catalog is a key subgraph in the federated supergraph
- **Cross-platform consumers** — web, mobile, TV apps, internal tools, ML pipelines, content production systems all consume catalog data
- **Data freshness matters** — when a new title launches, metadata must propagate quickly across all surfaces

**Likely technical challenges:**
- Schema evolution in a federated graph with dozens of consumer teams
- Balancing real-time consumer-facing query performance vs. batch/ML pipeline access patterns
- Data consistency and freshness across a globally distributed catalog
- N+1 query prevention and batch data loading at massive scale
- Handling the long tail of legacy catalog data while evolving the model
- Multi-region serving with low latency for global subscriber base

**Likely system design topics:**
- Catalog metadata service — multi-region, multi-language, schema evolution
- Content ingestion pipeline — new titles propagating across all surfaces
- Search/discovery backend — relevance ranking, low-latency serving

### 3b. Member Experience Core Systems (L5 — referred by connection)

- **Owns the member-facing experience** — browse page, home feed, profiles, session management, client-server data layer
- **Full Stack role** — expects both frontend (likely React/Node) and backend (JVM) fluency
- **Personalization at scale** — the home page is different for every user, assembled in real-time from recommendation models + business rules
- **A/B testing is central** — nearly every user-facing change is experimented on; this team builds and consumes that infrastructure

**Likely technical challenges:**
- Home feed assembly — merging outputs from multiple recommendation models into a coherent page
- Client-server data contract — efficient data fetching for diverse devices (TV, mobile, web)
- Profile and session management across devices
- Performance optimization for low-powered devices (smart TVs, set-top boxes)
- A/B testing infrastructure — experiment assignment, holdout groups, feature flagging

**Likely system design topics:**
- Home page feed system — personalized row assembly, ranking, caching per user
- A/B testing platform — experiment assignment, statistical significance, feature flags
- Profile/session service — cross-device sync, authentication, preferences

### Leveling Strategy

The referred L5 position may be the easier path in the door. If the recruiter reaches out about L5:
- Be upfront: "I'm excited about Member Experience Core Systems. I also applied for the L6 Technical Catalog role — given my experience leading platform-level work at [previous companies], I believe I can contribute at staff scope. Is there flexibility to discuss leveling?"
- Netflix often determines final level after interviews based on performance — getting in at L5 isn't necessarily a ceiling
- But set the L6 expectation early rather than negotiating after an L5 offer
- If both processes move forward, having two active paths gives you leverage

---

## 4. Why You're a Strong Fit

| Their Need | Your Evidence |
|---|---|
| Netflix DGS experience | Built a DGS subgraph at CarGurus — directly relevant, not theoretical |
| GraphQL federation | Schema federation, batch data loaders, N+1 prevention |
| JVM performance | JVM warmup strategies for cold-start elimination, JIT profiling |
| Cross-org platform architecture | Led migrations across 10+ teams, 3 departments |
| Data platform thinking | Consolidated 12 downstream integrations into 5 well-defined services |
| Autonomy & ownership | 0→1 MCP server (sole backend engineer, shipped under ambiguity) |
| Mentoring | Mentored senior engineers to Principal-level scope |

**Your unique differentiator:** You are one of very few external candidates who has **production DGS subgraph experience**. Most Netflix DGS users are internal. This is a significant signal — lean into it hard.

---

## 5. Interview Mindset — B2C Category

**Core philosophy to project:** *"Optimize for user experience at massive scale. Availability > consistency for most things. Degrade gracefully, never fail hard."*

**System design framing (say this early):**
> "The most important thing for this system is availability and latency — the user should never see an error or a slow page. I'll design for eventual consistency where safe, and make sure we degrade gracefully if any component fails."

**Key concepts to weave into every answer:**
- **Latency obsession** — P50, P95, P99. "How would you reduce this?" should be second nature.
- **Availability over consistency** — AP in CAP for read-heavy paths. Eventual consistency is the default. "It's better to show slightly stale metadata than show nothing."
- **Graceful degradation** — "If the recommendation service is down, serve cached/default results, not a 500."
- **A/B testing & experimentation** — feature flags, gradual rollouts, data-driven decisions.
- **Scale thinking** — 200M+ users, global distribution. Your designs should handle this without blinking.
- **GraphQL federation specifics** — query planning, entity resolution, @key directives, batch loading.

**System design topics likely asked:**
- Content metadata platform / catalog service
- GraphQL federation gateway architecture
- Recommendation system (serving layer, not ML)
- Video streaming pipeline (less likely for this team, but possible)
- Search/discovery system with personalization

---

## 6. STAR Stories to Prepare (Ranked by Relevance)

| Priority | # | Story | Why It Fits |
|---|---|---|---|
| **Must tell** | 7 | DGS Subgraph — Federation Migration | Direct DGS experience — your strongest differentiator |
| **Must tell** | 8 | DGS Subgraph — JVM Warmup & Performance | JVM depth, performance engineering |
| **Must tell** | 1 | API Modernization — Cross-Org Migration | Scale, leadership, cross-team coordination |
| **Strong** | 5 | MCP Server — 0→1 Under Ambiguity | Autonomy, independent judgment (culture fit) |
| **Strong** | 4 | Architectural Standards Adoption | Cross-org influence, earning trust |
| **Strong** | 12 | Driving Consensus via RFCs | Decision-making, candor, written communication |
| **Good** | 2 | API Modernization — 5× Latency Reduction | Performance depth |
| **Good** | 17 | GenAI Engine — Hybrid Architecture | Intellectual curiosity, 0→1 thinking |
| **Good** | 11 | Mentoring to Principal Level | People development |
| **Wildcard** | 19 | Disagree and Commit | Candor culture fit — shows healthy pushback |
| **Wildcard** | 20 | Failure & Learning | Self-awareness — critical for Netflix culture |

**Story selection strategy per round:**
- **Behavioral (autonomy/judgment):** Stories 5, 19, 20
- **Behavioral (technical leadership):** Stories 1, 7, 12
- **Behavioral (candor/conflict):** Stories 19, 12
- **Technical deep-dive follow-up:** Stories 7, 8, 2

---

## 7. Questions to Ask Interviewers

### Recruiter Screen
- What does the interview process look like, and what's the expected timeline?
- How does the Technical Catalog team fit within the broader Data Platform org?
- What does the "freedom and responsibility" culture look like concretely for this team?
- Is this a backfill or a new headcount? What's driving the hire?

### Hiring Manager
- What's the current state of GraphQL federation adoption across Netflix? How many subgraphs exist today?
- What are the main consumers of catalog metadata — primarily content discovery, or does it extend to operations and content production?
- How does the team balance serving real-time consumer-facing queries vs. batch/ML pipelines?
- What's the biggest data consistency or freshness challenge in the catalog?
- How do you measure success for this role in the first 6-12 months?
- What does the on-call rotation look like? What's the incident frequency for catalog services?

### Team Match / Technical
- How does the team handle schema evolution in the federated graph — breaking changes, versioning?
- What does the DGS development experience look like internally vs. the open-source version?
- What's the biggest performance bottleneck in catalog serving today?
- How does the team collaborate with the ML/recommendation teams that consume catalog data?
- What's something you wish you'd known before joining this team?

---

## 8. "Why Netflix?" Answer

> "Two things. First, direct technical alignment — I recently built a Netflix DGS subgraph at CarGurus with schema federation, batch data loaders, and JVM warmup strategies. I'm one of the few engineers outside Netflix who has production DGS experience, and I want to contribute at the source. Second, the problem itself — building the metadata platform that powers content discovery for 200M+ subscribers is a deeply compelling data and federation challenge. The intersection of GraphQL federation, cross-platform data serving, and performance at global scale is exactly where I want to be."

---

## 9. Netflix-Specific Interview Advice

### Culture Fit is Make-or-Break
Netflix rejects strong technical candidates who don't fit the culture. Prepare for these explicitly:

- **"Tell me about a time you made a decision with incomplete information."** → Story 5 (MCP Server 0→1)
- **"Tell me about a time you disagreed with your manager or a senior leader."** → Story 19 (Disagree and Commit)
- **"Tell me about a time something you built failed or didn't work out."** → Story 20 (Failure & Learning)
- **"Why should we hire you instead of someone else?"** → Your DGS production experience. No one else has it.

### Keeper Test — What Makes You Hard to Replace
Be ready to articulate this clearly:
- Production DGS + federation experience (rare externally)
- 13 years of Java depth with JVM performance expertise
- Track record of cross-org platform architecture adoption
- 0→1 builder who also scales existing systems

---

## 10. Red Flags to Watch For

- If the "freedom" part means "no support, figure it out yourself" (healthy autonomy ≠ abandonment)
- If the team is purely maintenance on an established platform with no evolution
- If the L6 scope is really L5 work (cross-org influence should be expected at L6)
- If on-call is brutal and normalized as "part of the culture"

---

## 11. Technical Coding Prep — Netflix

Netflix weights system design most heavily, then behavioral, then coding. Coding rounds lean practical. Expect design-oriented problems and streaming/data structure questions.

**Frequently reported:**

| # | Problem | Difficulty | Pattern | Notes |
|---|---------|-----------|---------|-------|
| 146 | LRU Cache | Medium | Design, HashMap + DLL | Content caching — very Netflix |
| 981 | Time Based Key-Value Store | Medium | Design, Binary Search | Versioned data |
| 362 | Design Hit Counter | Medium | Design, Queue | Request rate tracking |
| 295 | Find Median from Data Stream | Hard | Heap | Streaming statistics |
| 239 | Sliding Window Maximum | Hard | Monotonic Deque | Streaming metrics |
| 76 | Minimum Window Substring | Hard | Sliding Window | Classic hard |
| 42 | Trapping Rain Water | Hard | Two Pointers, Stack | Classic hard |
| 56 | Merge Intervals | Medium | Intervals, Sorting | Time range operations |
| 23 | Merge k Sorted Lists | Hard | Heap | k-way merge — log/event streams |
| 347 | Top K Frequent Elements | Medium | Heap, Bucket Sort | Content ranking |
| 297 | Serialize and Deserialize Binary Tree | Hard | Tree, Design | Data encoding |
| 155 | Min Stack | Medium | Stack, Design | Quick design warmup |
| 34 | Find First and Last Position | Medium | Binary Search | Boundary search |
| 99 | Recover Binary Search Tree | Medium | Tree, Inorder | Find swapped nodes |
| 88 | Merge Sorted Array | Easy | Two Pointers | Warmup — merge in-place |

---

## 12. System Design Prep — Netflix

Netflix weighs system design very heavily. Key differences from standard interviews:
- **Team-specific prompts** — questions come from your hiring team, not a generic bank
- **Conversational format** — often no shared drawing tool, primarily verbal discussion
- **Domain expertise > framework fluency** — they want to see you've genuinely built relevant systems

**Prep tips**: read the Netflix Tech Blog extensively. Research your interviewers' backgrounds. Practice designing verbally without a whiteboard. Connect solutions to your real past experience.

**For Technical Catalog (L6):**

| Topic | Key Design Challenges |
|---|---|
| **Content Catalog / Metadata Service** | Multi-region, multi-language metadata, schema evolution, GraphQL federation |
| **Content Ingestion Pipeline** | New title metadata propagating to all surfaces, data freshness guarantees |
| **Search / Discovery Backend** | Relevance ranking, low-latency serving, personalized browse |
| **Federated GraphQL Platform** | Subgraph composition, N+1 prevention, batch data loading, schema registry |
| **Event Logging System** | High-throughput ingestion, schema evolution, exactly-once processing |

**For Member Experience Core Systems (L5):**

| Topic | Key Design Challenges |
|---|---|
| **Home Page Feed System** | Personalized row assembly from multiple recommendation models, per-user caching |
| **A/B Testing Platform** | Experiment assignment, statistical significance, feature flagging, holdout groups |
| **Profile / Session Service** | Cross-device sync, authentication, preferences, multi-profile per account |
| **Client-Server Data Layer** | Efficient data fetching for diverse devices (TV, mobile, web), BFF pattern |
| **Recommendation Serving** | Real-time model inference, fallback strategies, cold-start for new users |

**General Netflix design topics (either role):**

| Topic | Key Design Challenges |
|---|---|
| **Video Streaming CDN** | Adaptive bitrate (ABR), edge caching (Open Connect), multi-region distribution |
| **Video Encoding Pipeline** | Transcoding at scale, format/resolution matrix, cost optimization |
| **Content Delivery Network** | Cache invalidation, geographic routing, failover, capacity planning |

**Netflix-specific concepts to know:**
- **Availability over consistency** (CAP) — Netflix's default trade-off. Always discuss this
- **Chaos engineering** — Chaos Monkey, resilience testing. Discuss failure modes and graceful degradation
- **Microservices at massive scale** — service mesh, circuit breakers, bulkheads
- **Streaming domain**: ABR, HLS/DASH protocols, encoding ladders, Netflix Open Connect CDN

---

## 13. Pre-Interview Checklist

- [ ] Re-read this doc
- [ ] Re-read resume_netflix.html
- [ ] Practice Stories 7, 8, 1, 5 aloud (2 min each)
- [ ] Practice culture fit answers: incomplete info, disagreement, failure
- [ ] Review system_design_playbook.md: Chat System (WebSocket patterns), Distributed Message Queue
- [ ] Review Netflix DGS documentation — be ready to discuss @DgsQuery, DataLoader, federation directives
- [ ] Review technical_playbook.md: JVM internals, concurrency
- [ ] Have "Why Netflix?" answer ready
- [ ] Prepare 3 questions per interviewer
