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
| Scheduled payment drain | Called at start of every method | `tryLock` drain (see note below) | Prevents out-of-order execution for same account |
| Spenders map | `HashMap` | `ConcurrentHashMap` | Thread-safe merge |
| Accounts map | `HashMap` | `ConcurrentHashMap` | Thread-safe lookup/insert |

**Deadlock prevention:** Always acquire per-account locks in sorted `accountId` order. If Thread A transfers (acct1 -> acct2) and Thread B transfers (acct2 -> acct1), both acquire acct1's lock first — no circular wait.

**Why the drain lock (`paymentDrainLock`)?**

The per-account lock in `makePayment` already protects balance correctness — two payments from different accounts can safely execute in parallel. The drain lock exists for **per-account ordering**. Without it:

- Thread A polls P1 (acct1, seq 1, amount 700)
- Thread B polls P2 (acct1, seq 2, amount 700) — same account, same timestamp
- Thread B acquires acct1's lock first, executes P2 (balance 1000 -> 300)
- Thread A acquires acct1's lock, executes P1 (balance 300 — insufficient, skipped!)
- Correct behavior: P1 should execute first (1000 -> 300), P2 should be skipped.

The `tryLock` (not `lock`) is deliberate — if another thread is already draining, skip and proceed. The next call catches up. This avoids blocking all operations on payment processing.

**If the interviewer says ordering doesn't matter:** you can drop the drain lock entirely. Per-account locks in `makePayment` are sufficient for balance correctness.

**Why `volatile` on `mergedInto` / `mergedAt`?**

These fields are read **without holding a lock** on several hot paths:

```java
// deposit — early rejection before acquiring lock
if (account.isDeleted()) return false;

// makePayment — redirect before acquiring lock
if (account.mergedInto != null) account = account.mergedInto;
```

Without `volatile`: Thread A completes `mergeAccounts` and sets `mergedInto` under the account lock, but Thread B's CPU core may still see the cached `null` from its local cache. Result: Thread B deposits into a dead account or skips the payment redirect.

`volatile` forces the write to flush to main memory immediately, and forces all reads to go to main memory — no stale cached values. This is cheaper than acquiring the account lock before every `isDeleted()` check, which would add contention on the most frequent code path.

The `mergedAt` field is also `volatile` because `getBalance` reads it outside the lock for the early `-1` return on merged accounts. Without `volatile`, a thread could see `mergedInto != null` (merged) but stale `mergedAt == -1` (not yet merged) — inconsistent state.

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

> "For concurrency, each `BankAccount` gets a `ReentrantLock`. Single-account ops lock one account; transfers and merges lock both in sorted accountId order to prevent deadlock. The payment counter becomes an `AtomicInteger`, the heap becomes a `PriorityBlockingQueue`, and the payment tracking sets become concurrent sets. Payments from different accounts can execute in parallel — the per-account lock handles balance correctness. If strict creation-order execution matters for same-account same-timestamp payments, I'd serialize the drain with a `tryLock` so one thread processes at a time; if not, the per-account lock is sufficient. The `mergedInto` and `mergedAt` fields are `volatile` so lock-free reads on hot paths (deposit's `isDeleted()` check, `makePayment`'s redirect) see the merge immediately without acquiring the account lock."
