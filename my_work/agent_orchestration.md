# How I Work — Agent Orchestration

> Source material for the resume rewrite and AI-competency interview answers.
> Established: September 2026. See `job_search/round3_plan.md` for how this feeds the search.

Since ~September 2026 I work full-stack (frontend + backend) on CarGurus' AI agentic system, entirely in TypeScript. Before that, over summer 2026, I built the infrastructure and foundation for the same system.

My working method is agent orchestration across the whole lifecycle. I author the plan and own every judgment call; the writing and coding are delegated.

---

## The pipeline

| # | Step | Who |
|---|---|---|
| 1 | Gather ticket requirements; read the codebase to understand the requested change | AI |
| 2 | **Author the implementation + testing + release + monitoring plan** | **Me** |
| 3 | Validate the plan against the codebase, enrich with implementation detail; iterate on it | AI + me |
| 4 | **Adversarially stress-test the final plan against cases** | **Separate agent** |
| 5 | Write the code | AI |
| 6 | **Review the code** | **Me** |
| 7 | Double-check the code | Another agent |
| 8 | Deploy and test | Another agent |
| 9 | Resolve review comments, revisit testing | AI |
| 10 | Validate post-release; write monitoring queries; build dashboards + alerts | AI |
| 11 | Write documentation and the stakeholder release notification | AI |

**Track record:** ~2 months of this. Nothing has escaped to production.

---

## Why the structure holds

The load-bearing piece is **step 4**, and it is easy to miss why.

Steps 5–9 all validate against the plan. Agent B reviewing agent A's code answers *"does this implement the plan"* — not *"is the plan right."* Tests generated from the plan encode the plan's assumptions, so they pass. Without an independent check on the plan itself, the plan becomes an unchecked single point of failure and the defect class migrates from implementation bugs to **specification bugs** — rarer, but far more expensive and discovered much later.

Step 2 keeps origination human. Step 4 gives the plan the same adversarial treatment the code gets. That pairing is what makes the rest safe to delegate.

---

## What actually counts as signal

*"I orchestrate agents and review the output"* is table stakes and scores nothing on its own — by now everyone says it.

The signal is the **overrides**:
- where the plan-review agent surfaced a case I had missed
- where I rejected the AI's enrichment because it had misread the codebase
- where I discarded my own plan after the validation pass

With no production escapes to draw on, these are the credible evidence that judgment is being applied rather than claimed. **They decay fast — capture them while they happen.**

### Override log

<!-- Append as they happen: what the agent proposed → what was wrong with it → how it was caught → what I did instead. Date each one. -->

_(empty — start filling this during the Sept–Oct study period)_

---

## Known risks, and the answers to have ready

**Review is the only human gate on a large code volume.** Review depth degrades as volume rises — a long-standing code review finding, not an AI-specific one. If output tripled, either review got shallower or the throughput was never really 3x. Have a real answer for how review stays deep.

**Not writing code costs the friction signal.** *"This is awkward to implement, therefore the design is wrong"* only arrives while writing. Losing it removes the earliest warning on my own plans, which compounds the step-2 risk.

**"Quality is my first concern" reads as an IC virtue at Staff+.** The differentiating answer is knowing *where* to spend the verification budget, not applying maximum rigor uniformly. Expect *"how do you decide how much verification is enough?"* — and have an example of deliberately spending less.

**Cost.** The pipeline exceeds expense limits. Not presented as a strength: the org is early on token expense auditing and so am I. If asked directly, one sentence — aware, rough magnitude, accepted tradeoff — then move on. Do not lead with it.

---

## Why this matters for the search

Coinbase published their AI-era interview rebuild in July 2026, and their stated bar describes this pipeline: ~100% AI-generated code, human-reviewed, with engineers authoring specs, directing AI, reviewing AI PRs, and catching architectural errors AI introduces. Details in `companies/coinbase/prep_coinbase.md`. Their cooldown resets ~November 2026.

It is also the most directly relevant experience I have for Anthropic — an agentic system, in TypeScript, built with Claude Code daily.

Neither is reflected in any resume yet.
