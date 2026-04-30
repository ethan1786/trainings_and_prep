# Application Design Round (60 min, Excalidraw on CoderPad)

**Format:** Whiteboarding, full-stack architecture — data model, API design, frontend considerations
**Tool:** Excalidraw on CoderPad, no AI allowed
**Deliverables:** Data models (pseudo-code), Swagger/OpenAPI endpoint specs, frontend discussion

This is the most unique round — it tests full-stack product thinking, not just backend infrastructure.

---

## What They're Evaluating

From the interview doc: "modeling data in the database, API interface design, frontend client considerations, and product sense."

Translation: Can you take a product requirement and design the full vertical — database → API → client?

---

## Framework

### 1. Clarify Product Requirements (5-7 min)
- What is the user trying to do? Who are the users?
- What are the core entities?
- What are the key workflows?
- What's the MVP vs nice-to-have?

### 2. Data Model (10-15 min)
- Draw entity-relationship diagram
- Write pseudo-code models in your preferred language:

```java
class Patient {
    Long id;
    String name;
    String email;
    String phone;
    LocalDateTime createdAt;
}

class LoanApplication {
    Long id;
    Long patientId;       // FK → Patient
    Long providerId;      // FK → Provider
    BigDecimal amount;
    LoanStatus status;    // PENDING, APPROVED, ACTIVE, COMPLETED, DEFAULTED
    LocalDateTime createdAt;
    LocalDateTime approvedAt;
}
```

- Call out: indexes, foreign keys, constraints, enum types
- Discuss: normalization vs denormalization tradeoffs

### 3. API Design (15-20 min)
- Write OpenAPI-style endpoint specs:

```yaml
POST /api/v1/loans
  Request:
    patientId: Long
    providerId: Long
    amount: BigDecimal
    term: Integer
  Response: 201
    loanId: Long
    status: "PENDING"

GET /api/v1/loans/{loanId}
  Response: 200
    id, patientId, providerId, amount, status, createdAt, ...

GET /api/v1/patients/{patientId}/loans
  Query params: status, page, pageSize, sort
  Response: 200
    items: [Loan], total, page, pageSize

PATCH /api/v1/loans/{loanId}/approve
  Response: 200
    status: "APPROVED"
```

- Cover: pagination, filtering, sorting, error responses
- Discuss: REST conventions, idempotency, versioning

### 4. Frontend Considerations (10 min)
- What pages/views does the client need?
- What data does each view fetch? (map to your endpoints)
- Loading states, error states, optimistic updates
- Caching: what's safe to cache client-side?
- Real-time: does anything need WebSocket/SSE? (e.g., payment status)

### 5. Iterate on New Requirements (ongoing)
- The interviewer will add requirements mid-session
- Don't redesign from scratch — extend your model
- "I'd add a `PaymentSchedule` entity here and a new endpoint..."
- This tests adaptability, not perfection

---

## Cherry-Relevant Domains to Practice

### Loan Application Flow (most likely)
- Entities: Patient, Provider, LoanApplication, PaymentPlan, Payment
- Workflows: apply → credit check → approve/deny → disburse → repay
- API: CRUD for applications, payment endpoints, status transitions
- Frontend: patient portal (apply, view status), provider portal (view applications), admin dashboard

### Provider Management
- Entities: Provider, Location, PlanConfiguration
- API: onboarding, plan setup, reporting
- Frontend: provider signup flow, dashboard with metrics

### Payment Processing
- Entities: Payment, PaymentMethod, Transaction, Refund
- State machine: scheduled → processing → completed / failed
- Idempotency keys on payment creation
- Audit trail: every state change logged

---

## Data Modeling Tips

- **Start with the core entity** — for BNPL, that's probably `LoanApplication`
- **Use enums for status fields** — show the state machine
- **Timestamps on everything** — createdAt, updatedAt, state transition times
- **Soft deletes** — financial data is never hard-deleted (compliance)
- **Money as BigDecimal** — never float/double. Call this out explicitly.
- **Separate auth from domain** — User/auth tables vs domain entities

## API Design Tips

- **Noun-based URLs:** `/loans`, `/patients`, not `/createLoan`
- **HTTP verbs:** POST (create), GET (read), PATCH (partial update), DELETE
- **Pagination:** offset-based (`page`, `pageSize`) or cursor-based (for real-time feeds)
- **Error responses:** consistent shape: `{ error: string, code: string, details: object }`
- **Versioning:** `/api/v1/` prefix
- **Idempotency:** `Idempotency-Key` header on POST for payment operations

## Frontend Considerations Tips

- **What data does the page need?** Map each view to 1-2 API calls
- **Optimistic updates:** "When the user clicks Approve, I'd update the UI immediately and roll back if the API fails"
- **Loading/error states:** "Each API call has loading, success, and error states — I'd use a state machine or React Query-style pattern"
- **Forms:** validation client-side AND server-side, never trust the client
- **Responsive:** mention mobile considerations if relevant

---

## Practice Exercise

Design a "Patient Loan Application" feature end-to-end:

1. Patient visits provider's office, wants to finance $5,000 procedure
2. Provider enters patient info and amount into their portal
3. System runs credit check (async)
4. Patient gets approved/denied notification
5. If approved: patient sees payment schedule, makes monthly payments
6. Provider gets paid upfront (Cherry fronts the money)

Draw: data model, 5-6 API endpoints, 3 frontend views (provider portal, patient portal, admin). Time yourself — 45 minutes.
