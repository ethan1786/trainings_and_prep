# Bank System

**Category:** Coding
**Difficulty:** Hard
**Time Estimate:** 60 min
**Key Topics:** HashMap, Min-Heap, Lazy Deletion, Binary Search, Temporal Queries

---

## Problem Statement

Build a banking system that supports account management, fund transfers, scheduled payments, and point-in-time balance queries. Operations arrive with monotonically increasing timestamps in milliseconds.

## Requirements

### Level 1: Core Account Operations

```java
class BankSystem {
    boolean createAccount(int timestamp, String accountId);
    // Create account with $0 balance. False if ID already exists.

    boolean deposit(int timestamp, String accountId, int amount);
    // Deposit to account. False if account doesn't exist.

    boolean transfer(int timestamp, String sourceId, String targetId, int amount);
    // Transfer funds. False if: account missing, same account, insufficient balance.
}
```

### Level 2: Spending Analytics

```java
    List<String> topSpenders(int timestamp, int n);
    // Return top N accounts by total outgoing transfers.
    // Format: ["acc1(700)", "acc2(300)"]
    // Tiebreak: alphabetical by account_id.
    // Only successful transfers count — deposits do not.
```

### Level 3: Scheduled Payments

```java
    String schedulePayment(int timestamp, String accountId, int amount, int delay);
    // Schedule a deferred payment due at (timestamp + delay).
    // Returns unique payment ID like "payment1". Returns "" if account missing.
    // If balance insufficient at execution time, payment is silently skipped.
    // Successful payments count toward topSpenders.
    // Multiple same-timestamp payments execute in creation order.

    boolean cancelPayment(int timestamp, String accountId, String paymentId);
    // Cancel a pending payment. False if: already executed, already cancelled,
    // or doesn't belong to this account.
    // Critical: due payments execute BEFORE the cancel is evaluated.
```

**Execution ordering rule:** Every public method must process all due scheduled payments at the current timestamp *before* executing its own logic.

### Level 4: Account Merge and History

```java
    boolean mergeAccounts(int timestamp, String accountId1, String accountId2);
    // Merge accountId2 into accountId1.
    // - Balances and outgoing totals combine into accountId1.
    // - Pending payments from accountId2 transfer to accountId1.
    // - accountId2 is deleted but its history remains queryable for times before the merge.

    int getBalance(int timestamp, String accountId, int timeAt);
    // Return balance of account at historical time timeAt.
    // Returns -1 if: account never existed, didn't exist yet at timeAt,
    // or was already merged/deleted at timeAt.
```

---

## Solution Approach

### Level 1

**Core Idea:** HashMap from account_id to balance; all operations are O(1) lookups.

**Key Decisions:** No need for ordered structures at this level. Transfer validation order matters: existence check before same-account check before balance check.

```java
class BankSystem {
    private Map<String, Integer> accounts = new HashMap<>();

    boolean createAccount(int timestamp, String accountId) {
        if (accounts.containsKey(accountId)) return false;
        accounts.put(accountId, 0);
        return true;
    }

    boolean deposit(int timestamp, String accountId, int amount) {
        if (!accounts.containsKey(accountId)) return false;
        accounts.merge(accountId, amount, Integer::sum);
        return true;
    }

    boolean transfer(int timestamp, String sourceId, String targetId, int amount) {
        if (!accounts.containsKey(sourceId) || !accounts.containsKey(targetId)) return false;
        if (sourceId.equals(targetId)) return false;
        if (accounts.get(sourceId) < amount) return false;
        accounts.merge(sourceId, -amount, Integer::sum);
        accounts.merge(targetId, amount, Integer::sum);
        return true;
    }
}
```

**Complexity:** O(1) time per operation, O(N) space total.

### Level 2

**Core Idea:** Track cumulative outgoing per account in a parallel map; sort on demand.

**Key Decisions:** Don't maintain a sorted structure — `topSpenders` can be a rare query so O(A log A) sort at call time is fine. If it were called frequently, a heap or sorted container would be worth it.

```java
class BankSystem {
    private Map<String, Integer> accounts = new HashMap<>();
    private Map<String, Integer> outgoing = new HashMap<>();

    boolean createAccount(int timestamp, String accountId) {
        if (accounts.containsKey(accountId)) return false;
        accounts.put(accountId, 0);
        outgoing.put(accountId, 0);
        return true;
    }

    boolean transfer(int timestamp, String sourceId, String targetId, int amount) {
        // ... validation unchanged ...
        accounts.merge(sourceId, -amount, Integer::sum);
        accounts.merge(targetId, amount, Integer::sum);
        outgoing.merge(sourceId, amount, Integer::sum);
        return true;
    }

    List<String> topSpenders(int timestamp, int n) {
        return outgoing.entrySet().stream()
            .filter(e -> e.getValue() > 0)
            .sorted(Map.Entry.<String, Integer>comparingByValue(Comparator.reverseOrder())
                .thenComparing(Map.Entry.comparingByKey()))
            .limit(n)
            .map(e -> e.getKey() + "(" + e.getValue() + ")")
            .collect(Collectors.toList());
    }
}
```

**Complexity:** transfer O(1), topSpenders O(A log A) where A = number of accounts.

### Level 3

**Core Idea:** Min-heap keyed on `(due_time, creation_order)` for O(log P) scheduling. Lazy deletion via a `cancelled` set to avoid O(P) heap removal.

**Data Structures:**
- `scheduled`: min-heap of `int[] {dueTime, seq, amount}` plus parallel maps for paymentId/accountId
- `cancelled`: set of payment IDs — checked at pop time, not at insertion
- `executed`: set to prevent re-cancellation of already-fired payments

**Key Decisions:** The lazy deletion pattern is the core insight here. Removing from the middle of a heap is O(P); marking as cancelled and ignoring on pop is O(log P) amortized.

```java
class BankSystem {
    private Map<String, Integer> accounts = new HashMap<>();
    private Map<String, Integer> outgoing = new HashMap<>();
    private int paymentCounter = 0;
    // heap entry: [dueTime, seq, amount], parallel arrays for paymentId/accountId
    private PriorityQueue<int[]> scheduled = new PriorityQueue<>(
        Comparator.comparingInt((int[] e) -> e[0]).thenComparingInt(e -> e[1])
    );
    private Map<Integer, String> seqToPaymentId = new HashMap<>();
    private Map<Integer, String> seqToAccountId = new HashMap<>();
    private Set<String> cancelled = new HashSet<>();
    private Set<String> executed = new HashSet<>();

    private void processScheduled(int timestamp) {
        while (!scheduled.isEmpty() && scheduled.peek()[0] <= timestamp) {
            int[] entry = scheduled.poll();
            int seq = entry[1], amount = entry[2];
            String paymentId = seqToPaymentId.get(seq);
            String accountId = seqToAccountId.get(seq);
            if (cancelled.contains(paymentId)) continue;
            executed.add(paymentId);
            if (accounts.containsKey(accountId) && accounts.get(accountId) >= amount) {
                accounts.merge(accountId, -amount, Integer::sum);
                outgoing.merge(accountId, amount, Integer::sum);
            }
        }
    }

    String schedulePayment(int timestamp, String accountId, int amount, int delay) {
        processScheduled(timestamp);
        if (!accounts.containsKey(accountId)) return "";
        int seq = ++paymentCounter;
        String paymentId = "payment" + seq;
        seqToPaymentId.put(seq, paymentId);
        seqToAccountId.put(seq, accountId);
        scheduled.offer(new int[]{timestamp + delay, seq, amount});
        return paymentId;
    }

    boolean cancelPayment(int timestamp, String accountId, String paymentId) {
        processScheduled(timestamp);
        if (cancelled.contains(paymentId) || executed.contains(paymentId)) return false;
        for (int[] entry : scheduled) {
            int seq = entry[1];
            if (seqToPaymentId.get(seq).equals(paymentId)
                    && seqToAccountId.get(seq).equals(accountId)) {
                cancelled.add(paymentId);
                return true;
            }
        }
        return false;
    }
}
```

**Complexity:** schedulePayment O(log P), cancelPayment O(P) scan (unavoidable without a secondary index), processScheduled O(K log P) for K due payments.

### Level 4

**Core Idea:** Append `(timestamp, balance)` pairs to a per-account history list on every balance change. Use binary search on `timeAt` to answer point-in-time queries in O(log H).

**Key Decisions:** Keeping full history enables audit trails (financial regulatory requirement). The `mergedAt` sentinel distinguishes "never existed" from "existed then deleted."

```java
import java.util.*;

class BankSystem {
    private Map<String, Integer> accounts = new HashMap<>();
    private Map<String, Integer> outgoing = new HashMap<>();
    private int paymentCounter = 0;
    private PriorityQueue<int[]> scheduled = new PriorityQueue<>(
        Comparator.comparingInt((int[] e) -> e[0]).thenComparingInt(e -> e[1])
    );
    private Map<Integer, String> seqToPaymentId = new HashMap<>();
    private Map<Integer, String> seqToAccountId = new HashMap<>();
    private Set<String> cancelled = new HashSet<>();
    private Set<String> executed = new HashSet<>();
    private Map<String, List<int[]>> balanceHistory = new HashMap<>(); // accountId -> [[ts, bal]]
    private Map<String, Integer> createdAt = new HashMap<>();
    private Map<String, Integer> mergedAt = new HashMap<>();

    private void record(String accountId, int timestamp) {
        balanceHistory.get(accountId).add(new int[]{timestamp, accounts.get(accountId)});
    }

    private void processScheduled(int timestamp) {
        while (!scheduled.isEmpty() && scheduled.peek()[0] <= timestamp) {
            int[] entry = scheduled.poll();
            int dueTime = entry[0], seq = entry[1], amount = entry[2];
            String paymentId = seqToPaymentId.get(seq);
            String accountId = seqToAccountId.get(seq);
            if (cancelled.contains(paymentId)) continue;
            executed.add(paymentId);
            if (accounts.containsKey(accountId) && accounts.get(accountId) >= amount) {
                accounts.merge(accountId, -amount, Integer::sum);
                outgoing.merge(accountId, amount, Integer::sum);
                record(accountId, dueTime);
            }
        }
    }

    boolean createAccount(int timestamp, String accountId) {
        processScheduled(timestamp);
        if (accounts.containsKey(accountId)) return false;
        accounts.put(accountId, 0);
        outgoing.put(accountId, 0);
        createdAt.put(accountId, timestamp);
        balanceHistory.put(accountId, new ArrayList<>(List.of(new int[]{timestamp, 0})));
        return true;
    }

    boolean deposit(int timestamp, String accountId, int amount) {
        processScheduled(timestamp);
        if (!accounts.containsKey(accountId)) return false;
        accounts.merge(accountId, amount, Integer::sum);
        record(accountId, timestamp);
        return true;
    }

    boolean transfer(int timestamp, String sourceId, String targetId, int amount) {
        processScheduled(timestamp);
        if (!accounts.containsKey(sourceId) || !accounts.containsKey(targetId)) return false;
        if (sourceId.equals(targetId)) return false;
        if (accounts.get(sourceId) < amount) return false;
        accounts.merge(sourceId, -amount, Integer::sum);
        accounts.merge(targetId, amount, Integer::sum);
        outgoing.merge(sourceId, amount, Integer::sum);
        record(sourceId, timestamp);
        record(targetId, timestamp);
        return true;
    }

    List<String> topSpenders(int timestamp, int n) {
        processScheduled(timestamp);
        return outgoing.entrySet().stream()
            .filter(e -> e.getValue() > 0)
            .sorted(Map.Entry.<String, Integer>comparingByValue(Comparator.reverseOrder())
                .thenComparing(Map.Entry.comparingByKey()))
            .limit(n)
            .map(e -> e.getKey() + "(" + e.getValue() + ")")
            .collect(Collectors.toList());
    }

    String schedulePayment(int timestamp, String accountId, int amount, int delay) {
        processScheduled(timestamp);
        if (!accounts.containsKey(accountId)) return "";
        int seq = ++paymentCounter;
        String paymentId = "payment" + seq;
        seqToPaymentId.put(seq, paymentId);
        seqToAccountId.put(seq, accountId);
        scheduled.offer(new int[]{timestamp + delay, seq, amount});
        return paymentId;
    }

    boolean cancelPayment(int timestamp, String accountId, String paymentId) {
        processScheduled(timestamp);
        if (cancelled.contains(paymentId) || executed.contains(paymentId)) return false;
        for (int[] entry : scheduled) {
            int seq = entry[1];
            if (seqToPaymentId.get(seq).equals(paymentId)
                    && seqToAccountId.get(seq).equals(accountId)) {
                cancelled.add(paymentId);
                return true;
            }
        }
        return false;
    }

    boolean mergeAccounts(int timestamp, String accountId1, String accountId2) {
        processScheduled(timestamp);
        if (!accounts.containsKey(accountId1) || !accounts.containsKey(accountId2)) return false;
        if (accountId1.equals(accountId2)) return false;

        accounts.merge(accountId1, accounts.get(accountId2), Integer::sum);
        outgoing.merge(accountId1, outgoing.get(accountId2), Integer::sum);

        // Snapshot final balance of deleted account before removing
        balanceHistory.get(accountId2).add(new int[]{timestamp, accounts.get(accountId2)});
        mergedAt.put(accountId2, timestamp);

        // Re-assign pending payments from accountId2 to accountId1
        List<int[]> newEntries = new ArrayList<>();
        List<int[]> oldEntries = new ArrayList<>(scheduled);
        scheduled.clear();
        for (int[] e : oldEntries) {
            int seq = e[1];
            String acct = seqToAccountId.get(seq);
            if (acct.equals(accountId2) && !cancelled.contains(seqToPaymentId.get(seq))) {
                seqToAccountId.put(seq, accountId1);
            }
            scheduled.offer(e);
        }

        accounts.remove(accountId2);
        outgoing.remove(accountId2);
        record(accountId1, timestamp);
        return true;
    }

    int getBalance(int timestamp, String accountId, int timeAt) {
        processScheduled(timestamp);
        if (!balanceHistory.containsKey(accountId)) return -1;
        if (createdAt.getOrDefault(accountId, 0) > timeAt) return -1;
        if (mergedAt.containsKey(accountId) && mergedAt.get(accountId) <= timeAt) return -1;

        List<int[]> history = balanceHistory.get(accountId);
        // Binary search: find latest entry with timestamp <= timeAt
        int lo = 0, hi = history.size() - 1, idx = -1;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (history.get(mid)[0] <= timeAt) { idx = mid; lo = mid + 1; }
            else hi = mid - 1;
        }
        return idx >= 0 ? history.get(idx)[1] : -1;
    }
}
```

**Complexity:**

| Method | Time | Space |
|---|---|---|
| createAccount, deposit, transfer | O(log P) amortized (scheduled drain) | O(1) |
| topSpenders | O(A log A) | O(A) |
| schedulePayment | O(log P) | O(1) |
| cancelPayment | O(P) | O(1) |
| mergeAccounts | O(P) | O(1) |
| getBalance | O(log H) | O(1) |

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Concurrency:** Each account needs per-account locking for transfers (two-phase locking to avoid deadlock: always acquire in sorted account_id order). The scheduled heap needs its own lock.
- **Scheduled payment drift:** If the process is paused or crashes, payments that were due during downtime must execute correctly on restart. Timestamp monotonicity alone doesn't guarantee this — you need a persistent priority queue (e.g., backed by a sorted set in Redis or a DB table).
- **History growth:** `balance_history` grows unbounded. In production, you'd periodically archive old entries to cold storage and retain only a configurable lookback window in memory.
- **Atomic transfers:** At scale, cross-account transfers need to be atomic transactions. Double-spend or partial failure (debit succeeds, credit fails) is a serious correctness issue in financial systems.

### Common Interview Traps

- **_process_scheduled ordering:** Forgetting to call `_process_scheduled` in `cancel_payment` means a payment due *right now* could be cancelled instead of firing — violates the spec.
- **cancel_payment O(P) scan:** Most candidates miss that the `scheduled` heap doesn't support O(1) lookup by payment ID. An interviewer will probe this. Fix: maintain a secondary `dict[payment_id -> heap_entry]`.
- **merge_accounts history:** Deleting `account_id2` without appending a final snapshot means `get_balance` queries at the merge timestamp return wrong data.
- **Same-timestamp multiple entries:** `_record` can append multiple entries with the same timestamp. `bisect_right` handles this correctly; a naive linear scan may not.

### How to Push Forward as Staff+

- Proactively note that `cancel_payment` is O(P) and propose the secondary index fix before being asked.
- Mention that in a real payment system, scheduled payments would be stored durably (not in-memory heap) to survive restarts — connect to Coinbase's actual infrastructure concerns.
- Raise idempotency: what if the same `deposit` call is retried? Financial systems need idempotency keys.
- Point out that `merge_accounts` is a dangerous operation in real banking — it typically requires compliance checks, customer consent, and an audit trail. The interviewer may not have thought this through; surfacing it demonstrates domain awareness.
- Ask whether `get_balance` needs to be strongly consistent or can tolerate read-your-writes lag — relevant if the system is distributed.

---

## My Solution

**Design decisions vs reference solution:**
- `BankAccount` class with linked `Transaction` history instead of parallel maps — encapsulates per-account state cleanly
- `mergedInto` pointer on `BankAccount` — merged accounts silently redirect scheduled payments to the surviving account without an O(P) reassignment scan during merge
- Composite `fullPaymentId = accountId + ":" + paymentId` — gives O(1) ownership validation in `cancelPayment` (reference does O(P) heap scan)
- Linear scan for `getBalance` instead of binary search — simpler to code under time pressure; mention binary search upgrade if asked

**Key invariant:** merged accounts stay in the `accounts` map (for payment redirection and history queries) but `isDeleted()` returns true, so public operations reject them.

```java
class BankSystem {
    private static final String PAYMENT_ID_DELIMITER = ":";

    Map<String, BankAccount> accounts = new HashMap<>();
    Map<String, Integer> spenders = new HashMap<>();
    PriorityQueue<Payment> pendingPayment = new PriorityQueue<>((a, b) -> {
        if (a.timestamp != b.timestamp) {
            return a.timestamp - b.timestamp;
        }
        return a.paymentId.compareTo(b.paymentId);
    });
    int paymentSequence = 1;
    Set<String> existingPaymentIds = new HashSet<>();
    Set<String> cancelPaymentIds = new HashSet<>();

    boolean createAccount(int timestamp, String accountId) {
        checkAndExecutePayment(timestamp);
        if (accounts.containsKey(accountId)) {
            return false;
        }
        accounts.put(accountId, new BankAccount(timestamp, accountId));
        return true;
    }

    boolean deposit(int timestamp, String accountId, int amount) {
        checkAndExecutePayment(timestamp);
        if (!accounts.containsKey(accountId)) {
            return false;
        }
        BankAccount account = accounts.get(accountId);
        if (account.isDeleted()) {
            return false;
        }
        account.addTransaction(timestamp, amount);
        return true;
    }

    boolean transfer(int timestamp, String sourceId, String targetId, int amount) {
        checkAndExecutePayment(timestamp);
        if (!accounts.containsKey(sourceId) || !accounts.containsKey(targetId) || sourceId.equals(targetId)) {
            return false;
        }
        BankAccount s = accounts.get(sourceId);
        BankAccount t = accounts.get(targetId);
        if (s.getBalance() < amount || s.isDeleted() || t.isDeleted()) {
            return false;
        }
        s.addTransaction(timestamp, -amount);
        t.addTransaction(timestamp, amount);
        spenders.merge(sourceId, amount, Integer::sum);
        return true;
    }

    List<String> topSpenders(int timestamp, int n) {
        checkAndExecutePayment(timestamp);
        return spenders.entrySet().stream()
                .sorted((a, b) -> {
                    int cmp = Integer.compare(b.getValue(), a.getValue());
                    return cmp != 0 ? cmp : a.getKey().compareTo(b.getKey());
                })
                .limit(n)
                .map(entry -> entry.getKey() + "(" + entry.getValue() + ")")
                .toList();
    }

    void makePayment(int timestamp, String accountId, int amount) {
        if (!accounts.containsKey(accountId)) {
            return;
        }
        BankAccount account = accounts.get(accountId);
        if (account.mergedInto != null) {
            account = account.mergedInto;
        }
        if (account.getBalance() < amount) {
            return;
        }
        account.addTransaction(timestamp, -amount);
        spenders.merge(account.accountId, amount, Integer::sum);
    }

    void checkAndExecutePayment(int timestamp) {
        while (!pendingPayment.isEmpty() && pendingPayment.peek().timestamp <= timestamp) {
            Payment p = pendingPayment.poll();
            if (cancelPaymentIds.contains(p.paymentId)) {
                cancelPaymentIds.remove(p.paymentId);
            } else {
                makePayment(p.timestamp, p.accountId, p.amount);
            }
            existingPaymentIds.remove(p.paymentId);
        }
    }

    String schedulePayment(int timestamp, String accountId, int amount, int delay) {
        checkAndExecutePayment(timestamp);
        if (!accounts.containsKey(accountId)) {
            return "";
        }
        BankAccount account = accounts.get(accountId);
        if (account.isDeleted()) {
            return "";
        }
        int nextPaymentId = paymentSequence++;
        String paymentId = "payment" + nextPaymentId;
        String fullPaymentId = accountId + PAYMENT_ID_DELIMITER + paymentId;
        pendingPayment.offer(new Payment(fullPaymentId, timestamp + delay, accountId, amount));
        existingPaymentIds.add(fullPaymentId);
        return paymentId;
    }

    boolean cancelPayment(int timestamp, String accountId, String paymentId) {
        checkAndExecutePayment(timestamp);
        String fullPaymentId = accountId + PAYMENT_ID_DELIMITER + paymentId;
        if (!existingPaymentIds.contains(fullPaymentId) || cancelPaymentIds.contains(fullPaymentId)) {
            return false;
        }
        cancelPaymentIds.add(fullPaymentId);
        return true;
    }

    boolean mergeAccounts(int timestamp, String accountId1, String accountId2) {
        checkAndExecutePayment(timestamp);
        if (!accounts.containsKey(accountId1) || !accounts.containsKey(accountId2) || accountId1.equals(accountId2)) {
            return false;
        }
        BankAccount merged = accounts.get(accountId1);
        BankAccount toDelete = accounts.get(accountId2);
        if (merged.isDeleted() || toDelete.isDeleted()) {
            return false;
        }
        merged.addTransaction(timestamp, toDelete.getBalance());
        spenders.merge(accountId1, spenders.getOrDefault(accountId2, 0), Integer::sum);
        spenders.remove(accountId2);
        toDelete.mergeInto(merged, timestamp);
        return true;
    }

    int getBalance(int timestamp, String accountId, int timeAt) {
        checkAndExecutePayment(timestamp);
        if (!accounts.containsKey(accountId)) {
            return -1;
        }
        BankAccount account = accounts.get(accountId);
        if (account.isDeleted() && account.mergedAt <= timeAt) {
            return -1;
        }
        List<Transaction> transactions = account.transactions;
        if (transactions.getFirst().timestamp > timeAt) {
            return -1;
        }
        if (transactions.getLast().timestamp <= timeAt) {
            return transactions.getLast().balance;
        }
        for (int i = 0; i < transactions.size() - 1; i++) {
            if (transactions.get(i).timestamp <= timeAt && transactions.get(i + 1).timestamp > timeAt) {
                return transactions.get(i).balance;
            }
        }
        return -1;
    }

    private static class BankAccount {
        String accountId;
        List<Transaction> transactions;
        BankAccount mergedInto;
        int mergedAt = -1;

        BankAccount(int timestamp, String id) {
            accountId = id;
            transactions = new ArrayList<>();
            transactions.add(new Transaction(timestamp, 0));
        }

        void addTransaction(int timestamp, int amount) {
            transactions.add(new Transaction(timestamp, getBalance() + amount));
        }

        int getBalance() {
            return transactions.getLast().balance;
        }

        void mergeInto(BankAccount target, int timestamp) {
            mergedInto = target;
            mergedAt = timestamp;
        }

        boolean isDeleted() {
            return mergedInto != null;
        }
    }

    private static class Transaction {
        int timestamp;
        int balance;

        Transaction(int t, int b) {
            timestamp = t;
            balance = b;
        }
    }

    private static class Payment {
        String paymentId;
        int timestamp;
        String accountId;
        int amount;

        Payment(String p, int t, String a, int m) {
            paymentId = p;
            timestamp = t;
            accountId = a;
            amount = m;
        }
    }
}
```

---

## Concurrent Version (Follow-Up Discussion)

**Key changes from single-threaded version:**

| Component | Single-threaded | Concurrent | Why |
|---|---|---|---|
| Payment counter | `int` | `AtomicInteger` | Lock-free unique ID generation |
| Payment heap | `PriorityQueue` | `PriorityBlockingQueue` | Thread-safe poll/offer |
| Payment tracking sets | `HashSet` | `ConcurrentHashMap.newKeySet()` | Thread-safe contains/add/remove |
| Per-account balance | Unprotected | `ReentrantLock` on `BankAccount` | Protects balance reads/writes |
| Transfer (two accounts) | Unprotected | Lock both in **sorted accountId order** | Prevents deadlock |
| Scheduled payment drain | Called at start of every method | Separate draining with its own lock | Prevents concurrent double-execution |
| Spenders map | `HashMap` | `ConcurrentHashMap` | Thread-safe merge |
| Accounts map | `HashMap` | `ConcurrentHashMap` | Thread-safe lookup/insert |

**Deadlock prevention:** Always acquire per-account locks in sorted `accountId` order. If Thread A transfers (acct1 → acct2) and Thread B transfers (acct2 → acct1), both acquire acct1's lock first — no circular wait.

```java
class ConcurrentBankSystem {
    private static final String PAYMENT_ID_DELIMITER = ":";

    ConcurrentHashMap<String, BankAccount> accounts = new ConcurrentHashMap<>();
    ConcurrentHashMap<String, Integer> spenders = new ConcurrentHashMap<>();
    PriorityBlockingQueue<Payment> pendingPayment = new PriorityBlockingQueue<>(11, (a, b) -> {
        if (a.timestamp != b.timestamp) {
            return a.timestamp - b.timestamp;
        }
        return a.paymentId.compareTo(b.paymentId);
    });
    AtomicInteger paymentSequence = new AtomicInteger(1);
    Set<String> existingPaymentIds = ConcurrentHashMap.newKeySet();
    Set<String> cancelPaymentIds = ConcurrentHashMap.newKeySet();
    private final ReentrantLock paymentDrainLock = new ReentrantLock();

    private void lockTwo(BankAccount a, BankAccount b) {
        if (a.accountId.compareTo(b.accountId) < 0) {
            a.lock.lock();
            b.lock.lock();
        } else {
            b.lock.lock();
            a.lock.lock();
        }
    }

    private void unlockTwo(BankAccount a, BankAccount b) {
        a.lock.unlock();
        b.lock.unlock();
    }

    boolean createAccount(int timestamp, String accountId) {
        checkAndExecutePayment(timestamp);
        return accounts.putIfAbsent(accountId, new BankAccount(timestamp, accountId)) == null;
    }

    boolean deposit(int timestamp, String accountId, int amount) {
        checkAndExecutePayment(timestamp);
        BankAccount account = accounts.get(accountId);
        if (account == null || account.isDeleted()) {
            return false;
        }
        account.lock.lock();
        try {
            if (account.isDeleted()) return false;
            account.addTransaction(timestamp, amount);
            return true;
        } finally {
            account.lock.unlock();
        }
    }

    boolean transfer(int timestamp, String sourceId, String targetId, int amount) {
        checkAndExecutePayment(timestamp);
        if (sourceId.equals(targetId)) return false;
        BankAccount s = accounts.get(sourceId);
        BankAccount t = accounts.get(targetId);
        if (s == null || t == null) return false;
        lockTwo(s, t);
        try {
            if (s.isDeleted() || t.isDeleted()) return false;
            if (s.getBalance() < amount) return false;
            s.addTransaction(timestamp, -amount);
            t.addTransaction(timestamp, amount);
            spenders.merge(sourceId, amount, Integer::sum);
            return true;
        } finally {
            unlockTwo(s, t);
        }
    }

    List<String> topSpenders(int timestamp, int n) {
        checkAndExecutePayment(timestamp);
        return spenders.entrySet().stream()
                .sorted((a, b) -> {
                    int cmp = Integer.compare(b.getValue(), a.getValue());
                    return cmp != 0 ? cmp : a.getKey().compareTo(b.getKey());
                })
                .limit(n)
                .map(entry -> entry.getKey() + "(" + entry.getValue() + ")")
                .toList();
    }

    void makePayment(int timestamp, String accountId, int amount) {
        BankAccount account = accounts.get(accountId);
        if (account == null) return;
        if (account.mergedInto != null) {
            account = account.mergedInto;
        }
        account.lock.lock();
        try {
            if (account.getBalance() < amount) return;
            account.addTransaction(timestamp, -amount);
            spenders.merge(account.accountId, amount, Integer::sum);
        } finally {
            account.lock.unlock();
        }
    }

    void checkAndExecutePayment(int timestamp) {
        if (!paymentDrainLock.tryLock()) return;
        try {
            while (!pendingPayment.isEmpty() && pendingPayment.peek().timestamp <= timestamp) {
                Payment p = pendingPayment.poll();
                if (cancelPaymentIds.remove(p.paymentId)) {
                    // cancelled — skip
                } else {
                    makePayment(p.timestamp, p.accountId, p.amount);
                }
                existingPaymentIds.remove(p.paymentId);
            }
        } finally {
            paymentDrainLock.unlock();
        }
    }

    String schedulePayment(int timestamp, String accountId, int amount, int delay) {
        checkAndExecutePayment(timestamp);
        BankAccount account = accounts.get(accountId);
        if (account == null || account.isDeleted()) return "";
        int nextPaymentId = paymentSequence.getAndIncrement();
        String paymentId = "payment" + nextPaymentId;
        String fullPaymentId = accountId + PAYMENT_ID_DELIMITER + paymentId;
        pendingPayment.offer(new Payment(fullPaymentId, timestamp + delay, accountId, amount));
        existingPaymentIds.add(fullPaymentId);
        return paymentId;
    }

    boolean cancelPayment(int timestamp, String accountId, String paymentId) {
        checkAndExecutePayment(timestamp);
        String fullPaymentId = accountId + PAYMENT_ID_DELIMITER + paymentId;
        if (!existingPaymentIds.contains(fullPaymentId) || cancelPaymentIds.contains(fullPaymentId)) {
            return false;
        }
        cancelPaymentIds.add(fullPaymentId);
        return true;
    }

    boolean mergeAccounts(int timestamp, String accountId1, String accountId2) {
        checkAndExecutePayment(timestamp);
        if (accountId1.equals(accountId2)) return false;
        BankAccount merged = accounts.get(accountId1);
        BankAccount toDelete = accounts.get(accountId2);
        if (merged == null || toDelete == null) return false;
        lockTwo(merged, toDelete);
        try {
            if (merged.isDeleted() || toDelete.isDeleted()) return false;
            merged.addTransaction(timestamp, toDelete.getBalance());
            spenders.merge(accountId1, spenders.getOrDefault(accountId2, 0), Integer::sum);
            spenders.remove(accountId2);
            toDelete.mergeInto(merged, timestamp);
            return true;
        } finally {
            unlockTwo(merged, toDelete);
        }
    }

    int getBalance(int timestamp, String accountId, int timeAt) {
        checkAndExecutePayment(timestamp);
        BankAccount account = accounts.get(accountId);
        if (account == null) return -1;
        account.lock.lock();
        try {
            if (account.isDeleted() && account.mergedAt <= timeAt) return -1;
            List<Transaction> transactions = account.transactions;
            if (transactions.getFirst().timestamp > timeAt) return -1;
            if (transactions.getLast().timestamp <= timeAt) return transactions.getLast().balance;
            for (int i = 0; i < transactions.size() - 1; i++) {
                if (transactions.get(i).timestamp <= timeAt && transactions.get(i + 1).timestamp > timeAt) {
                    return transactions.get(i).balance;
                }
            }
            return -1;
        } finally {
            account.lock.unlock();
        }
    }

    private static class BankAccount {
        final String accountId;
        final ReentrantLock lock = new ReentrantLock();
        List<Transaction> transactions;
        volatile BankAccount mergedInto;
        volatile int mergedAt = -1;

        BankAccount(int timestamp, String id) {
            accountId = id;
            transactions = new ArrayList<>();
            transactions.add(new Transaction(timestamp, 0));
        }

        void addTransaction(int timestamp, int amount) {
            transactions.add(new Transaction(timestamp, getBalance() + amount));
        }

        int getBalance() {
            return transactions.getLast().balance;
        }

        void mergeInto(BankAccount target, int timestamp) {
            mergedInto = target;
            mergedAt = timestamp;
        }

        boolean isDeleted() {
            return mergedInto != null;
        }
    }

    private static class Transaction {
        final int timestamp;
        final int balance;

        Transaction(int t, int b) {
            timestamp = t;
            balance = b;
        }
    }

    private static class Payment {
        final String paymentId;
        final int timestamp;
        final String accountId;
        final int amount;

        Payment(String p, int t, String a, int m) {
            paymentId = p;
            timestamp = t;
            accountId = a;
            amount = m;
        }
    }
}
```

**What to say in the interview:**

> "For concurrency, each `BankAccount` gets a `ReentrantLock`. Single-account ops lock one account; transfers and merges lock both in sorted accountId order to prevent deadlock. The payment counter becomes an `AtomicInteger`, the heap becomes a `PriorityBlockingQueue`, and the payment tracking sets become concurrent sets. The drain loop uses `tryLock` so only one thread processes due payments — others skip and proceed, relying on the next call to catch up. The `mergedInto` and `mergedAt` fields are `volatile` so the redirect is visible to other threads immediately after merge."
