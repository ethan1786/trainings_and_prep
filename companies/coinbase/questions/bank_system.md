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

```python
class BankSystem:
    def create_account(self, timestamp: int, account_id: str) -> bool:
        """Create account with $0 balance. False if ID already exists."""

    def deposit(self, timestamp: int, account_id: str, amount: int) -> bool:
        """Deposit to account. False if account doesn't exist."""

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> bool:
        """Transfer funds. False if: account missing, same account, insufficient balance."""
```

### Level 2: Spending Analytics

```python
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        Return top N accounts by total outgoing transfers.
        Format: ["acc1(700)", "acc2(300)"]
        Tiebreak: alphabetical by account_id.
        Only successful transfers count — deposits do not.
        """
```

### Level 3: Scheduled Payments

```python
    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str:
        """
        Schedule a deferred payment due at (timestamp + delay).
        Returns unique payment ID like "payment1". Returns "" if account missing.
        If balance insufficient at execution time, payment is silently skipped.
        Successful payments count toward top_spenders.
        Multiple same-timestamp payments execute in creation order.
        """

    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        """
        Cancel a pending payment. False if: already executed, already cancelled,
        or doesn't belong to this account.
        Critical: due payments execute BEFORE the cancel is evaluated.
        """
```

**Execution ordering rule:** Every public method must process all due scheduled payments at the current timestamp *before* executing its own logic.

### Level 4: Account Merge and History

```python
    def merge_accounts(self, timestamp: int, account_id1: str, account_id2: str) -> bool:
        """
        Merge account_id2 into account_id1.
        - Balances and outgoing totals combine into account_id1.
        - Pending payments from account_id2 transfer to account_id1.
        - account_id2 is deleted but its history remains queryable for times before the merge.
        """

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int:
        """
        Return balance of account at historical time time_at.
        Returns -1 if: account never existed, didn't exist yet at time_at,
        or was already merged/deleted at time_at.
        """
```

---

## Solution Approach

### Level 1

**Core Idea:** HashMap from account_id to balance; all operations are O(1) lookups.

**Key Decisions:** No need for ordered structures at this level. Transfer validation order matters: existence check before same-account check before balance check.

```python
class BankSystem:
    def __init__(self):
        self.accounts = {}  # account_id -> balance

    def create_account(self, timestamp: int, account_id: str) -> bool:
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = 0
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> bool:
        if account_id not in self.accounts:
            return False
        self.accounts[account_id] += amount
        return True

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> bool:
        if source_id not in self.accounts or target_id not in self.accounts:
            return False
        if source_id == target_id:
            return False
        if self.accounts[source_id] < amount:
            return False
        self.accounts[source_id] -= amount
        self.accounts[target_id] += amount
        return True
```

**Complexity:** O(1) time per operation, O(N) space total.

### Level 2

**Core Idea:** Track cumulative outgoing per account in a parallel dict; sort on demand.

**Key Decisions:** Don't maintain a sorted structure — `top_spenders` can be a rare query so O(A log A) sort at call time is fine. If it were called frequently, a heap or sorted container would be worth it.

```python
    def __init__(self):
        self.accounts = {}
        self.outgoing = {}  # account_id -> total sent

    def create_account(self, timestamp, account_id):
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = 0
        self.outgoing[account_id] = 0
        return True

    def transfer(self, timestamp, source_id, target_id, amount):
        # ... validation unchanged ...
        self.accounts[source_id] -= amount
        self.accounts[target_id] += amount
        self.outgoing[source_id] += amount
        return True

    def top_spenders(self, timestamp: int, n: int) -> list:
        spenders = [(aid, total) for aid, total in self.outgoing.items() if total > 0]
        spenders.sort(key=lambda x: (-x[1], x[0]))
        return [f"{aid}({total})" for aid, total in spenders[:n]]
```

**Complexity:** transfer O(1), top_spenders O(A log A) where A = number of accounts.

### Level 3

**Core Idea:** Min-heap keyed on `(due_time, creation_order)` for O(log P) scheduling. Lazy deletion via a `cancelled` set to avoid O(P) heap removal.

**Data Structures:**
- `scheduled`: min-heap of `(due_time, seq, payment_id, account_id, amount)`
- `cancelled`: set of payment IDs — checked at pop time, not at insertion
- `executed`: set to prevent re-cancellation of already-fired payments

**Key Decisions:** The lazy deletion pattern is the core insight here. Removing from the middle of a heap is O(P); marking as cancelled and ignoring on pop is O(log P) amortized.

```python
import heapq

class BankSystem:
    def __init__(self):
        self.accounts = {}
        self.outgoing = {}
        self.payment_counter = 0
        self.scheduled = []
        self.cancelled = set()
        self.executed = set()

    def _process_scheduled(self, timestamp: int):
        while self.scheduled and self.scheduled[0][0] <= timestamp:
            due_time, _, payment_id, account_id, amount = heapq.heappop(self.scheduled)
            if payment_id in self.cancelled:
                continue
            self.executed.add(payment_id)
            if account_id in self.accounts and self.accounts[account_id] >= amount:
                self.accounts[account_id] -= amount
                self.outgoing[account_id] += amount

    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str:
        self._process_scheduled(timestamp)
        if account_id not in self.accounts:
            return ""
        self.payment_counter += 1
        payment_id = f"payment{self.payment_counter}"
        heapq.heappush(
            self.scheduled,
            (timestamp + delay, self.payment_counter, payment_id, account_id, amount)
        )
        return payment_id

    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        self._process_scheduled(timestamp)
        if payment_id in self.cancelled or payment_id in self.executed:
            return False
        for entry in self.scheduled:
            if entry[2] == payment_id and entry[3] == account_id:
                self.cancelled.add(payment_id)
                return True
        return False
```

**Complexity:** schedule_payment O(log P), cancel_payment O(P) scan (unavoidable without a secondary index), _process_scheduled O(K log P) for K due payments.

### Level 4

**Core Idea:** Append `(timestamp, balance)` tuples to a per-account history list on every balance change. Use binary search on `time_at` to answer point-in-time queries in O(log H).

**Key Decisions:** Keeping full history enables audit trails (financial regulatory requirement). The `merged_at` sentinel distinguishes "never existed" from "existed then deleted."

```python
import heapq
from bisect import bisect_right

class BankSystem:
    def __init__(self):
        self.accounts = {}
        self.outgoing = {}
        self.payment_counter = 0
        self.scheduled = []
        self.cancelled = set()
        self.executed = set()
        self.balance_history = {}   # account_id -> [(timestamp, balance)]
        self.created_at = {}
        self.merged_at = {}         # account_id -> merge timestamp

    def _record(self, account_id: str, timestamp: int):
        self.balance_history[account_id].append((timestamp, self.accounts[account_id]))

    def _process_scheduled(self, timestamp: int):
        while self.scheduled and self.scheduled[0][0] <= timestamp:
            due_time, _, payment_id, account_id, amount = heapq.heappop(self.scheduled)
            if payment_id in self.cancelled:
                continue
            self.executed.add(payment_id)
            if account_id in self.accounts and self.accounts[account_id] >= amount:
                self.accounts[account_id] -= amount
                self.outgoing[account_id] += amount
                self._record(account_id, due_time)

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process_scheduled(timestamp)
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = 0
        self.outgoing[account_id] = 0
        self.created_at[account_id] = timestamp
        self.balance_history[account_id] = [(timestamp, 0)]
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> bool:
        self._process_scheduled(timestamp)
        if account_id not in self.accounts:
            return False
        self.accounts[account_id] += amount
        self._record(account_id, timestamp)
        return True

    def transfer(self, timestamp: int, source_id: str, target_id: str, amount: int) -> bool:
        self._process_scheduled(timestamp)
        if source_id not in self.accounts or target_id not in self.accounts:
            return False
        if source_id == target_id:
            return False
        if self.accounts[source_id] < amount:
            return False
        self.accounts[source_id] -= amount
        self.accounts[target_id] += amount
        self.outgoing[source_id] += amount
        self._record(source_id, timestamp)
        self._record(target_id, timestamp)
        return True

    def top_spenders(self, timestamp: int, n: int) -> list:
        self._process_scheduled(timestamp)
        spenders = [(aid, t) for aid, t in self.outgoing.items() if t > 0]
        spenders.sort(key=lambda x: (-x[1], x[0]))
        return [f"{aid}({t})" for aid, t in spenders[:n]]

    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str:
        self._process_scheduled(timestamp)
        if account_id not in self.accounts:
            return ""
        self.payment_counter += 1
        pid = f"payment{self.payment_counter}"
        heapq.heappush(self.scheduled, (timestamp + delay, self.payment_counter, pid, account_id, amount))
        return pid

    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        self._process_scheduled(timestamp)
        if payment_id in self.cancelled or payment_id in self.executed:
            return False
        for entry in self.scheduled:
            if entry[2] == payment_id and entry[3] == account_id:
                self.cancelled.add(payment_id)
                return True
        return False

    def merge_accounts(self, timestamp: int, account_id1: str, account_id2: str) -> bool:
        self._process_scheduled(timestamp)
        if account_id1 not in self.accounts or account_id2 not in self.accounts:
            return False
        if account_id1 == account_id2:
            return False

        self.accounts[account_id1] += self.accounts[account_id2]
        self.outgoing[account_id1] += self.outgoing[account_id2]

        # Snapshot final balance of deleted account before removing
        self.balance_history[account_id2].append((timestamp, self.accounts[account_id2]))
        self.merged_at[account_id2] = timestamp

        # Re-assign pending payments from account_id2 to account_id1
        self.scheduled = [
            (t, seq, pid, account_id1 if acct == account_id2 and pid not in self.cancelled else acct, amt)
            for t, seq, pid, acct, amt in self.scheduled
        ]
        heapq.heapify(self.scheduled)

        del self.accounts[account_id2]
        del self.outgoing[account_id2]
        self._record(account_id1, timestamp)
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int:
        self._process_scheduled(timestamp)
        if account_id not in self.balance_history:
            return -1
        if self.created_at.get(account_id, 0) > time_at:
            return -1
        if account_id in self.merged_at and self.merged_at[account_id] <= time_at:
            return -1

        history = self.balance_history[account_id]
        # Binary search: find latest entry with timestamp <= time_at
        idx = bisect_right(history, (time_at, float('inf'))) - 1
        return history[idx][1] if idx >= 0 else -1
```

**Complexity:**

| Method | Time | Space |
|---|---|---|
| create_account, deposit, transfer | O(log P) amortized (scheduled drain) | O(1) |
| top_spenders | O(A log A) | O(A) |
| schedule_payment | O(log P) | O(1) |
| cancel_payment | O(P) | O(1) |
| merge_accounts | O(P) | O(1) |
| get_balance | O(log H) | O(1) |

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
