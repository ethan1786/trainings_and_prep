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

## Sourcer claims (unverified — pin with HM, get in writing at offer)

- "These are Staff/Principal level, the highest level in the team, with direct leadership on design."
- "Comp is all cash: $350–400K base + 20–30% bonus" → **$420–520K total.**
- ⚠️ Discrepancies to note: posted titles are "Senior," posted base band tops at **$325K**; the Oct 20 email said "~$400K total." The numbers have drifted *up* in the sourcer's mouth. Possible band-breaking for exceptional candidates — or optimism. No equity (all cash); employee-owned firm — probe profit-sharing at HM stage.

---

## Fit + career read

- **Depth axis is different, not lower.** Quant research platforms are deep in data volume, real-time correctness, compute orchestration — not payments/transaction correctness. Neither JD is a career trap at these numbers; both are respected internal-platform engineering.
- **Real risks:** (1) title runway — if Senior-title carries Staff expectations and Staff is the team ceiling, growth is lateral; (2) small user base (hundreds of internal users, not millions); (3) Python shift; (4) fund intensity + on-call (JD2 explicit).
- **Deciding question for the user:** is 5 years of data/compute platform more interesting than payments? Side projects (quant trading) suggest real interest. Comp, if real, exceeds the $300–450K target.

---

## Behavioral prep (HM screen)

**The one-line story:** "You're describing the job I've been doing — building the shared platform other teams depend on — plus the domain I practice in my spare time."

**Likely HM questions → answer sources** (all in `behavioral_playbook.md`):

| Question | Answer source |
|---|---|
| Walk me through your background / why this role | Direct Questions: "Tell me about yourself" + Arrowstreet "Why this company" |
| What does your data-platform work look like at CarGurus? | Stories 3, 3b, 3c |
| Tell me about debugging a hard production problem | Story 3c (MongoDB 71K-span diagnosis) |
| How do you use AI day-to-day? | Story 19 + Direct Questions AI answer |
| Tell me about a security-sensitive design | Story 17 |
| Why did you rebuild your trading platform? | Story 18 ("Why Rebuild" answer) |
| Tell me about a disagreement | Story 8 |
| What level/scope are you operating at? | Direct Questions: promotion answer (Principal = Staff scope) |
| Python vs Java | Direct Questions: Java-recency answer |

**Level-scope positioning:** "I'm currently Principal — that's Staff scope at most companies, and I've been operating at that scope: cross-org initiatives, architecture standards, 10+ teams. The level question matters because I want the scope to match the title — I'm not looking for a de-level, and if your Senior carries Staff scope internally, I'm happy to be evaluated against that."

**WLB/on-call probe** (ask, don't answer): on-call rotation reality, week intensity, how the platform team is valued vs. research.

## Next steps

- [ ] **Behavioral update in progress — see `behavioral/story_update_plan.md`** (new stories for this year's work; HM-ready by early Nov)
- [x] Resume variant created (`resume_arrowstreet.html`, Oct 22) — quant-framed: trading language restored, data-platform summary, V1/V2 pairing explicit. **This is the version sent to the sourcer.**
- [ ] Ask the sourcer: **which req am I being submitted to?** (different teams, different fits — JD1 preferred)
- [ ] HM screen ~early Nov; technical loop **late Nov** (framed as work delivery period, never "prep")
- [ ] HM questions: what's above this level in the team; comp in writing; why greenfield now (what's being replaced); WLB/on-call reality
- [ ] If JD1 progresses: pull **D13/D14/D17** forward; add a data catalog/lineage/governance study item to `open-questions.md`
- [ ] If JD2 progresses: add a Kubernetes compute-platform study item (knowledge base is light there)
- [ ] Interview in Java — confirmed acceptable per JD1 language line; re-confirm at screen
- [ ] Personal-trading compliance: side quant platform may need disclosure at offer stage — don't raise it
