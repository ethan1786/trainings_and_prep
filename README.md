# Interview Prep

> Restructured: September 11, 2026
> Principal SWE job search — Round 3. Organized by **lifecycle**, not by topic.

**→ Start at [`job_search/round3_plan.md`](job_search/round3_plan.md)** — current state, corrected diagnosis, action items, decisions already made. Read it first in a new session.

---

## Directory Structure

```
interview_prep/
│
├── job_search/                 ← Strategy and state
│   ├── round3_plan.md          ★ START HERE — active plan, action items, decisions
│   ├── reapply_timeline.md     — cooldowns and re-application schedule
│   └── archive/                — round1_todo.md, round2_todo.md (history)
│
├── my_work/                    ← (empty — consolidated Oct 2026)
│                                 Work-context material now lives in behavioral/behavioral_playbook.md:
│                                 Stories 3/3b/3c (agentic platform), 17 (secure identity), 18 (V1→V2
│                                 platforms), 19 (AI orchestration + override log), 20 (cross-team)
│
├── design/
│   ├── study/                  ← LIVING study system (git subtree, see below)
│   │   ├── design_knowledge_base.md  — distilled reference, rewritten in place
│   │   ├── corrections.md            — "what I believed → what's accurate → why I was wrong"
│   │   ├── open-questions.md         — unverified claims + what would settle them
│   │   ├── log/                      — append-only session log, 19 entries
│   │   └── README.md, SETUP.md       — the working loop and conventions
│   └── interview/              ← Delivery artifacts
│       ├── playbook.md         — staff+ framework, tradeoff articulation
│       ├── component_decision_tree.md — technology selection
│       ├── domain_playbook.md  — payments domain walkthrough
│       ├── platform_infra_angle.md
│       ├── system_design_cheatsheet.html, system_design_flow.html
│       └── examples/           — worked problems (+ coinbase/, openai/ sets)
│
├── coding/
│   ├── patterns.md             — patterns + data structures (was technical_playbook.md)
│   ├── lc_quickref.md          — "what pattern is this?" skim sheet
│   ├── study_plan.md
│   └── problems/               — coinbase_oa/, coinbase_vo/, openai/ (reusable sets)
│
├── behavioral/
│   ├── behavioral_playbook.md  — STAR stories, LP mapping
│   ├── assessment_playbook.md  — take-home strategy
│   └── disagree_to_commit_supportive.md
│
├── languages/
│   ├── java_playbook.md        — JVM, concurrency, collections (stale in daily practice)
│   └── typescript/             — EMPTY. Daily language now; no material yet.
│
├── companies/                  ← Live targets only
│   ├── anthropic/              — STUB. Boston office new, no reqs yet. Time-sensitive.
│   ├── coinbase/               — cooldown resets ~Nov 2026. AI-native format documented.
│   ├── meta/                   — applied, no recruiter contact
│   ├── netflix/                — referral resting to ~Feb 2027; cold apply unblocked
│   ├── google/                 — assessment cooldown ~Q1 2027
│   ├── cherry/                 — rejected, but HM said stay connected
│   ├── stripe/, reddit/, airbnb/ — re-apply candidates
│   └── archive/                — 12 closed or never-pursued companies
│
├── generic/                    — resume_base.html, interviewer_questions.md, salary_negotiation.md
└── tools/                      — find_remote_jobs.py
```

---

## The lifecycle split

Two kinds of content want opposite things, so they live apart.

| | Lifecycle | Rule |
|---|---|---|
| `design/study/design_knowledge_base.md` | **Rewritten in place** | Always reflects current best understanding. Delete what's wrong — git keeps history. |
| `design/study/log/` | **Append-only** | Never revised. Preserves the reasoning path, including wrong turns. |
| `design/study/corrections.md` | **Append-only** | The highest-value file here. Also the best source of design-round narration. |
| `design/interview/`, `coding/`, `behavioral/` | Artifacts | Interview delivery material, revised freely. |
| `my_work/` | Living | Ground truth about my own work; feeds resumes and stories. |
| `companies/` | Per-application | Archive when a target closes rather than deleting. |

### Reading pattern

- *"What should I do?"* → `design/study/design_knowledge_base.md`
- *"How did I get here, what did I believe before?"* → `design/study/log/`
- *"Am I about to repeat a known mistake?"* → `design/study/corrections.md`
- *"What should I dig into next?"* → `design/study/open-questions.md`
- *"Where does the search stand?"* → `job_search/round3_plan.md`

---

## `design/study/` is a git subtree

It tracks a separate repo so the study loop keeps its own history — `git log` there *is* the record of understanding evolving.

```bash
# Pull in new study sessions from the source repo
git subtree pull --prefix=design/study design-notes master

# Push changes made here back to it
git subtree push --prefix=design/study design-notes master
```

The `design-notes` remote points at a local path (`~/Downloads/design-notes`). **If you move that folder, update the remote:**

```bash
git remote set-url design-notes /new/path/to/design-notes
```

**Do not rename or relocate files inside `design/study/`** — that guarantees conflicts on every pull. Add new material through the source repo, or edit in place and push back.

---

## A note on `private/`

`design/study/private/vdp_orchestration_graphql_analysis.md` is internal analysis. It lives inside the subtree rather than under `my_work/private/` on purpose: moving it would make it reappear on every `subtree pull`.

This repo is **private on GitHub** — verify that before ever changing visibility, and note that `.gitignore` does not untrack what's already committed.
