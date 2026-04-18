# Task Management System

**Category:** Coding
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** HashMap, TTL/Lazy Expiration, Priority sorting, State machine (active/completed/expired), Quota enforcement

---

## Problem Statement

Build a task management system that supports creating and querying tasks, assigning them to users with per-user quotas and TTLs, and tracking task completion vs. expiration. Build incrementally across four levels.

## Requirements

### Level 1: Core Task CRUD

```python
class TaskManager:
    def create_task(self, task_id: str, name: str, priority: int) -> bool
    # Returns False if task_id already exists

    def get_task(self, task_id: str) -> str
    # Returns "task_id: name (priority P)" or "" if not found

    def update_task(self, task_id: str, name: str, priority: int) -> bool
    # Returns False if task_id not found
```

### Level 2: Listing and Filtering

```python
def list_tasks(self, n: int, substr: str = "") -> list[str]
# Top N tasks by priority DESC, then task_id ASC on ties
# Filter to tasks whose name contains substr (case-sensitive)
# Format: "task_id: name (priority P)"
```

### Level 3: Users, Quotas, and TTL Assignments

```python
def add_user(self, user_id: str, quota: int) -> bool
# Returns False if user already exists

def assign_task(self, timestamp: int, user_id: str, task_id: str, ttl: int) -> bool
# Assign task to user; expires at timestamp + ttl (exclusive: active while expiry > timestamp)
# Fails if: user/task missing, quota reached, or task already actively assigned to user

def list_user_tasks(self, timestamp: int, user_id: str) -> list[str]
# Active (non-expired, non-completed) assignments, sorted by priority DESC then task_id ASC
```

### Level 4: Completion and Expiry Tracking

```python
def complete_task(self, timestamp: int, user_id: str, task_id: str) -> bool
# Marks the earliest active assignment of task_id for user as completed
# Returns False if no active assignment exists

def list_expired_tasks(self, timestamp: int, user_id: str) -> list[str]
# Tasks whose assignment expired (expiry_time <= timestamp) without completion
# Sorted by priority DESC then task_id ASC
```

---

## Solution Approach

### Level 1

**Core Idea:** Dict from `task_id` to task metadata. All operations are O(1).

```python
class TaskManager:
    def __init__(self):
        self.tasks = {}        # task_id -> {"name": str, "priority": int}
        self.users = {}        # user_id -> {"quota": int}
        self.assignments = {}  # user_id -> [assignment_dict]

    def create_task(self, task_id: str, name: str, priority: int) -> bool:
        if task_id in self.tasks:
            return False
        self.tasks[task_id] = {"name": name, "priority": priority}
        return True

    def get_task(self, task_id: str) -> str:
        if task_id not in self.tasks:
            return ""
        t = self.tasks[task_id]
        return f"{task_id}: {t['name']} (priority {t['priority']})"

    def update_task(self, task_id: str, name: str, priority: int) -> bool:
        if task_id not in self.tasks:
            return False
        self.tasks[task_id] = {"name": name, "priority": priority}
        return True
```

**Complexity:** O(1) per operation

### Level 2

**Core Idea:** Linear filter + sort. A heap would help for pure top-K, but substring filtering requires scanning all tasks anyway, so sort dominates.

```python
def list_tasks(self, n: int, substr: str = "") -> list[str]:
    matching = [
        (tid, t) for tid, t in self.tasks.items()
        if not substr or substr in t["name"]
    ]
    matching.sort(key=lambda x: (-x[1]["priority"], x[0]))
    return [
        f"{tid}: {t['name']} (priority {t['priority']})"
        for tid, t in matching[:n]
    ]
```

**Complexity:** O(T log T) where T = total tasks

### Level 3

**Core Idea:** Track per-user assignments as a list of records. Quota and duplicate checks scan only the active subset (lazy expiration).

```python
def _is_active(self, a: dict, ts: int) -> bool:
    return not a["completed"] and a["expiry_time"] > ts

def add_user(self, user_id: str, quota: int) -> bool:
    if user_id in self.users:
        return False
    self.users[user_id] = {"quota": quota}
    self.assignments[user_id] = []
    return True

def assign_task(self, timestamp: int, user_id: str, task_id: str, ttl: int) -> bool:
    if user_id not in self.users or task_id not in self.tasks:
        return False
    active_count = 0
    for a in self.assignments[user_id]:
        if self._is_active(a, timestamp):
            if a["task_id"] == task_id:
                return False  # already active
            active_count += 1
    if active_count >= self.users[user_id]["quota"]:
        return False
    self.assignments[user_id].append({
        "task_id": task_id,
        "start_time": timestamp,
        "expiry_time": timestamp + ttl,
        "completed": False,
    })
    return True

def list_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
    if user_id not in self.users:
        return []
    seen, result = set(), []
    for a in self.assignments[user_id]:
        tid = a["task_id"]
        if self._is_active(a, timestamp) and tid not in seen and tid in self.tasks:
            seen.add(tid)
            result.append(tid)
    result.sort(key=lambda tid: (-self.tasks[tid]["priority"], tid))
    return [f"{tid}: {self.tasks[tid]['name']} (priority {self.tasks[tid]['priority']})"
            for tid in result]
```

**Complexity:** assign_task O(A), list_user_tasks O(A log A) where A = assignments for that user

### Level 4

**Core Idea:** Add a `completed` flag and separate helper to classify each assignment's state. `complete_task` targets the earliest active assignment (handles re-assignment after expiry).

```python
def _is_expired(self, a: dict, ts: int) -> bool:
    return not a["completed"] and a["expiry_time"] <= ts

def complete_task(self, timestamp: int, user_id: str, task_id: str) -> bool:
    if user_id not in self.users or task_id not in self.tasks:
        return False
    best = None
    for a in self.assignments[user_id]:
        if a["task_id"] == task_id and self._is_active(a, timestamp):
            if best is None or a["start_time"] < best["start_time"]:
                best = a
    if best is None:
        return False
    best["completed"] = True
    return True

def list_expired_tasks(self, timestamp: int, user_id: str) -> list[str]:
    if user_id not in self.users:
        return []
    seen, result = set(), []
    for a in self.assignments[user_id]:
        tid = a["task_id"]
        if self._is_expired(a, timestamp) and tid not in seen and tid in self.tasks:
            seen.add(tid)
            result.append(tid)
    result.sort(key=lambda tid: (-self.tasks[tid]["priority"], tid))
    return [f"{tid}: {self.tasks[tid]['name']} (priority {self.tasks[tid]['priority']})"
            for tid in result]
```

**Complexity:** complete_task O(A), list_expired_tasks O(A log A)

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Assignment list growth:** The list never shrinks — completed and expired records accumulate forever. At scale, a user with thousands of past assignments will cause O(A) scans on every `assign_task` call. Production fix: periodically archive old terminal records to a separate store (or a `history` list) so the active list stays bounded.
- **Quota race condition:** `assign_task` reads `active_count`, then writes. Two concurrent requests for the same user both pass the quota check before either commits. Requires per-user locking (mutex) or an atomic counter with compare-and-swap. Same pattern as Coinbase's order submission rate limits.
- **TTL precision and wall-clock drift:** The problem uses logical timestamps, but in a distributed deployment, monotonic logical timestamps diverge from wall time. If TTLs represent real-time durations (e.g., "this task expires in 30 seconds"), you need wall-clock TTLs with NTP-synchronized time sources — and accept ±1s of uncertainty.
- **`update_task` invalidates list_user_tasks:** If a task's priority changes after being assigned, `list_user_tasks` sees the new priority immediately. This is correct but worth stating — there's no "snapshot at assignment time" semantics. If that's needed, store priority at assignment time.
- **State machine correctness:** The three states (active, completed, expired) are mutually exclusive. The `completed` flag gates both `_is_active` and `_is_expired`, so setting `completed=True` on an already-expired assignment is harmless — `_is_expired` returns `False` for completed records regardless. Verify this invariant holds during `complete_task`.

### Common Interview Traps

- **Expiry boundary:** Active means `expiry_time > timestamp` (strict), expired means `expiry_time <= timestamp`. Confirm inclusive/exclusive with the interviewer — using `>=` vs `>` is the most common off-by-one.
- **`list_expired_tasks` vs `list_user_tasks`:** These are almost identical loops with different classification predicates. Factor out a `_classify_assignments` helper to avoid duplicating the seen-set deduplication logic.
- **`complete_task` and multiple assignments:** If a user is assigned the same task twice (first assignment expired, then re-assigned), both records exist in the list. `complete_task` must target the *active* one, not the expired one. Filtering by `_is_active` before selecting by `start_time` handles this correctly.
- **`add_user` deduplication:** `add_user` for an existing user should return `False`. Don't accidentally reset their quota or wipe their assignments.
- **Substring match is case-sensitive:** `substr in task["name"]` uses Python's case-sensitive `in`. Confirm with the interviewer whether it should be case-insensitive.

### How to Push Forward as Staff+

- **Name the growth problem proactively:** "The assignment list grows unbounded. I'd split it into `active_assignments` (bounded by quota) and `history` (append-only archive). Quota checks become O(quota) instead of O(all-time assignments)."
- **Propose a heap for priority queue operations:** "If `list_tasks` is called frequently and tasks rarely change, I'd maintain a sorted structure (e.g., a `SortedList` from `sortedcontainers`) to avoid O(T log T) on each call. The tradeoff is O(log T) writes vs. O(T log T) reads."
- **Connect to Coinbase domain:** This system maps cleanly to Coinbase's trading infrastructure: tasks are open orders, users are traders, quota is position limits, TTL is order expiry (GTC vs. day orders), and `complete_task` is order fill. `list_expired_tasks` is the audit trail of unfilled orders — a regulatory requirement.
- **Distributed sharding:** "In production, I'd shard by `user_id` — all assignments for a user live on one shard to avoid cross-shard quota checks. The `tasks` dict is read-heavy and can be replicated to all shards or cached."
- **Observability:** "I'd track quota utilization per user as a histogram metric. A user consistently at 100% quota signals either too-low quota or tasks not completing — both worth alerting on."
