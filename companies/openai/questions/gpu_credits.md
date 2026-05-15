# GPU Credits (Credit Ledger System)

**Category:** Coding — **#2 Most Frequent (8+ occurrences)**
**Difficulty:** Medium (progressive parts)
**Time:** 60 min
**Key Topics:** TreeMap/PriorityQueue, Sorted Expiry, State Management, Out-of-Order Events

---

## Problem Variants

### Version 1: Core GPU Credit Grants (Most Common)

Implement a GPU credits ledger that supports creating grants, subtracting credits, and querying balance. Credits are issued as grants, each with an expiration time. When subtracting credits, deduct from grants in order of **earliest expiration first**.

#### APIs

```
create_grant(grant_id, amount, expire_time)
subtract(amount, time)
get_balance(time)
```

#### Rules
- Only non-expired grants can be used (grant expired when `time >= expire_time`)
- Deduct in increasing `expire_time` order (earliest expiring first)
- `subtract` mutates remaining credits — affects future `subtract` and `get_balance` calls
- Up to 2 × 10^5 operations

#### Test Cases

```
# 1. Deduct earliest-expiring first
create_grant(A, 10, 5)
create_grant(B, 10, 7)
subtract(12, 4)
get_balance(4) => 8    # A had 10, B had 10. Deduct 10 from A, 2 from B. B has 8 left.

# 2. Expired credits not counted
create_grant(A, 10, 5)
get_balance(6) => 0    # A expired at time 5

# 3. Subtraction affects the future
create_grant(A, 10, 100)
subtract(3, 1)
get_balance(2) => 7    # A was 10, subtracted 3, now 7

# 4. Skip expired grants when subtracting
create_grant(A, 10, 5)
create_grant(B, 10, 100)
subtract(6, 10)        # At time 10, A is expired. Only B available.
get_balance(10) => 4   # B was 10, subtracted 6, now 4.

# 5. Insufficient balance (clarify behavior)
create_grant(A, 5, 100)
subtract(10, 1)
get_balance(1) => ?    # Clamp to 0? Error? Return failure?
```

### Version 2: Event-Based with Query Time

> Given a list of GPU credit change events (grant, consume, expire), compute remaining credits at a given query time or over a query interval. Handle event ordering and edge cases (multiple events at same timestamp).

### Version 3: Out-of-Order Events

> Events (adding or consuming credits) may arrive and be processed **out of order** with respect to their timestamp. At any time, you may query the total available credits at a particular timestamp or attempt to consume/revoke credits at a specified time.

### Version 4: Advanced (Multiple Accounts / Batch / Settlement)

> Add complex credit rules: multiple accounts, batch queries, prioritization/expiration strategies, settlement across time windows.

---

## Solution: Version 1 (Core)

**Core Idea:** Maintain grants sorted by `expire_time`. On subtract, iterate from earliest-expiring and deduct. On get_balance, sum all non-expired grants.

```java
class GPUCreditLedger {
    // TreeMap: expire_time → list of grants expiring at that time
    // Need to handle multiple grants with same expire_time
    // Better: sorted list of grants by expire_time
    
    private List<Grant> grants = new ArrayList<>(); // kept sorted by expire_time
    
    static class Grant {
        String id;
        int remaining;
        int expireTime;
        
        Grant(String id, int amount, int expireTime) {
            this.id = id;
            this.remaining = amount;
            this.expireTime = expireTime;
        }
    }
    
    void createGrant(String grantId, int amount, int expireTime) {
        Grant g = new Grant(grantId, amount, expireTime);
        // Insert in sorted order by expireTime
        int idx = 0;
        while (idx < grants.size() && grants.get(idx).expireTime <= expireTime) {
            idx++;
        }
        grants.add(idx, g);
    }
    
    void subtract(int amount, int time) {
        int remaining = amount;
        for (Grant g : grants) {
            if (remaining <= 0) break;
            if (g.expireTime <= time) continue;  // expired, skip
            if (g.remaining <= 0) continue;       // already depleted
            
            int deduct = Math.min(remaining, g.remaining);
            g.remaining -= deduct;
            remaining -= deduct;
        }
        // If remaining > 0: insufficient balance — clarify with interviewer
    }
    
    int getBalance(int time) {
        int balance = 0;
        for (Grant g : grants) {
            if (g.expireTime > time) {  // not expired
                balance += g.remaining;
            }
        }
        return balance;
    }
}
```

**Complexity:**
- `create_grant`: O(N) for sorted insertion (or O(log N) with TreeMap)
- `subtract`: O(N) scan through grants
- `get_balance`: O(N) scan through grants

**For 2×10^5 operations:** O(N) per operation = O(N^2) worst case = 4×10^10. Too slow?

**Optimization with TreeMap:**

```java
class GPUCreditLedger {
    // TreeMap<expireTime, List<Grant>> — sorted by expiry
    private TreeMap<Integer, List<Grant>> grantsByExpiry = new TreeMap<>();
    
    static class Grant {
        String id;
        int remaining;
        
        Grant(String id, int remaining) {
            this.id = id;
            this.remaining = remaining;
        }
    }
    
    void createGrant(String grantId, int amount, int expireTime) {
        grantsByExpiry.computeIfAbsent(expireTime, k -> new ArrayList<>())
                      .add(new Grant(grantId, amount));
    }
    
    void subtract(int amount, int time) {
        int remaining = amount;
        // tailMap(time, false) = all entries with key > time (not expired)
        // But we want earliest expiry first among non-expired
        // subMap(time+1, true, Integer.MAX_VALUE, true) = not expired, sorted by expiry
        for (Map.Entry<Integer, List<Grant>> entry : grantsByExpiry.tailMap(time, false).entrySet()) {
            if (remaining <= 0) break;
            for (Grant g : entry.getValue()) {
                if (remaining <= 0) break;
                if (g.remaining <= 0) continue;
                int deduct = Math.min(remaining, g.remaining);
                g.remaining -= deduct;
                remaining -= deduct;
            }
        }
    }
    
    int getBalance(int time) {
        int balance = 0;
        // All grants with expireTime > time are valid
        for (List<Grant> grantList : grantsByExpiry.tailMap(time, false).values()) {
            for (Grant g : grantList) {
                balance += g.remaining;
            }
        }
        return balance;
    }
}
```

**Note on expiry check:** A grant is expired when `time >= expire_time`. So valid grants have `expire_time > time`. Use `tailMap(time, false)` which gives all keys strictly greater than `time`.

---

## Solution: Version 3 (Out-of-Order Events)

**Key challenge:** Events arrive out of timestamp order. A subtract at time=5 might arrive AFTER a subtract at time=10.

**Approach 1: Replay-based (simple but slow)**
- Store all events in a list
- On every query, sort events by timestamp and replay from scratch
- O(N log N) per query — too slow for large N

**Approach 2: Snapshot + incremental**
- Maintain a sorted event log (by timestamp)
- When a new event arrives out of order, insert it at the correct position
- Invalidate and recompute state from that point forward
- Cache/snapshot state at intervals for faster replay

**Approach 3: Persistent data structure (functional)**
- Each timestamp has an immutable state
- Adding an event creates a new state branch
- Complex but correct

**For interview (pragmatic):**

```java
class GPUCreditLedgerV3 {
    // Store all events sorted by timestamp
    private TreeMap<Integer, List<Event>> events = new TreeMap<>();
    
    static class Event {
        enum Type { GRANT, SUBTRACT }
        Type type;
        String grantId;
        int amount;
        int expireTime; // for GRANT only
        
        // constructors...
    }
    
    void addGrant(String grantId, int amount, int expireTime, int eventTime) {
        events.computeIfAbsent(eventTime, k -> new ArrayList<>())
              .add(new Event(Event.Type.GRANT, grantId, amount, expireTime));
    }
    
    void subtract(int amount, int time) {
        events.computeIfAbsent(time, k -> new ArrayList<>())
              .add(new Event(Event.Type.SUBTRACT, null, amount, 0));
    }
    
    int getBalance(int queryTime) {
        // Replay all events up to queryTime in order
        // Build grant state, apply subtractions, return balance
        TreeMap<Integer, List<GrantState>> activeGrants = new TreeMap<>();
        
        for (Map.Entry<Integer, List<Event>> entry : events.headMap(queryTime, true).entrySet()) {
            int eventTime = entry.getKey();
            for (Event e : entry.getValue()) {
                if (e.type == Event.Type.GRANT) {
                    activeGrants.computeIfAbsent(e.expireTime, k -> new ArrayList<>())
                                .add(new GrantState(e.grantId, e.amount));
                } else { // SUBTRACT
                    subtractFromGrants(activeGrants, e.amount, eventTime);
                }
            }
        }
        
        // Sum remaining in non-expired grants
        int balance = 0;
        for (Map.Entry<Integer, List<GrantState>> entry : activeGrants.tailMap(queryTime, false).entrySet()) {
            for (GrantState g : entry.getValue()) {
                balance += g.remaining;
            }
        }
        return balance;
    }
    
    private void subtractFromGrants(TreeMap<Integer, List<GrantState>> grants, int amount, int time) {
        int remaining = amount;
        for (Map.Entry<Integer, List<GrantState>> entry : grants.tailMap(time, false).entrySet()) {
            if (remaining <= 0) break;
            for (GrantState g : entry.getValue()) {
                if (remaining <= 0) break;
                if (g.remaining <= 0) continue;
                int deduct = Math.min(remaining, g.remaining);
                g.remaining -= deduct;
                remaining -= deduct;
            }
        }
    }
    
    static class GrantState {
        String id;
        int remaining;
        GrantState(String id, int remaining) { this.id = id; this.remaining = remaining; }
    }
}
```

**Tradeoff:** Replay is O(N) per query but handles out-of-order correctly. For interview, explain the approach and optimize if asked.

---

## Edge Cases to Clarify with Interviewer

1. **Insufficient balance on subtract:** Return error? Clamp to 0? Deduct what's available and return remaining?
2. **Same expire_time for multiple grants:** Which is deducted first? FIFO (creation order)? Or doesn't matter?
3. **Subtract at exact expire_time:** Is the grant still valid? (Likely NO — `time >= expire_time` means expired)
4. **Create grant in the past (out-of-order):** Does it retroactively affect previous subtractions? (Version 3)
5. **Negative amounts:** Can amounts be 0? Negative?
6. **Future grants:** Can a grant be created with expire_time in the past? (Already expired on creation)

---

## Interview Strategy

| Part | What They Test | Time Target |
|---|---|---|
| Basic create_grant + get_balance | Data structure choice, expiry logic | 5-8 min |
| Add subtract (earliest expiry first) | Sorted iteration, mutation | 10-12 min |
| Edge cases (expired grants, insufficient balance) | Correctness, attention to detail | 5-8 min |
| Follow-up: out-of-order events | System design thinking, event sourcing | 15-20 min |
| Follow-up: multiple accounts or batch | Extensibility | If time permits |

**Tips:**
- Start with the simple ArrayList version — get it working first
- Mention TreeMap optimization proactively ("for 2×10^5 ops, I'd use a TreeMap for O(log N) lookups")
- The "expired at time" boundary condition is the #1 bug source — clarify: `expire_time > time` means valid
- Ask about insufficient balance behavior BEFORE coding

---

## Similarity to Coinbase Coding Questions

This problem is structurally similar to Coinbase's **Pagination** and **Crypto Order** questions:
- CRUD operations with state that evolves over time
- Need to handle ordering/priority (expire_time = cursor/offset)
- Edge cases around boundaries and mutations

If you've solved Coinbase coding questions, the pattern recognition transfers directly.
