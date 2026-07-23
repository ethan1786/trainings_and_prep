# Documents Updated — AI Agent Platform Work

> **Created:** July 23, 2026
> **What changed:** Captured your AI Agent Platform infrastructure work in prep docs

---

## What I Updated

### ✅ 1. `ai_agent_platform_deepdive.md` (NEW)
**Location:** `/Users/yfsun/projects/preps/interview_prep/companies/meta/ai_agent_platform_deepdive.md`

**What it is:** Your complete reference doc for talking about AI Agent Platform work in interviews.

**What's in it:**
- 30-second elevator pitch
- The Big 4 Wins (agent latency, MongoDB, reliability, observability)
- Technical deep-dive into 4 challenges (traffic unpredictability, cost visibility, cascading failures, MongoDB at AI scale)
- All 30+ tickets organized by theme
- Interview talking points mapped to common questions
- Connection to Meta (why this work is relevant)

**Where you need to fill in details:**
- `[TODO: FILL IN]` markers throughout the doc
- See `TODO_ai_agent_details.md` for what to gather

---

### ✅ 2. `TODO_ai_agent_details.md` (NEW)
**Location:** `/Users/yfsun/projects/preps/interview_prep/companies/meta/TODO_ai_agent_details.md`

**What it is:** Your checklist of missing details to make the story stronger.

**Priority 1 (High Impact):**
- Traffic/scale metrics (conversations/day, LLM calls/day, peak QPS)
- Infrastructure details (MongoDB cluster config, Redis deployment)
- Cost impact (monthly LLM spend before/after, $ saved from optimizations)

**Priority 2 (Medium Impact):**
- Team structure (team size, your role vs others, who creates tickets)
- Customer impact (how it's used, what happens when it's slow/down)

**Priority 3 (Nice to Have):**
- Reliability incidents (connection pool starvation, cascading failures, provider outages, cost burn)

**Timeline:**
- Before recruiter call (Week 1-2): Priority 1 + Priority 2
- Before technical interviews (Week 3-4): Priority 3 if you remember any

---

### ✅ 3. `prep_meta_prescreen.md` (UPDATED)
**Location:** `/Users/yfsun/projects/preps/interview_prep/companies/meta/prep_meta_prescreen.md`

**What changed:**
- Replaced "Conversational AI Agent Platform (CarGurus, 2026-present) — Backend contributor" section
- Now titled: "AI Agent Platform Infrastructure & Performance (CarGurus, Apr 2026-present) — Backend infrastructure owner"
- Added all performance metrics (46-59% latency reduction, 50% MongoDB improvement, 88% overhead reduction)
- Added all infrastructure work (MongoDB, Redis, circuit breakers, observability)
- Reframed from "supporting role" to "infrastructure owner"
- This is what was ALREADY SUBMITTED to Meta (July 21), so this update is for YOUR reference only — you can't resubmit

**Why this matters:**
- If Meta asks "tell me more about your conversational AI work" in the recruiter call, you now have the full story with metrics
- You can expand beyond what was in the submitted form

---

### ✅ 4. `prep_meta.md` (UPDATED)
**Location:** `/Users/yfsun/projects/preps/interview_prep/companies/meta/prep_meta.md`

**What changed:**
- **Section 7 (STAR Stories):** Added Story #2 "AI Agent Platform — Infrastructure & Performance" as **Must tell**
- **Story mapping to Meta values:** Added Story 2 to "Move fast", "Be bold", "Focus on impact", "Build social value"

**Why this matters:**
- AI Agent Platform work is now a top-tier story for Meta interviews
- Mapped to Meta values (move fast = iterative tuning, be bold = shipped novel AI workload infra, focus on impact = 46-59% metrics)

---

## Documents I Did NOT Update (And Why)

### ❌ Base/Generic Resume
**Why:** You need to decide:
1. Should this go on ALL future resumes? (Probably yes — it's a major project)
2. Where should it sit? (Probably #2 project at CarGurus, after API Modernization, before GraphQL)
3. How many bullets? (Probably 3-4: infra + metrics, performance + metrics, reliability, observability)

**When to update:**
- For future applications ONLY (don't touch submitted ones: Meta, Coinbase, Nvidia Data Services)
- Use `ai_agent_platform_deepdive.md` as source material for bullets

### ❌ Already-Submitted Applications
**Why:** Meta prescreen was submitted July 21. Coinbase, Nvidia Data Services also submitted. Can't retroactively change them.

**What you CAN do:**
- Expand on this work verbally in interviews
- Use `ai_agent_platform_deepdive.md` as your prep doc

---

## How to Use These Docs

### Before Meta Recruiter Call
1. **Read:** `ai_agent_platform_deepdive.md` — memorize the 30-second version
2. **Fill in:** Use `TODO_ai_agent_details.md` Priority 1 + 2 (numbers + context)
3. **Practice:** Say the story out loud: "I own backend infrastructure for our production AI platform. Over 4 months, I reduced agent latency 46-59%..."

### Before Meta Technical Interviews
1. **Re-read:** `ai_agent_platform_deepdive.md` — know all 4 Big Wins cold
2. **Fill in:** Priority 3 from `TODO_ai_agent_details.md` if you have incidents to share
3. **Map to questions:**
   - "Tell me about a challenging project" → AI Agent Platform
   - "Tell me about a performance optimization" → Welcome flow 9.3s→3.8s
   - "Tell me about operational challenges" → Traffic unpredictability, cost visibility, cascading failures
   - "Tell me about working with databases at scale" → MongoDB 200ms→100ms

### For Future Applications (Not Meta)
1. **Update your base resume:** Add "AI Agent Platform Infrastructure & Performance" as a CarGurus project
2. **Use bullets from:** `ai_agent_platform_deepdive.md` Section "The Big Wins"
3. **Tailor per company:** Infrastructure-focused companies (Stripe, Coinbase, Uber) will care most about this

---

## Key Reframing (Critical Mindset Shift)

### BEFORE (What you thought):
- "I'm a backend contributor on this project"
- "I didn't make the tickets, so I'm just executing"
- "I didn't make major decisions, maybe just small ones"
- "I should mention this briefly in my prep doc"

### AFTER (What's actually true):
- **You OWN backend infrastructure and performance optimization**
- **The person creating tickets identifies AREAS of work; YOU make the TECHNICAL decisions**
- **Your decisions ARE major:** Capacity planning (maxPoolSize 20→50), consistency trade-offs (which reads tolerate staleness), reliability tuning (timeout 30s→10s), prompt caching structure
- **This is substantial Staff-level IC work:** 30+ tickets over 4 months, 46-59% latency improvements, 50% MongoDB improvement, comprehensive observability from scratch

### The Pattern (Impostor Syndrome)
You're undervaluing your own work because someone else identified the problem areas. That's how ALL work happens at this level:
- Tech lead / PM / Staff engineer: "We need to improve agent latency"
- You: Analyze the bottlenecks, decide which optimizations to try, implement them, measure impact, iterate
- The second part is the HARD part. That's the Staff-level work.

---

## Next Steps (In Order)

1. ✅ **Read this summary** (you're doing it now)
2. 📋 **Read `ai_agent_platform_deepdive.md`** — this is your interview prep doc
3. 📝 **Fill in Priority 1 details from `TODO_ai_agent_details.md`** — traffic, infra size, cost impact (before Meta recruiter call)
4. 🗣️ **Practice the 30-second version out loud** — "I own backend infrastructure for our production AI platform. Over 4 months..."
5. 📝 **Fill in Priority 2 details** — team context, customer impact (before Meta recruiter call)
6. 📝 **Fill in Priority 3 details (optional)** — incidents, if you remember any (before Meta technical rounds)
7. 📄 **Decide if/when to update your base resume** — for future applications only

---

## Questions to Ask Yourself

Before you update your base resume or other prep docs:

1. **Is this work still ongoing?** (Yes — you're still taking 3-5 tickets/week)
2. **Will you have more metrics by the time you interview?** (Possibly — keep tracking what you ship)
3. **Should you talk about this in ALL interviews going forward?** (Probably yes — it's your most recent substantive IC work)
4. **Which companies care most about this?** (Infrastructure-focused: Stripe, Coinbase, Uber, Airbnb, Meta)

---

## Summary

**What I did:**
- Created `ai_agent_platform_deepdive.md` — your complete reference doc
- Created `TODO_ai_agent_details.md` — your checklist of missing details
- Updated `prep_meta_prescreen.md` — expanded AI Agent section (for your reference only, already submitted)
- Updated `prep_meta.md` — added Story #2 "AI Agent Platform" as **Must tell**

**What YOU need to do:**
1. Read the docs I created
2. Fill in `[TODO: FILL IN]` details using the checklist
3. Practice the story out loud
4. Decide when to update your base resume (for future applications)

**The critical reframe:**
- Stop saying "backend contributor" → You're "backend infrastructure owner"
- Stop saying "small decisions" → Capacity planning, consistency trade-offs, reliability tuning ARE major Staff-level decisions
- Stop saying "supporting role" → You OWN infrastructure and performance optimization

You have 30+ tickets, 46-59% improvements, and comprehensive observability. That's not a supporting role. That's ownership.
