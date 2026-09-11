# Interview Prep — Organized Structure

> Updated: July 2026
> Staff/Senior backend engineer job search materials, organized by topic.

---

## Directory Structure

```
interview_prep/
├── README.md                      ← You are here
│
├── behavioral/                    ← Behavioral interview prep
│   ├── behavioral_playbook.md     — STAR stories, LP mapping, company-specific angles
│   └── assessment_playbook.md     — Take-home assessment strategies
│
├── system_design/                 ← System design prep
│   ├── design_knowledge_base.md   — Core patterns, tools, constraint→solution mapping
│   ├── system_design_playbook.md  — Interview delivery, layering approach, tradeoffs
│   ├── domain_interview_playbook.md — Domain-specific scenarios (payments, auth, etc.)
│   ├── platform_infra_angle.md    — Platform/infra framing for design rounds
│   ├── chat_system.md             — Example: Chat system design
│   ├── news_feed.md               — Example: News feed design
│   ├── notification_system.md     — Example: Notification system
│   ├── rate_limiter.md            — Example: Rate limiter
│   ├── twitter.md                 — Example: Twitter-like system
│   ├── url_shortener.md           — Example: URL shortener
│   └── youtube.md                 — Example: Video platform
│
├── java/                          ← Java-specific prep
│   └── java_playbook.md           — Java interview topics, JVM, concurrency, collections
│
├── python/                        ← Python-specific prep (coming soon)
│   └── (empty — add Python LC, idioms, asyncio, Pydantic notes here)
│
├── job_search/                    ← Job search tracking & strategy
│   ├── round3_plan.md             — ★ START HERE. Active plan: state, diagnosis, action items, decisions
│   ├── job_search_todo.md         — Round 1–2 history, results, lessons (superseded as active doc)
│   ├── reapply_timeline.md        — Re-application schedule, cooldown tracking
│   └── job_search_todo_old.md     — Archived (pre-June 2026)
│
├── generic/                       ← Universal interview materials
│   ├── interviewer_questions.md   — Questions to ask interviewers (by stage + company)
│   ├── leetcode_study_plan.md     — LC patterns, study schedule
│   └── technical_playbook.md      — General technical interview strategies
│
├── companies/                     ← Company-specific resumes & materials
│   ├── coinbase/
│   ├── meta/
│   ├── nvidia/
│   ├── affirm/
│   ├── circle/
│   ├── spotify/
│   └── (others...)
│
├── cheatsheets/                   ← Quick reference sheets
│   └── (various cheat sheets)
│
└── .claude/                       ← Claude Code config & memory
    └── memory/                    — Auto-memory (feedback, project status, etc.)
```

---

## Quick Start by Interview Type

| Interview Type | What to Read |
|---|---|
| **System Design** | `system_design/design_knowledge_base.md` (patterns + tools) → `system_design/system_design_playbook.md` (delivery) |
| **Behavioral** | `behavioral/behavioral_playbook.md` → pick 3-4 stories, practice STAR format |
| **LeetCode** | `generic/leetcode_study_plan.md` → focus on patterns, not volume |
| **Java coding** | `java/java_playbook.md` → JVM, concurrency, collections deep dive |
| **Python coding** | `python/` (TBD — start with LC in Python, asyncio, Pydantic) |
| **Asking questions** | `generic/interviewer_questions.md` → manager screening, culture red flags |

---

## Current Job Search Status (as of July 2026)

**Active Pipeline:**
- Meta (E6) — referral submitted, waiting for recruiter contact
- Affirm — waiting on connection response
- Circle — waiting on connection response
- Spotify — ready to cold apply

**Upcoming:**
- Coinbase — November re-apply (6-month cooldown)
- NVIDIA — monitoring for new US-based roles

See `job_search/job_search_todo.md` and `job_search/reapply_timeline.md` for details.

---

## Prep Philosophy (lessons from 3 months of interviews)

1. **System Design:** Start simple, add complexity ONLY when constraint forces it. Show the WHY (tradeoffs), not just the WHAT (solution).
2. **Behavioral:** 2-3 min per story (30s setup, 60s what/why, 30s result). Pause and let them dig deeper. Show reasoning, not just outcomes.
3. **LeetCode:** Pattern recognition > volume. Know 10 patterns deeply, not 200 problems shallowly.
4. **Delivery:** Conversational > rehearsed. IBM energy > desperate Coinbase energy.
5. **Manager Screening:** Ask about autonomy, decision-making, and process vs. outcomes. Detect anxiety-driven management early.

---

## Key Learnings from April-June 2026

- **Coinbase (Staff):** Passed all rounds, feedback: show WHY (tradeoffs, reasoning) not just WHAT (solution). Re-apply November.
- **NVIDIA (Senior):** Passed 4 rounds, likely stalled due to HM leave + headcount moved to India. Monitor for new US roles.
- **IBM/HashiCorp (Senior II):** Offered but down-leveled + hybrid + comp didn't work. Declined.
- **Cherry (Staff):** Strong HM connection, "stay connected." Reach out September.
- **Stripe, GitHub, Reddit, Airbnb:** System rejections from cold apps. Warm referrals > cold apps, always.

**The gap identified:** Showing reasoning journey (options considered, tradeoffs made, why this choice) vs. just stating the solution.

**The fix:** "I need X. Options are A vs B. Picking A because [reason]. Tradeoff: [what I give up]."

---

## Memory System

Auto-memory lives in `.claude/memory/` and persists across conversations:

- `feedback_*.md` — What to do / not do (based on interview feedback, work frustrations)
- `project_*.md` — Job search status, pipeline tracking
- `user_*.md` — Your background, preferences, constraints

These inform the AI assistant's recommendations without needing to repeat context.

---

## What's Next

**Immediate (July 2026):**
- Wait for Affirm/Circle connections (1 week)
- Cold apply Spotify if no connection found
- Start Python LC warmup (for NVIDIA role)

**Medium-term (Aug-Oct 2026):**
- Re-apply wave to Stripe, Netflix, Dropbox (at Senior level)
- Keep browsing Meta for right infra role
- Prep Go basics (for Coinbase November)

**Long-term (Nov 2026+):**
- Coinbase re-apply (Staff, with improved delivery)
- Evaluate Klaviyo as safety net if needed
- Continue side project (options-ai) for learning + portfolio

---

## Contributing / Updating

This is your personal interview prep repo. Update freely:

- Add new company-specific questions to `generic/interviewer_questions.md`
- Log new applications in `job_search/job_search_todo.md`
- Add Python notes to `python/` as you learn
- Update `behavioral/behavioral_playbook.md` with new stories

Keep it organized. Future-you will thank present-you.
