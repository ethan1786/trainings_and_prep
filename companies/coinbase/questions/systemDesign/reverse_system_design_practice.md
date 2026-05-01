# Reverse System Design — Practice Case

## The Setup

The interviewer says:

> "I'm going to walk you through our Crypto Withdrawal Pipeline — the system that handles when a user withdraws crypto from their Coinbase account to an external wallet. I'll present the architecture, and I'd like you to ask questions, identify potential issues, and suggest improvements."

---

## The System They Present

```
User clicks "Withdraw 1 BTC to address abc123"
         │
         ▼
┌─────────────────┐
│  Withdrawal API  │ ── validates request (user auth, address format)
│  (REST, Go)      │ ── checks balance in User Balance Service
└────────┬────────┘
         │ sync HTTP call
         ▼
┌─────────────────┐
│ Risk Engine      │ ── fraud/AML checks (rules + ML model)
│ (Go + Python ML) │ ── returns APPROVE / DENY / MANUAL_REVIEW
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
 APPROVE   DENY/REVIEW
    │         │
    ▼         ▼
┌──────────┐  (user notified,
│ Signing   │   request logged)
│ Service   │
│ (HSM)     │ ── signs the transaction with private key
└────┬─────┘
     │
     ▼
┌──────────────┐
│ Broadcast     │ ── submits signed tx to Bitcoin network
│ Service       │ ── polls for confirmations (6 for BTC)
└────┬─────────┘
     │
     ▼
┌──────────────┐
│ Status        │ ── updates withdrawal status in PostgreSQL
│ Tracker       │ ── sends push notification + email to user
│ (cron, 30s)   │
└──────────────┘

Data stores:
- PostgreSQL: withdrawal records, status, audit log
- Redis: rate limiting, session cache
- User Balance Service: separate microservice, source of truth for balances
```

The interviewer adds:
- ~50K withdrawals/day, peaks at 200K during market volatility
- Average processing time: 2-5 seconds (API to broadcast)
- 6-confirmation wait for BTC is ~60 minutes
- The system has been running for 2 years, generally stable
- 3 engineers maintain it

---

## Phase 1: Listen & Clarify (first 10 min)

**Good clarifying questions to ask:**

> "What's the SLA for the end-to-end withdrawal? Is there a target time from user click to broadcast?"

*They say: "We target < 10 seconds from request to broadcast. 99.5% of the time we hit that."*

> "How is the balance check done — is it a reservation/hold, or just a read?"

*They say: "It's a read — we check if balance >= amount, then proceed."*

**You should notice:** This is a TOCTOU (time-of-check-time-of-use) issue. You'll come back to this.

> "What happens to the user's balance — when does it actually get debited?"

*They say: "The balance is debited after the Signing Service succeeds."*

> "Is the Risk Engine call synchronous? What's its p99 latency?"

*They say: "Yes, synchronous. p99 is about 800ms, but during spikes it can hit 3 seconds."*

> "How many teams consume or depend on this pipeline?"

*They say: "Compliance team monitors it, customer support handles stuck withdrawals, and the mobile/web teams display status."*

---

## Phase 2: Probe & Identify (next 30 min)

### Issue 1: Balance Check Race Condition (Correctness)

**Your question:**
> "You mentioned the balance check is a read, and the debit happens after signing. What prevents a user from submitting two withdrawals simultaneously that both pass the balance check?"

*They say: "Hmm, we have rate limiting but no explicit lock."*

**Your observation:**
> "This is a classic TOCTOU race. If a user has 1 BTC and submits two 1 BTC withdrawals within milliseconds, both could pass the balance check before either debits. You'd end up sending 2 BTC from a 1 BTC account."

**Your suggestion:**
> "I'd change the balance check from a read to a reservation — an atomic `debit-and-hold` that reduces the available balance immediately. If the withdrawal fails downstream, you release the hold. This is the same pattern as authorization holds on credit cards. At CarGurus, we used a similar approach for inventory reservations — you can't sell the same car twice."

**Tradeoff to mention:**
> "The cost is tighter coupling with the Balance Service — it now needs to support holds, not just reads. But for a financial system, correctness here is non-negotiable."

---

### Issue 2: Risk Engine as a Synchronous Bottleneck (Reliability)

**Your question:**
> "The Risk Engine is synchronous with 800ms p99. What happens when it's slow or down? Does the whole pipeline block?"

*They say: "Yes — if the Risk Engine is slow, withdrawals queue up. We had an incident last month where latency spiked to 10 seconds and users saw timeouts."*

**Your observation:**
> "A synchronous dependency with 800ms p99 is your biggest latency contributor and single point of failure. If the Risk Engine goes down, all withdrawals stop — even legitimate ones."

**Your suggestion:**
> "I'd consider two changes. First, add a circuit breaker between the API and the Risk Engine — if the Risk Engine is degraded, you can either fail fast with a user-friendly message or fall back to a simplified rule set for low-risk withdrawals (small amounts, verified addresses). Second, for the MANUAL_REVIEW path, make that async — queue it and notify the user, rather than holding the HTTP connection."

**Reference your experience:**
> "At CarGurus, our orchestration layer had a similar problem — 12 downstream dependencies, any of which could block the entire request. We added circuit breaking and fault isolation per dependency, which is what got our availability from 98% to 99.9%."

---

### Issue 3: Status Tracker is a Cron Job (Observability / UX)

**Your question:**
> "The Status Tracker runs on a 30-second cron. What does the user see between broadcast and the first status update?"

*They say: "They see 'Processing' until the cron picks it up and updates to 'Broadcast'. Then it polls for confirmations."*

**Your question:**
> "So there's a 0-30 second gap where the transaction is already on the blockchain but the user still sees 'Processing'? And what if the cron job fails — how would you know?"

*They say: "We have a basic health check but no alerting on individual stuck withdrawals."*

**Your observation:**
> "Two issues here. First, the 30-second cron creates a poor user experience — the user doesn't know if their withdrawal succeeded. Second, if the cron fails silently, withdrawals get stuck in 'Processing' indefinitely with no alert."

**Your suggestion:**
> "I'd replace the polling cron with an event-driven approach. The Broadcast Service publishes a 'TransactionBroadcast' event to a message queue. The Status Tracker consumes it and updates immediately — near-zero delay. For confirmation tracking, a separate consumer polls the blockchain and publishes 'ConfirmationReceived' events. If a withdrawal stays in 'Broadcast' for longer than expected (say, 10 minutes without a confirmation), that triggers an alert."

**Tradeoff:**
> "Event-driven is more complex to operate than a cron — you need queue monitoring, dead letter handling, consumer lag alerting. But for user-facing status updates in a financial system, the accuracy and responsiveness are worth it."

---

### Issue 4: No Reconciliation (Correctness)

**Your question:**
> "How do you verify that what's in your PostgreSQL withdrawal records matches what actually happened on the blockchain?"

*They say: "We don't have an automated reconciliation process. If something looks wrong, an engineer investigates manually."*

**Your observation:**
> "This is concerning for a financial system. Silent discrepancies between your internal state and on-chain reality could mean money was sent but not recorded, or recorded but not sent. Without automated reconciliation, you're relying on users to report problems."

**Your suggestion:**
> "I'd add a reconciliation job that runs every N minutes. It compares: (1) all withdrawals in 'Completed' status in PostgreSQL against (2) the corresponding transactions on-chain. Any mismatch — amount differs, transaction not found, or extra on-chain transactions not in the DB — triggers an alert to the on-call engineer and the compliance team. At CarGurus, I built exactly this kind of correctness verification — a parity testing framework that compared new vs. legacy system outputs at 50% production traffic. Same principle: automated comparison of two sources of truth with divergence alerting."

---

### Issue 5: Audit Trail Gaps (Compliance)

**Your question:**
> "What gets logged in the audit trail? Is every state transition recorded, or just the final outcome?"

*They say: "We log the initial request and the final status. State transitions aren't logged consistently."*

**Your observation:**
> "For a regulated financial service, you need a complete audit trail — every state transition with timestamp, actor, and context. If a regulator asks 'why was this withdrawal approved at 2:03 PM?', you need to show the full chain: request received, balance checked (result), risk check (result + score), signing (key ID), broadcast (tx hash), each confirmation."

**Your suggestion:**
> "I'd add an append-only event log — every state transition writes an immutable record. This serves three purposes: audit compliance, debugging (you can replay the full lifecycle of any withdrawal), and reconciliation (the event log becomes a source of truth you can compare against PostgreSQL and the blockchain)."

---

## Phase 3: Summarize & Prioritize (last 5-10 min)

**How to wrap up:**

> "If I had to prioritize, here's what I'd tackle in order:
>
> 1. **Balance race condition** — this is a correctness bug that could lose money. Fix first with atomic balance holds.
> 2. **Reconciliation** — add automated comparison between internal state and on-chain. Non-negotiable for a financial system.
> 3. **Risk Engine circuit breaker** — biggest reliability risk. One slow dependency shouldn't block all withdrawals.
> 4. **Event-driven status updates** — replaces the cron, improves UX and observability.
> 5. **Audit trail** — compliance requirement, also improves debugging.
>
> The first two are correctness issues — money could be wrong. The next two are reliability and UX. The last is compliance. I'd frame it that way to stakeholders: fix correctness first, then reliability, then operational improvements."

---

## What Makes This a Strong Performance

| Signal | How you showed it |
|---|---|
| Correctness thinking | Caught the TOCTOU race on balance check — financial systems instinct |
| Reliability judgment | Identified the synchronous bottleneck, proposed circuit breaker |
| Platform experience | Referenced your own parity testing, circuit breaking, orchestration work |
| Operational maturity | Asked about alerting gaps, proposed event-driven over cron |
| Compliance awareness | Raised audit trail gaps unprompted — shows financial domain sense |
| Prioritization | Ranked issues by impact: correctness > reliability > UX > compliance |
| Communication | Stated issue → risk → solution → tradeoff → experience for each |

## Common Mistakes to Avoid

- **Listing 10 surface-level issues** instead of going deep on 3-4
- **Redesigning the whole system** instead of suggesting incremental improvements
- **Being critical without acknowledging what works** — "The separation of concerns between services is solid, and the HSM-based signing is the right approach"
- **Forgetting to ask about scale/SLA first** — you need context before you can judge
- **Not referencing your own experience** — this is where your stories add credibility
