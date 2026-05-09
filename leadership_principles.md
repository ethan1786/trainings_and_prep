# Leadership Principles — Behavioral Interview Reference + Story Map

> Amazon-style leadership principles with example questions and mapped STAR stories.
> Stories are in `star_stories.md`. Each has STAR spoken-style, bullet recap, and long-form formats.
> Useful for any behavioral interview (Coinbase, Cherry, NVIDIA, etc.)
>
> **Story numbering (current):** 1=API Mod, 2=Parity, 3=MCP/AI, 4=Digital Shopping, 5=Mentoring, 6=RFCs, 7=GenAI, 8=Disagree&Commit, 9=AI Cross-Domain, 10=DGS, 11=Applause Auth, 12=Applause CQRS, 13=Toast, 14=Failure, 15=Customer Obsession, 16=Peer Conflict

---

## Customer Obsession
**Principle:** Start with the customer and work backwards — leaders obsess over customers.

| Question | Best Stories |
|---|---|
| A time you used customer feedback to drive improvement | **15** (Dealer notifications — redesigned from batch to real-time based on dealer feedback) |
| Most difficult customer interaction | **3** (MCP — competing stakeholders with conflicting needs: PMs, AI team, directors) |
| Balance needs of customer vs. business | **4** (Digital shopping — pragmatic tradeoffs to ship fast for customers during pandemic) |
| Prioritized customer over engineering convenience | **15** (Chose real-time delivery for dealers over simpler batch system) |

---

## Insists on Highest Standards
**Principle:** Have relentlessly high standards and continuously raise the bar / drive others to do the same.

| Question | Best Stories |
|---|---|
| A time you were unsatisfied with the status quo. How would you change it? | **1** (API mod — refused to accept "a bit faster," pushed for 5x latency reduction) |
| Describe the most significant improvement project you've led | **1** (API mod — full cross-org modernization, 5x latency, 99.9% avail) |
| How do you seek out feedback on performance? | **10** (DGS warmup — profiled JVM, measured cold-start vs. steady-state, load tested) |

---

## Delivers Results
**Principle:** Focus on key inputs and deliver with high quality in a timely fashion.

| Question | Best Stories |
|---|---|
| Realized halfway in it may not be the best goal | **14** (Failure — caching strategy wrong for experimentation context, pivoted) |
| A goal that took a long time to achieve | **1** (API mod — 6-month first milestone, completed ahead of schedule) |
| Delivered a project under tight deadline | **4** (Digital shopping — 0→1 product under pandemic pressure) |

---

## Are Right A Lot
**Principle:** Strong judgment and good instincts.

| Question | Best Stories |
|---|---|
| A difficult decision and how you knew it was right | **8** (Disagree & commit — structured 5-dimension analysis to push back on tech choice) |
| A decision without data | **3** (MCP — bias for action, built modular architecture before requirements were clear) |
| A bad decision and how you learned from it | **14** (Failure — aggressive caching broke A/B tests, learned to ask about mutation patterns) |

---

## Bias for Action
**Principle:** Speed is crucial — value calculated risk taking.

| Question | Best Stories |
|---|---|
| Calculated risk where speed was crucial | **4** (Digital shopping — launched with eventual consistency to ship faster) |
| Important decision without consulting your manager | **3** (MCP — chose modular architecture and delivered demo in first sprint) |
| Removed serious roadblocks preventing progress | **3** (MCP — unblocked PM/director demos by delivering working POC quickly) |

---

## Invent and Simplify
**Principle:** Expect and require innovation from yourself and those around you — always find ways to simplify.

| Question | Best Stories |
|---|---|
| Most innovative thing you've done | **7** (GenAI — hybrid rules + LLM architecture with explainability) |
| Solved a complex problem with a simple solution | **2** (Parity testing — replayed prod traffic for structural diff instead of manual QA) |
| Creative idea that was difficult to implement | **9** (AI cross-domain validation — LLM + spec validation to automate multi-team coordination) |

---

## Ownership
**Principle:** Think long term and don't sacrifice value for short-term results — there is no such thing as "not my job."

| Question | Best Stories |
|---|---|
| Took on something significant outside your responsibility | **13** (Toast — built DevOps/QA from scratch, not assigned) |
| Sacrificed short-term for long-term goal | **4** (Digital shopping — invested in feature flags + retirement playbook upfront) |
| Saw a peer struggling and stepped in | **5** (Mentoring — pulled senior engineers into cross-team problems, helped them grow) |

---

## Dive Deep
**Principle:** Stay connected to details, audit frequently, and question when metrics differ.

| Question | Best Stories |
|---|---|
| Went down several layers to figure out a problem | **10** (DGS — profiled JVM startup, found JIT + DGS lazy init as dual cold-start causes) |
| Linked two or more problems and identified underlying issue | **1** (API mod — traced sequential calls + shared timeouts + no circuit breaking as compound latency cause) |
| A metric you used to identify need for change | **1** (API mod — p99 latency + per-hop SLO budgets revealed which services were the bottleneck) |

---

## Learn and Be Curious
**Principle:** Always seeking improvement — curious about new possibilities and love to explore them. Leaders are never done learning.

| Question | Best Stories |
|---|---|
| Needed deeper subject matter expertise | **10** (DGS — learned Netflix DGS framework, federation spec, subgraph patterns from scratch) |
| Took on work outside comfort area and found it rewarding | **7** (GenAI — independent project exploring LLM architecture, Bayesian optimization) |
| Didn't know what to do next / challenging problem | **3** (MCP — new protocol, evolving SDK, no internal precedent) |
| Coolest thing you learned on your own that helped your job | **7** (GenAI — self-directed LLM exploration → directly led to MCP work and AI initiative) |

---

## Have Backbone; Disagree and Commit
**Principle:** Obligation to respectfully challenge decisions when you disagree, even when doing so is uncomfortable or exhausting. Leaders have conviction and are tenacious. They do not compromise for the sake of social cohesion. Once a decision is made, commit fully.

| Question | Best Stories |
|---|---|
| Strongly disagreed with your manager/leader | **8** (Pushed back on senior leader's tech stack choice with structured 5-dimension analysis) |
| Unpopular stance in a meeting with peers/leaders | **8** (Same — advocated against momentum with data) |
| Went along with group decision even if you disagreed | **8** (Committed fully on testing strategy decision where group went different direction) |
| Disagreed with a peer — how did you resolve it? | **16** (Service boundary disagreement — found real concern, proposed compromise, documented as ADR) |
| Submitted good idea and faced resistance | **6** (RFC process — pre-socialized proposals, incorporated feedback, drove adoption through consensus) |

---

## Earn Trust
**Principle:** Listen attentively, speak candidly, and treat others respectfully.

| Question | Best Stories |
|---|---|
| Significantly contributed to improving morale/productivity | **5** (Mentoring — helped engineers grow scope, one promoted) |
| How do you build trust with new teams? | **6** (RFCs — pre-socialized, incorporated feedback, committed to group decisions publicly) |
| A time you received tough or critical feedback | **14** (Failure — PMs frustrated by caching decision, took ownership and fixed it) |
| Resolved a conflict between two people/teams | **16** (Peer conflict — 1-on-1 to find real concern, proposed compromise both sides accepted) |

---

## Hire and Develop The Best
**Principle:** Raise the performance bar with every hire and promotion. Recognize talent, and willingness to move them throughout the organization.

| Question | Best Stories |
|---|---|
| How you help team members develop their careers | **5** (Mentoring — cross-team exposure, design doc feedback, modeling decision-making) |
| Provided feedback to develop someone's strengths | **5** (Same — specific, actionable feedback on communication framing for cross-org audience) |
| Raised the engineering bar for the org | **1** (API mod influence layer — RFCs, standards, paired with other teams) |

---

## Think Big
**Principle:** Thinking small is a self-fulfilling prophecy. Leaders create and communicate bold directions that inspire results.

| Question | Best Stories |
|---|---|
| Radical approach to solve a big problem | **9** (AI cross-domain validation — using LLM + MCP to automate multi-team coordination) |
| Took a big risk and it failed | **14** (Failure — aggressive caching was a calculated bet that didn't account for experimentation) |
| Proposed something ambitious that others were skeptical of | **1** (API mod — proposed full modernization of highest-traffic page, some thought it was too risky) |
