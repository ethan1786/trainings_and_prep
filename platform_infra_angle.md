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

## Direct Questions — Platform/Infra Version (Full Coverage)

### About You

**"Tell me your strengths."**
> "Technical depth combined with operational ownership. I don't just design systems — I keep them running. I think in terms of SLOs, failure modes, and backward compatibility. And I communicate technical decisions through design docs and RFCs that other engineers can trust and build on. Plus, I bring a consumer perspective — I've depended on platform infrastructure (Terraform, Keycloak, Kafka) for years, so I know what good infra feels like from the user side."

**"Why should we hire you?"**
> "I bring two things most infra candidates don't have together. First, I've built production security and identity infrastructure — Keycloak SSO, RBAC at the API gateway, mTLS service mesh, zero-downtime auth migration. That's not theoretical — I operated it in production. Second, I've been a platform consumer for 13 years — I know what frustrates engineers about the tools they depend on. Breaking changes without migration paths, poor error messages, missing docs. I'll build the infra I wish I had. Most candidates have built infrastructure; few have been on both sides."

**"Tell me your weaknesses."**
> "I used to overweight design elegance over operational depth. I'd focus on getting the architecture right — clean abstractions, good patterns — but not go deep enough on how it would behave under production stress. Early at CarGurus I deployed a Mongo collection with solid design but sized for average traffic — it fell over during a peak spike from connection pool starvation. The architecture was fine; the operational depth wasn't. Since then, I've shifted to 'design is half the job — the other half is understanding every failure mode at every layer.' That's why I now think in terms of resource ceilings, peak-to-average ratios, and bulkheaded isolation."

**"Tell me about yourself."**
> "Staff/Principal backend engineer, 13 years, focused on platform infrastructure and reliability. Three chapters: early engineer at Toast where I built core infrastructure from scratch — deployment pipelines, API gateway, monitoring — before dedicated teams existed. Then Applause where I led security infrastructure modernization — Keycloak SSO, OAuth/SAML federation, Kong API gateway with custom RBAC, service mesh with mTLS. For the last 6 years at CarGurus, I've been the platform technical lead — redesigned the highest-traffic API with per-service SLOs, circuit breakers, and zero-regression rollout. I build infrastructure other engineers depend on."

**"Why are you leaving?"**
> "I want vertical technical depth. After years of broad product work — touching frontend, backend, product, data — I want to own a single domain deeply. I want sustained ownership where I can stay with a system through multiple evolution cycles, not just build it and move to the next product feature. Platform infrastructure is where my experience and interest converge — I want to build something that's rock-solid and relied upon by thousands of engineers."

**"Why this company?"**
> - **HashiCorp/IBM:** "I use Terraform daily — I know the HashiCorp ecosystem from the consumer side. My auth background (Keycloak, Kong, mTLS) maps directly to Vault and Boundary. I want to go from being a consumer of great infrastructure to building it. IBM's backing gives the team stability to invest long-term in getting things right."
> - **NVIDIA:** "The platform challenge at GPU-cluster scale is genuinely interesting — resource scheduling, fleet health, multi-tenancy. My distributed systems background translates directly. I want to build infrastructure where reliability and efficiency both matter because GPU time is expensive."

### Career & Growth

**"Why haven't you been promoted?"**
> "My title is Principal at CarGurus, which maps to Staff at most larger companies. I've been operating at that scope — platform architecture, SLO frameworks, cross-team standards. The honest answer: the next level requires sustained depth on a single company-critical system, and at CarGurus I've been spread across product features. That's exactly why I'm here — I want a role where I can go deep on one domain and own it for years, rather than broad impact across many surfaces."

**"Where do you see yourself in 5 years?"**
> "As the technical authority on a critical infrastructure domain. The person other engineers come to because I understand the system at every layer — from the API contract down to the failure modes at 3 AM. Whether that's through an IC path or engineering management depends on where I can have the most impact. What I know for sure: I want depth, sustained ownership, and a system I'm proud to keep running."

**"What does your first 90 days look like?"**
> "First 30 days: learn the system deeply. Read the code, understand the architecture, trace requests end-to-end, read past incident reports and design docs. Ship something small to learn the deploy process and build credibility. Days 30-60: identify reliability gaps or operational improvements — things that have been accepted as normal but shouldn't be. Days 60-90: propose a fix through the team's design doc process, get reviews from the team, and start executing. I don't come in with an agenda — I come in with deep curiosity about why the system is the way it is."

### Role & Style

**"What are you looking for in your next role?"**
> "Vertical technical depth. I've spent years doing broad product work — touching every layer, every team. Now I want to go deep on a single domain, own it completely, and build platform infrastructure that's relied upon by thousands of engineers. I want the bar to be correctness and reliability, not just shipping speed. And I want sustained ownership — stay with a system long enough to see it through multiple evolution cycles."

**"What's your leadership style?"**
> "For platform infrastructure: lead with rigor. I write the design doc that defines the technical direction, get reviews from the right people, and only commit when the contract is right. I don't mandate — I earn credibility by showing my work (measurements, prototypes, documented tradeoffs). When I disagree, I prove it with data, not opinions. When I'm overruled, I commit fully and help the decision succeed."

**"What role do you play on a team?"**
> "The person who owns the hardest technical problems and makes the system more reliable. I go deep where others skim the surface — profiling, root-cause analysis, failure mode enumeration. But I also multiply the team: I write design docs that become reference material, I define SLOs that give everyone shared language for reliability, and I mentor engineers to think about operational excellence, not just feature delivery."

**"How do you make technical decisions?"**
> "For platform infrastructure, I start with: what are the breaking change implications? Who depends on this? What's the backward compatibility story? Then I evaluate options through the lens of reliability and maintainability, not just performance or delivery speed. I document my reasoning in a design doc, get reviews from consumers of the platform, and only commit when the contract is right — because changing it later is 10x harder."

**"What does ownership mean to you?"**
> "Owning it in production. Not just 'I built it and moved on' — but I monitor it, I'm on-call for it, I know what breaks it and how to fix it at 3 AM. For platform infrastructure, ownership means: if something I built causes an outage for a team building on top of me, that's MY problem to solve."

### Situational

**"How do you handle disagreements with your manager?"**
> "I present my case with data — measurements, prototypes, documented tradeoffs. For infrastructure decisions, I focus on: what are the reliability implications? What's the backward compatibility cost? If we disagree, I try to understand what constraint they're optimizing for that I'm not seeing. Once decided, I commit fully — for platform infra, half-hearted execution is more dangerous than a wrong decision fully committed to."

**"How do you prioritize when everything is urgent?"**
> "For infrastructure: correctness beats availability beats performance beats new features. If there's a data integrity issue, everything else stops. Beyond that: I start the longest-turnaround items first (design reviews, cross-team alignment) and work the immediate items in parallel. I don't cut corners on backward compatibility or skip design review to save a day — those shortcuts create years of tech debt in platform code."

**"How do you handle ambiguity?"**
> "In platform infrastructure, ambiguity is usually about 'how to build it right' not 'what to build.' My approach: write a design doc with 2-3 options and explicit tradeoffs. Get reviews from the engineers who'll consume or maintain it. Sometimes I'll build a prototype to measure real performance rather than theorize. The design doc forces clarity — once you write down the contract, the ambiguity resolves."

**"Tell me about a time you had to say no."**
> "In platform work, 'no' is often 'not without a migration path.' A consuming team wanted a breaking API change shipped immediately. Instead of blocking them or rushing it, I said: 'We can do this, but we need to version the endpoint and give consumers 2 weeks to migrate. Here's the plan.' They got their change; nobody's production broke. For infrastructure, saying no without an alternative is just being a bottleneck. Saying 'yes, and here's how we do it safely' is the job."

**"Have you ever been a people manager? Would you want to?"**
> "I've done the leadership work that overlaps with management — mentoring, cross-team alignment, hard feedback, driving consensus. I'm open to management if the situation calls for it. But right now, what excites me is going deep technically. I want to be the person who understands a system at every layer — and you can only do that as a hands-on engineer, not from a management seat."

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
