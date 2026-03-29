# Figma — Software Engineer, Distributed Systems (Infrastructure)

> **Full prep doc.** Read before recruiter screen, hiring manager call, and on-site.
> Last updated: March 2026

---

## 1. Company Overview

**What they do:** Collaborative design platform — real-time multiplayer editing for UI/UX design, prototyping, and developer handoff. The "Google Docs of design." Used by virtually every major tech company's design team.

**Mission:** Make design accessible to everyone.

**Scale:** 4M+ paying users, used by teams at Microsoft, Google, Airbnb, Uber, and most of the Fortune 500. Handles millions of concurrent collaborative editing sessions. Real-time multiplayer is the core technical differentiator.

**Recent news worth mentioning:**
- Independence after Adobe acquisition fell through ($20B deal blocked by regulators in 2024)
- Figma AI — generative design features, auto-layout suggestions, design-to-code
- Dev Mode expansion — bridging design-to-development handoff
- Enterprise adoption growth — larger organizations, more complex permission/governance needs
- Significant investment in infrastructure to support real-time collaboration at growing scale
- Slides product launch — expanding beyond design tools

---

## 2. Engineering Culture & Values

- **Small, high-caliber engineering team:** Figma is selective. Every engineer has outsized impact. Think "small team, big problems."
- **Real-time collaboration is the core technical differentiator:** CRDTs, distributed storage, WebSocket infrastructure are foundational, not nice-to-haves.
- **Strong emphasis on developer experience and internal tooling:** Infrastructure engineers build platforms that product engineers consume.
- **Languages:** Rust, C++ (real-time engine), TypeScript (frontend), distributed systems backend. Growing use of Kafka, PostgreSQL, custom storage.
- **High coding bar:** Expect medium-hard algorithmic problems. They value engineers who can write clean, efficient code.
- **Build vs. buy culture:** Figma builds a lot of custom infrastructure when off-the-shelf doesn't meet their latency/consistency requirements.

**What this means for your interview:**
- Expect a strong coding round. Practice LeetCode medium-hard, especially graph/tree problems and concurrency.
- Show you can design systems with **real-time constraints** — sub-100ms latency for collaborative operations.
- Demonstrate you understand the tradeoffs of building custom infrastructure vs. using managed services.
- Show breadth AND depth — small team means you'll touch many areas.

---

## 3. Team Context — Distributed Systems / Infrastructure

- **Backend infrastructure:** Distributed storage, streaming pipelines, data infrastructure, service platform
- **Supporting real-time collaboration at scale:** Every keystroke, drag, and resize must propagate to all collaborators in real-time
- **Core systems:** Kafka-based event pipelines, PostgreSQL (with custom extensions), distributed caching, WebSocket infrastructure
- **Growing challenges:** Enterprise adoption means multi-region, larger files, more concurrent editors, stricter data residency

**Likely technical challenges:**
- Distributed storage that supports real-time concurrent access (CRDT-based or OT-based conflict resolution)
- Streaming pipeline for propagating design changes to all connected clients
- Data pipeline for analytics, search indexing, and ML features (Figma AI needs training data)
- Multi-region deployment for enterprise customers with data residency requirements
- Database scaling — PostgreSQL sharding and read replica management as data volume grows
- File storage and versioning — design files can be large, with deep version history

---

## 4. Why You're a Strong Fit

| Their Need | Your Evidence |
|---|---|
| Distributed service architecture | 12→5 service consolidation, well-defined service boundaries |
| Kafka and event-driven pipelines | Built Kafka-based event-driven pipelines for commerce workflows |
| GraphQL federation and schema design | Netflix DGS subgraph, schema federation, batch data loaders |
| Platform architecture for other teams | Built internal developer platforms, shared services, architecture standards |
| Database and storage systems | PostgreSQL expertise, caching strategies, data-structure-level optimization |
| Cross-org migrations | Led migration across 10+ teams, parity testing for zero regressions |
| Event sourcing / CQRS | Introduced at Applause — directly relevant to real-time systems |

---

## 5. Interview Mindset — B2B Infrastructure Category

**Core philosophy to project:** *"Build custom when the problem demands it, use off-the-shelf when it doesn't. Optimize for developer experience — infrastructure teams exist to make product teams faster."*

**System design framing (say this early):**
> "For a real-time collaborative system, the key constraints are latency (operations must propagate sub-100ms), consistency (all collaborators must converge to the same state), and availability (losing a user's work is unacceptable). I'll design around CRDTs or OT for conflict resolution, with a streaming layer for change propagation."

**Key concepts to weave into every answer:**
- **CRDTs (Conflict-Free Replicated Data Types)** — data structures that merge concurrent operations without coordination. State-based vs. operation-based. Figma uses a custom CRDT for their multiplayer engine.
- **Operational Transformation (OT)** — alternative to CRDTs, used by Google Docs. Transform concurrent operations against each other. Requires a central server.
- **Real-time constraints** — sub-100ms for local operations, sub-500ms for propagation to remote collaborators.
- **Event-driven streaming** — Kafka for durable event log, WebSocket for real-time push to clients.
- **Multi-tenancy** — enterprise customers need isolation, data residency, access controls.
- **Build vs. buy** — know when custom storage beats managed services (e.g., custom CRDT storage vs. using DynamoDB).

**System design topics likely asked:**
- Real-time collaborative editing system (CRDT/OT, conflict resolution, presence)
- Distributed storage system for design files (versioning, large binary objects)
- Search and indexing pipeline for design assets
- Notification/activity feed for design collaboration
- Multi-region deployment with data residency constraints

---

## 6. STAR Stories to Prepare (Ranked by Relevance)

| Priority | # | Story | Why It Fits |
|---|---|---|---|
| **Must tell** | 7 | DGS Subgraph — Federation Migration | Schema design, service consolidation, API evolution |
| **Must tell** | 2 | API Modernization — 5× Latency Reduction | Performance depth, profiling, optimization |
| **Must tell** | 14 | Applause — Event Sourcing / CQRS | Directly relevant to real-time event-driven systems |
| **Strong** | 3 | Parity Testing Framework | Rigorous testing, migration safety |
| **Strong** | 13 | Applause — Auth Modernization | Database migration, minimal downtime |
| **Strong** | 16 | Toast — DevOps & QA from Scratch | Building infrastructure from 0→1, small team impact |
| **Good** | 1 | API Modernization — Cross-Org Migration | Scale, leadership |
| **Good** | 8 | DGS Subgraph — JVM Warmup | Performance engineering depth |
| **Good** | 11 | Mentoring to Principal Level | People development |
| **Wildcard** | 19 | Disagree and Commit | Technical conviction |
| **Wildcard** | 20 | Failure & Learning | Growth mindset |

**Story selection strategy per round:**
- **Behavioral (distributed systems):** Stories 7, 14, 13
- **Behavioral (performance/depth):** Stories 2, 8, 3
- **Behavioral (leadership/people):** Stories 1, 11, 16
- **Coding round follow-up:** Discuss data structure choices, complexity tradeoffs

---

## 7. Questions to Ask Interviewers

### Recruiter Screen
- Which specific infrastructure area would this role focus on — storage, streaming, data pipelines?
- What does the engineering team size look like, and how are infrastructure teams organized?
- What does the interview process look like, and what's the expected timeline?
- Is this a backfill or a new headcount? What's driving the hire?

### Hiring Manager
- What's the distributed storage architecture — custom-built, Postgres-based, or something else?
- How does the team handle real-time data consistency for collaborative editing at the backend level?
- What are the biggest scaling challenges as Figma grows enterprise adoption?
- How does the team think about the tradeoff between building custom infrastructure vs. leveraging managed services?
- What's the most interesting unsolved infrastructure problem on the team right now?
- How do you measure success for this role in the first 6-12 months?

### Team Match / Technical
- What's the development experience like for infrastructure engineers — deployment, testing, local dev?
- How does the team collaborate with the real-time/multiplayer engineering team?
- What does the data pipeline look like for Figma AI training data?
- What's the on-call experience like for infrastructure services?
- What's something you wish you'd known before joining this team?

---

## 8. "Why Figma?" Answer

> "The distributed systems challenges behind real-time collaboration are fascinating — building storage and streaming infrastructure where operations must propagate sub-100ms to all collaborators, with guaranteed convergence and no data loss, is a genuinely hard problem at the intersection of distributed systems and real-time computing. At CarGurus, I consolidated 12 distributed services into 5, built Kafka-based streaming pipelines, and introduced event sourcing patterns — all of which are directly relevant to the infrastructure that powers Figma's multiplayer engine. I also love that Figma's infrastructure team builds custom systems when the problem demands it. The combination of small team, outsized impact, and deeply technical problems is where I do my best work."

---

## 9. Technical Deep-Dive Preparation

### CRDTs — Know the Basics
Figma uses a custom CRDT for their multiplayer engine. You should understand:

- **What:** Data structures that can be modified concurrently without coordination and always converge to the same state
- **State-based (CvRDT):** Merge function combines states. Requires full state transfer. Example: G-Counter (grow-only counter per replica, sum across replicas).
- **Operation-based (CmRDT):** Replicate operations, not state. Requires reliable broadcast. More efficient.
- **Common types:** G-Counter, PN-Counter, G-Set, OR-Set (observed-remove), LWW-Register (last-writer-wins)
- **Figma's approach:** Custom CRDT that represents a tree of design objects. Each object has properties that are LWW-Registers. Tree structure uses a custom ordered list CRDT.
- **Tradeoffs:** CRDTs can grow unboundedly (tombstones for deletions). Need garbage collection. Semantic conflicts aren't resolved (two users move same object to different positions — CRDT resolves it, but the result may not be what either intended).

### Real-Time Architecture Pattern
```
Client A edits → local CRDT apply → send op to server
                                          ↓
                                    Server validates + persists
                                          ↓
                              Broadcast to all other clients via WebSocket
                                          ↓
Client B, C, D receive → local CRDT merge → UI updates
```

### PostgreSQL at Scale
- Sharding strategies: application-level sharding by org/workspace, pg_partitioning
- Read replicas for read-heavy workloads (analytics, search indexing)
- Connection pooling (PgBouncer) for high-concurrency
- Custom extensions for specialized data types or operations

---

## 10. Coding Round Preparation

Figma has a **strong coding bar**. Expect medium-hard problems. Focus areas:

- **Graph/Tree problems** — DFS/BFS, tree traversal (design files are tree structures)
- **Concurrency** — producer-consumer, read-write locks, concurrent data structures
- **Interval/range problems** — overlapping regions, conflict detection
- **String/parsing** — design file formats, CSS-like property parsing
- **System design coding** — implement a simplified version of a system component

Practice tip: Do 2-3 Figma-tagged problems on LeetCode if available. Otherwise focus on tree manipulation, interval merging, and concurrent data structure problems.

---

## 11. Red Flags to Watch For

- If the infrastructure team is siloed from the real-time/multiplayer team (should collaborate closely)
- If the role is primarily maintaining existing systems with no greenfield work
- If the engineering team is growing too fast (diluting the small-team culture)
- If data residency/enterprise features are consuming all infrastructure bandwidth (compliance over innovation)

---

## 12. Pre-Interview Checklist

- [ ] Re-read this doc
- [ ] Re-read resume_figma.html
- [ ] Practice Stories 7, 2, 14 aloud (2 min each)
- [ ] Review system_design_playbook.md: Chat System (real-time patterns), Distributed Message Queue, KV Store
- [ ] Review technical_playbook.md: trees, graphs, concurrency, data structures
- [ ] Brush up on CRDTs (at least understand G-Counter, OR-Set, LWW-Register)
- [ ] Do 3-4 medium-hard LeetCode problems (tree/graph/concurrency focus)
- [ ] Have "Why Figma?" answer ready
- [ ] Prepare 3 questions per interviewer
