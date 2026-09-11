# Setup — versioning these notes locally

## 1. Get the files

Download `design-notes.zip` and unzip it wherever you keep personal notes, e.g.:

```
~/notes/design-notes/
```

## 2. Start version history

```bash
cd ~/notes/design-notes
git init
git add .
git commit -m "Initial: knowledge base, corrections, open questions, 8 log entries"
```

That single commit is your baseline. From here, `git log` on `design_knowledge_base.md` becomes the record of your understanding evolving — every future correction shows up as a diff of what you previously believed.

Optional remote (use a **private** repo, given `private/`):

```bash
git remote add origin git@github.com:<you>/design-notes.git
git push -u origin main
```

## 3. Open in Obsidian

`Open folder as vault` → select `design-notes/`. It operates directly on these `.md` files — no import, no proprietary store. You get `[[wiki-links]]`, backlinks, and fast search without leaving Markdown.

Suggested settings: enable **Wikilinks** off (keep standard Markdown links so the files render identically on GitHub), and turn on **Show backlinks in document**.

Any other viewer works too — GitHub, VS Code preview, Typora.

## 4. The working loop

After each study session:

1. **Append a log entry** — `log/YYYY-MM-DD-topic.md`, using the template in `log/README.md`. Never revise old entries.
2. **Update the reference in place** — edit `design_knowledge_base.md` to reflect current best understanding. Delete what's now wrong; git keeps the history.
3. **Append any corrections** — `corrections.md`, with *why the error was tempting*. This is the highest-value habit here.
4. **Update open questions** — add new unknowns with "what would settle it"; delete resolved ones (the resolution belongs in the log entry).
5. **Add the row** to the table in `log/README.md`.
6. **Commit with a message that names the change in understanding**, not the file:

```bash
git commit -am "Caching: repeat-rate x source-cost is the trigger, not traffic volume"
```

Good commit messages make `git log` readable as a learning history.

## 5. Useful commands

```bash
# How has my understanding of the reference changed?
git log --oneline -- design_knowledge_base.md

# What did I believe about caching before?
git log -p -S "write-through" -- design_knowledge_base.md

# What did I learn on a given day?
git show --stat <commit>

# Everything I've ever corrected
cat corrections.md
```

## 6. Keeping `private/` private

`private/vdp_orchestration_graphql_analysis.md` is intended to stay local. Options:

- **Simplest:** keep the whole repo private and local-only (no remote).
- **If you add a remote:** either keep the repo private, or add `private/` to `.gitignore` before the first commit so it's versioned nowhere.

Note that `.gitignore` only prevents *future* tracking — if you commit it once, it's in history. Decide before the first commit.
