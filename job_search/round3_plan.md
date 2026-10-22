# Job Search — Round 3 (Active Plan)

> **START HERE in a new session.** This is the working doc: current state, corrected diagnosis, action items, and decisions already made.
> Last updated: September 11, 2026
> History for Rounds 1–2 lives in `archive/`. Re-apply schedule in `reapply_timeline.md`. Repo map in `../README.md`.

---

## Snapshot

| | |
|---|---|
| **Who** | Principal SWE at CarGurus. 13 years. Java backend, distributed systems, payments. |
| **Now doing** | Full-stack (frontend + backend) on CarGurus' AI agentic system. **Entirely TypeScript.** Shifted ~Sept 2026; summer was infra/foundation work on the same system. |
| **Target level** | Senior/Staff at higher-bar companies (Senior there = Staff scope/comp elsewhere) |
| **Target comp** | $300–450K+ TC |
| **Lane** | Product backend — payments, commerce, transactions, state machines, API/GraphQL layers. **Not** infra, **not** security/IAM, **not** ML. |
| **Status** | Round 3 restarted September 11, 2026. Currently in a Sept–Oct foundations study phase. |

---

## The Diagnosis — corrected September 2026

**Round 1's conclusion was:** *"The gap is NOT knowledge — it's delivery. I know all the correct answers but deploy them too fast."*

**That was incomplete.** The delivery symptom was concealing genuinely missing WHY. There was no reasoning to narrate because pattern recall had substituted for understanding.

Evidence:
- *"Use WebSocket because crypto exchanges do"* — not a presentation failure. The product requirements that justify the choice were never articulated because they weren't known.
- NVIDIA: said "topological sort" instantly, interviewer had to probe. First instinct was *"this is the typical pattern, what else is there to say?"* — that reaction is the tell.
- Coinbase feedback: *"more proactive on requirements, better tradeoff clarification."*

**Consequence for prep:** foundations study is the fix, not presentation polish. Delivery practice on top of missing knowledge just produces smoother hand-waving. Sequence is foundations → then delivery drills.

---

## Current Phase — Sept–Oct 2026 Foundations Study

**This is already running in `design/study/`** — a living knowledge base (2676 lines), an append-only session log (19 entries since Aug 11), `corrections.md`, and `open-questions.md`, with a defined per-session working loop in `design/study/SETUP.md`.

**The method:** read the basics of each technology/tool/database in the stack, then pair it with **how that decision was actually made at CarGurus** — so it becomes his story rather than textbook knowledge.

Why this beats textbook study: a real decision carries its constraints with it (team skills, existing infra, deadline, cost ceiling, sunk investment). "Postgres vs Mongo" in the abstract has no right answer, which is why reciting one reads as thin. Staff+ rounds test reasoning *under constraints*, and real decisions are the only free source of constraints. It also survives depth — textbook knowledge collapses at the third consecutive "why."

**Capture two columns per item, not one** (the existing `In practice (CG):` convention already does this):
1. **WHY depth** — when it's the right choice, when it's wrong, what the alternatives are, how it fails
2. **When it mattered to my area** — the moment this decision had a consequence for his product

Column 1 alone is still someone else's knowledge with a CarGurus label on it. Column 2 is what makes it his.

**Scope guard:** "every technology" is unbounded and will eat two months. Bound it to the items that appear in his own stack and his own stories — the agentic system (MongoDB, Redis, LLM providers, circuit breakers, connection pools), the payments/Java history, and what recurs in design rounds. `design/study/open-questions.md` is the queue; work it rather than browsing.

**Forcing function — already built in.** The log template's *"The wrong turn worth keeping"* and *"Pressure I applied"* sections are exactly this, and `corrections.md` is the record. Reading reliably produces the *feeling* of understanding; the test isn't "did I read it," it's **can I take three consecutive whys without reaching for a pattern name.** Confidence labels (`verified` / `inferred` / `unverified`) keep that honest.

**Handling decisions other teams made** — honest framing, already settled:
> Another team owned it. I followed the process closely to understand how and why it was done, and whether it would affect my product area. Being aware of and actively following technical decisions is how I operate as a Principal here — so when a project lands on me, I pick it up fast and make sound calls with that context already in place.

Two cautions on that story:
- "Being aware" is a claim about internal state and can't be scored. It needs one instance where the awareness **produced an outcome** — raised a concern that changed another team's design, pre-adapted his area before a decision landed, made a correct week-one call that would have cost someone else a month, or stopped his team building something incompatible. **Open item — find one.**
- Don't let this become the dominant mode of technical depth, or the loop reads *well-informed observer*. Headline depth must be decisions he owned.

---

## How I Work Now — the AI orchestration pipeline

Source material for AI-competency stories and the resume rewrite. **Full detail and the override log: `behavioral/behavioral_playbook.md`, Story 19.**

1. AI gathers ticket requirements, reads codebase to understand the change
2. **He authors** the implementation + testing + release + monitoring plan
3. AI validates the plan against the codebase, enriches with implementation detail; he iterates
4. **A separate agent adversarially stress-tests the final plan** against cases
5. Agent writes the code
6. **He manually reviews**
7. Another agent double-checks
8. Deploy + test with another agent
9. Agents resolve review comments, revisit testing
10. Post-merge: AI validates the release, writes monitoring queries, builds dashboards + alerts
11. AI writes documentation and the stakeholder release notification

**Track record:** ~2 months, nothing escaped to production.

**What makes this structurally sound:** human origination of the plan, plus independent adversarial review *of the plan itself* — not just of the code. Without step 4 the plan would be an unchecked single point of failure, and every downstream agent would validate against it rather than question it.

**What actually scores in an interview:** not "I orchestrate agents and review output" — that's table stakes and worth nothing on its own. The signal is the **overrides**: where the plan-review agent surfaced a case he'd missed, where he rejected AI enrichment because it misread the codebase, where he discarded his own plan after validation. No prod escapes to draw on, so these override moments are the credible evidence.

**Known risks to have answers for:**
- Review is the only human gate on a large code volume, and review depth degrades as volume rises
- Not writing code costs the friction signal ("this is awkward to implement, so the design is wrong")
- "Quality is my first concern" reads as an IC virtue at Staff+; the differentiating answer is knowing *where* to spend verification budget. Expect *"how do you decide how much verification is enough?"* and have an instance of deliberately spending less.

---

## Action Items

### A. During the study phase (Sept–Oct) — do these now

- [ ] **Keep a running override log.** Decaying asset — these specifics will be gone by November. Capture: what the agent proposed, what was wrong with it, how it was caught, what he did instead.
- [ ] **Find one instance where cross-team awareness produced a concrete outcome** (see cautions above)
- [x] ~~Fill in `my_work/TODO_details.md`~~ **Obsolete (Oct 22)** — stories now carry their own verified metrics (3c: 71K spans/30s/200–400ms; 3b: 46–59% latency etc.). File removed.
- [ ] **Re-warm Java.** Stale in daily practice since ~March — zero Java at work now. Matters for Netflix and any Java shop.
- [ ] Identify the actual knowledge holes as they surface, so the eventual WHY-depth list is targeted

### B. Anthropic — highest fit, gated on location

**Corrected September 11, 2026 after checking the live board.** The earlier premise ("no reqs yet, wait for the hiring wave") was wrong. Anthropic has ~200 engineering roles open *now*, several dead-center in lane:

| Role | Location | Note |
|---|---|---|
| **Staff SWE, Billing Platform** | SF / NYC / SEA | Payments + commerce. Best lane match in the entire pipeline, any company. |
| Staff+ SWE, Backend | SF / NYC / SEA | |
| Staff+ SWE, Claude Managed Agents | SF / NYC | Agentic systems = current day job |
| Senior Staff SWE, API | SF / NYC | |
| Senior / Staff+ SWE, Full-stack | SF / NYC / SEA | |

**The gate is location, not the coding bar.** Product engineering at Anthropic is onsite SF/NYC/SEA; remote-friendly roles cluster in Public Sector, People Products, Data Infrastructure, and Inference Velocity, mostly with travel requirements. Boston is already in their office filter, but the roles tagged Boston today are IT Systems Engineer, Technical Deployment Lead, Head of GovTech Sales, Executive Services PM, and Physical Security Design Lead — **GTM, deployment, IT and physical security, not product engineering.** Exactly one engineering-titled Boston role exists and it's IT/mobile-client under Security.

**His decision (Sept 11):** will **not** relocate to SF or NYC. **Cambridge office 3 days/week is acceptable.** Plans to wait ~1–2 months, then apply, and raise Boston basing if they reach out.

**Trigger to watch is req composition, not the calendar.** If engineering titles beyond IT start appearing for Boston, that's the green light and it may come before November. If Boston fills out with sales and enterprise deployment only, product engineering isn't coming and Anthropic drops down the list regardless of fit.

**Sequencing note:** waiting does not improve eligibility — an SF/NYC/SEA tag today will still be there in November; whether Boston gets product eng is Anthropic's call, not a function of his timing. The wait buys prep; it costs open reqs closing. Also: ask the location question as an *inquiry* (recruiter note or connection: "is this org open to a Boston-based candidate?") rather than applying to an onsite-tagged role and hoping to convert it later. Recruiters screen on location early, so applying-and-hoping yields a fast no that teaches nothing.

**Open:** does he have any Anthropic connection? The ask would be unusually cheap and specific — not "refer me," just "is this org open to Boston." Unlike the Netflix situation, that burns nothing.

**Repo had zero Anthropic material** until today; `companies/anthropic/prep_anthropic.md` is now a stub to build out.

- [ ] Set up a job alert for Anthropic Boston + remote engineering reqs
- [ ] Create `companies/anthropic/` — prep doc, resume variant, questions
- [ ] Research their interview format (not yet verified — don't assume it resembles Coinbase's or OpenAI's)
- [ ] Positioning: an agentic system, in TypeScript, built with Claude Code daily is about as directly relevant as experience gets. This is the strongest target in the pipeline on fit.
- [ ] Prep *before* reqs post. Rushing a vague application after the fact is the exact failure mode that wasted the Netflix referral.

### C. Resume & positioning

All four `resume_*.html` variants predate June 2026 and describe a Java backend engineer. None mention full-stack, TypeScript, or the agentic system.

- [ ] New variant leading with full-stack TypeScript + AI agentic systems + agent orchestration
- [ ] Anthropic-specific resume + cover
- [ ] Decide how to handle the Java-recency question — 13 years of Java, but the last 6+ months are TypeScript. Not fatal; needs a prepared answer, not improvisation.
- [ ] Update the `## Resume Strategy` table in `archive/round2_todo.md` once a new variant exists

### D. Story updates needed (from the Sept 11 conversation)

- [ ] **Convert `design/study/corrections.md` into design-round narration.** This is the most interview-valuable and least-used asset in the repo: *"the intuitive answer is X — that's what I believed — but it's wrong because Y"* IS narrating the journey. Same for the log's "Pressure I applied" sections, which are pre-built answers to interviewer pushback. 2676 lines of reference and 19 log entries currently reach zero interview material.
- [ ] Add AI-competency material to `behavioral/behavioral_playbook.md`, built on override moments — not on "I use AI"
- [ ] Rewrite the cross-team awareness story to include a produced outcome
- [ ] Add an answer to "how do you decide how much verification is enough?" including a case of deliberately spending less
- [ ] Prepare a defensible one-liner on token cost (see decisions below) — aware, rough magnitude, accepted tradeoff. Don't lead with it; just don't be caught flat.
- [ ] Make sure headline depth stories are ones he owned: the agent pipeline, connection pool starvation fix, circuit breakers, cost/token reduction work

### E. Coding practice (Sept–Oct)

Record shows coding was mostly fine — Coinbase coding OK, NVIDIA Q1 clean, Cherry coding strong. Real gaps are narrow: **LC Hard under pressure** (NVIDIA Q2), the *"recognized too fast, had to be probed"* narration problem, and a **format shift** he hasn't practiced.

The delegation split for AI-enabled rounds:
- **Hand-write:** the core algorithm. It carries the signal, and delegating it leaves nothing to narrate — which is the exact thing he's been dinged on. Also anything under ~30 lines he knows cold; prompting is genuinely slower there and his instinct on that is correct.
- **Delegate:** edge-case test generation (best available delegation — faster, low-risk, demonstrates verification instinct), scaffolding/fixtures/input parsing, API and syntax recall for Java, and repo navigation.
- **Say the decision out loud:** *"I'll write the core logic myself since that's where the thinking is — once the shape settles I'll have the agent generate edge-case tests."* That sentence is the judgment being scored.

- [ ] Practice on a **repo-based, timed** exercise — not blank-slate LC. Take a real work ticket, box it to 45 minutes, narrate every delegation decision aloud. His day job is already this; the missing constraints are the clock and speaking.
- [ ] LC Hard specifically
- [ ] Note the two Coinbase rounds differ: pre-screen is *"AI-Assisted Coding, AI tools throughout"*; onsite coding is *"AI Support & Reference enabled"* + repo-based debugging. Both allow AI. Details in `companies/coinbase/prep_coinbase.md`.

### F. Company targets & timing

| Company | Status | Timing |
|---|---|---|
| **Anthropic** | ~200 eng roles open now; in-lane ones are SF/NYC/SEA. Boston has no product-eng reqs yet. | Best fit, gated on location. Watch what Boston posts next. Apply ~Nov. |
| **Coinbase** | Rejected May 2026 (Staff). AI-native format already documented in prep doc. | Cooldown resets **~Nov 2026**. Strong re-target — his current work matches their published bar. |

**The convergence point has moved to mid-Nov / early Dec** (decided Sep 30 — no outreach before then). Working backwards, that makes **resume done by early-to-mid November** the hard deadline.
| **Meta** | Applied, no recruiter contact | Passive. Prep docs exist. |
| **Netflix** | Two referred apps got no response. Referral connection **resting until ~Feb 2027**. | Cold apply anytime — nothing blocks it. **JR41744 Pricing, Catalog and Offers (USA Remote)** was the best in-lane fit and was never applied to. Verify still open. |
| **Google** | Failed hiring assessment April 2026 | ~Q1 2027 |
| **Cherry** | Rejected, but HM said stay connected | Anytime |
| **Stripe / Affirm / Reddit / Dropbox / Airbnb** | Cold apps, all silent since May | Re-apply candidates at Senior. See `reapply_timeline.md`. |

### G. Deferred until after the study phase — do not re-offer unprompted

- [ ] Build the bounded 12–15 item WHY-depth list (each item = why-depth + "when this mattered to my area")
- [ ] Resume rewrite session
- [ ] Timed AI-enabled mock rounds with live pushback

---

## Decisions Already Made — don't re-litigate

- **Token spend is not a story.** It exceeds expense limits; his org is early on token expense auditing and so is he. Not presented as a strength. Only needs a defensible one-sentence answer if asked directly.
- **Netflix referral connection rests ~6 months** (until ~Feb 2027). Two referred applications got no response; the failure was his own targeting, not the connection. Next ask must arrive with a specific, obviously-matched req.
- **No claiming ownership of other teams' decisions.** Honest framing only (see study phase section).
- **Apply at Senior level** to widen the funnel — worked for Coinbase and NVIDIA in Round 1. Companies level up strong candidates in the loop.
- **Foundations before delivery polish.** See corrected diagnosis.
- **Study through Sept–Oct** before resume/mock/list work.
- **No outreach or re-applications until mid-Nov / early Dec (decided Sep 30).** Sickness shifted the prep start ~2 weeks; the wait buys prep runway (6–8 weeks by then) and lets old applications cool. **Exception:** if a dead-center Anthropic Boston product-eng req appears before then, the req-composition trigger overrides the calendar (§B).

---

## Open Questions

1. ~~Is there a concrete instance where following another team's decision produced an outcome for his area?~~ **Answered Oct 22:** VOC routing data-integrity catch — studied the AWN/VOC engine instead of treating it as a black box, found reusing AI_DISCOVERY would contaminate Discover's VoC data, changed the design to config-driven routing with a dedicated area (PR merged). Story 20 in `behavioral_playbook.md`, with alternates: dealer-review critical-path removal, Ontario contract, financing-auth pre-adaptation.
2. What are the actual knowledge holes? (Surfaces during study; feeds the deferred list.)
3. How to answer the Java-recency question.
4. What does Anthropic's interview process actually look like? (Unverified.)

---

## Doc Map

| Need | File |
|---|---|
| Round 1–2 history, results, lessons | `job_search/archive/round2_todo.md` |
| Re-apply schedule, cooldowns | `job_search/reapply_timeline.md` |
| STAR stories, LP mapping | `behavioral/behavioral_playbook.md` |
| Design mental model + delivery | `design/interview/playbook.md` |
| Patterns, constraint→solution mapping | `design/study/design_knowledge_base.md` (live, 2676 lines) |
| **Why I was wrong before** — best narration source | `design/study/corrections.md` |
| Study session reasoning paths | `design/study/log/` (19 entries) |
| Payments domain walkthrough | `design/interview/domain_playbook.md` |
| Java depth | `languages/java_playbook.md` |
| Coinbase AI-native interview format | `companies/coinbase/prep_coinbase.md` |
| CarGurus agentic system detail | `behavioral/behavioral_playbook.md` Stories 3, 3b, 3c |
| How I work now; override log | `behavioral/behavioral_playbook.md` Story 19 |
| Coding patterns + practice problems | `coding/` |
