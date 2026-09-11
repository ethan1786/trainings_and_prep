# AI Agent Platform Infrastructure & Performance — Deep Dive

> **Project for interview discussions**
> Timeline: April 2026 - Present (ongoing)
> Role: Backend infrastructure and performance optimization owner
> Work: ~30 tickets over 3-4 months (3-5 tickets/week sustained pace)

---

## Executive Summary (30-second version)

> "I own the backend infrastructure and performance optimization for CarGurus' production conversational AI platform. Over the past 4 months, I've reduced agent response latency by 46-59%, cut MongoDB query latency in half (200ms→100ms), and built comprehensive observability with Prometheus metrics and Grafana dashboards. The work spans database performance tuning, circuit breakers for reliability, cost optimization (60% cheaper welcome flow), and operational maturity for AI workloads that behave completely differently from traditional APIs."

---

## The Big Wins (Lead With These)

### 1. Agent Response Latency: 46-59% Improvement

**Before/After:**
- Welcome flow: 9.3s → 3.8s (59% faster, 60% cheaper)
- Agent orchestration: 14s → 7.5s (46% faster)
- Memory inheritance overhead: 1,355ms → 167ms (88% reduction)

**How:**
- Prompt caching: reordered prompt structure to maximize OpenAI cache hits
- Token reduction: filtered context 76% smaller (removed unnecessary listing data)
- Model upgrades: switched to gpt-5.4-mini and gpt-4.1 (faster inference)
- Architectural simplification: retired multi-agent wrapper, consolidated to single agent
- Pre-fetching: load data before LLM call instead of during

**Why it matters:** AI agents are customer-facing. Every second of latency = abandonment risk.

### 2. MongoDB Performance: 50% Latency Reduction

**Before/After:**
- p99 query latency: 200ms → 100ms (50% reduction)
- Primary DB load: reduced 30-40% via read-replica splitting

**How:**
- Index consolidation: replaced 6 redundant compound indexes with 1 consolidated index
- Read-replica splitting: created separate connection pools for primary/secondary reads (critical operations stay on primary, read-heavy on secondaries)
- Connection pool tuning: fixed starvation by increasing maxPoolSize 20→50, minPoolSize 2→5, added waitQueueTimeoutMS: 10s for fast-fail
- TTL indexes: auto-delete old telemetry data to prevent unbounded growth
- Query-specific indexes: added indexes for spanType, entityName, resourceId+spanType queries

**Why it matters:** MongoDB is the conversation memory. Slow queries = slow agent responses.

### 3. Production Reliability: Zero to Mature

**What I built:**
- **Circuit breakers:** Fast-fail on external dependency degradation (prevents cascading failures)
- **Connection pool monitoring:** Prometheus metrics caught starvation before it caused outages
- **Functional readiness probes:** Health checks validate MCP tool availability and circuit breaker state
- **Hard timeouts:** 30s→10s for tool calls (3× faster worker recovery when upstream degrades)
- **Proper error surfacing:** Emit 5xx for pre-stream failures (was swallowing as 200), set OTel span status to ERROR

**Why it matters:** AI systems fail differently. LLM providers throttle, hallucinate, or return gibberish with 200 OK. Traditional monitoring doesn't catch this.

### 4. Comprehensive Observability: Blind to Instrumented

**What I built:**
- **Prometheus metrics (10+):** Tool call duration with error_type labels, error rates, circuit breaker state, connection pool health (active/idle/wait queue), in-flight requests, active streams, service start time
- **Grafana dashboards:** Service health overview, deployment annotations, tool call performance, MongoDB pool metrics
- **OpenTelemetry tracing:** Inject trace_id/span_id into Mastra logs for correlation
- **Alerting:** Tool-call error rate thresholds, circuit breaker trips, connection pool exhaustion

**Before:** Cost was invisible, couldn't diagnose failures, no visibility into LLM provider health
**After:** See token usage by endpoint/user/provider, trace failures end-to-end, proactive alerts

---

## Technical Deep-Dive (For System Design / Behavioral Questions)

### Challenge 1: Traffic Unpredictability

**Problem:**
- Traditional APIs: 50-200ms per request, predictable concurrency
- AI agents: 2-10 seconds per streaming response, unpredictable session lengths, LLM latency varies 10× depending on response length and provider load

**What I had to do:**
- Size connection pools without historical data (no baseline to extrapolate from)
- Set timeouts that balance false failures vs. worker starvation
- Handle bursts (one viral social post = 50× traffic spike)

**Solution:**
- Started conservative: small pools (20), aggressive timeouts (10s)
- Instrumented heavily: connection pool metrics (active/idle/wait queue depth)
- Tuned iteratively based on production data: maxPoolSize 20→50, waitQueueTimeout added
- Circuit breakers: fail fast on provider degradation instead of exhausting pools

**Lesson:** Can't capacity plan for AI workloads like traditional APIs. Need instrumentation + iterative tuning.

### Challenge 2: Cost Visibility

**Problem:**
- First week in production: [TODO: FILL IN - how much $ burned? or just say "burned budget quickly"]
- One endpoint was calling LLM 5× per request due to a bug
- No visibility into which endpoints/users/providers were expensive

**Solution:**
- Built dashboards tracking token usage by: endpoint, user, provider
- Now see cost hotspots within hours, not weeks
- Token reduction work (76% smaller contexts) saved [TODO: FILL IN - how much $/month?]

**Lesson:** LLM costs are different from compute costs. Per-token pricing means context size matters as much as request count.

### Challenge 3: Cascading Failures

**Problem:**
- LLM providers aren't like internal services
- OpenAI rate-limits with 429s, Anthropic has regional outages, latency can spike 10× during peak hours
- When one provider degrades, requests queue up and exhaust connection pools → entire service goes down

**Solution:**
- Circuit breakers per provider with fallback logic
- If OpenAI is degraded, fail fast and try Anthropic
- Connection pool monitoring catches exhaustion before it cascades

**Lesson:** Treat AI providers like unreliable external dependencies (because they are).

### Challenge 4: MongoDB at Scale for AI Workloads

**The difference:**
- Traditional APIs: predictable read/write patterns
- AI agents: every conversation is append-heavy (new messages), then read-heavy (load context for next turn), then append again

**What I learned:**
- Compound indexes matter: wrong index = full collection scan on every agent turn
- Read-replica splitting: context reads can tolerate stale data (eventual consistency OK), but new messages must go to primary
- Connection pool sizing: AI sessions hold connections longer than CRUD APIs (streaming responses)
- TTL indexes: conversation history grows unbounded without cleanup

**Specific decisions I made:**
- Consolidated 6 indexes → 1 (analyzed query patterns, most were redundant)
- Split reads: non-critical (load context) → secondary, critical (write messages) → primary
- TTL on telemetry: 7 days retention, auto-cleanup

---

## The Ticket Backlog (Organized by Theme)

### MongoDB Performance & Reliability
- ✅ Split read preferences (CNAI-449) — Separate pools for primary/secondary
- ✅ Index consolidation (CNAI-349) — 6 redundant indexes → 1 consolidated
- ✅ Connection pool tuning — maxPoolSize 20→50, waitQueueTimeoutMS added (multiple tickets)
- ✅ TTL indexes (CNAI-237) — Auto-delete old telemetry
- ✅ Query-specific indexes (CNAI-228, CNAI-231) — spanType, entityName, resourceId+spanType
- ✅ Removed unused semantic recall (CNAI-450) — Eliminated MongoDBVector

### Agent Performance Optimization
- ✅ Welcome latency (CNAI-218) — 9.3s→3.8s (59% faster, 60% cheaper)
- ✅ Agent orchestration (CNAI-50) — 14s→7.5s (46% faster), memory inheritance 1,355ms→167ms
- ✅ OpenAI prefix caching (CNAI-440) — Reordered prompt structure
- ✅ Strip stale listing context (CNAI-404) — Reduce tokens, prevent hallucinations
- ✅ Remove IMV data (CNAI-242) — Context size reduction
- ✅ Listing details projection — 76% smaller tool results
- ✅ Single-agent architecture — Retired multi-agent wrapper

### Reliability & Resilience
- ✅ MCP tool timeout (CNAI-244) — 30s→10s (3× faster recovery)
- ✅ Lazy-load MCP tools (CNAI-163) — Background-eager with exponential backoff
- ✅ Circuit breakers (CNAI-385) — External dependency resilience
- ✅ Hard timeout for streams (CNAI-406) — Prevent indefinite hangs
- ✅ Functional readiness probe (CNAI-387) — MCP + circuit breaker health checks
- ✅ 5xx error surfacing (CNAI-354) — Emit 5xx for pre-stream failures
- ✅ Client disconnect handling (CNAI-422) — Don't treat aborts as errors

### Observability & Monitoring
- ✅ Prometheus metrics (CNAI-390, CNAI-364, CNAI-328, CNAI-438) — Tool calls, pools, streams, service health
- ✅ Circuit breaker alerts (CNAI-385) — Error rate thresholds
- ✅ OpenTelemetry improvements (CNAI-436) — trace_id/span_id injection
- ✅ Grafana dashboard migration (CNAI-363) — NGINX + Envoy Gateway support
- ✅ Deploy annotations (CNAI-447) — Track deployments in Grafana
- ✅ HTTP access logs to Fluentd (CNAI-344) — Structured logging
- ✅ Metrics accuracy fixes (CNAI-414) — Pool gauge drift, TTFB histogram buckets

---

## Details to Fill In (TODO)

### Production Traffic & Scale
- [ ] **How many conversations/day?** [TODO: FILL IN]
- [ ] **How many LLM calls/day?** [TODO: FILL IN]
- [ ] **Peak QPS?** [TODO: FILL IN]
- [ ] **MongoDB cluster size?** (e.g., "3-node replica set, 100GB storage") [TODO: FILL IN]
- [ ] **Redis cluster size?** [TODO: FILL IN]

### Cost Metrics
- [ ] **How much $ burned in first week before instrumentation?** [TODO: FILL IN or remove if sensitive]
- [ ] **Cost savings from token reduction (76% smaller contexts)?** (e.g., "$X/month saved") [TODO: FILL IN or estimate]
- [ ] **Cost savings from 60% cheaper welcome flow?** [TODO: FILL IN or estimate]

### Reliability Incidents
- [ ] **Did connection pool starvation cause an outage before your fix?** (If yes, describe briefly) [TODO: FILL IN]
- [ ] **Any cascading failure incidents before circuit breakers?** [TODO: FILL IN]
- [ ] **Any specific provider outage you handled with fallback logic?** [TODO: FILL IN]

### Team Context
- [ ] **Who creates the tickets?** (Tech lead? PM? You self-identify work?) [TODO: FILL IN]
- [ ] **How many engineers on the team?** [TODO: FILL IN]
- [ ] **Your role vs. others?** (e.g., "I own infrastructure/perf, others own agent logic") [TODO: FILL IN]
- [ ] **Who do you collaborate with?** (DB reliability team? SRE? DevOps?) [TODO: FILL IN]

### Customer Impact
- [ ] **How is this used?** (Website chatbot? Internal tool? Which products?) [TODO: FILL IN]
- [ ] **What happens when it's slow/down?** (User abandonment? Support tickets?) [TODO: FILL IN]

---

## Interview Talking Points

### For "Tell me about a challenging project"
**Lead with:** AI Agent Platform Infrastructure & Performance
**Hook:** "I own backend infrastructure for our production AI platform. Over 4 months, I reduced agent latency 46-59% and built the observability stack from scratch."
**Tell the story:** Started in April, service was slow and opaque, worked through 30+ tickets systematically improving performance, reliability, and visibility.
**Result:** 46-59% faster, 60% cheaper, comprehensive observability, production-ready reliability.

### For "Tell me about a performance optimization"
**Pick one:** Welcome flow 9.3s→3.8s (59% faster, 60% cheaper)
**How:** Prompt caching, token reduction, model upgrade, pre-fetching, architectural simplification
**Trade-off:** Faster model = slightly less capable, but speed mattered more for welcome experience

### For "Tell me about operational challenges"
**Challenge:** AI traffic is unpredictable, costs were invisible, providers fail creatively
**What you did:** Built instrumentation first (Prometheus + Grafana), then tuned iteratively
**Lesson:** Can't rely on traditional monitoring for AI systems — need cost metrics, quality metrics, provider-level SLOs

### For "Tell me about working with databases at scale"
**MongoDB work:** 200ms→100ms via index consolidation, read-replica splitting, connection pool tuning
**Key decision:** Split critical (primary) vs. non-critical (secondary) reads — had to analyze which queries tolerate stale data
**Trade-off:** Eventual consistency on context reads OK, but new messages must be strongly consistent

---

## Connection to Meta

**Why this is relevant for Meta Infrastructure:**
- Meta operates AI at planet scale (Meta AI, Llama-powered features, AI-powered feeds/ads)
- Your work shows you understand:
  1. **AI workloads are different** (unpredictable, expensive, fail creatively)
  2. **Performance optimization matters** (46-59% improvements = measurable user impact)
  3. **Operational maturity** (observability, circuit breakers, cost visibility)
  4. **Iterative tuning** (can't design perfectly upfront, need instrumentation + data-driven decisions)

**In interviews, frame as:**
> "At CarGurus scale (millions of users), I learned that AI infrastructure has unique challenges — unpredictable traffic, cost visibility, provider reliability. At Meta scale (3B+ users), those challenges are amplified. The patterns I learned — instrumentation-first, iterative tuning, treating AI like external dependencies — will scale."
