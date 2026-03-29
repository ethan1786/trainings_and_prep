# STAR Stories — Master Reference

> **Format per story:** STAR Spoken-Style → Bullet Recap → Long-Form Narrative
> **LP Tags** map to Amazon-style Leadership Principles for quick lookup.
> **Company Tags** show which target companies each story is most relevant for.

---

## Quick Index

| # | Story | Anchor Project | LP Tags | Best For |
|---|-------|---------------|---------|----------|
| 1 | API Modernization — Leading the Cross-Org Migration | API Modernization | Ownership, Delivers Results, Think Big | Stripe, Airbnb, Datadog, Circle |
| 2 | API Modernization — 5× Latency Reduction | API Modernization | Insists on Highest Standards, Dive Deep | Airbnb, Datadog, Figma |
| 3 | API Modernization — Parity Testing Framework | API Modernization | Invent and Simplify, Dive Deep | Stripe, Datadog, Figma |
| 4 | API Modernization — Architectural Standards Adoption | API Modernization | Think Big, Earn Trust | Stripe, Circle, Netflix |
| 5 | MCP Server — 0→1 Under Ambiguity | MCP Server | Bias for Action, Invent and Simplify, Customer Obsession | Stripe, Netflix, Circle |
| 6 | MCP Server — Stakeholder Management | MCP Server | Earn Trust, Customer Obsession, Delivers Results | All |
| 7 | DGS Subgraph — GraphQL Federation Migration | DGS Subgraph | Ownership, Learn and be Curious | Netflix, Figma, Stripe |
| 8 | DGS Subgraph — JVM Warmup & Performance | DGS Subgraph | Dive Deep, Insists on Highest Standards | Airbnb, Datadog, Netflix |
| 9 | Digital Shopping — 0→1 Product Under Pressure | Digital Shopping | Bias for Action, Delivers Results, Customer Obsession | Coinbase, Stripe |
| 10 | Digital Shopping — Safe Experiment Retirement | Digital Shopping | Ownership, Are Right A Lot | Coinbase, Stripe, Circle |
| 11 | Cross-Org Leadership — Mentoring to Staff Level | Leadership | Hire & Develop The Best, Earn Trust | All |
| 12 | Cross-Org Leadership — Driving Consensus via RFCs | Leadership | Disagree and Commit, Earn Trust | Circle, Stripe, Netflix |
| 13 | Applause — Auth Modernization with Minimal Downtime | Applause Auth | Delivers Results, Ownership, Dive Deep | Coinbase, Figma |
| 14 | Applause — Event Sourcing / CQRS Initiative | Applause CQRS | Invent and Simplify, Think Big | Stripe, Figma, Coinbase |
| 15 | Toast — Early Engineer in Hypergrowth | Toast | Ownership, Bias for Action, Learn and be Curious | All |
| 16 | Toast — Building DevOps & QA from Scratch | Toast | Invent and Simplify, Ownership | Datadog, Figma, Circle |
| 17 | GenAI Engine — Hybrid Rules + LLM Architecture | GenAI (Independent) | Invent and Simplify, Think Big, Learn and be Curious | Netflix, Stripe, Coinbase |
| 18 | GenAI Engine — Prompt Lab & Experimentation | GenAI (Independent) | Learn and be Curious, Insists on Highest Standards | Datadog, Airbnb |
| 19 | Disagree and Commit — Pushing Back on Architecture | Cross-cutting | Have Backbone, Disagree and Commit | All |
| 20 | Failure & Learning — A Decision That Didn't Work Out | Cross-cutting | Are Right A Lot, Learn and be Curious | All |

---

## Story 1: API Modernization — Leading the Cross-Org Migration

**Anchor:** High-Traffic Legacy API Modernization · **LPs:** Ownership, Delivers Results, Think Big
**Best for:** Stripe, Airbnb, Datadog, Circle

### STAR Spoken-Style

**Situation:** CarGurus' most-visited page — the vehicle listing page — was powered by a monolithic API handling about 8,000 requests per minute with millions of daily impressions. The codebase had years of accumulated domain logic spread across roughly 12 downstream integrations. It was slow, fragile, and very hard to deploy safely. P99 latency was around 250 ms, availability was about 99%, and deploys took about an hour because of the blast radius.

**Task:** I was asked to lead the modernization of this API. It wasn't just a rewrite — it touched almost every team's data. I needed to coordinate with about 10 teams across 3 departments, lead a small group of 3 principal and senior engineers, and deliver something that could safely take over production traffic without regressions.

**Action:** I started by producing the initial architecture proposal in about two weeks. The key insight was introducing an orchestration service and a GraphQL boundary that consolidated those 12 downstream integrations into 5 well-defined services. This reduced fan-out and simplified failure modes dramatically. I ran architecture reviews across all affected teams to build consensus, then we shipped the first production milestone in 6 months. We ran the new implementation in A/B testing handling 50% of traffic side-by-side with the legacy stack.

**Result:** We completed the modernization ahead of schedule. P99 went from 250 ms to about 50 ms — a 5× improvement. Availability improved from 99% to 99.999%. Deploy time dropped from an hour to about 3 minutes — 20× faster. The patterns we established became the architectural standard for new services across the org.

### Bullet Recap

- **S:** Monolithic API powering highest-traffic page, 8k rpm, 250ms p99, ~99% availability, 1hr deploys
- **T:** Lead full modernization; coordinate 10 teams / 3 depts; deliver without regressions
- **A:** Produced architecture in 2 weeks; orchestration service + GraphQL boundary; 12→5 service consolidation; A/B tested at 50% traffic; built parity testing framework
- **R:** p99 250ms→50ms (5×), availability 99%→99.999%, deploy 1hr→3min (20×), completed ahead of schedule, patterns adopted org-wide

### Long-Form Narrative

The vehicle listing page is CarGurus' bread and butter — millions of consumers visit it daily, and the API behind it handled roughly 8,000 requests per minute. Over the years, the implementation had become a monolith with tendrils reaching into a dozen downstream services, each with its own quirks and hidden domain logic. Latency was hovering around 250 ms at the 99th percentile, and availability was around 99% — which sounds fine until you consider the volume. Deploys were nerve-wracking hour-long affairs because a bug in any part of the stack could cascade.

I was tapped to lead the modernization. My first move was to map the entire dependency graph and identify the real boundaries. Within about two weeks, I had an architecture proposal centered on a new orchestration service that would sit behind a GraphQL boundary, consolidating 12 downstream integrations into 5 clearly defined services with explicit contracts. I presented this to all affected teams — roughly 10 teams across engineering, data, and product — and iterated on the design based on their feedback.

I led a core team of 3 principal and senior engineers. We shipped the first production milestone in 6 months and set up an A/B test where the new implementation handled 50% of live traffic. I also built a parity-testing framework that validated the full response payload and data integrity against the legacy stack, which gave us high confidence during rollout.

The results spoke for themselves: p99 latency dropped to about 50 ms, availability climbed to 99.999%, and deploy time went from an hour to about 3 minutes. We completed the project ahead of the original timeline. Perhaps more importantly, the architectural patterns we established — the orchestration layer, the service boundaries, the testing approach — became the standard for new microservices across the organization.

---

## Story 2: API Modernization — 5× Latency Reduction

**Anchor:** High-Traffic Legacy API Modernization · **LPs:** Insists on Highest Standards, Dive Deep
**Best for:** Airbnb, Datadog, Figma

### STAR Spoken-Style

**Situation:** During the API modernization at CarGurus, we had consolidated the architecture, but I wasn't satisfied with the performance profile. The legacy system had a p99 of around 250 ms, and while the new architecture was cleaner, I wanted to push much further.

**Task:** My goal was to achieve a step-function improvement in latency, not just incremental — I wanted the new stack to be demonstrably faster in a way that moved key business metrics.

**Action:** I dove deep into profiling — tracing every downstream call, analyzing serialization overhead, caching behavior, and connection pooling. I found that the old system was making redundant fan-out calls and wasn't efficiently batching data fetches. In the new orchestration layer, I designed the call graph to minimize sequential hops, batch where possible, and aggressively cache stable data. I also worked with teams to set SLOs on each downstream service so we had a latency budget per hop.

**Result:** The new stack achieved a p99 of about 50 ms — a 5× improvement. This wasn't just a vanity metric; the reduced latency directly improved user engagement metrics on the listing page. The SLO framework we introduced became the model for how other teams think about latency budgets.

### Bullet Recap

- **S:** Legacy API p99 ~250ms; new architecture cleaner but performance not yet optimized
- **T:** Achieve step-function latency improvement, not incremental
- **A:** Deep profiling of call graph; eliminated redundant fan-out; batched data fetches; aggressive caching of stable data; introduced per-hop SLO latency budgets
- **R:** p99 250ms→50ms (5×); improved user engagement; SLO framework adopted across teams

### Long-Form Narrative

After we'd designed the new service architecture, I turned my attention to performance. The legacy system ran at about 250 ms p99, and while the new topology was much cleaner, I wasn't going to settle for "a bit faster." I set an internal goal of getting under 100 ms p99 and saw the potential to go further.

I spent time profiling every layer. The old system made redundant calls to the same downstream services from different code paths, had no batching, and had poor cache utilization because cache keys were too granular. In the new orchestration service, I redesigned the call graph to minimize sequential hops — if two downstream calls don't depend on each other, they run in parallel. I introduced batched data fetching where the graph allowed it, and implemented a two-tier caching strategy: a fast in-memory cache for data that changes rarely (like dealer metadata) and a shorter-TTL distributed cache for semi-dynamic data.

I also introduced a latency budget framework — each downstream service got an SLO for its contribution to the total request, and we monitored it in Datadog dashboards. This made it immediately visible when any single service regressed.

The end result was about 50 ms p99 — a 5× improvement. Beyond the raw numbers, this translated to measurable improvements in user engagement on the listing page. The SLO budgeting approach became a model that other teams adopted.

---

## Story 3: API Modernization — Parity Testing Framework

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

## Story 4: API Modernization — Architectural Standards Adoption

**Anchor:** High-Traffic Legacy API Modernization · **LPs:** Think Big, Earn Trust
**Best for:** Stripe, Circle, Netflix

### STAR Spoken-Style

**Situation:** During the API modernization at CarGurus, I realized the patterns we were establishing — service boundaries, orchestration layers, GraphQL contracts, testing strategies — were solving problems that every team in the org was going to face.

**Task:** I wanted to make sure these patterns didn't just live in our codebase. I wanted them to become the organizational standard so that future services would be built consistently and we wouldn't have to keep solving the same problems.

**Action:** I documented the patterns in formal design docs and RFCs, covering service decomposition guidelines, API contract standards, caching strategy, and the parity-testing approach. I presented these at architecture reviews and engineering all-hands. Importantly, I didn't just dictate — I incorporated feedback from other teams' tech leads, which built buy-in. I also paired with engineers from other teams when they started new services, helping them apply the patterns to their specific contexts.

**Result:** The patterns were adopted across multiple teams and departments. New microservices consistently followed the same architecture template, which reduced onboarding time for engineers moving between teams and made our system more predictable. Several team leads told me these standards saved them weeks of design work on their own projects.

### Bullet Recap

- **S:** API modernization patterns solving problems applicable across the whole org
- **T:** Codify patterns into organizational standards; drive adoption beyond own team
- **A:** Wrote RFCs and design docs; presented at architecture reviews and all-hands; incorporated cross-team feedback; paired with other teams on new service launches
- **R:** Patterns adopted org-wide; reduced onboarding friction; saved other teams weeks of design work; consistent architecture across new services

### Long-Form Narrative

One of the things I'm most proud of from the API modernization is what happened after the project itself. During the work, we established clear patterns: how to decompose a monolith into bounded services, how to set up orchestration layers, how to define GraphQL contracts between services, how to use caching effectively, and how to validate correctness during migration.

I recognized these weren't just useful for our project — they were general solutions. So I invested time in writing them up as formal design docs and RFCs. I covered service decomposition principles, contract-first API design, a tiered caching playbook, and a migration testing playbook based on our parity framework.

I presented these at architecture review boards and at engineering all-hands sessions. The key to adoption wasn't just writing good docs — it was incorporating feedback. I invited other team leads to critique the proposals, and I adjusted based on their input. This turned the standards from "the listing team's way of doing things" into "our org's way of doing things."

I also went beyond documentation and actively paired with engineers from other teams when they started building new services. Helping them apply the patterns to their specific domains cemented the adoption. Multiple team leads later told me these standards saved them weeks of upfront design work on their own projects.

---

## Story 5: MCP Server — 0→1 Under Ambiguity

**Anchor:** ChatGPT Apps SDK MCP Server · **LPs:** Bias for Action, Invent and Simplify, Customer Obsession
**Best for:** Stripe, Netflix, Circle

### STAR Spoken-Style

**Situation:** CarGurus wanted to integrate with ChatGPT through the OpenAI Apps SDK as a high-visibility proof-of-concept. The idea was to expose CarGurus' core capabilities — vehicle search, pricing, delivery estimates — into ChatGPT so users could interact with our data through conversational AI. But there was no existing framework for this internally, the Apps SDK was new, and requirements were evolving daily.

**Task:** I was the sole backend engineer on this. I needed to design and implement an MCP server from scratch, compatible with the OpenAI Apps SDK, while navigating rapidly changing requirements and unblocking stakeholders who needed demos on tight timelines.

**Action:** I took a bias-for-action approach. Rather than waiting for a complete spec, I built a flexible MCP server architecture that could expose different CarGurus capabilities as tools. I designed it to be incrementally extensible — each new capability could be added without touching the core protocol layer. I delivered a working demo within the first sprint that PMs and directors could show to leadership. As requirements evolved, I iterated quickly, keeping the system safe for an eventual production rollout by designing clear boundaries between the demo path and the production path.

**Result:** The POC was a success — it unblocked demos for PMs and directors and generated significant excitement. The architecture I designed was flexible enough to absorb several rounds of requirement changes without rework. The system is designed for incremental production rollout alongside existing APIs. This project also informed how we thought about the new AI chatbot/shopping assistant platform that the DGS subgraph later supported.

### Bullet Recap

- **S:** ChatGPT integration via OpenAI Apps SDK; no internal framework; requirements evolving daily; high executive visibility
- **T:** Sole backend engineer; design + implement MCP server from scratch; unblock stakeholder demos
- **A:** Built flexible, extensible MCP architecture; delivered working demo in first sprint; iterated rapidly on changing requirements; designed clean demo/production boundary for safe rollout
- **R:** POC successful; unblocked PM/director demos; absorbed multiple requirement changes without rework; architecture designed for production rollout; informed AI platform strategy

### Long-Form Narrative

When CarGurus decided to explore a ChatGPT integration, it was a greenfield initiative with high executive visibility but very little definition. The OpenAI Apps SDK was relatively new, and nobody internally had experience building an MCP server. Requirements were coming from PMs, directors, and the AI team simultaneously, and they shifted frequently.

I was assigned as the sole backend engineer. My first challenge was deciding how much to wait for clarity versus how much to build now. I chose action. I studied the MCP protocol and Apps SDK deeply in the first few days, then designed a server architecture that was deliberately modular: a core protocol handler that spoke MCP, with a plugin-style system where each CarGurus capability (vehicle search, pricing, delivery estimates) was a separate tool that could be registered independently.

Within the first sprint, I had a working demo that PMs could use in stakeholder presentations. This was critical — there was real pressure to show progress quickly. As requirements evolved (new capabilities to expose, different response formats, safety considerations for production), the modular architecture absorbed the changes cleanly. I didn't have to rewrite the core; I just added or adjusted tools.

I was also careful about the long-term path. I designed a clear separation between the demo configuration and what a production deployment would look like — different authentication, rate limiting, and monitoring. This meant the code wasn't throwaway; it was a genuine foundation.

The POC generated significant excitement and directly informed the company's broader AI strategy, including the chatbot/shopping assistant platform that I later built the DGS subgraph to support.

---

## Story 6: MCP Server — Stakeholder Management

**Anchor:** ChatGPT Apps SDK MCP Server · **LPs:** Earn Trust, Customer Obsession, Delivers Results
**Best for:** All companies

### STAR Spoken-Style

**Situation:** The MCP server project had multiple stakeholders pulling in different directions. PMs wanted flashy demos for leadership. The AI team wanted a robust foundation for the chatbot platform. Directors wanted to see production readiness. And requirements kept changing — sometimes weekly — because the OpenAI Apps SDK was itself evolving.

**Task:** As the sole backend engineer, I needed to manage these competing priorities, keep everyone aligned, and deliver something that satisfied both the short-term demo needs and the long-term platform vision.

**Action:** I set up a lightweight but consistent communication cadence. I gave PMs early access to working demos so they could shape their narratives. With the AI team, I held weekly syncs to align on the tool interface contracts. For directors, I maintained a clear roadmap showing what was demo-ready vs. production-ready and what the gap was. When requirements changed, I didn't push back blindly — I assessed the impact, proposed alternatives when the ask was too expensive, and committed when it was feasible. I was transparent about tradeoffs: "We can add this capability for the demo, but it won't be production-safe until we add rate limiting and auth."

**Result:** Every stakeholder group felt heard and got what they needed. PMs got their demos on time. The AI team got a clean interface they could build on. Directors had confidence in the production path. The project was cited internally as an example of how to run a cross-functional POC well. No requirement change caused a fire drill because I'd built trust through transparency.

### Bullet Recap

- **S:** Multiple stakeholders (PMs, AI team, directors) with competing priorities; rapidly evolving requirements
- **T:** Sole engineer balancing demo needs, platform foundation, and production readiness
- **A:** Lightweight communication cadence; early demo access for PMs; weekly AI team syncs; clear demo-vs-production roadmap for directors; transparent tradeoff communication; proposed alternatives when asks were too expensive
- **R:** All stakeholder groups satisfied; demos delivered on time; AI team got clean interface; directors confident in production path; project cited as model for cross-functional POCs

### Long-Form Narrative

The MCP server project was technically interesting, but the harder challenge was managing the human side. I had three distinct stakeholder groups, each with legitimate but sometimes conflicting priorities.

PMs needed flashy demos — they were presenting to leadership and wanted to show CarGurus data flowing through ChatGPT. The AI team cared about the long-term foundation — they were building a chatbot platform and needed clean, stable tool interfaces. Directors wanted to know when this could be in production and what the risks were.

I handled this by being proactive and transparent. I gave PMs early access to working demos — not polished, but functional — so they could start building their presentations. This bought me goodwill and time. With the AI team, I set up weekly syncs focused on the tool interface contracts, so they could start building their side in parallel. For directors, I maintained a simple roadmap document that clearly separated demo-ready capabilities from production-ready ones, with explicit notes on what was needed to close the gap (auth, rate limiting, monitoring).

The hardest moments were when requirements changed. The OpenAI Apps SDK itself was evolving, and sometimes a PM would come with a new demo idea that would require significant rework. Instead of saying "no," I'd assess the impact honestly: "We can do this in two days for the demo, but it won't be production-safe. Here's the alternative that gets you 80% of the demo value and is also on the production path." This approach — transparent tradeoffs, not binary yes/no — built trust with everyone.

The project was later cited internally as an example of how to run a cross-functional POC effectively. I think the key was that nobody was ever surprised — I communicated early and honestly.

---

## Story 7: DGS Subgraph — GraphQL Federation Migration

**Anchor:** Netflix DGS Subgraph · **LPs:** Ownership, Learn and be Curious
**Best for:** Netflix, Figma, Stripe

### STAR Spoken-Style

**Situation:** The Delivery Lookup service at CarGurus — which I primarily own — provides vehicle delivery cost estimates based on geographic locations. It was being consumed by only 2 clients via RESTful APIs. But the company was launching a new AI chatbot and shopping assistant platform, and we were also building a federated GraphQL gateway to simplify cross-platform data access. The Delivery Lookup service needed to be exposed through this new graph.

**Task:** I needed to design and integrate a Netflix DGS subgraph for the Delivery Lookup service, making it a first-class citizen in the federated GraphQL gateway. This would expose the data to frontend, backend, and AI consumers from a single graph endpoint.

**Action:** I dove into the Netflix DGS framework — I hadn't worked with it before, so I spent time studying the federation spec, DGS documentation, and best practices for subgraph design. I designed the schema to be federation-friendly, with proper entity definitions and `@key` directives. I implemented batch data loaders to prevent N+1 query issues — critical because the gateway would be resolving delivery costs for multiple vehicles in a single request. I also identified a cold-start risk: since this was a JVM-based service, the first requests after deployment would hit JIT compilation latency. I implemented a warmup strategy that pre-exercised critical code paths before the service accepted live traffic. I built load tests to validate performance and staging GraphQL integration tests to verify the subgraph worked correctly within the federated graph.

**Result:** The subgraph is integrated and tested. The migration from legacy REST endpoints is in progress, with the new AI chatbot/shopping assistant as the primary new consumer. The batch data loader approach eliminated N+1 concerns, and the warmup strategy prevented latency spikes on deployment. The patterns I established are being used as a reference for other teams integrating their services into the federated graph.

### Bullet Recap

- **S:** Delivery Lookup service served 2 REST consumers; company launching AI chatbot + federated GraphQL gateway
- **T:** Design and integrate Netflix DGS subgraph into federated gateway for cross-platform data access
- **A:** Learned DGS framework; designed federation-friendly schema; batch data loaders (N+1 prevention); JVM warmup strategy for cold starts; load tests + staging GraphQL integration tests
- **R:** Subgraph integrated and tested; migration in progress; N+1 eliminated; no cold-start latency spikes; patterns used as reference for other teams' subgraphs

### Long-Form Narrative

The Delivery Lookup service is one I primarily own at CarGurus. It's a relatively focused service — it takes geographic locations and returns vehicle delivery cost estimates. Most of the data is cached and it serves on main pages, but historically it only had 2 consumers via REST endpoints.

Two things changed: the company started building an AI chatbot/shopping assistant, and we were standing up a federated GraphQL gateway to simplify how different platforms (web, mobile, backend services, AI) access data. My service needed to join this federation.

I chose Netflix DGS as the framework because it's the company's standard for Java-based GraphQL services. I hadn't used DGS before, so I invested time learning the federation spec and DGS-specific patterns. The schema design was important — I needed to define proper entities with `@key` directives so the gateway could resolve delivery costs alongside vehicle data from other subgraphs in a single query.

The biggest technical challenges were batching and cold starts. For batching, I implemented DGS batch data loaders. When the gateway resolves a list of vehicles, each needing a delivery cost, the naive approach would fire N individual requests. The batch loader collects them and makes a single batched call. For cold starts, since this is a JVM service, the first requests after deployment would hit JIT compilation overhead. I built a warmup routine that exercises the critical code paths with synthetic requests before the service registers itself as healthy in the load balancer.

I wrote load tests to validate throughput and latency under realistic traffic patterns, and staging integration tests that verify the subgraph resolves correctly within the full federated graph. The patterns I established — schema design, batch loading, warmup strategy — are now being used as a reference by other teams integrating their services into the federation.

---

## Story 8: DGS Subgraph — JVM Warmup & Performance

**Anchor:** Netflix DGS Subgraph · **LPs:** Dive Deep, Insists on Highest Standards
**Best for:** Airbnb, Datadog, Netflix

### STAR Spoken-Style

**Situation:** When I was integrating the Delivery Lookup service as a Netflix DGS subgraph, I noticed that newly deployed instances showed significant latency spikes on the first few hundred requests. In a federated GraphQL gateway, one slow subgraph can bottleneck the entire query resolution.

**Task:** I needed to understand the root cause of the cold-start latency and eliminate it before the service went into the federated graph, where it would serve high-traffic pages and the AI chatbot.

**Action:** I profiled the JVM during startup and identified two causes: JIT compilation hadn't optimized the hot paths yet, and the DGS framework itself has initialization overhead on first query parsing. I designed a warmup strategy with two components. First, I added a startup routine that sends synthetic GraphQL queries through the full resolution stack — not just pinging health endpoints, but exercising the actual data loaders, caching layers, and serialization. Second, I configured the service's readiness probe so it wouldn't receive production traffic until warmup completed. I validated this with load tests, comparing cold-start vs. warmed instances.

**Result:** The warmup eliminated cold-start latency spikes entirely. Newly deployed instances served their first production requests at the same latency as steady-state instances. This was critical for the federated gateway — it meant deployments wouldn't cause latency regressions visible to end users. The warmup pattern was adopted by other JVM-based services in the federation.

### Bullet Recap

- **S:** Newly deployed JVM instances showed latency spikes; slow subgraph would bottleneck entire federated graph
- **T:** Eliminate cold-start latency before production federation rollout
- **A:** Profiled JVM startup; identified JIT + DGS initialization overhead; built warmup routine exercising full resolution stack with synthetic queries; gated readiness probe on warmup completion; validated with load tests
- **R:** Cold-start spikes eliminated; first production requests at steady-state latency; no deployment-time regressions; warmup pattern adopted by other JVM services

### Long-Form Narrative

Performance work often involves finding the non-obvious bottleneck. When I deployed the DGS subgraph to staging and ran initial load tests, the first few hundred requests showed p99 latency 3-5× higher than steady state. After that, latency settled down. Classic JVM cold-start behavior, but in a federated GraphQL gateway, this matters a lot — the gateway resolves multiple subgraphs in parallel, and the slowest one determines the user-visible latency.

I profiled the JVM during the startup window. Two factors stood out: the JIT compiler hadn't yet optimized the hot code paths (GraphQL resolution, data loader invocation, JSON serialization), and the DGS framework itself does lazy initialization of query parsing structures on first use.

My fix was a warmup routine that runs during startup, before the service marks itself as ready. It sends a representative set of synthetic GraphQL queries through the full resolution pipeline — not just a /health ping, but queries that exercise the batch data loaders, hit the cache layer, serialize real response structures. This forces the JIT to compile the hot paths and DGS to initialize its structures.

I gated the Kubernetes readiness probe on warmup completion, so the load balancer wouldn't route traffic to the instance until it was fully warmed. Load tests confirmed: warmed instances served their first real request at the same latency as instances that had been running for hours.

This pattern was adopted by other teams bringing JVM services into the federated graph. It's a small thing, but it's the kind of detail that separates a service that "works" from one that works well in production.

---

## Story 9: Digital Shopping — 0→1 Product Under Pressure

**Anchor:** Digital Shopping & Online Leads Products · **LPs:** Bias for Action, Delivers Results, Customer Obsession
**Best for:** Coinbase, Stripe

### STAR Spoken-Style

**Situation:** When the pandemic hit in 2020, the automotive industry shifted overnight. Consumers couldn't visit dealerships, and CarGurus needed a way to capture online leads and enable digital shopping experiences. There was enormous business pressure to launch something quickly — the market was moving and competitors were racing to fill the gap.

**Task:** I was tasked with leading the backend design and implementation for a new digital shopping product from scratch. It needed to handle inventory, merchandising, and lead flows, and it needed to be production-ready fast.

**Action:** I chose a microservice and event-driven architecture because it let us build and deploy components independently — we didn't have to wait for a monolithic release. I designed the core services for inventory sync, lead capture, and merchandising, with Kafka-based event pipelines connecting them. This decoupling meant different sub-teams could work in parallel. I focused on getting the critical path — lead capture — to production first, then iterating on the merchandising and inventory features. I made pragmatic tradeoffs: we launched with eventual consistency where strong consistency wasn't strictly needed, which let us move faster.

**Result:** We launched the digital shopping product within the target timeline, capturing a meaningful volume of online leads during a period when the company's traditional business model was under stress. The event-driven architecture proved its value when we later iterated on the product — we could swap out components without affecting the rest of the pipeline.

### Bullet Recap

- **S:** Pandemic forced automotive industry online overnight; competitors racing to fill gap; enormous business pressure
- **T:** Lead backend for 0→1 digital shopping product; handle inventory, merchandising, leads; ship fast
- **A:** Chose microservice + event-driven architecture; Kafka pipelines for decoupling; parallel team development; shipped critical path (lead capture) first; pragmatic tradeoffs (eventual consistency where safe)
- **R:** Launched on timeline; captured meaningful online leads during business disruption; architecture enabled fast iteration; components swappable independently

### Long-Form Narrative

The pandemic created an existential shift for CarGurus. The company's business model assumed consumers would visit dealerships, but suddenly nobody could. We needed a digital shopping experience — a way for consumers to browse, compare, and express purchase intent entirely online. And we needed it fast, because every week mattered.

I led the backend design from scratch. The first decision was architectural: microservices with event-driven communication via Kafka. This wasn't just a technical preference — it was a strategic choice. By decoupling inventory sync, lead capture, and merchandising into separate services connected by event streams, different sub-teams could develop and deploy independently. We didn't have to coordinate monolithic releases.

I prioritized ruthlessly. Lead capture was the critical business path — getting consumer intent to dealers — so that went to production first. Merchandising and inventory features followed in subsequent sprints. I made pragmatic tradeoffs: for example, inventory data could be eventually consistent (it was already slightly stale from dealer feeds), which simplified the architecture and let us move faster. But lead data needed to be reliable, so that pipeline had stronger delivery guarantees.

We launched within the target timeline. The product captured a meaningful volume of leads during a period when the company's core business was under significant pressure. But the real payoff of the architecture came later: when we iterated on the product (adding features, changing flows, eventually retiring parts of it), the event-driven design meant we could modify or replace individual components without disturbing the rest.

---

## Story 10: Digital Shopping — Safe Experiment Retirement

**Anchor:** Digital Shopping & Online Leads Products · **LPs:** Ownership, Are Right A Lot
**Best for:** Coinbase, Stripe, Circle

### STAR Spoken-Style

**Situation:** After launching the digital shopping product, the company ran several additional digital commerce experiments — new lead flows, different merchandising approaches, pricing experiments. Some succeeded and some didn't. Over time, we had several products in various states of use, and the codebase was accumulating complexity from these experiments.

**Task:** I needed to ensure that we could safely retire experiments that weren't working without destabilizing the core systems they were connected to. This sounds straightforward, but each experiment had integrations, data pipelines, and sometimes dealer-facing configurations that couldn't just be turned off.

**Action:** I designed a retirement playbook. For each experiment, I mapped all integration points — API consumers, event pipelines, database tables, config flags, and dealer-facing settings. I built feature flags and circuit breakers around experimental features from the start, which made retirement much easier than ripping out embedded code. When retiring an experiment, I followed a phased approach: first disable new traffic, then drain existing pipelines, then clean up data and configs, then remove code. I documented each retirement so the team had a repeatable process.

**Result:** We successfully retired multiple experiments without a single customer-facing incident. The retirement playbook became a standard process used by other teams. More importantly, the upfront investment in feature flags and clean boundaries meant the core platform stayed healthy even as experiments came and went — which gave the business confidence to keep experimenting.

### Bullet Recap

- **S:** Multiple digital commerce experiments in various states; codebase accumulating complexity; experiments intertwined with core systems
- **T:** Safely retire unsuccessful experiments without destabilizing core platform
- **A:** Mapped all integration points per experiment; feature flags + circuit breakers from day one; phased retirement (disable traffic → drain pipelines → clean data → remove code); documented retirement playbook
- **R:** Multiple experiments retired with zero incidents; playbook adopted by other teams; core platform stayed healthy; business gained confidence to keep experimenting

### Long-Form Narrative

Product experimentation is great until you have to clean up. After the initial digital shopping launch, CarGurus ran several follow-on experiments — different lead flows, merchandising variations, pricing models. Some worked, some didn't. The problem was that each experiment had tentacles: API endpoints, Kafka topics, database tables, config flags, dealer-facing settings. You couldn't just delete the code and call it done.

I saw this problem coming and had designed the original architecture with clean boundaries — feature flags gating experimental code paths, circuit breakers isolating experimental components, and clear event stream contracts. But retirement still needed a disciplined process.

I created a retirement playbook: (1) map every integration point for the experiment, (2) disable new traffic via feature flag, (3) drain any in-flight events and confirm pipeline quiescence, (4) clean up dealer-facing configs and database artifacts, (5) remove the code and associated infrastructure. Each step had verification criteria. I documented the first retirement thoroughly, then the playbook became self-service for subsequent retirements.

We retired multiple experiments without a single customer-facing incident. Other teams adopted the playbook for their own feature retirement processes. The bigger win was cultural: because the business saw that experiments could be safely retired, they were more willing to approve new ones. The clean architecture and disciplined process turned experimentation from risky to routine.

---

## Story 11: Cross-Org Leadership — Mentoring to Staff Level

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

## Story 12: Cross-Org Leadership — Driving Consensus via RFCs

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

## Story 13: Applause — Auth Modernization with Minimal Downtime

**Anchor:** Authentication & Identity Modernization · **LPs:** Delivers Results, Ownership, Dive Deep
**Best for:** Coinbase, Figma

### STAR Spoken-Style

**Situation:** At Applause, the authentication system was home-grown — a custom auth layer that had been bolted onto different products over the years. Internal tools, an enterprise partner platform, and a large external community all had separate login experiences with different auth mechanisms. Social login and mobile login weren't supported. The system was fragile and a security risk.

**Task:** I was tasked with leading the migration to a modern Keycloak-based SSO platform that would unify authentication across all products. The critical constraint was minimal downtime — the external community had thousands of active users, and the partner platform had contractual SLAs.

**Action:** I designed a phased migration. First, I stood up Keycloak and configured it to support the various identity providers we needed: internal LDAP, social login (Google, Facebook), and mobile auth. Then I implemented a dual-auth bridge — the existing auth system and Keycloak ran in parallel, with sessions accepted from both. This let us migrate products one at a time without a flag day. I migrated the internal tools first (lowest risk), then the partner platform (medium risk, but we could coordinate with partners), then the external community (highest risk, most users). For each migration, I wrote runbooks and rollback procedures. I worked closely with the Angular, Node.js, and Java monolith teams to update their auth integrations.

**Result:** The migration was completed with minimal downtime — no SLA violations, no mass session invalidations, no customer-facing auth outages. All products were unified under a single SSO with social and mobile login support. The dual-auth bridge approach was key — it gave us a safe, incremental migration path instead of a risky big-bang cutover.

### Bullet Recap

- **S:** Home-grown auth across multiple products; separate login experiences; no social/mobile login; fragile and security risk
- **T:** Migrate to Keycloak SSO across internal tools, partner platform, external community; minimal downtime; contractual SLAs
- **A:** Phased migration: Keycloak + multi-provider setup; dual-auth bridge for parallel operation; migrated low→medium→high risk sequentially; runbooks + rollback procedures; coordinated with Angular/Node.js/Java teams
- **R:** Completed with minimal downtime; zero SLA violations; unified SSO with social/mobile login; dual-auth bridge enabled safe incremental migration

### Long-Form Narrative

Authentication migrations are among the riskiest infrastructure changes you can make. At Applause, the situation was particularly complex because the home-grown auth system was deeply embedded in multiple products — internal tools, an enterprise partner platform, and a large external community. Each had its own login flow, its own session management, its own user store.

My approach was to avoid the big-bang cutover entirely. I designed a dual-auth bridge: Keycloak and the legacy auth system ran in parallel, and the session validation layer accepted tokens from both. This meant I could migrate products one at a time. A user who was migrated to Keycloak would get the new login experience. A user who hadn't been migrated yet would continue using the legacy flow. Both could coexist.

I migrated in order of risk: internal tools first (if something broke, only employees were affected), then the partner platform (we could coordinate downtime windows with partners), then the external community (the highest user count and least tolerance for disruption). For each phase, I wrote detailed runbooks and rollback procedures — if anything went wrong during a migration window, we could revert to the legacy auth in minutes.

The coordination across teams was substantial. The various products were built on different stacks — Angular frontends, Node.js APIs, Java monoliths — and each needed its auth integration updated. I worked with each team to ensure the transition was smooth and tested.

The result was a unified SSO across all products with social and mobile login support, completed with minimal downtime and zero SLA violations. The dual-auth bridge pattern was the enabler — it turned a scary flag-day migration into a series of small, controllable steps.

---

## Story 14: Applause — Event Sourcing / CQRS Initiative

**Anchor:** Event Sourcing & CQRS Initiative · **LPs:** Invent and Simplify, Think Big
**Best for:** Stripe, Figma, Coinbase

### STAR Spoken-Style

**Situation:** At Applause, the existing architecture was a set of tightly coupled services that shared databases directly. Any change to a data model risked breaking downstream consumers. The system was hard to evolve, and building new features required coordinating schema changes across multiple teams.

**Task:** I wanted to introduce a fundamentally better architectural pattern that would decouple services and make the system more evolvable. I saw event sourcing and CQRS as the right approach — separating the write model from the read model and using events as the source of truth.

**Action:** I drove the initial design and prototyping of an event-sourced architecture. I defined the foundational patterns: how services emit events, how event stores are structured, how read models are built from event streams, and how to handle eventual consistency. I built a proof-of-concept for one domain to demonstrate the approach concretely. I also created documentation and ran workshops to help other engineers understand the paradigm shift — event sourcing is a significant mental model change from traditional CRUD.

**Result:** The patterns I defined were adopted by new service domains at Applause. Teams building new features used the event-sourcing patterns instead of the old shared-database approach, which gave them much better autonomy and evolvability. The CQRS separation made it possible to optimize read and write paths independently, which improved performance for read-heavy use cases.

### Bullet Recap

- **S:** Tightly coupled services sharing databases; schema changes required cross-team coordination; hard to evolve
- **T:** Introduce event sourcing + CQRS to decouple services and improve evolvability
- **A:** Designed foundational patterns (event emission, stores, read models, eventual consistency); built POC for one domain; created documentation and ran workshops for paradigm adoption
- **R:** Patterns adopted by new service domains; better team autonomy; independent read/write optimization; improved performance for read-heavy paths

### Long-Form Narrative

At Applause, the architecture had a common anti-pattern: services were coupled through shared databases. Service A would read directly from Service B's database tables. This meant any schema change in B required coordinating with A (and C and D). It was a significant drag on development velocity and a constant source of production incidents.

I proposed adopting event sourcing and CQRS for new service development. This was a significant paradigm shift — instead of services reading each other's databases, services would emit events to an event store, and downstream consumers would build their own read models from those event streams. The write model and read model would be explicitly separated.

I started with a concrete proof-of-concept in one domain. I designed the event schema, built the event store, implemented the write side (command handlers that validate and emit events) and the read side (projections that build query-optimized views from the event stream). I handled the tricky parts: idempotent event processing, snapshot strategies for performance, and how to handle schema evolution of events over time.

Beyond the code, I invested in education. Event sourcing requires a fundamentally different way of thinking about data — you're not mutating state, you're appending facts. I ran workshops and wrote documentation to help engineers make the mental model shift.

The patterns were adopted by multiple new service domains. Teams had much more autonomy — they could evolve their read models independently without coordinating schema migrations. The CQRS separation also enabled performance optimizations: read models could be denormalized for fast queries without compromising the write model's integrity.

---

## Story 15: Toast — Early Engineer in Hypergrowth

**Anchor:** Toast Hypergrowth · **LPs:** Ownership, Bias for Action, Learn and be Curious
**Best for:** All companies

### STAR Spoken-Style

**Situation:** I joined Toast when it was very early — the company was growing from its first customer to hundreds within a few years. The engineering team was small, and there was no established architecture, no dedicated DevOps, and no QA team. Every engineer wore multiple hats.

**Task:** I needed to build core backend services that would become the foundation for the company's restaurant management platform, while also solving infrastructure and quality problems that would typically be handled by specialized teams.

**Action:** I designed and implemented several foundational services — the Order Service, the Labor Service, and shared APIs that other features built on top of. These needed to be reliable from day one because restaurants depended on them in real time. I also took ownership of infrastructure: I built the initial AWS deployment pipelines because there was no DevOps team, and I created the first automated testing framework because there was no QA team. I made pragmatic technology choices that prioritized time-to-market while leaving room to evolve — for example, I chose a straightforward monolith-first approach for services that didn't yet need to be decomposed.

**Result:** The services I built became the backbone of the Toast platform. The Order Service processed thousands of orders daily for growing restaurant clients. The deployment pipelines I created were used until a dedicated DevOps team was formed and could replace them with more sophisticated tooling. The testing framework caught critical issues before they reached production during a period of extremely rapid development. The experience taught me that in hypergrowth, the best architecture is the simplest one that solves today's problem and doesn't preclude tomorrow's evolution.

### Bullet Recap

- **S:** Very early-stage company; first customer to hundreds; no DevOps, no QA, small engineering team
- **T:** Build foundational backend services + solve infrastructure and quality gaps simultaneously
- **A:** Designed Order Service, Labor Service, shared APIs; built initial AWS deployment pipelines; created first automated testing framework; pragmatic tech choices (monolith-first where appropriate)
- **R:** Services became platform backbone; deployment pipelines used until dedicated DevOps team formed; testing framework caught critical issues during rapid growth; learned simplest viable architecture principle

### Long-Form Narrative

Toast was a formative experience. I joined when the company was truly early — a handful of engineers, a handful of restaurant customers, and a massive vision for what the platform could become. There was no established architecture, no DevOps team, no QA team. If something needed to be built, you built it.

I focused on the core domain: the Order Service (the heart of a restaurant platform — every transaction flows through it), the Labor Service (scheduling, time tracking), and shared APIs that other features would depend on. These had to work reliably from day one. A bug in the Order Service means a restaurant can't process payments. A bug in Labor means employees don't get paid correctly. The stakes were real even at small scale.

Beyond the services themselves, I took ownership of gaps that had nobody assigned. I built the initial AWS deployment pipelines — CI/CD that got code from commit to production in a repeatable way. Before that, deploys were manual and error-prone. I also created the first automated testing framework — a suite of integration tests that ran against a staging environment and caught issues that unit tests missed. This was critical during a period when the codebase was changing daily.

My technology choices were deliberately pragmatic. For services that didn't yet need to be microservices, I kept them monolithic. Premature decomposition would have been a tax on a small team. I focused on clean interfaces so that when the time came to split services (and it did), the boundaries were already clear.

The services I built processed thousands of orders daily as Toast grew. The deployment pipelines I created were used for over a year until a dedicated DevOps team was hired. The lesson I carry forward: in hypergrowth, the best architecture is the simplest one that works today and doesn't prevent you from evolving tomorrow.

---

## Story 16: Toast — Building DevOps & QA from Scratch

**Anchor:** Toast Hypergrowth · **LPs:** Invent and Simplify, Ownership
**Best for:** Datadog, Figma, Circle

### STAR Spoken-Style

**Situation:** At early-stage Toast, there was no DevOps team and no QA team. Deployments were manual, risky, and infrequent. Testing was ad-hoc — mostly manual spot-checking. As the product grew and more restaurants depended on us, this was becoming a serious risk.

**Task:** I needed to create reliable deployment and testing infrastructure from scratch — not because it was assigned to me, but because I saw it as a critical gap that would eventually cause a production outage if left unaddressed.

**Action:** For deployments, I built an AWS-based CI/CD pipeline: automated builds triggered by commits, automated tests in a staging environment, and a streamlined deployment process that reduced the manual steps and human error. For testing, I created an integration testing framework that ran against a staging environment mirroring production. The tests covered critical paths — order processing, payment flows, labor calculations — and ran automatically on every build. I also established practices around deployment checklists and rollback procedures, creating the foundation for what later became a full DevOps function.

**Result:** Deployment frequency increased significantly because the risk of each deployment was much lower. The testing framework caught several critical bugs that would have impacted restaurants in production. When Toast eventually hired dedicated DevOps and QA engineers, they inherited a working foundation rather than starting from zero. I learned that in a startup, the engineer who builds the safety nets is as important as the engineer who builds the features.

### Bullet Recap

- **S:** No DevOps, no QA; manual deployments; ad-hoc testing; growing production risk as more restaurants onboarded
- **T:** Build deployment and testing infrastructure from scratch (self-directed, not assigned)
- **A:** Built AWS CI/CD pipeline; created integration testing framework for critical paths; established deployment checklists and rollback procedures; laid foundation for future DevOps/QA functions
- **R:** Increased deployment frequency; caught critical bugs pre-production; gave dedicated teams a working foundation when hired; safety nets as valuable as features

### Long-Form Narrative

In Toast's early days, deploying code was a manual, anxiety-inducing process. Someone would SSH into servers, pull the latest code, restart services, and hope for the best. Testing was whatever the developer remembered to check manually. For a platform that restaurants depended on for every transaction, this was a ticking time bomb.

Nobody asked me to fix this — I just saw it as the highest-leverage problem I could solve. I built a CI/CD pipeline on AWS: automated builds triggered by git commits, a staging environment that mirrored production, automated test suites that ran against staging, and a streamlined deployment process that replaced the SSH-and-pray approach.

The testing framework focused on critical business paths. I didn't try to achieve 100% coverage — that would have been premature for a fast-moving startup. Instead, I identified the paths where a bug would cause real business harm (order processing, payment capture, labor calculations) and built integration tests for those. The tests ran on every build, so developers got fast feedback.

I also created soft infrastructure: deployment checklists, rollback procedures, a simple runbook for common failure modes. These were documents, not code, but they were just as important — they turned tribal knowledge into repeatable process.

When Toast hired dedicated DevOps and QA engineers, they didn't start from zero. They inherited working pipelines, a test framework, and documented procedures. They improved everything significantly, but the foundation was there. The experience reinforced a belief I still hold: in a startup, the engineer who builds the safety nets is as valuable as the engineer who builds the features.

---

## Story 17: GenAI Engine — Hybrid Rules + LLM Architecture

**Anchor:** GenAI Decision Engine (Independent) · **LPs:** Invent and Simplify, Think Big, Learn and be Curious
**Best for:** Netflix, Stripe, Coinbase

### STAR Spoken-Style

**Situation:** I was building an independent project — a GenAI decision engine — and I encountered a fundamental design tension. Pure LLM-based decisions were too slow and expensive for real-time use cases, but pure rule-based systems couldn't handle the nuance and flexibility that made GenAI valuable. I needed an architecture that combined both.

**Task:** I wanted to design a system that could make real-time decisions by choosing between fast rule-based inference and deeper LLM-based inference depending on the context, while maintaining explainability and configurability.

**Action:** I designed a hybrid architecture with two inference paths. The fast path used deterministic rules and lightweight models for decisions that could be made quickly and cheaply. The deep path used LLM-based reasoning for decisions requiring nuance, context, or creativity. A routing layer evaluated each incoming request and chose the appropriate path based on configurable criteria — complexity signals, cost budget, latency requirements. On top of this, I built a policy overlay that processed heterogeneous telemetry data and applied enterprise-configurable rules to constrain the decision space. The entire system produced explainable outputs — every decision came with a trace showing which path was taken and why.

**Result:** The architecture achieved real-time performance for the majority of requests via the fast path, while preserving the quality of LLM-based reasoning for complex cases. The policy overlay made it enterprise-ready — organizations could configure their own constraints without modifying the engine code. The explainability trace was critical for building trust in the system's outputs.

### Bullet Recap

- **S:** Pure LLM too slow/expensive for real-time; pure rules too rigid for nuanced decisions; needed both
- **T:** Design hybrid system combining fast rules + deep LLM inference with explainability and configurability
- **A:** Two-path architecture (fast rules vs. deep LLM); configurable routing layer (complexity, cost, latency); policy overlay with heterogeneous telemetry; enterprise-configurable constraints; explainability traces on every decision
- **R:** Real-time performance for majority of requests; LLM quality preserved for complex cases; enterprise-ready via policy layer; trust built through explainability

### Long-Form Narrative

The core challenge of building a GenAI decision engine is the tension between speed and quality. LLMs produce nuanced, context-aware outputs, but they're slow and expensive. Rule-based systems are fast and cheap, but they can't handle the breadth of situations that make AI valuable. Most real-world applications need both.

I designed a hybrid architecture. The system has two inference paths: a fast path (deterministic rules, lightweight scoring models, cached lookups) and a deep path (full LLM reasoning with prompt engineering and multi-step chains). Every incoming request hits a routing layer that evaluates which path to use based on configurable signals: estimated complexity of the decision, the latency budget available, the cost budget, and whether the request type has a high-quality rule available.

On top of the inference paths, I built a policy overlay. This layer processes heterogeneous telemetry — user behavior signals, contextual data, historical patterns — and applies enterprise-configurable rules to constrain the decision space. For example, an enterprise client might say "never recommend products in category X" or "always prioritize cost savings over quality for this segment." These policies are stored in a database and can be updated without code changes or deployments.

Every decision comes with an explainability trace: which path was taken, which rules fired, which telemetry signals influenced the routing, and what the LLM's reasoning was (if the deep path was used). This was critical for building trust — stakeholders need to understand why the system made a particular recommendation, not just what it recommended.

---

## Story 18: GenAI Engine — Prompt Lab & Experimentation

**Anchor:** GenAI Decision Engine (Independent) · **LPs:** Learn and be Curious, Insists on Highest Standards
**Best for:** Datadog, Airbnb

### STAR Spoken-Style

**Situation:** After building the hybrid GenAI engine, I realized that optimizing the system — choosing the right prompts, tuning parameters, configuring routing thresholds — was itself a major challenge. There was no systematic way to evaluate different configurations against historical data. Changes were made by intuition and spot-checked manually.

**Task:** I wanted to build a comprehensive experimentation platform — a "Prompt Lab" — that would let me systematically evaluate, backtest, and optimize every tunable aspect of the engine.

**Action:** I built Prompt Lab with several components. First, a historical backfill system that could replay past decision requests through the engine, capturing what the system would have decided under different configurations. Second, an end-to-end decision simulation mode for offline evaluation. Third, a parameter search capability supporting both grid search and Bayesian optimization — it could sweep across prompt variations, model parameters, routing thresholds, and policy configs to find optimal settings. Fourth, I built a scheduler to run these experiments as background jobs with proper observability. The platform supported multiple LLM providers so I could compare performance across models.

**Result:** Prompt Lab transformed how I optimized the engine. Instead of making changes and hoping they were better, I could run controlled experiments against historical data and see exactly how each change affected decision quality, latency, and cost. The Bayesian optimization found parameter combinations that I wouldn't have tried manually. The multi-provider support revealed significant quality and cost differences between LLM providers for different decision types. The platform embodies the principle that you can't improve what you can't measure.

### Bullet Recap

- **S:** GenAI engine optimization was ad-hoc; no systematic evaluation against historical data; changes based on intuition
- **T:** Build comprehensive experimentation platform for systematic evaluation, backtesting, and parameter optimization
- **A:** Built Prompt Lab: historical backfill + replay; offline decision simulation; grid + Bayesian parameter search; background job scheduler with observability; multi-provider LLM support
- **R:** Transformed optimization from intuition to data-driven; Bayesian search found non-obvious optimal configs; revealed provider-specific quality/cost tradeoffs; embodied "can't improve what you can't measure"

### Long-Form Narrative

Building a GenAI engine is only half the battle — optimizing it is the other half, and it's arguably harder. The system has dozens of tunable parameters: prompt templates, model selection, temperature settings, routing thresholds, policy weights, caching TTLs. Changing any one of them affects the system's behavior in ways that are hard to predict.

Initially, I was optimizing by intuition: change a prompt, run a few test cases, see if the output looked better. This doesn't scale and doesn't give you confidence that you haven't regressed on other cases.

I built Prompt Lab to solve this systematically. The core capability is historical replay: I can take a corpus of past decision requests — real data with known good outcomes — and run them through the engine under any configuration. This gives me a ground-truth comparison: did this prompt change improve decision quality? Did this routing threshold change reduce latency without hurting quality?

Beyond replay, I built parameter search. Grid search lets me sweep across discrete configuration spaces (e.g., try these 5 prompts × 3 temperatures × 2 routing thresholds = 30 configurations). Bayesian optimization handles continuous parameters more efficiently — it builds a probabilistic model of the objective function and samples intelligently, finding good configurations in far fewer iterations than grid search.

All of this runs as background jobs managed by a scheduler with proper observability — I can see experiment progress, intermediate results, and resource consumption in dashboards. The multi-provider support was another key feature: I could run the same experiment against GPT-4, Claude, and other models and compare quality, latency, and cost side by side.

The platform revealed insights I wouldn't have found manually. Bayesian optimization discovered that a non-obvious combination of a lower temperature with a more detailed prompt template outperformed both the high-temperature creative approach and the low-temperature simple-prompt approach. Multi-provider comparisons showed that different models excelled at different decision types — one model was better at structured analytical decisions while another was better at creative recommendations.

---

## Story 19: Disagree and Commit — Pushing Back on Architecture

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

## Story 20: Failure & Learning — A Decision That Didn't Work Out

**Anchor:** Cross-cutting · **LPs:** Are Right A Lot, Learn and be Curious
**Best for:** All companies

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

## LP Quick-Reference Matrix

| Leadership Principle | Stories |
|---|---|
| **Customer Obsession** | 5, 6, 9 |
| **Ownership** | 1, 7, 9, 10, 13, 15, 16 |
| **Invent and Simplify** | 3, 5, 14, 16, 17 |
| **Are Right A Lot** | 10, 20 |
| **Learn and be Curious** | 7, 15, 17, 18, 20 |
| **Hire & Develop The Best** | 11 |
| **Insists on Highest Standards** | 2, 8, 18 |
| **Think Big** | 1, 4, 14, 17 |
| **Bias for Action** | 5, 9, 15 |
| **Dive Deep** | 2, 3, 8, 13 |
| **Earn Trust** | 4, 6, 11, 12 |
| **Delivers Results** | 1, 6, 9, 13 |
| **Have Backbone; Disagree and Commit** | 12, 19 |

## Company Quick-Reference Matrix

| Company | Best Stories |
|---|---|
| **Stripe** | 1, 3, 4, 5, 7, 9, 10, 12, 14, 17 |
| **Netflix** | 4, 5, 7, 8, 12, 17 |
| **Datadog** | 1, 2, 3, 8, 16, 18 |
| **Coinbase** | 9, 10, 13, 14, 17 |
| **Airbnb** | 1, 2, 5, 8, 18 |
| **Figma** | 2, 3, 7, 13, 14, 16 |
| **Circle** | 1, 4, 5, 10, 12, 16 |
| **All** | 6, 11, 15, 19, 20 |
