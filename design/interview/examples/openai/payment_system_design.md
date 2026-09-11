# Payment System Design

**Category:** System Design — **#1 Most Frequent SD (10+ occurrences)**
**Difficulty:** Medium-Hard
**Time:** 60 min
**Key Topics:** State Machine, Idempotency, Reconciliation, Batch Processing, Eventual Consistency

---

## Version 1: Offline Card Payment System (Hold + Batch Capture)

> Design a payment system that simulates in-person card-present transactions (not e-commerce).

### Flow
1. **Hold / Authorization:** authorize and place a hold when the card is presented.
2. **Capture / Charge:** perform the actual charge at a fixed nightly time via batch processing.

Payment Service forwards authorization/capture requests to a downstream external Credit Card Provider.

### Required APIs

```
authorize(merchant_id, card_token, amount, currency, idempotency_key)
capture(batch_time) or capturePendingAuthorizations()
void(auth_id)         // optional
refund(payment_id, amount)  // optional
```

### Requirements

1. **Data model:** key entities/fields for authorization, payment/charge, merchant, ledger/transactions.
2. **State machines:** state transitions for authorization and capture (e.g., PENDING → AUTHORIZED → CAPTURED → FAILED/EXPIRED/VOIDED).
3. **Idempotency & dedup:** handle merchant retries/network issues (idempotency key, provider request id).
4. **Reconciliation & consistency:**
   - Retries on failed nightly batch capture
   - Handling provider timeouts/unknown outcomes
   - Ensure "no double charge / no missing charge"
5. **Concurrency & isolation:** multiple authorizations for the same card/merchant in short time; avoid duplicate capture.
6. **Expiration & release:** hold TTL (e.g., 7 days) and auto-void on expiry.
7. **Observability:** logs/metrics/tracing/alerts to track a transaction end-to-end.

### Constraints (define your own)
- Authorization peak QPS (state assumptions)
- Batch capture window (e.g., 00:00–01:00) and worst-case backlog
- Eventual consistency acceptable, but money movement must NEVER double-charge

### Expected Output
- Architecture (components, storage, queues, schedulers, provider integration)
- Key sequences (authorize and nightly batch capture)
- Failure scenarios and compensating actions

---

## Version 2: General Payment System

> Design the core architecture of a payment system.

### Scope & Actors
- Payer (user/merchant)
- Payee
- External payment rails/providers

### Required APIs

```
createPayment(payer, payee, amount, currency, idempotency_key)
confirmPayment(payment_id)  // or executePayment
getPaymentStatus(payment_id)
cancelPayment(payment_id)
refund(payment_id, amount)
```

### Requirements

1. **Data model:** Payment / Charge / Authorization / Refund (as you see fit)
2. **State machine:** Pending → Authorized → Captured → Failed → Refunded, etc.
3. **Idempotency:** idempotency key on create
4. **Consistency & distributed transactions:** Saga / Outbox / eventual consistency
5. **Retries & deduplication**
6. **Reconciliation**
7. **Risk controls & rate limiting**
8. **Observability**

### Capacity/Performance Assumptions
- QPS, peak traffic, latency and availability targets

### Failure Modes & Mitigations
- Provider timeouts / duplicate callbacks / partial success
- Refund failures or delayed settlement

### Expected Output
- High-level architecture (services/components and interactions)
- Sequence of successful payment and failure+retry flow
- Storage choices and key schema fields

---

## Solution Approach

### High-Level Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Merchant /  │────▶│  Payment Service  │────▶│  Card Provider  │
│  Client      │     │  (Orchestrator)   │◀────│  (External)     │
└──────────────┘     └────────┬─────────┘     └─────────────────┘
                              │                        │
                    ┌─────────┼──────────┐             │
                    ▼         ▼          ▼             │
              ┌──────────┐ ┌────────┐ ┌──────────┐    │
              │Payment DB│ │ Ledger │ │  Queue   │    │
              │(Postgres)│ │(append)│ │(batch job)│    │
              └──────────┘ └────────┘ └──────────┘    │
                                                       │
                              ┌─────────────────┐      │
                              │  Webhook Handler │◀─────┘
                              │  (async events)  │
                              └─────────────────┘
```

### Core Components

| Component | Responsibility |
|---|---|
| **Payment Service** | Orchestrates auth/capture flow, manages state machine, handles idempotency |
| **Payment DB (Postgres)** | Source of truth for payment/authorization state |
| **Ledger** | Append-only audit trail of all money movements (double-entry) |
| **Batch Capture Job** | Scheduled nightly — queries AUTHORIZED payments, sends capture to provider |
| **Webhook Handler** | Listens for async provider events (confirmations, failures, chargebacks) |
| **Reconciliation Job** | Daily — compares internal state vs provider settlement file |

### Data Model

```sql
-- Authorization
CREATE TABLE authorizations (
    id              UUID PRIMARY KEY,
    merchant_id     UUID NOT NULL,
    card_token      VARCHAR NOT NULL,
    amount          BIGINT NOT NULL,  -- cents
    currency        VARCHAR(3) NOT NULL,
    idempotency_key VARCHAR UNIQUE NOT NULL,
    provider_auth_id VARCHAR,         -- from card provider
    status          VARCHAR NOT NULL, -- PENDING, AUTHORIZED, EXPIRED, VOIDED
    authorized_at   TIMESTAMP,
    expires_at      TIMESTAMP,        -- hold TTL (e.g., +7 days)
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Payment / Capture
CREATE TABLE payments (
    id              UUID PRIMARY KEY,
    authorization_id UUID REFERENCES authorizations(id),
    amount          BIGINT NOT NULL,
    status          VARCHAR NOT NULL, -- PENDING_CAPTURE, CAPTURED, FAILED, REFUNDED
    provider_charge_id VARCHAR,
    captured_at     TIMESTAMP,
    batch_id        VARCHAR,          -- which nightly batch processed this
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Ledger (append-only, double-entry)
CREATE TABLE ledger_entries (
    id              UUID PRIMARY KEY,
    payment_id      UUID REFERENCES payments(id),
    entry_type      VARCHAR NOT NULL, -- DEBIT, CREDIT
    account         VARCHAR NOT NULL, -- merchant_account, platform_account
    amount          BIGINT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### State Machine

```
Authorization States:
  PENDING → AUTHORIZED → CAPTURED
                       → EXPIRED (hold TTL exceeded)
                       → VOIDED (merchant cancelled)
            → DECLINED (provider rejected)

Payment/Capture States:
  PENDING_CAPTURE → CAPTURED → REFUNDED (partial or full)
                  → FAILED → RETRY_PENDING → CAPTURED
                           → PERMANENTLY_FAILED
```

### Key Sequences

#### Authorize Flow

```
1. Merchant calls authorize(merchant_id, card_token, amount, currency, idempotency_key)
2. Payment Service:
   a. Check idempotency_key in DB — if exists, return cached result
   b. Create authorization record (status=PENDING)
   c. Call Provider.authorize(card_token, amount)
   d. Provider returns auth_id + success/failure
   e. Update authorization (status=AUTHORIZED, provider_auth_id, expires_at=now+7d)
   f. Return auth_id to merchant
```

#### Nightly Batch Capture Flow

```
1. Scheduler triggers capturePendingAuthorizations() at 00:00
2. Query: SELECT * FROM authorizations WHERE status='AUTHORIZED' AND expires_at > NOW()
3. For each authorization:
   a. Create payment record (status=PENDING_CAPTURE)
   b. Call Provider.capture(provider_auth_id, amount)
   c. If success: update payment (status=CAPTURED), write ledger entries
   d. If failure: update payment (status=FAILED), schedule retry
   e. If timeout: mark UNKNOWN, reconciliation job will resolve
4. Log batch summary (total, success, failed, unknown)
```

#### Failure + Retry Flow

```
1. Provider.capture() times out → payment status = UNKNOWN
2. Reconciliation job (runs after batch):
   a. Query provider for status of UNKNOWN payments
   b. Provider says "captured" → update to CAPTURED + write ledger
   c. Provider says "not captured" → retry capture (up to 3 attempts)
   d. Provider says "auth expired" → mark PERMANENTLY_FAILED, alert
3. If all retries fail → alert ops team, manual resolution
```

### Idempotency Design

```
authorize():
  - Idempotency key = merchant-provided (e.g., transaction_ref)
  - Before processing: SELECT WHERE idempotency_key = ?
  - If exists: return cached result (same auth_id, same status)
  - If not: proceed with new authorization

capture():
  - Natural idempotency: one authorization → one capture attempt
  - Guard: IF payment.status already CAPTURED → skip
  - Provider-side: provider_auth_id used as dedup key at provider

Webhook:
  - Provider may send same webhook multiple times
  - Dedup: store webhook event_id, skip if already processed
```

### Concurrency & Isolation

**Problem:** Two capture attempts for same authorization (batch retry + manual retry)

**Solution:** Optimistic locking
```sql
UPDATE authorizations 
SET status = 'CAPTURED', version = version + 1
WHERE id = ? AND status = 'AUTHORIZED' AND version = ?
-- If rows_affected = 0 → someone else captured it, skip
```

Or: database advisory lock per authorization_id during capture.

### Expiration & Auto-Void

```
-- Scheduled job every hour:
UPDATE authorizations 
SET status = 'EXPIRED'
WHERE status = 'AUTHORIZED' AND expires_at < NOW()

-- Optionally: call Provider.void(provider_auth_id) to release hold on card
```

### Reconciliation

```
Daily reconciliation job:
1. Fetch settlement file from provider (all captures in last 24h)
2. Compare against internal ledger:
   - Provider has capture we don't → ALERT (money moved without our record)
   - We have capture provider doesn't → ALERT (we think charged but provider didn't)
   - Amounts don't match → ALERT
3. Auto-resolve known patterns (e.g., timezone edge cases)
4. Flag unresolvable discrepancies for manual review
```

### Observability

| Signal | What to Monitor |
|---|---|
| Auth success rate | Per merchant, per provider — detect degradation |
| Batch capture duration | Should complete within window (00:00-01:00) |
| Failed captures | Count per batch — alert if > threshold |
| UNKNOWN payment count | Should be near zero after reconciliation |
| Hold expiration rate | High rate = merchants not capturing timely |
| Reconciliation mismatches | Should be zero — any mismatch is critical |

### Capacity Assumptions (state in interview)

```
Authorization QPS:
  - Assume 10K merchants, each with ~100 transactions/day
  - = 1M auths/day ÷ 100K seconds = ~10 QPS average, ~50 QPS peak
  - Single Postgres handles this easily

Batch capture:
  - 1M pending authorizations to capture in 1-hour window
  - = ~280 captures/sec — parallelizable, not a bottleneck
  - Use 10 worker threads, each processing ~28/sec

Storage:
  - 1M rows/day × 500 bytes = 500MB/day = ~180GB/year
  - Postgres handles this. Archive after 90 days if needed.
```

---

## Connection to Your Experience (Domain Interview Overlap)

This question is almost identical to your Coinbase domain interview prep:
- **Auth-then-capture** = your reservation deposit flow (STARTED → CONFIRMED → CAPTURED)
- **Webhook handling** = your payment provider webhook + idempotency
- **Reconciliation** = your daily batch validation against provider
- **State machine** = your reservation states
- **Idempotency** = your Redis dedup key (customer_id + vehicle_id)

**Lead with:** "I've built exactly this system. Here's how it works..."

---

## Key Talking Points (Staff+ Signals)

1. **"Money can never be double-charged"** — idempotency at every layer (client key, DB unique constraint, provider dedup)
2. **"Unknown is the hardest state"** — provider timeout means you don't know if money moved. Reconciliation is the safety net.
3. **"Ledger is append-only"** — never mutate financial records. Every state change is a new entry.
4. **"Batch processing has failure modes"** — what if batch job crashes mid-way? Answer: each capture is independent + idempotent. Restart picks up where it left off.
5. **"Reconciliation catches everything else"** — belt and suspenders. Even with perfect idempotency, verify against provider daily.
