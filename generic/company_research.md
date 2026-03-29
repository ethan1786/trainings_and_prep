# Company Research Cheat Sheets

> Quick-reference for each target company: what they do, eng culture, recent news, interview tips.
> Use before applications, recruiter calls, and on-sites.

---

## 1. Stripe

**What they do:** Financial infrastructure / payments platform for the internet. APIs for accepting payments, managing subscriptions, handling payouts, fraud detection, and financial operations.

**Eng culture:**
- Engineering-driven company; engineers have significant product influence
- Strong writing culture — design docs, RFCs, and written proposals are the norm
- "Increase the GDP of the internet" is the mission
- Values rigor, craftsmanship, and long-term thinking over speed hacks
- Ruby (legacy) + Java + Go; moving toward more service-oriented architecture

**Team context (Service Platform / Workflow Engine):**
- Builds the orchestration and workflow infrastructure that other Stripe teams use
- Critical path for payment flows, subscription lifecycle, disbursements
- Reliability and correctness are paramount — financial transactions

**Why you're a fit:**
- Orchestration service experience (12→5 consolidation)
- API design standards and cross-org adoption
- Parity testing for safe migrations
- Strong writing/RFC culture match

**Recent news to mention:** Stripe's continued push into financial services beyond payments (Treasury, Issuing, Revenue Recognition). Their scale (~$1T+ in payment volume annually).

**Interview tips:**
- Expect system design focused on reliability, idempotency, distributed transactions
- Behavioral rounds test for cross-team influence and written communication
- "Why Stripe?" → infrastructure that powers the internet economy; building reliable systems at massive scale

---

## 2. Netflix

**What they do:** Streaming entertainment — content creation, delivery, and discovery platform serving 200M+ subscribers globally.

**Eng culture:**
- "Freedom and Responsibility" — high autonomy, high expectations
- Keeper test: "Would I fight to keep this person?"
- All-cash compensation (no equity vesting games)
- Strong Java ecosystem; Netflix OSS (Zuul, Eureka, DGS, Conductor)
- Data-driven culture; heavy investment in experimentation and A/B testing

**Team context (Technical Catalog / Data Platform):**
- Manages metadata about Netflix's content catalog
- Powers content discovery, search, recommendations, and operational workflows
- GraphQL federation is central — Netflix DGS is their own framework
- Cross-platform data consumers (web, mobile, TV, internal tools, ML pipelines)

**Why you're a fit:**
- Netflix DGS subgraph experience (directly relevant)
- GraphQL federation, batch data loaders, schema design
- Cross-org platform architecture
- Java depth, JVM performance optimization

**Recent news to mention:** Netflix's investment in live events (sports, comedy specials), ad-supported tier growth, continued global expansion. Their open-source contributions (DGS, Conductor).

**Interview tips:**
- Expect deep Java/JVM questions and system design at massive scale
- Culture fit is critical — they screen hard for autonomy, judgment, candor
- "Why Netflix?" → building metadata infrastructure that powers discovery for 200M+ users; love the DGS framework and want to contribute at the source

---

## 3. Datadog

**What they do:** Cloud monitoring and observability platform — metrics, traces, logs, security, CI/CD visibility. The "single pane of glass" for infrastructure and application monitoring.

**Eng culture:**
- Strong engineering-first culture; product quality is paramount
- Emphasis on performance, scale, and reliability (they monitor other companies' infrastructure)
- Primarily Go, Python, Java; large-scale data ingestion and query systems
- Rapid product expansion — new products ship frequently
- Hybrid work in Boston and NYC offices

**Team context (Staff SWE):**
- Likely working on core platform: ingestion pipelines, query engines, or storage systems
- Scale is enormous — trillions of data points per day
- Performance engineering is table-stakes

**Why you're a fit:**
- Deep performance engineering (5× latency reduction, SLO budgets)
- Observability mindset (Datadog/Grafana user, structured logging)
- Platform architecture at scale
- Cross-org standards and developer experience focus

**Recent news to mention:** Datadog's expansion into security (SIEM, Cloud Security), LLM observability, CI/CD visibility. IPO success and continued growth.

**Interview tips:**
- Expect system design focused on high-throughput data pipelines, time-series storage
- Performance and scalability will be deeply probed
- "Why Datadog?" → passionate about observability; building the tools that help every other engineer do their job better

---

## 4. Coinbase

**What they do:** Cryptocurrency exchange and financial platform. Buy/sell/store crypto, institutional trading, staking, wallet infrastructure, Base L2 blockchain.

**Eng culture:**
- Mission-driven: "increase economic freedom in the world"
- Remote-first since 2020
- Strong emphasis on security, compliance, and reliability
- Go, Ruby, Kotlin/Java for backend; heavy use of Kafka and PostgreSQL
- Startup speed with financial-grade reliability requirements

**Team context (Financial Hub):**
- Core financial infrastructure: ledger systems, transaction processing, settlement
- Correctness and auditability are critical — financial regulations
- Event-driven architecture for transaction flows

**Why you're a fit:**
- Event-driven architecture experience (Kafka pipelines, CQRS)
- Transaction-grade reliability (99.9% availability)
- Microservice decomposition and safe migrations
- Feature flags and safe experiment retirement

**Recent news to mention:** Coinbase's Base L2 chain, regulatory wins (international expansion), institutional custody growth, potential crypto policy shifts.

**Interview tips:**
- Expect questions about financial system design: ledgers, double-entry, idempotency
- Reliability and correctness will be emphasized over raw performance
- "Why Coinbase?" → building financial infrastructure for the next generation of money; the intersection of distributed systems and financial engineering

---

## 5. Airbnb

**What they do:** Online marketplace for lodging, experiences, and travel. Connects hosts and guests globally.

**Eng culture:**
- Design-driven company with strong engineering collaboration
- "Belong anywhere" mission
- Significant investment in internal tools and developer productivity
- Java, Kotlin, Ruby backend; strong GraphQL adoption
- Performance is a direct lever on booking conversion

**Team context (Performance):**
- Core platform performance: page load, API latency, availability
- Direct impact on business metrics (conversion, engagement)
- Cross-cutting role — works with many product teams

**Why you're a fit:**
- 5× latency reduction on highest-traffic API
- JVM profiling and optimization
- SLO budgeting framework
- Cross-org leadership on performance standards

**Recent news to mention:** Airbnb's profitability focus, expansion into experiences and services, app redesign, AI-powered features for hosts and guests.

**Interview tips:**
- Expect deep performance engineering questions
- System design likely involves booking/search/pricing systems
- "Why Airbnb?" → performance engineering at Airbnb directly impacts millions of travelers; latency is a business metric, not just a technical one

---

## 6. Figma

**What they do:** Collaborative design platform — real-time multiplayer editing for UI/UX design, prototyping, and developer handoff.

**Eng culture:**
- Small, high-caliber engineering team
- Real-time collaboration is the core technical differentiator
- CRDTs, distributed storage, WebSocket/streaming infrastructure
- Rust, C++, TypeScript on the frontend; distributed systems focus on the backend
- Strong emphasis on developer experience and internal tooling

**Team context (Distributed Systems):**
- Backend infrastructure: distributed storage, streaming, data pipelines
- Supporting real-time collaboration at scale
- Kafka, PostgreSQL, custom storage systems

**Why you're a fit:**
- Distributed service consolidation (12→5)
- Kafka and event-driven pipeline experience
- GraphQL federation and schema design
- Platform architecture enabling other teams

**Recent news to mention:** Figma's independence after Adobe deal fell through, AI features (Figma AI), expansion into developer tools (Dev Mode), growth in enterprise adoption.

**Interview tips:**
- Expect system design around real-time systems, distributed storage, CRDTs
- Strong coding bar — expect medium-hard algorithmic problems
- "Why Figma?" → the distributed systems challenges behind real-time collaboration are fascinating; building infrastructure that enables creative tools at scale

---

## 7. Circle

**What they do:** Financial technology company focused on USDC stablecoin and blockchain-based payment/settlement infrastructure.

**Eng culture:**
- Mission-driven: "raise global economic prosperity through the frictionless exchange of value"
- Remote-friendly
- Building regulated financial infrastructure on blockchain rails
- Go, Java/Kotlin backend; blockchain integration layer
- Security and compliance are first-class concerns

**Team context (Distinguished SWE):**
- Company-wide technical direction and platform architecture
- Likely spans multiple teams — expected to influence engineering org broadly
- Building foundational services for USDC infrastructure

**Why you're a fit:**
- 13 years setting technical direction across organizations
- Built internal platforms and standards adopted broadly
- Auth/identity modernization experience (regulated environments)
- Mentoring engineers and raising the engineering bar

**Recent news to mention:** USDC adoption growth, Circle's IPO plans, MiCA regulation compliance in Europe, partnerships with major financial institutions.

**Interview tips:**
- Expect questions about setting technical direction at org scale
- System design likely involves payment/settlement infrastructure
- "Why Circle?" → building the financial rails for the internet; the Distinguished Engineer role to set long-term technical direction is exactly the scope of impact I want

---

## General Interview Prep Reminders

1. **Before each interview:** Re-read the company section + your tailored resume + 5-6 relevant STAR stories
2. **Recruiter screen:** Have "why this company" and "why this role" ready; ask about team, scope, timeline
3. **System design:** Use your system_design_playbook.md; practice talking through designs aloud
4. **Behavioral:** Use lp_story_map.md for instant story recall; practice STAR spoken-style delivery
5. **Coding:** Continue LeetCode practice from leetcode_study_plan.md; focus on patterns from technical_playbook.md
6. **Questions to ask:** Team size, biggest technical challenge right now, how success is measured, on-call expectations, remote collaboration model
