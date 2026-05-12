# Platform / Infrastructure Interview Angle

> Shared context for HashiCorp/IBM and NVIDIA interviews.
> Different mindset from Coinbase/Cherry (product-driven, consumer-facing).
> Use this to switch context before Wed May 13 (HashiCorp) and Thu May 14 (NVIDIA).

---

## The Mindset Switch

| | Product-Driven (Coinbase, Cherry) | Platform/Infra (HashiCorp, NVIDIA) |
|---|---|---|
| **Customer** | End user / consumer / dealer | Other engineers / internal teams |
| **Success metric** | Feature shipped, revenue, conversion | Zero breaking changes, uptime, reliability |
| **Speed vs quality** | Speed often wins (validate fast, iterate) | Quality always wins (you break everyone) |
| **Ambiguity source** | "What should we build?" (product/market) | "How should we build it right?" (technical depth) |
| **Worst outcome** | Bad feature (revert, experiment failed) | Bad API / bad contract (stuck with it forever) |
| **Ownership means** | Ship fast, retire experiments safely | Keep it running, don't break consumers |
| **Communication** | Align product/frontend/data eng on what | RFCs + design docs for HOW, API contracts for consumers |
| **What impresses** | Pragmatic tradeoffs under business pressure | Technical rigor, backward compatibility, operational excellence |

---

## "Why leave?" / "Why come here?" — Reframed

**Product angle (Coinbase/Cherry):**
> "I've outgrown the problems. I want higher stakes and larger scale."

**Platform/infra angle (HashiCorp/NVIDIA):**
> "I want more technical depth. After years of broad product work — touching frontend, backend, product, data — I want vertical technical ownership. I want to go deep on a single domain, own it end-to-end in production, and build something that's rock-solid and relied upon by thousands of engineers. Platform infrastructure is where my experience and my interest converge."

---

## Key Messages for Platform/Infra Interviews

1. **"Consumer perspective is my edge"** — "Most infra engineers have only built infrastructure. I've also been the consumer — I've depended on Terraform, Keycloak, Kafka, and API gateways to ship products. I know what frustrates consumers of platform tools: breaking changes without migration paths, poor error messages, undocumented edge cases. I bring that consumer empathy to the builder side — I'll build the infra I wish I had."

2. **"Solid first, fast second"** — "I don't ship until it's right. When other engineers depend on your infrastructure, a bad release isn't a rollback — it's a breaking change you live with forever."

2. **"Depth over breadth"** — "I've done broad product work. Now I want to go deep — own a domain vertically, understand it at every layer, and build infrastructure that's authoritative."

3. **"Ownership = operational excellence"** — "I own it in production. Dashboards, on-call, SLOs, incident response. Not just 'I shipped it' but 'I keep it running at 99.99%.'"

4. **"Communication = API contracts and design docs"** — "My communication is aimed at engineering consumers. How do I evolve this API without breaking 500 integrations? How do I write a design doc that other platform engineers can review and trust?"

5. **"Platform infrastructure has a higher bar"** — "You can't move fast and break things when your users are other engineers building on your foundation. I optimize for correctness and stability first, velocity second."

---

## BQ Stories — Reframed for Platform/Infra

Same stories, different emphasis. Lead with the TECHNICAL decision and RELIABILITY outcome, not the cross-org collaboration.

| Story | Product Angle (Coinbase/Cherry) | Platform/Infra Angle (HashiCorp/NVIDIA) |
|---|---|---|
| **Story 1 (API Mod)** | "Led 10 teams, drove consensus, shipped ahead of schedule" | "Built platform infrastructure that 10+ teams depend on. Per-service SLOs, circuit breakers, zero regressions during rollout. Parity testing guaranteed correctness." |
| **Story 4 (Digital Shopping)** | "Shipped 0→1 under pressure, cleared ambiguity with product" | "Designed transaction state machine with strong consistency for money flows. Chose monolith-first because operational simplicity mattered more than architectural purity." |
| **Story 8 (GraphQL)** | "Disagreed, committed, helped succeed" | "Made a technical judgment call about performance (sync hop in critical path). Proved it with a deployed dev router and real measurements. Let data decide, not opinions." |
| **Story 11 (Applause Auth)** | Brief reference for identity background | **LEAD STORY** — "Built production IAM platform from scratch. Keycloak SSO, RBAC at gateway, mTLS service mesh. Dual-auth bridge for zero-downtime migration. Zero SLA violations." |
| **Story 13 (Toast)** | "Startup builder, wore many hats" | "Built core infrastructure from scratch — deployment pipelines, API gateway, monitoring — before dedicated teams existed. Foundational platform that scaled with the company." |
| **Story 14 (Failure)** | "Learned to consider peak traffic" | "Learned that operational planning matters as much as architecture. Connection pool starvation taught me to design for peak × resource ceilings — directly shaped my later work with bulkheads and per-service isolation." |

---

## Direct Questions — Platform/Infra Version

**"Tell me your strengths."**
> "Technical depth combined with operational ownership. I don't just design systems — I keep them running. I think in terms of SLOs, failure modes, and backward compatibility. And I communicate technical decisions through design docs and RFCs that other engineers can trust and build on."

**"What are you looking for in your next role?"**
> "Vertical technical depth. I've spent years doing broad product work — touching every layer, every team. Now I want to go deep on a single domain, own it completely, and build platform infrastructure that's relied upon by thousands of engineers. I want the bar to be correctness and reliability, not just shipping speed."

**"How do you make technical decisions?"**
> "For platform infrastructure, I start with: what are the breaking change implications? Who depends on this? What's the backward compatibility story? Then I evaluate options through the lens of reliability and maintainability, not just performance or delivery speed. I document my reasoning in a design doc, get reviews from consumers of the platform, and only commit when the contract is right — because changing it later is 10x harder."

**"What does ownership mean to you?"**
> "Owning it in production. Not just 'I built it and moved on' — but I monitor it, I'm on-call for it, I know what breaks it and how to fix it at 3 AM. For platform infrastructure, ownership means: if something I built causes an outage for a team building on top of me, that's MY problem to solve."

---

## AI & Depth — If It Comes Up

**If asked "how do you see AI changing engineering?":**
> "AI raises the floor — anyone can generate CRUD code now. But it doesn't raise the ceiling: system design judgment, operational reliability, deep domain expertise. That's why I'm drawn to platform infrastructure — the value is in depth and judgment, not code output volume. AI is great at generating well-known patterns; it can't make architectural judgment calls, own production reliability, or understand why a system was designed a certain way."

**If asked "why platform/infra?"** (weave in as one reason):
> "Part of it is where I see engineering heading. As AI makes surface-level code generation commodity, the differentiator becomes depth — understanding a domain deeply enough to make decisions AI can't. Platform infrastructure is where that expertise matters most."

**Rules:**
- Don't bring up unprompted as "why I'm switching" — sounds defensive
- Use only if they ask about AI or if it fits naturally into "why depth?"
- One sentence max in passing, full answer only if directly asked

---

## What NOT to Say in Platform/Infra Interviews

- ❌ "I shipped fast under business pressure" — sounds like you cut corners
- ❌ "I worked with product to define requirements" — they don't have product managers the same way
- ❌ "We launched on timeline" — they care about "it hasn't broken in 2 years"
- ❌ "I cleared ambiguity with stakeholders" — reframe as "I wrote the design doc that defined the technical direction"

## What TO Say

- ✅ "I built infrastructure that other teams depend on"
- ✅ "Zero regressions during the migration"
- ✅ "I own it in production — dashboards, SLOs, on-call"
- ✅ "I design for backward compatibility because my consumers can't absorb breaking changes"
- ✅ "I proved my position with measurements, not opinions"
- ✅ "I optimize for correctness first, speed second"

---

## Quick Pre-Interview Checklist

Before HashiCorp or NVIDIA interviews, re-read this doc and ask yourself:
- [ ] Am I leading with TECHNICAL depth (not cross-org collaboration)?
- [ ] Am I emphasizing RELIABILITY and CORRECTNESS (not shipping speed)?
- [ ] Am I framing ownership as OPERATIONAL (not just delivery)?
- [ ] Am I using the Applause auth story as a lead (not Toast/Digital Shopping)?
- [ ] Is my "why this company" about DEPTH and PLATFORM (not scale or business impact)?
