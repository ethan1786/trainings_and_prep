# Design Notes

Personal study notes on distributed-systems design, built from an extended architecture study series.

## Files

See `SETUP.md` for how to unzip, initialize git, open in Obsidian, and the per-session working loop.

## How these files work

The files are split by **lifecycle**, not by topic. Two kinds of content want opposite things, so they live apart.

| File / folder | Lifecycle | Purpose |
|---|---|---|
| `design_knowledge_base.md` | **Rewritten in place** | Distilled reference. Always reflects current best understanding. History deliberately discarded (git keeps it). |
| `log/` | **Append-only** | Chronological study sessions. Never revised. Preserves the reasoning path, including wrong turns. |
| `corrections.md` | **Append-only** | "What I believed → what's accurate → why I was wrong." The highest-value file here. |
| `open-questions.md` | Living | Unverified claims, each with what would settle it. Next-investigation queue. |
| `private/` | Private | Analysis not intended for sharing. |

### The reading pattern

- **"What should I do?"** → `design_knowledge_base.md`
- **"How did I get here, and what did I believe before?"** → `log/`
- **"Am I about to repeat a known mistake?"** → `corrections.md`
- **"What should I dig into next?"** → `open-questions.md`

### The linking convention

Each log entry ends with **What changed in the reference**. Each reference section that came from a session carries a **See also** pointer back to the log entry. That bidirectional link is the audit trail: you can always walk from a rule back to the reasoning that justified it.

### Why Markdown + git

Plain text, diffable, portable, renders everywhere, no lock-in. `git log` on the reference doc *is* the record of understanding evolving — every correction shows up as a diff of what was previously believed.

Recommended viewer: **Obsidian** (operates directly on these `.md` files; adds `[[wiki-links]]`, backlinks, and fast search without leaving Markdown). GitHub, VS Code preview, and Typora all render it fine too.

## Conventions

- **Dates** in log filenames are `YYYY-MM-DD-topic-slug.md`.
- **Corrections** are dated and never edited once written — if a correction is itself later corrected, append a new entry referencing the old one.
- **Confidence** is stated explicitly: `verified` (read the source), `inferred` (reasoned from evidence), `unverified` (plausible, untested).
