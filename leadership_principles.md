# Leadership Principles — Behavioral Interview Reference + Story Map

> Amazon-style leadership principles with example questions and mapped STAR stories.
> Stories are in `star_stories.md`. Each has STAR spoken-style, bullet recap, and long-form formats.
> Useful for any behavioral interview (Coinbase, Cherry, NVIDIA, etc.)

---

## Customer Obsession
**Principle:** Start with the customer and work backwards — leaders obsess over customers.

| Question | Best Stories |
|---|---|
| A time you used customer feedback to drive improvement | **6** (MCP stakeholder mgmt — adapted based on PM/director feedback) |
| Most difficult customer interaction | **6** (MCP — competing stakeholders with conflicting needs) |
| Balance needs of customer vs. business | **9** (Digital shopping — pragmatic tradeoffs to ship fast for customers during pandemic) |

---

## Insists on Highest Standards
**Principle:** Have relentlessly high standards and continuously raise the bar / drive others to do the same.

| Question | Best Stories |
|---|---|
| A time you were unsatisfied with the status quo. How would you change it? | **2** (API mod — refused to accept "a bit faster," pushed for 5x latency reduction) |
| Describe the most significant improvement project you've led | **1** (API mod — full cross-org modernization, 5x latency, 99.9% avail) |
| How do you seek out feedback on performance? | **8** (DGS warmup — profiled JVM, measured cold-start vs. steady-state, load tested) |

---

## Delivers Results
**Principle:** Focus on key inputs and deliver with high quality in a timely fashion.

| Question | Best Stories |
|---|---|
| Realized halfway in it may not be the best goal | **20** (Failure — caching strategy wrong for experimentation context, pivoted) |
| A goal that took a long time to achieve | **1** (API mod — 6-month first milestone, completed ahead of schedule) |
| Delivered a project under tight deadline | **9** (Digital shopping — 0→1 product under pandemic pressure) |

---

## Are Right A Lot
**Principle:** Strong judgment and good instincts.

| Question | Best Stories |
|---|---|
| A difficult decision and how you knew it was right | **19** (Disagree & commit — structured 5-dimension analysis to push back on tech choice) |
| A decision without data | **5** (MCP — bias for action, built modular architecture before requirements were clear) |
| A bad decision and how you learned from it | **20** (Failure — aggressive caching broke A/B tests, learned to ask about mutation patterns) |

---

## Bias for Action
**Principle:** Speed is crucial — value calculated risk taking.

| Question | Best Stories |
|---|---|
| Calculated risk where speed was crucial | **9** (Digital shopping — launched with eventual consistency to ship faster) |
| Important decision without consulting your manager | **5** (MCP — chose modular architecture and delivered demo in first sprint) |
| Removed serious roadblocks preventing progress | **5** (MCP — unblocked PM/director demos by delivering working POC quickly) |

---

## Invent and Simplify
**Principle:** Expect and require innovation from yourself and those around you — always find ways to simplify.

| Question | Best Stories |
|---|---|
| Most innovative thing you've done | **17** (GenAI — hybrid rules + LLM architecture with explainability) |
| Solved a complex problem with a simple solution | **3** (Parity testing — replayed prod traffic for structural diff instead of manual QA) |
| Creative idea that was difficult to implement | **14** (Applause CQRS — event sourcing paradigm shift, required education and POC) |

---

## Ownership
**Principle:** Think long term and don't sacrifice value for short-term results — there is no such thing as "not my job."

| Question | Best Stories |
|---|---|
| Took on something significant outside your responsibility | **16** (Toast — built DevOps/QA from scratch, not assigned) |
| Sacrificed short-term for long-term goal | **10** (Digital shopping — invested in feature flags + retirement playbook upfront) |
| Saw a peer struggling and stepped in | **11** (Mentoring — pulled senior engineers into cross-team problems, helped them grow) |

---

## Dive Deep
**Principle:** Stay connected to details, audit frequently, and question when metrics differ.

| Question | Best Stories |
|---|---|
| Went down several layers to figure out a problem | **8** (DGS — profiled JVM startup, found JIT + DGS lazy init as dual cold-start causes) |
| Linked two or more problems and identified underlying issue | **2** (API mod — traced redundant fan-out + poor caching + no batching as compound latency cause) |
| A metric you used to identify need for change | **2** (API mod — p99 latency + per-hop SLO budgets revealed bottlenecks) |

---

## Learn and Be Curious
**Principle:** Always seeking improvement — curious about new possibilities and love to explore them. Leaders are never done learning.

| Question | Best Stories |
|---|---|
| Needed deeper subject matter expertise | **7** (DGS — learned Netflix DGS framework, federation spec, subgraph patterns from scratch) |
| Took on work outside comfort area and found it rewarding | **17** (GenAI — independent project exploring LLM architecture, Bayesian optimization) |
| Didn't know what to do next / challenging problem | **5** (MCP — new protocol, evolving SDK, no internal precedent) |
| Coolest thing you learned on your own that helped your job | **17** (GenAI — self-directed LLM exploration, applied to production evaluation platform) |

---

## Have Backbone; Disagree and Commit
**Principle:** Obligation to respectfully challenge decisions when you disagree, even when doing so is uncomfortable or exhausting. Leaders have conviction and are tenacious. They do not compromise for the sake of social cohesion. Once a decision is made, commit fully.

| Question | Best Stories |
|---|---|
| Strongly disagreed with your manager | **19** (Pushed back on senior leader's tech stack choice with structured analysis) |
| Unpopular stance in a meeting with peers/leaders | **19** (Same — advocated against momentum with data) |
| Went along with group decision even if you disagreed | **19** (Committed fully on testing strategy decision where group went different direction) |
| Strongly disagreed on something important to the business | **19** (Tech stack choice — prepared 5-dimension comparison, advocated firmly but respectfully) |
| Submitted good idea and manager didn't take action | **12** (RFC process — pre-socialized proposals, incorporated feedback, drove adoption through consensus) |

---

## Earn Trust
**Principle:** Listen attentively, speak candidly, and treat others respectfully.

| Question | Best Stories |
|---|---|
| Significantly contributed to improving morale/productivity | **11** (Mentoring — helped engineers grow scope, one promoted) |
| 3 things you're working on to improve effectiveness | **4** (Standards adoption — writing better docs, incorporating cross-team feedback, pairing with other teams) |
| A time you received tough or critical feedback | **20** (Failure — PMs frustrated by caching decision, took ownership and fixed it) |

---

## Hire and Develop The Best
**Principle:** Raise the performance bar with every hire and promotion. Recognize talent, and willingness to move them throughout the organization.

| Question | Best Stories |
|---|---|
| How you help team members develop their careers | **11** (Mentoring — cross-team exposure, design doc feedback, modeling decision-making) |
| Provided feedback to develop someone's strengths | **11** (Same — specific, actionable feedback on communication framing for cross-org audience) |

---

## Think Big
**Principle:** Thinking small is a self-fulfilling prophecy. Leaders create and communicate bold directions that inspire results.

| Question | Best Stories |
|---|---|
| Radical approach to solve a big problem | **14** (Applause CQRS — introduced event sourcing paradigm to decouple shared-database architecture) |
| Took a big risk and it failed | **20** (Failure — aggressive caching was a calculated bet that didn't account for experimentation) |
