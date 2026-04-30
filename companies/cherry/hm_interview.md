# HM Interview — Tim Way (May 11, 60 min)

**Format:** Conversational — part informational, part behavioral. Not a formal BQ gauntlet.
**Goal:** Mutual fit. Tim wants to know how you work on a team. You want to learn about the eng org, tech stack, and what you'd actually be doing.

---

## What They're Evaluating

From the interview doc: "how you collaborate, make decisions, balance technical excellence with business needs, navigate challenges, and grow in a professional setting."

Translation: They want stories about real situations, not hypotheticals.

---

## Stories to Have Ready (pick 3-4, don't force all of them)

### 1. Cross-Team Leadership — CarGurus API Redesign
**Use for:** collaboration, ownership, navigating differing perspectives

- Led 3 engineers, partnered with ~10 teams across 3 departments
- Had to get buy-in from teams that owned downstream services
- Built parity testing to make the rollout data-driven, not political
- Result: p99 5x improvement, 99.9% availability

**Key angle for Cherry:** "I wasn't the VP mandating a rewrite — I was the engineer who had to convince 10 teams to change their APIs. That required understanding their priorities, not just mine."

### 2. Early Engineer / Startup Builder — Toast
**Use for:** end-to-end ownership, startup mentality, wearing many hats

- Among earliest engineers during hypergrowth
- Built core services (Order, Labor), customer-facing dashboards, Android app
- Set up AWS infrastructure, deployment pipelines, monitoring — before DevOps existed
- Built custom Nginx API gateway with Lua rate limiting

**Key angle for Cherry:** "I've been the person who sets up the infrastructure, writes the backend, builds the frontend, and answers the support ticket. That's what early-stage requires."

### 3. Full-Stack Delivery — Applause
**Use for:** full-stack skills, auth/security, working across layers

- Built customer apps + admin dashboards end-to-end (Angular, TypeScript, Node.js BFF)
- Modernized auth: Keycloak SSO + custom Kong plugins in Python
- Set up service mesh (Linkerd + K8s)

**Key angle for Cherry:** "I owned the full vertical — from the Angular frontend through the Node BFF to the auth layer and API gateway config."

### 4. Navigating Disagreement / Tradeoffs
**Use for:** "differing perspectives" question

- Pick a specific case: maybe a design disagreement during the API redesign, or a build-vs-buy decision
- Show: listened, stated your case with data, committed to the outcome even if it wasn't your preference

---

## Questions to Ask Tim

These serve double duty — they show thoughtfulness AND give you information to decide if Cherry is right.

**About the team:**
- What does the eng team look like today? How many engineers, and how are they organized?
- What's the biggest technical challenge the team is facing right now?
- How do you balance speed vs. quality at this stage?

**About the role:**
- What would success look like in the first 90 days for this role?
- What's the split between frontend and backend work day-to-day?
- What's the tech stack in detail? (React version, Node vs. other backend, database, infra)

**About the business:**
- How does the BNPL model work for healthcare specifically? What makes it different from consumer BNPL?
- What's the growth trajectory? Are you pre-revenue, post-revenue, profitable?
- What's the team's relationship with compliance/regulatory? (BNPL in healthcare = regulated)

**About Tim:**
- What brought you to Cherry from Lyft?
- What's your engineering philosophy — what do you optimize for when you have to make tradeoffs?

---

## Tone

This is a conversation, not an interrogation. Tim reached out to you — he's selling Cherry as much as you're selling yourself. Be curious, be genuine, show you've thought about what you want. Don't over-prepare canned answers — have the stories in your head, let the conversation guide which ones you tell.
