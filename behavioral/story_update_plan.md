# Behavioral Story Update Plan (Oct 22 → HM screen)

> **Why now:** the resume now leads with this year's work (agentic platform, reliability, secure auth, V1→V2 quant platforms) — but no story covers it. Arrowstreet sourcer call next week, HM screen likely early-mid Nov. This is the interview-driven override: behavioral work jumps the queue ahead of design/coding sessions until the stories land.
> **Source of truth for story format:** `behavioral_playbook.md` (Angle Guide → STAR Spoken-Style → Bullet Recap → Likely Follow-Ups).
> **Coding stays alive as a daily 20–30 min Java drill habit; design queue pauses except D11 material (corrections → narration) which feeds Phase 3.**

---

## Phase 1 — Capture before it decays (URGENT, do first)

**S1 · Override-log sweep** — `my_work/agent_orchestration.md` override log is still empty. Reconstruct the past month's override moments while memory holds: what the agent proposed → what was wrong → how it was caught → what happened instead. One evening, work backwards from last week. Then keep the running habit (jot same-day, batch weekly).
*Output: 5–10 dated override entries. These become the AI-competency stories (Phase 2, S8).*

**S2 · Metrics gathering pass** — `my_work/TODO_details.md` is still unfilled. Pull the numbers once: conversations/day, LLM calls/day, MongoDB cluster config, Redis deployment, team structure, token cost magnitude. Without these, the new stories can't carry metrics — and every new story below needs at least one number.
*Output: filled TODO_details.md.*

## Phase 2 — Draft the new stories (one session each, ~2 hrs)

Each session produces a full story in playbook format and slots it into `behavioral_playbook.md`.

- **S3 · MongoDB 71K-span diagnosis** — the observability-queries → 30s gateway timeouts → compound indexes story. Your best new debugging/data story; metrics already verified (71K+ spans, 30s, sub-2s validation). Check overlap with Story 3b and merge rather than duplicate.
- **S4 · Circuit breakers & telemetry isolation** — designing domain-specific breakers so telemetry failures can't stall core conversations. Design-judgment story: what made this different from a stock circuit breaker.
- **S5 · Secure shopper auth + PII** — opaque session key, request-scoped context, lazy Redis resolution, bearer injection, credentials never in prompts/logs. Ownership + security story; have the "what was the threat model" answer ready.
- **S6 · AI-backend migration breakdown** — MCP tool ownership, handler decomposition, regression evaluation, config-driven feedback routing with allowlisted metadata. Staff+ scoping story: "turned a complex migration into testable, incremental work."
- **S7 · V1→V2 platform rebuild** — the personal quant platforms: why the rebuild, what the new architecture fixed, A/B paper-trading validation, token-cost dashboards. **This is the Arrowstreet HM hook** — the "why did you rebuild?" 3-minute answer must be crisp. Also usable as a general initiative/drive story.
- **S8 · AI-competency story set** — built from S1's override log: where the plan-review agent surfaced a missed case, where AI enrichment was rejected, where a plan was discarded after validation. Also **rewrite Story 3** (MCP POC → the production agentic platform; merge with 3b) so the AI story reflects today, not May 2026.

## Phase 3 — Close the named gaps (round3_plan open items)

- **S9 · Cross-team awareness with a produced outcome** — open question #1 still blocks the Principal-level cross-team story. Hunt for the instance: a concern raised that changed another team's design, a pre-adaptation before a decision landed, a week-one call that saved a month. If none exists, pick the strongest *real* recent instance and frame it honestly.
- **S10 · "How do you decide how much verification is enough?"** — needs a case of deliberately spending less. Pull from S1 (override log) or the migration story.
- **S11 · Token-cost one-liner + Java-recency answer** — aware, rough magnitude, accepted tradeoff; and the TypeScript-last-6-months answer. Both are 30-second prepared answers, not stories.

## Phase 4 — Integration & delivery

- **S12 · Playbook restructure + mapping** — renumber the new stories, update the Quick Index, map every story to: Coinbase values + AI-competency rubric (Usage/Application/Limits) + Arrowstreet HM question set. Update `prep_arrowstreet.md` with a behavioral section (why quant, V1→V2, disagreement, level-scope questions).
- **S13 · Mock behavioral run-through** — 3 stories aloud, 2 min each, with live pushback; include at least one new story and one Arrowstreet-likely question ("walk me through how you use AI day-to-day").

## Timeline

| Window | Sessions | Milestone |
|---|---|---|
| Oct 22–25 | S1, S2, S3, S4 | Captures done; 2 new stories drafted |
| Oct 26–30 | S5, S6, S7, S8 | All new stories drafted; sourcer call answered |
| Oct 31–Nov 6 | S9, S10, S11, S12 | Gaps closed; playbook integrated; Arrowstreet HM prep ready |
| Before HM screen | S13 | Mock run-through with pushback |

**Deliverable gate:** before the HM screen, every resume bullet from this year's work has a matching story with metrics, and the playbook index maps stories → interview question types.
