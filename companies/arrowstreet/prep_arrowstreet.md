# Arrowstreet Capital — Prep Doc

> **Status:** Recruiter inbound Oct 20 (Sam Hughes, recruitment consultant). Sourcer call Oct 21 — rushy, sent two JDs. Company identity still to be confirmed in writing, but JDs are Arrowstreet reqs (R1373, R1367).
> Boston-based systematic asset manager; internal Investment Technology org; hybrid 1 day/week Boston.

---

## The two roles (different teams — ask which track the submission targets)

### R1373 — Senior SWE, Investment Platform Engineering (Shared Data Platform)

- Build/evolve the **Shared Data Platform**: dataset access, discovery, lineage, governance, ingestion, cost management, performance.
- Technical roadmap for a shared platform supporting **batch + real-time workloads**; cloud-native services, APIs, frameworks; onboarding of new datasets.
- Stack signals: AWS, Terraform/IaC, OpenAPI/FastAPI, Kafka/Kinesis. **"Python, C#, Java, Go, or similar" — Java explicitly acceptable.**
- 5+ yrs. Base band posted: $135–325K.
- **Closer to lane:** platform + APIs + real-time + stakeholders. This is the "greenfield data platform" from the original email.

### R1367 — Senior Engineer, Investment Technology Platform (Compute Platforms team)

- Compute platform, **workflow, messaging, AI and observability** systems — orchestration + infra for research.
- Heavy K8s/Docker, Terraform, CI/CD (GitLab), on-call rotation, "hardware architecture, OS, networking" proficiency.
- 8+ yrs, 4+ yrs leading architecture, 3+ yrs distributed systems. Python-primary.
- **Infra-adjacent — against the "not infra" positioning** (round3_plan), despite workflow/AI/observability overlapping the CarGurus day job.

---

## Sourcer claims (verified Oct 22)

- **Title/level: "Associate Director"** — mirrors investment-division titles; Sam claims AD = Lead/Principal externally, everyone placed at AD came from Lead/Staff/Principal. Scope: higher-level IC — design/architecture, roadmap, stakeholders, technical direction + mentoring, hands-on coding. **This resolves the level question — scope matches Principal.**
- **Comp: ~$250K base / $400K TC** (all cash, no equity). Bonus ≈ $150K (60% of base): **25% paid July, 75% EOY.** Posted base band $135–325K → $250K is *mid-band*, not top.
- Sam's pitch: 70 placements at Arrowstreet, bonus "always paid" incl. COVID/crashes; minimum = offer letter; top performers overshoot; 95% family health coverage; 7% 401k match; "top of market in Boston except big tech."
- ⚠️ **History check:** original email "~$400K total" → call "$350–400K base + 20–30% bonus" ($420–520K) → now "$250K base / $400K TC." Base was inflated ~40%; TC claim held. Treat all numbers as directional until the offer letter.
- **Open negotiation points:** base vs. top of posted band ($325K); year-1 bonus proration (joining mid-cycle — 25% July / 75% EOY timing); guaranteed minimum in offer letter; sign-on to bridge a partial first cycle.
- **Title note for the future:** "Associate Director" needs translation on future resumes ("Principal-equivalent scope") — manageable, but the scope bullet list should be documented while at the firm.

---

## Fit + career read

- **Depth axis is different, not lower.** Quant research platforms are deep in data volume, real-time correctness, compute orchestration — not payments/transaction correctness. Neither JD is a career trap at these numbers; both are respected internal-platform engineering.
- **Real risks:** (1) title runway — if Senior-title carries Staff expectations and Staff is the team ceiling, growth is lateral; (2) small user base (hundreds of internal users, not millions); (3) Python shift; (4) fund intensity + on-call (JD2 explicit).
- **Deciding question for the user:** is 5 years of data/compute platform more interesting than payments? Side projects (quant trading) suggest real interest. Comp, if real, exceeds the $300–450K target.

---

## Interview process intel (verified via Glassdoor + aggregators, Oct 24)

**Loop structure:** recruiter screen → 30-min technical screen (Python/engineering fundamentals) → 45–60 min coding (LC-mediums; explain approach + complexity while coding) → 1-hr architecture discussion with two engineers (microservices/distributed design) → 30-min culture call with senior director.

**Reported coding topics:** tree vertical-order traversal, best-time-to-buy-sell, merge intervals, BFS/graph, linked lists, hash maps, sliding window — plus practical tasks (moving-average class, basic SQL, string suffix manipulation). Difficulty ~3.5/5; one report calls the coding round "the easiest coding problem I've done."

**Prep implication:** the coding bar is LOW for a Staff candidate. Priority re-sort for Arrowstreet: **architecture discussion (SD) > culture call (behavioral) > coding.** SD prep = `design/interview/playbook.md` (data-platform topics: KV store, message queues, event pipelines, metrics — sections 32–35 especially). Behavioral = the HM map in this doc. Coding = triage pass + canonical patterns only.

## Behavioral prep (HM screen)

**The one-line story:** "You're describing the job I've been doing — building the shared platform other teams depend on — plus the domain I practice in my spare time."

**Likely HM questions → answer sources** (all in `behavioral_playbook.md`):

| Question | Answer source |
|---|---|
| Walk me through your background / why this role | Direct Questions: "Tell me about yourself" + Arrowstreet "Why this company" |
| What does your data-platform work look like at CarGurus? | Stories 3, 3b, 3c |
| Tell me about debugging a hard production problem | Story 3c (MongoDB 71K-span diagnosis) |
| How do you use AI day-to-day? | Story 19 + Direct Questions AI answer |
| How hands-on are you? (JDs emphasize hands-on coding) | Direct Questions: "Do you still write code?" — hands-on = plan authoring + full review, not typing |
| Tell me about a security-sensitive design | Story 17 |
| Why did you rebuild your trading platform? | Story 18 ("Why Rebuild" answer) |
| Tell me about a disagreement | Story 8 |
| What level/scope are you operating at? | Direct Questions: promotion answer (Principal = Staff scope) |
| Python vs Java | Direct Questions: Java-recency answer |

**Level-scope positioning:** "I'm currently Principal — that's Staff scope at most companies, and I've been operating at that scope: cross-org initiatives, architecture standards, 10+ teams. The level question matters because I want the scope to match the title — I'm not looking for a de-level, and if your Senior carries Staff scope internally, I'm happy to be evaluated against that."

**WLB/on-call probe** (ask, don't answer): on-call rotation reality, week intensity, how the platform team is valued vs. research.

## Next steps

- [x] **Behavioral docs complete (Oct 22)** — new stories 3c/17/18/19/20 in `behavioral_playbook.md`; HM question map in this doc. Remaining: mock run-through (30 min, day before HM).
- [x] Resume variant created (`resume_arrowstreet.html`, Oct 22) — quant-framed: trading language restored, data-platform summary, V1/V2 pairing explicit. **This is the version sent to the sourcer.**
- [ ] Ask the sourcer: **which req am I being submitted to?** (different teams, different fits — JD1 preferred)
- [ ] HM screen ~early Nov; technical loop **late Nov** (framed as work delivery period, never "prep")
- [ ] HM questions: what's above this level in the team; comp in writing; why greenfield now (what's being replaced); WLB/on-call reality
- [ ] If JD1 progresses: pull **D13/D14/D17** forward; add a data catalog/lineage/governance study item to `open-questions.md`
- [ ] If JD2 progresses: add a Kubernetes compute-platform study item (knowledge base is light there)
- [ ] Interview in Java — confirmed acceptable per JD1 language line; re-confirm at screen
- [ ] Personal-trading compliance: side quant platform may need disclosure at offer stage — don't raise it
