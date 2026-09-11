# TODO: Fill In AI Agent Platform Details

> **Before Meta recruiter call or technical interviews**
> These details will make your stories more concrete and credible

---

## Priority 1: Numbers (High Impact)

### Traffic & Scale
- [ ] **Conversations per day** (approximate)
  - Check Grafana dashboard or Prometheus
  - Even ballpark helps ("hundreds/day" vs "thousands/day")

- [ ] **LLM API calls per day** (approximate)
  - Tool call metrics should have this
  - Useful for "how do you monitor AI systems" question

- [ ] **Peak QPS** (if measurable)
  - How many requests/second during busy periods
  - Shows you think about capacity

### Infrastructure Details
- [ ] **MongoDB cluster config**
  - Example: "3-node replica set" or "Atlas M30 tier"
  - Storage size if known
  - Helps frame "MongoDB at scale" discussion

- [ ] **Redis deployment**
  - Single node? Cluster? ElastiCache?
  - Memory size?
  - Shows you know the infrastructure

### Cost Impact (If Not Sensitive)
- [ ] **Rough monthly LLM spend** (before/after optimizations)
  - Or just % saved
  - "Token reduction saved ~$X/month" is powerful
  - If sensitive, skip and say "significant cost savings"

- [ ] **60% cheaper welcome flow = $ amount?**
  - Or just leave as 60% (still good)

---

## Priority 2: Context (Medium Impact)

### Team Structure
- [ ] **Team size**
  - How many engineers total?
  - Helps frame "my role vs others"

- [ ] **Your role vs. others**
  - Example: "I own infra/perf, [Name] owns agent logic, [Name] owns tools"
  - OR: "I'm the only backend engineer, others are full-stack/frontend"

- [ ] **Who creates tickets?**
  - Tech lead? PM? You self-identify work?
  - Helps explain "I didn't make tickets" concern

- [ ] **Who do you collaborate with?**
  - DB reliability team (you mentioned them)
  - SRE? DevOps? Platform team?

### Customer Impact
- [ ] **How is this used?**
  - Website chatbot? Which part of CarGurus site?
  - Internal tool? Customer-facing?

- [ ] **What happens when it's slow/down?**
  - User abandonment?
  - Support ticket volume increase?
  - Helps frame "why performance matters"

---

## Priority 3: Incidents (Nice to Have)

### Reliability Stories
- [ ] **Connection pool starvation incident**
  - Did this cause an outage before your fix?
  - If yes, brief description (1-2 sentences)
  - Great for "tell me about a production fire" question

- [ ] **Cascading failure before circuit breakers**
  - Did one LLM provider take down the whole service?
  - Makes circuit breaker work more concrete

- [ ] **Specific provider outage you handled**
  - OpenAI had a regional outage and you failed over to Anthropic?
  - Shows operational maturity

- [ ] **Cost burn incident**
  - First week: "burned $X" or "hit monthly budget in 3 days"
  - Makes "cost visibility" work more urgent

---

## How to Gather This Info

### For Traffic/Scale Metrics:
```bash
# Check Grafana dashboards (you set these up)
# Look for:
# - Total conversations/day (or per hour × 24)
# - Tool calls/day
# - Peak QPS

# Or ask teammate who has access to production metrics
```

### For Infrastructure:
```bash
# MongoDB cluster info
# Check your Terraform/deployment configs or MongoDB Atlas console

# Redis info
# Check deployment configs or AWS ElastiCache console
```

### For Cost:
```bash
# Check internal cost dashboards (you built token tracking)
# Or ask finance/eng lead for monthly LLM spend

# If sensitive, just note "significant savings" instead of $
```

### For Team Context:
```bash
# Just recall from memory or ask teammates:
# - How many on the team?
# - Who does what?
# - Who assigned you these tickets?
```

### For Incidents:
```bash
# Check Slack archives for:
# - "#incident" channel or similar
# - Mentions of outages related to AI agent service
# - Your own memory of "oh shit" moments

# PagerDuty/incident tracking system if you have one
```

---

## Timeline for Filling This In

**Before recruiter call (Week 1-2):**
- Priority 1 numbers (traffic, infra size)
- Priority 2 context (team, customer use case)

**Before technical interviews (Week 3-4):**
- Priority 3 incidents (if you remember any)
- Refine stories based on what you gathered

**If you can't find something:**
- Just say "approximate" or "hundreds/thousands scale"
- Interviewers care more about your thinking than exact numbers
- "I don't have the exact number, but approximately..." is fine

---

## Where These Details Go

Once you fill these in:

1. **Update:** `ai_agent_platform.md` (the doc I just created)
   - Replace all `[TODO: FILL IN]` sections
   - Use this doc to prep for interviews

2. **Update:** Your resume (if metrics are impressive)
   - Add traffic scale if significant ("supporting Xk conversations/day")
   - Add cost savings if measurable ("$X/month saved" or "60% cost reduction")

3. **Practice:** Verbal stories
   - 30-second version (elevator pitch)
   - 2-minute version (recruiter call)
   - 5-minute version (technical deep-dive)

---

## Don't Overthink It

**You don't need ALL of this** — even 50% will make your stories much stronger.

**The work speaks for itself:**
- 30+ tickets in 4 months
- 46-59% latency improvements
- 88% overhead reduction
- Comprehensive observability

**The details just make it more concrete.** "I reduced latency 59%" is already impressive. "I reduced latency from 9.3s to 3.8s on a service handling Xk conversations/day" is even better.

Start with Priority 1 (numbers), then Priority 2 (context), then Priority 3 (incidents) if you have time.
