# Meta — Prescreen Form Responses

> Submitted: July 21, 2026
> Roles: Infrastructure (E6) + Product Leadership (E6/E7)
> Infrastructure role moved forward first

---

## Application Status

**Applied to:**
1. **Software Engineer, Infrastructure** (E6, $184K-$257K) — **MOVED FORWARD**
2. Software Engineer - Product (Technical Leadership) (E6/E7, $219K-$301K) — In review

**Referral:** Junyan Ji  
**Availability:** 3-4 weeks (mid-Aug target, post-Yellowstone trip)  
**Locations:** Boston, MA / Cambridge, MA

---

## Prescreen Responses

### Why looking for new opportunities?

> After 7 years at CarGurus, I've outgrown the problem space and am ready for my next growth stage. I want to work on infrastructure that operates at planet scale — billions of users, not millions — where every architectural decision has massive leverage. Meta's combination of scale, impact, and technical depth is exactly what I'm looking for. I'm particularly drawn to Meta's AI-first transformation and the opportunity to build infrastructure that enables AI at scale.

### Most important things in next job?

> Three things:
>
> 1. **Scale** — I want to work on systems where architectural decisions matter at billions of users, not millions. The jump from CarGurus (millions of daily users) to Meta (3B+ daily active people) is the kind of challenge that forces you to think differently about reliability, performance, and fault tolerance.
>
> 2. **Technical depth** — I want to work with world-class engineers on hard distributed systems problems. Meta's infrastructure — Thrift, TAO, Cassandra origins — represents the kind of engineering rigor I want to be part of.
>
> 3. **AI at the center** — I want to be part of the AI transformation, not on the sidelines. Meta's bet on AI (Llama, Meta AI, AI-powered feeds/ads) means every infrastructure decision needs to account for AI workloads. That's the future, and I want to build it.

### AI tools in daily workflows?

> I use AI tools daily across three areas:
>
> **1. Code generation and review (Claude Code, CodeRabbit, Mauve):**
> - **Claude Code:** Primary tool for all coding workflows — code generation (Spring Boot controllers, JUnit scaffolding), code review (ask "What edge cases am I missing?" or "Are there concurrency bugs?"), exploring API design alternatives ("Show me 3 ways to structure this GraphQL schema"), and iterative development
> - **Mauve:** CarGurus' internal agentic orchestration system that uses Claude Code agents to implement entire Jira tickets autonomously (spec → PR → CI → merge). I work alongside Mauve — it handles well-scoped tickets while I focus on complex architecture.
> - **CodeRabbit:** Automated PR review tool for code quality checks
> - **Key insight:** AI generates options; I provide judgment on which fits our constraints
>
> **2. System design exploration (Claude Code):**
> - Claude Code: Design space exploration — "What are trade-offs between CDC and dual-write for Elasticsearch sync?"
> - Claude Code: Evaluate technology choices — "Compare Kafka vs RabbitMQ for this use case"
> - Claude Code: Generate architecture concepts and think through failure modes
> - AI accelerates ideation; I make final architectural decisions
>
> **3. Documentation and knowledge synthesis (Claude Code):**
> - Claude Code: Summarize Slack threads, RFCs, design docs — "What are the key decisions and open questions?"
> - Claude Code: Generate design doc first drafts, then I fill in specifics
> - Claude Code: Transform meeting notes into actionable follow-ups
>
> **The pattern:** AI speeds up mechanical parts (scaffolding, first drafts, exploration), giving me more time for judgment calls — picking the right trade-off, understanding business constraints, knowing when to override the model.

### AI-Native projects?

> **Three projects — two where I owned the architecture end-to-end, and one I'm currently contributing to as a main backend engineer:**
>
> **1. MCP Server for Agent Orchestration (CarGurus, 2025-present) — Full ownership:**
> - **What:** Backend server exposing CarGurus capabilities as tools callable by all AI agents. Enables agents to search inventory, retrieve vehicle details, and answer product questions.
> - **Responsible design approach:**
>   - Rate limiting per agent/user to prevent runaway queries
>   - Input validation and sanitization (agents can hallucinate malformed inputs)
>   - Audit logging: every tool call logged with agent ID, input, output, latency
>   - Graceful degradation: if a tool fails, return structured error (don't let agent guess)
> - **Challenge:** Agents don't follow rate limits like humans do. I implemented token bucket rate limiting at the tool level because agents would parallelize calls aggressively.
>
> **2. AI Agent Platform Infrastructure & Performance (CarGurus, Apr 2026-present) — Backend infrastructure owner:**
> - **What:** I own the backend infrastructure and performance optimization for CarGurus' production conversational AI platform. Over 4 months, I've worked through ~30 tickets (3-5/week sustained pace) improving performance, reliability, and observability.
> - **Performance wins:**
>   - **MongoDB:** p99 query latency 200ms→100ms (50% reduction), primary DB load reduced 30-40% via read-replica splitting
>   - **Agent latency:** Welcome flow 9.3s→3.8s (59% faster, 60% cheaper), agent orchestration 14s→7.5s (46% faster), memory inheritance overhead 1,355ms→167ms (88% reduction)
>   - **Token optimization:** 76% context size reduction, 40% duplicate LLM call reduction via Redis caching
> - **Infrastructure & reliability work:**
>   - **MongoDB infrastructure:** Provisioned cluster, index consolidation (6 redundant indexes→1), read-replica splitting (primary for writes, secondaries for reads), connection pool tuning (maxPoolSize 20→50, waitQueueTimeoutMS added), TTL indexes for auto-cleanup
>   - **Redis caching:** LLM call results, prompt caching structure, tool API responses
>   - **Circuit breakers:** Fast-fail on external dependency degradation, timeout tuning (30s→10s), health checks (MCP tool availability + circuit breaker state)
>   - **Observability:** 10+ Prometheus metrics (tool calls, connection pools, streams, service health), Grafana dashboards with deployment annotations, OpenTelemetry tracing with trace_id/span_id injection, alerting for tool-call error rates and circuit breaker trips
> - **Operational challenges:**
>   - **Traffic unpredictability:** AI workloads are different from traditional APIs. Sized connection pools and set timeout thresholds without historical data. Built instrumentation first (connection pool metrics, active/idle/wait queue depth), then tuned iteratively based on production data.
>   - **Cost visibility:** First week in production burned through budget quickly. Built dashboards tracking token usage by endpoint/user/provider. Token reduction work (76% smaller contexts) saved significant monthly costs.
>   - **Cascading failures:** When one LLM provider degrades (rate limits, timeouts, regional outages), requests queue up and exhaust connection pools. Implemented circuit breakers per provider with fallback logic.
> - **Key lesson:** AI-native systems have operational failure modes traditional systems don't. You can't just monitor uptime — you need cost metrics, quality metrics, and provider-level SLOs because the AI itself is an external dependency. Can't capacity plan like traditional APIs — need instrumentation + iterative tuning.
>
> **3. GenAI Evaluation Platform (Personal Project, 2025-present) — Full ownership:**
> - **What:** Multi-provider LLM evaluation system with prompt engineering, A/B testing, and quality assessment for decision-making workflows.
> - **Responsible design approach:**
>   - **Bias monitoring:** Track decisions by demographic attributes to detect bias
>   - **Quality gates:** Automated accuracy tests against golden dataset before promotion
>   - **Explainability:** Decision outputs include reasoning traces for human audit
>   - **Human-in-the-loop:** High-stakes decisions require human approval
> - **Challenge:** Attribution and evaluation in production. It's hard to isolate whether a single decision was good or bad when you're tuning prompts — outcomes depend on many factors outside the AI's control. I initially tried using ROI as a proxy metric (do better prompts lead to better business outcomes?), but ROI is noisy and lagging (you don't know for weeks if a decision was right). The solution was continuous evaluation in production: sample outputs, human review of edge cases, and tracking leading indicators (user satisfaction, decision confidence scores, reasoning quality) rather than waiting for business outcomes. This means accepting that prompt tuning is iterative and data-driven, not a one-time optimization.
>
> **Key lessons across all three:** AI-native systems fail differently than traditional systems. You can't just catch exceptions — you need to monitor output quality continuously (hallucinations, bias drift, latency spikes). I treat AI components like external dependencies: circuit breakers, fallbacks, and assume they'll fail in creative ways.

### How evaluate AI quality/reliability?

> I evaluate AI quality at three stages:
>
> **Pre-deployment (Offline Evaluation):**
> - **Accuracy metrics:** For my GenAI platform, I run each prompt version against a golden dataset (100+ test cases) and measure: exact match accuracy, semantic similarity (cosine distance of embeddings), hallucination rate (factual errors)
> - **Latency:** p50, p99, p99.9 across multiple LLM providers (OpenAI, Anthropic, local models)
> - **Cost:** Tokens per query, $ per 1K decisions
> - **Tool:** Custom Python scripts + pytest for automated regression testing
>
> **Post-deployment (Production Monitoring):**
> - **Output quality drift:** Sample 1% of production outputs daily and manually review (spot-check for hallucinations, bias, degraded reasoning)
> - **Latency SLOs:** Alert if p99 > 2 seconds (user-facing) or > 10 seconds (background)
> - **Error rate:** Track 4xx/5xx from LLM APIs, fallback invocations, timeout rate
> - **Tool:** Grafana for metrics, custom dashboards for quality drift
>
> **Failure modes I watch for:**
> - **Silent degradation:** Model quality drops but doesn't error (e.g., AI returns gibberish or failure message but with 200 OK)
> - **Bias drift:** Model behavior changes over time (OpenAI updates the model, changes responses)
> - **Latency spikes:** Provider throttling, rate limits, regional outages
>
> **The key insight:** Traditional SLOs (latency, availability) are necessary but not sufficient for AI systems. You also need quality SLOs — 'hallucination rate < 1%', 'bias metric stays within bounds' — and you need humans in the loop to validate those metrics.

### How stay current with AI?

> I stay current through three channels:
>
> **1. Hands-on experimentation:**
> - Built an MCP server when the protocol launched — this forced me to understand agent orchestration, tool-calling, and prompt engineering at a deep level
> - Experimented with prompt chaining, few-shot learning, and retrieval-augmented generation (RAG) for my GenAI platform
> - Currently exploring agentic workflows (agents that break down complex tasks into sub-tasks)
>
> **2. Reading and community:**
> - Follow key researchers and labs (Anthropic, OpenAI, Meta AI) on blogs/posts
> - Keep up with latest news as part of the AI engineering community in CarGurus
> - Using AI chat to read and explore articles
>
> **3. Production use:**
> - I use Claude daily for engineering workflows, which keeps me grounded in what actually works vs. what's hype
>
> **Recent trends I've incorporated:**
> - **MCP (Model Context Protocol):** Built a production MCP server for agent tool-calling
> - **Structured outputs:** Switched from string parsing to JSON schema validation for LLM outputs (reduces hallucinations, makes responses parsable)
> - **Multi-provider orchestration:** Route queries to different LLM providers based on cost/latency/accuracy trade-offs
> - **Prompt versioning and A/B testing:** Treat prompts like code — version control, test before deploying, rollback on regression
>
> **What I'm watching next:**
> - **Agentic reasoning:** How agents decompose complex tasks (relevant for both my MCP work and Meta's AI products)
> - **Model distillation:** Running smaller, faster models for production (cost/latency optimization)
> - **Responsible AI at scale:** How Meta handles bias, safety, and quality for billions of users (this is the frontier)

---

## Next Steps

**Prep Plan (2 weeks before interview):**
1. **Week 1-2:** System design deep-dive (continue current work)
2. **Week 3-4:** LC prep (after system design foundation)

**Expected Timeline:**
- Recruiter call within 1-2 weeks (early Aug)
- Technical rounds mid-Aug (post-Yellowstone)
- Likely 4-5 rounds: 2 coding (2 problems each), 1-2 system design, 1 behavioral

**Key Talking Points for Recruiter Call:**
- Why Meta: Scale (3B users), technical depth (Thrift/TAO), AI-first transformation
- Why leaving: Outgrown CarGurus problem space, ready for planet scale
- AI experience: MCP server, conversational AI (production), GenAI platform
- Focus: Infrastructure role (hands-on systems) over Product Leadership (cross-org strategy)
