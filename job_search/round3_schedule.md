# Round 3 — Session Schedule (Sept 23 → offer)

> Companion to `round3_plan.md`. Every session lists its exact questions/topics — no hunting needed.
> ~10 hrs/week = 4 sessions/week (2 design, 2 coding), ~2.5 hrs each.
> **Prep continues until an offer lands.** When a company responds, its prep doc + problem set jumps the queue (reapply_timeline rule).
> **Calibration verdict (Sep 23):** algorithm memory intact, Java syntax rusty, narration thin. Week 1 = skim, not redo; schedule stands as written. Skim `languages/java_playbook.md` pitfalls before each Java drill. **Design assignments are fixed.**

### Per-session protocol

- **Design (study loop):** work the assigned open-questions item → per `design/study/SETUP.md`: log entry, knowledge-base update, corrections append, open-questions update, commit naming the change in understanding.
- **Coding:** solve **in the LeetCode editor** — interviews use online editors where syntax check is basic and expected, so plain-text solving is unnecessary practice. Timed (25 min M / 35 min H), narrate out loud + type decision points, one-sentence pattern note, check the `coding/study_plan.md` tracker. Paste the final solution into the session file after. Solve cold — repo solutions only after.
- **Language:** **Java only** in all coding sessions. TypeScript is work-only.

### Extra time — where it goes (don't cut design)

Adding hours beyond ~10/wk: **keep the 2 design sessions fixed** — that's the round-3 foundations fix. Extra time goes to coding, in this order:

1. Stretch problems already listed in the session.
2. Pull forward the next coding session in the schedule — it's sequential, just advance down the list.
3. Review exam days (standalone ~1 hr, 3 timed problems) — can start now, don't wait for November.
4. Coinbase OA re-solves as warm-ups (Java).

Same rules on every extra problem: timed + narrated. Volume without narration just re-practices the quiet solving that caused the round-2 ding.

### Reading map — spare-time reading, in priority order

Reading supports sessions; it never replaces them (bare reading = the "feeling of understanding" trap).

**Coding (second-pass refresh — dups make it cheap):**
1. `coding/lc_quickref.md` — skim first: pure problem→pattern re-linking.
2. `coding/patterns.md` — skim decision tree + "when to use" + pitfalls. **Skip code templates for problems still scheduled as timed drills** — reading them right before turns the solve into typing. Only read templates after solving.
3. `coding/study_plan.md` — tracker only; don't re-read problem lists.
4. Review-exam days and stretch problems stay **unskimmed** — they're the cold signal.

**Design:**
1. `design/study/corrections.md` — now. Highest value, feeds D11.
2. `design/study/open-questions.md` — 10 min; the session menu for D1–D8.
3. `design/interview/playbook.md` — skim once before week 4.
4. `design/study/design_knowledge_base.md` — **lookup only** (2676 lines): read the section matching each design session's topic before that session.
5. `design/interview/component_decision_tree.md` — skim before weeks 4–5.
6. `design/interview/domain_playbook.md` — skim before D10 (payment/settlement).
7. `design/study/log/*` — only the entries the schedule pairs with sessions. Not all 19.
8. `design/interview/examples/**` — **do NOT pre-read.** Draw-then-diff needs them unspoiled.
9. `design/interview/platform_infra_angle.md` — optional, lowest.
10. `design/interview/system_design_cheatsheet.html` — print near interview time.

---

## Coverage audit — does the list cover everything?

**Design classics (all ~25 scheduled across the phases):**
Covered in weeks 0–5: URL shortener, rate limiter, news feed, Twitter, YouTube, chat, notification, payment, exchange/order book, realtime market data, S3. Added Nov: KV store/cache, message queue, indexer, reconciliation, custody, metrics. Added Dec: web crawler, typeahead, top-K, unique ID, Uber/proximity, Ticketmaster, Dropbox.

**Coding — full `study_plan.md` coverage:** all 106 problems + 10 review-exam days + bonus sets are mapped below. Intentionally light, per your own study plan: DP (pattern recognition only), concurrency (low-med), strings/two-pointers (light), segment tree/KMP/Manacher (reference only, never asked).

---

## Week 0 — Sep 23–27 · Calibration + resume the loop

| # | Track | Session |
|---|---|---|
| D1 | Design | Caching thread — open-questions "Does the SSR layer set cache headers?" Skim log `2026-08-19-caching-strategies` + `2026-08-21-caching-design-principles` first (15 min). |
| D2 | Design | Connection pool thread — open-questions pool-latency-under-burst (Little's Law) + client-disconnect fix. Pairs with the starvation-fix story; two-column capture. |
| C1 | Coding | Calibration — `coding/sessions/2026-09-23_calibration.md`: LC 1396 (M). If fast + clean: LC 239 (H). |
| C2 | Coding | Hash maps / design (Coinbase core) — LC 146 LRU (M), LC 981 Time Based KV (M). Stretch: LC 895 (H). |

---

## Week 1 — Sep 29–Oct 3

| # | Track | Session |
|---|---|---|
| D3 | Design | S3 verification batch — open-questions #1–4 (snapshot TTL, multipart abort, tiering, cross-region replication). Quick Terraform/console checks; ONE log entry. |
| D4 | Design | Event-driven vs polling — open-questions "object-storage event notifications?" (highest-leverage S3 nit). |
| C3 | Coding | Design structures (Coinbase OA style) — LC 588 (H, P; matches repo `cloud_file_system`), LC 380 (M), LC 1146 Snapshot Array (M; matches `in_memory_database`). |
| C4 | Coding | Graphs — LC 200 (M), LC 207 (M; topo sort — the NVIDIA probe), LC 399 (M; weighted UF/BFS). |

---

## Week 2 — Oct 6–10

| # | Track | Session |
|---|---|---|
| D5 | Design | GraphQL thread — open-questions router entity-dedup + response/entity caching. |
| D6 | Design | Coordination thread — open-questions "KV store as P1 dependency?" |
| C5 | Coding | Graphs cont + intervals — LC 133 (M), LC 56 (M), LC 253 (M, P), LC 435 (M). |
| C6 | Coding | Coinbase VO pool (Java) — `1_query_pagination` (#1 freq, design the OOD), `2_mining_block` (greedy — don't cave to DP/heap push), `3_food_delivery_system`. Read repo solutions only after solving. |

---

## Week 3 — Oct 13–17

| # | Track | Session |
|---|---|---|
| D7 | Design | Redis in the agentic system — two-column capture (WHY Redis + when it mattered at CG). |
| D8 | Design | MongoDB in the agentic system — same method; revisit log `2026-08-18-mongodb-usage`. Queue dry → next in-scope: circuit breakers, LLM providers (add to `open-questions.md` first). |
| C7 | Coding | Coinbase VO cont (Java) — `4_crypto_order_event_processing` (state machine + idempotency key), `7_interleave_iterator`, `8_log_file_parser` (`split(":", 4)` insight). |
| C8 | Coding | LC Hard focus (your named gap) — LC 295 (H), LC 23 (H), LC 127 (H). 35 min each, narrate under pressure. |

---

## Week 4 — Oct 20–24

| # | Track | Session |
|---|---|---|
| D9 | Design | SD walkthrough #1 — realtime market data (Coinbase topic #1). Draw from memory, then diff vs `examples/coinbase/1_realtime_market_data.md`; log gaps as corrections. |
| D10 | Design | SD walkthrough #2 — payment/settlement or rate limiter (repo examples both). Draw-then-diff. |
| C9 | Coding | DP recognition (light) — LC 322 (M), LC 518 (M), LC 198 (M), LC 139 (M). |
| C10 | Coding | Format-shift drill — (a) repo-based timed ticket, 45 min, narrate delegation decisions; (b) LC 2043 bank progression Levels 0–5 (prep doc §12). |

---

## Week 5 — Oct 27–31

| # | Track | Session |
|---|---|---|
| D11 | Design | corrections.md → design-round narration — convert 2–3 into *"the intuitive answer is X — that's what I believed — but it's wrong because Y"*. |
| D12 | Design | SD walkthrough #3 — notification system or S3 (repo examples both). Draw-then-diff. |
| C11 | Coding | Review — re-solve 2 weakest cold + LC 1244 Leaderboard (M, P; matches Coinbase OA topSpenders). |
| C12 | Coding | Hard + narration — LC 239 (H, if pending), LC 84 (H), LC 621 (M). |

---

# Phase 2 — November · Finish coverage + Coinbase re-apply window

> Study phase closes; **mock rounds with live pushback begin here** (round3_plan §G). Coinbase cooldown resets ~Nov 1 — OA re-solve distributed as warm-ups all month.

| # | Track | Session |
|---|---|---|
| D13 | Design | **Distributed KV store + cache** — consistent hashing, replication, conflict resolution, eviction. (Prep doc §13 medium priority.) |
| D14 | Design | **Distributed message queue / event pipeline** — Kafka ordering, exactly-once, DLQs, consumer rebalancing. (Prep doc high priority; maps to your Kafka experience.) |
| D15 | Design | **Blockchain transaction indexer** — reorg handling, cross-chain ingestion, eventual consistency. (Coinbase topic.) |
| D16 | Design | **Financial correctness / reconciliation system** — invariant enforcement, real-time vs batch. (Prep doc likely topic; pairs with your parity-testing story.) |
| D17 | Design | **Metrics / monitoring & alerting** — time-series storage, SLO alerting. (Prep doc likely topic.) |
| D18 | Design | **Mock SD #1 with live pushback** — realtime market data redraw, full 60 min. |
| D19 | Design | **Crypto custody + internal platform tooling** — hot/cold wallets, key mgmt, approval flows; multi-tenant ops platform. |
| D20 | Design | **Mock SD #2** — payment/settlement redraw, full 60 min. |
| C13 | Coding | Sliding window core — LC 3 (M), LC 76 (H), LC 424 (M), LC 567 (M). |
| C14 | Coding | Sliding window hard — LC 239 (H, if pending), LC 1438 (M), LC 862 (H), LC 739 (M; monotonic-stack intro). |
| C15 | Coding | Prefix sum + two pointers — LC 560 (M), LC 525 (M), LC 15 (M), LC 42 (H). |
| C16 | Coding | Union-find + trees — LC 684 (M), LC 721 (M), LC 236 (M), LC 297 (H), LC 102 (M). |
| C17 | Coding | Heaps + design — LC 347 (M), LC 973 (M), LC 215 (M), LC 355 (M). |
| C18 | Coding | Linked lists + matrix — LC 206 (E), LC 25 (H), LC 142 (M), LC 48 (M), LC 54 (M). |
| C19 | Coding | Binary search — LC 33 (M), LC 4 (H), LC 528 (M). |
| C20 | Coding | Backtracking + trie — LC 46 (M), LC 79 (M), LC 208 (M), LC 212 (H), LC 17 (M). Stretch: LC 51 (H). |
| — | Warm-ups | **Coinbase OA re-solve (Java)** — one per coding session all month: bank_system, cloud_file_system, in_memory_database, recipe_manager, task_management, flappyBird. Cold, ~20 min each. |
| — | Cadence | **Review exam days begin** — 1 per week, ~1 hr: 3 timed problems each. See checklist below. |

---

# Phase 3 — December · Generic breadth + review

| # | Track | Session |
|---|---|---|
| D21 | Design | **Web crawler** — politeness, dedup (URL frontier), robots. |
| D22 | Design | **Search autocomplete / typeahead** — trie, prefix caching, ranking. |
| D23 | Design | **Top-K / leaderboard service** — streaming counting, heavy hitters. |
| D24 | Design | **Unique ID generator** — Snowflake, clock skew. |
| D25 | Design | **Uber / proximity service** — quadtree/geohash, matching flow. |
| D26 | Design | **Ticketmaster / booking** — seat holds, idempotency, overselling. |
| D27 | Design | **Dropbox / Drive** — sync protocol, conflict resolution, dedup (skip if S3 walkthrough covered it). |
| D28 | Design | **Mock SD #3 + #4** — topics picked by whichever interviews are live; pushback format. |
| C21 | Coding | Stack parsing + greedy — LC 224 (H), LC 227 (M), LC 394 (M), LC 134 (M). |
| C22 | Coding | Bits + concurrency + design — LC 191 (E), LC 338 (E), LC 1188 (M, P), LC 1117 (M, P), LC 432 (H), LC 460 (H), LC 1166 (M, P), LC 362 (M, P). |
| C23 | Coding | DP round 2 — LC 300 (M), LC 152 (M), LC 72 (M), LC 416 (M), LC 1143 (M). Light: LC 91, LC 62. |
| C24 | Coding | Intervals + graphs advanced — LC 57 (M), LC 759 (H, P), LC 1235 (H), LC 994 (M), LC 417 (M), LC 210 (M), LC 269 (H, P). |
| C25 | Coding | Bonus — Airbnb classics: LC 68 (H), LC 336 (H), LC 787 (M). |
| C26 | Coding | Bonus — Pinterest/OpenAI: LC 772 (H), LC 277 (M, P), LC 632 (H), LC 1116 (M), LC 284 (M). |
| C27 | Coding | Rotation — re-solve 2 weakest of the year cold + 1 new from a live interview trend. |
| C28 | Coding | Rotation — same format; verify all `study_plan.md` tracker boxes + all 10 exam days done. |

---

# Phase 4 — January 2027+ · Rotation mode (until offer)

- **1 design mock/week** with pushback — rotating topics from the full list above; redraw from memory, diff against repo examples or your notes.
- **1–2 coding sessions/week** — rotation: 1 new problem + 1 weakest re-solve; exam days until done.
- **Interview-driven:** any company response → switch to that company's `companies/*/prep_*.md` + its problem set. (Google assessment ~Q1 2027; Netflix referral usable ~Feb 2027.)
- **Keep the study loop alive:** new corrections → `corrections.md` → convert to narration; keep the override log current.
- **When to stop:** only when an offer is signed. Then archive like rounds 1–2.

---

## Review exam days (checklist — burn 1/week starting November)

Each day: 3 problems, 25 min M / 35 min H, no notes, narrate. Answer key + scoring in `coding/study_plan.md`.

- [ ] **Day 1:** 992 · 547 · 378
- [ ] **Day 2:** 310 · 1472 · 494
- [ ] **Day 3:** 735 · 743 · 153
- [ ] **Day 4:** 97 · 143 · 542
- [ ] **Day 5:** 410 · 211 · 287
- [ ] **Day 6:** 752 · 986 · 767
- [ ] **Day 7:** 11 · 377 · 692
- [ ] **Day 8:** 150 · 218 · 279
- [ ] **Day 9:** 78 · 309 · 124
- [ ] **Day 10:** 875 · 907 · 73

## Warm-up / variant pack (1–2 per coding session, 10–15 min)

Skimmable or one-trick — don't let them eat a full session. From `study_plan.md` Week 1 variants + minor patterns:

- **Sliding-window variants:** 438, 209, 1004, 30, 159 (P), 727 (P)
- **Prefix variants:** 523, 974, 304, 238, 49
- **Two-pointer variants:** 271 (P), 15 (already main in C15)
- **Quick wins (5 min each):** 169, 53, 75, 41, 876, 382, 164
- **Know the concept (10 min):** 211, 31, 528
- **Reference only (never asked — skim):** segment tree/BIT, KMP, Manacher, A*, suffix array

---

## Deliberately deferred (per round3_plan §G — don't start early)

- The bounded WHY-depth list (12–15 items) — feeds from these sessions' corrections/log entries; build after the study phase.
- Resume rewrite — separate track, hard deadline Oct 31.

## Open items to keep alive

- **Override log** (`my_work/agent_orchestration.md`) — capture at work weekly; batch into a session.
- Cross-team awareness outcome instance (round3_plan open question #1) — watching for it.
