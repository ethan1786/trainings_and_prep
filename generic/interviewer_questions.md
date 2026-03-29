# Questions to Ask Interviewers

> Organized by interview stage and tailored per company.
> Pick 2-3 per round. Don't ask things easily Googleable.

---

## Universal Questions (Any Company, Any Stage)

### Recruiter Screen
- What does the interview process look like, and what's the expected timeline?
- Is this a backfill or a new headcount? What's driving the hire?
- How is the team structured? How many engineers, and what's the seniority distribution?
- What does remote collaboration look like day-to-day for this team?
- Is there flexibility on level, or is this firmly scoped to [Staff/L6/etc.]?

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

## Company-Specific Questions

### 1. Stripe — Staff Engineer, Workflow Engine

**Recruiter:**
- How does the Service Platform team interact with product teams that consume the workflow engine?
- What's the team size and composition for the Workflow Engine group specifically?

**Hiring Manager:**
- What are the biggest reliability or scalability challenges the workflow engine faces today?
- How does the workflow engine handle failure modes — retries, dead letters, human intervention?
- What's the migration story for teams currently on older orchestration patterns?
- How much of the workflow engine is Stripe-proprietary vs. built on open-source foundations?

**Team Match:**
- What does a typical workflow definition look like — code-based, config-based, DSL?
- How does the team think about backward compatibility when evolving the workflow API?

---

### 2. Netflix — L6, Technical Catalog

**Recruiter:**
- How does the Technical Catalog team fit within the broader Data Platform org?
- What does the "freedom and responsibility" culture look like concretely for this team?

**Hiring Manager:**
- What's the current state of GraphQL federation adoption across Netflix? How many subgraphs exist today?
- What are the main consumers of catalog metadata — is it primarily content discovery, or does it extend to operations and content production?
- How does the team balance serving real-time consumer-facing queries vs. batch/ML pipelines?
- What's the biggest data consistency or freshness challenge in the catalog?

**Team Match:**
- How does the team handle schema evolution in the federated graph — breaking changes, versioning?
- What does the DGS development experience look like internally vs. the open-source version?

---

### 3. Datadog — Staff Software Engineer

**Recruiter:**
- Which specific team or product area would this role be on?
- How does Datadog think about hybrid work for the Boston office?

**Hiring Manager:**
- What's the scale of the ingestion pipeline — events per second, data volume?
- What are the biggest performance or scalability bottlenecks the team is tackling right now?
- How does the team balance shipping new product capabilities vs. scaling existing infrastructure?
- What's the observability stack for observing Datadog itself?

**Team Match:**
- What's the deployment cadence? How does the team handle rollouts at this scale?
- How do you handle multi-tenancy — noisy neighbor problems, isolation guarantees?

---

### 4. Coinbase — Senior Staff SWE, Financial Hub

**Recruiter:**
- How does the Financial Hub team relate to the broader backend infrastructure?
- What's the regulatory environment like for this team — do engineers interact directly with compliance?

**Hiring Manager:**
- What does the transaction processing pipeline look like end-to-end — from user intent to settlement?
- How does the team handle idempotency and exactly-once semantics in financial flows?
- What's the biggest reliability or correctness challenge the Financial Hub faces today?
- How does the team think about auditability and regulatory compliance in the architecture?

**Team Match:**
- What's the testing strategy for financial correctness — property-based testing, chaos engineering, formal verification?
- How does the on-call experience compare to a non-financial engineering team?

---

### 5. Airbnb — Senior Staff Engineer, Performance

**Recruiter:**
- Is this role embedded in a specific product area, or is it a cross-cutting platform role?
- How does Airbnb measure performance impact on business metrics?

**Hiring Manager:**
- What's the current performance profile — what are the main latency bottlenecks today?
- How does the performance team prioritize work — top-down business metrics vs. bottom-up profiling discoveries?
- What tools and infrastructure does the team use for continuous performance monitoring and regression detection?
- How much of the performance work is JVM/backend vs. client-side/rendering?

**Team Match:**
- What's a recent performance win the team shipped, and what was the approach?
- How does the team handle performance regressions introduced by product feature work?

---

### 6. Figma — SWE, Distributed Systems

**Recruiter:**
- Which specific infrastructure area would this role focus on — storage, streaming, data pipelines?
- What does the engineering team size look like, and how are infrastructure teams organized?

**Hiring Manager:**
- What's the distributed storage architecture — custom-built, Postgres-based, or something else?
- How does the team handle real-time data consistency for collaborative editing at the backend level?
- What are the biggest scaling challenges as Figma grows enterprise adoption?
- How does the team think about the tradeoff between building custom infrastructure vs. leveraging managed services?

**Team Match:**
- What's the development experience like for infrastructure engineers — deployment, testing, local dev?
- How does the team collaborate with the real-time/multiplayer engineering team?

---

### 7. Circle — Distinguished Software Engineer

**Recruiter:**
- How does Circle define the Distinguished Engineer role — is it primarily technical direction, or does it include people management?
- What's the engineering org size, and how is it structured?

**Hiring Manager:**
- What's the current technical architecture of the USDC infrastructure — monolithic, microservices, event-driven?
- What's the biggest platform-level technical debt or architectural challenge right now?
- How does the Distinguished Engineer role influence roadmap and strategy beyond engineering?
- What does "setting long-term technical direction" look like concretely — design docs, architecture councils, something else?

**Team Match:**
- How does the team handle the tension between moving fast and maintaining financial-grade reliability?
- What's the security and compliance review process for architectural changes?

---

## Red Flag Questions (Ask Yourself After Each Interview)

- Did they struggle to articulate the team's biggest challenge? (may indicate unclear direction)
- Did they dodge questions about on-call or work-life balance? (may indicate burnout culture)
- Did the team match interviewer seem disengaged or negative? (may indicate retention issues)
- Did they oversell the role without specifics? (may indicate the role isn't well-defined)
- Did they seem surprised by technical depth questions? (may indicate the role is less technical than posted)
