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

```java
class TaskManager {
    boolean createTask(String taskId, String name, int priority)
    // Returns false if taskId already exists

    String getTask(String taskId)
    // Returns "taskId: name (priority P)" or "" if not found

    boolean updateTask(String taskId, String name, int priority)
    // Returns false if taskId not found
}
```

### Level 2: Listing and Filtering

```java
List<String> listTasks(int n, String substr)
// Top N tasks by priority DESC, then taskId ASC on ties
// Filter to tasks whose name contains substr (case-sensitive)
// Format: "taskId: name (priority P)"
```

### Level 3: Users, Quotas, and TTL Assignments

```java
boolean addUser(String userId, int quota)
// Returns false if user already exists

boolean assignTask(int timestamp, String userId, String taskId, int ttl)
// Assign task to user; expires at timestamp + ttl (exclusive: active while expiry > timestamp)
// Fails if: user/task missing, quota reached, or task already actively assigned to user

List<String> listUserTasks(int timestamp, String userId)
// Active (non-expired, non-completed) assignments, sorted by priority DESC then taskId ASC
```

### Level 4: Completion and Expiry Tracking

```java
boolean completeTask(int timestamp, String userId, String taskId)
// Marks the earliest active assignment of taskId for user as completed
// Returns false if no active assignment exists

List<String> listExpiredTasks(int timestamp, String userId)
// Tasks whose assignment expired (expiryTime <= timestamp) without completion
// Sorted by priority DESC then taskId ASC
```

---

## Solution Approach

### Level 1

**Core Idea:** Map from `taskId` to task metadata. All operations are O(1).

```java
class TaskManager {
    private record Task(String name, int priority) {}

    private record Assignment(String taskId, int startTime, int expiryTime, boolean completed) {
        Assignment withCompleted() { return new Assignment(taskId, startTime, expiryTime, true); }
    }

    private final Map<String, Task> tasks = new HashMap<>();
    private final Map<String, Integer> users = new HashMap<>();          // userId -> quota
    private final Map<String, List<Assignment>> assignments = new HashMap<>();

    public boolean createTask(String taskId, String name, int priority) {
        if (tasks.containsKey(taskId)) return false;
        tasks.put(taskId, new Task(name, priority));
        return true;
    }

    public String getTask(String taskId) {
        Task t = tasks.get(taskId);
        if (t == null) return "";
        return taskId + ": " + t.name() + " (priority " + t.priority() + ")";
    }

    public boolean updateTask(String taskId, String name, int priority) {
        if (!tasks.containsKey(taskId)) return false;
        tasks.put(taskId, new Task(name, priority));
        return true;
    }
}
```

**Complexity:** O(1) per operation

### Level 2

**Core Idea:** Linear filter + sort. A heap would help for pure top-K, but substring filtering requires scanning all tasks anyway, so sort dominates.

```java
public List<String> listTasks(int n, String substr) {
    return tasks.entrySet().stream()
        .filter(e -> substr.isEmpty() || e.getValue().name().contains(substr))
        .sorted((a, b) -> {
            int cmp = Integer.compare(b.getValue().priority(), a.getValue().priority());
            return cmp != 0 ? cmp : a.getKey().compareTo(b.getKey());
        })
        .limit(n)
        .map(e -> e.getKey() + ": " + e.getValue().name() + " (priority " + e.getValue().priority() + ")")
        .collect(Collectors.toList());
}
```

**Complexity:** O(T log T) where T = total tasks

### Level 3

**Core Idea:** Track per-user assignments as a list of records. Quota and duplicate checks scan only the active subset (lazy expiration).

```java
private boolean isActive(Assignment a, int ts) {
    return !a.completed() && a.expiryTime() > ts;
}

public boolean addUser(String userId, int quota) {
    if (users.containsKey(userId)) return false;
    users.put(userId, quota);
    assignments.put(userId, new ArrayList<>());
    return true;
}

public boolean assignTask(int timestamp, String userId, String taskId, int ttl) {
    if (!users.containsKey(userId) || !tasks.containsKey(taskId)) return false;
    int activeCount = 0;
    for (Assignment a : assignments.get(userId)) {
        if (isActive(a, timestamp)) {
            if (a.taskId().equals(taskId)) return false;  // already active
            activeCount++;
        }
    }
    if (activeCount >= users.get(userId)) return false;
    assignments.get(userId).add(new Assignment(taskId, timestamp, timestamp + ttl, false));
    return true;
}

public List<String> listUserTasks(int timestamp, String userId) {
    if (!users.containsKey(userId)) return Collections.emptyList();
    Set<String> seen = new HashSet<>();
    List<String> result = new ArrayList<>();
    for (Assignment a : assignments.get(userId)) {
        if (isActive(a, timestamp) && seen.add(a.taskId()) && tasks.containsKey(a.taskId())) {
            result.add(a.taskId());
        }
    }
    result.sort((a, b) -> {
        int cmp = Integer.compare(tasks.get(b).priority(), tasks.get(a).priority());
        return cmp != 0 ? cmp : a.compareTo(b);
    });
    return result.stream()
        .map(tid -> tid + ": " + tasks.get(tid).name() + " (priority " + tasks.get(tid).priority() + ")")
        .collect(Collectors.toList());
}
```

**Complexity:** assignTask O(A), listUserTasks O(A log A) where A = assignments for that user

### Level 4

**Core Idea:** Add a `completed` flag and separate helper to classify each assignment's state. `completeTask` targets the earliest active assignment (handles re-assignment after expiry).

```java
private boolean isExpired(Assignment a, int ts) {
    return !a.completed() && a.expiryTime() <= ts;
}

public boolean completeTask(int timestamp, String userId, String taskId) {
    if (!users.containsKey(userId) || !tasks.containsKey(taskId)) return false;
    List<Assignment> userAssignments = assignments.get(userId);
    Assignment best = null;
    int bestIdx = -1;
    for (int i = 0; i < userAssignments.size(); i++) {
        Assignment a = userAssignments.get(i);
        if (a.taskId().equals(taskId) && isActive(a, timestamp)) {
            if (best == null || a.startTime() < best.startTime()) {
                best = a;
                bestIdx = i;
            }
        }
    }
    if (bestIdx == -1) return false;
    userAssignments.set(bestIdx, best.withCompleted());
    return true;
}

public List<String> listExpiredTasks(int timestamp, String userId) {
    if (!users.containsKey(userId)) return Collections.emptyList();
    Set<String> seen = new HashSet<>();
    List<String> result = new ArrayList<>();
    for (Assignment a : assignments.get(userId)) {
        if (isExpired(a, timestamp) && seen.add(a.taskId()) && tasks.containsKey(a.taskId())) {
            result.add(a.taskId());
        }
    }
    result.sort((a, b) -> {
        int cmp = Integer.compare(tasks.get(b).priority(), tasks.get(a).priority());
        return cmp != 0 ? cmp : a.compareTo(b);
    });
    return result.stream()
        .map(tid -> tid + ": " + tasks.get(tid).name() + " (priority " + tasks.get(tid).priority() + ")")
        .collect(Collectors.toList());
}
```

**Complexity:** completeTask O(A), listExpiredTasks O(A log A)

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Assignment list growth:** The list never shrinks — completed and expired records accumulate forever. At scale, a user with thousands of past assignments will cause O(A) scans on every `assignTask` call. Production fix: periodically archive old terminal records to a separate store (or a `history` list) so the active list stays bounded.
- **Quota race condition:** `assignTask` reads `activeCount`, then writes. Two concurrent requests for the same user both pass the quota check before either commits. Requires per-user locking (mutex) or an atomic counter with compare-and-swap. Same pattern as Coinbase's order submission rate limits.
- **TTL precision and wall-clock drift:** The problem uses logical timestamps, but in a distributed deployment, monotonic logical timestamps diverge from wall time. If TTLs represent real-time durations (e.g., "this task expires in 30 seconds"), you need wall-clock TTLs with NTP-synchronized time sources — and accept ±1s of uncertainty.
- **`updateTask` invalidates listUserTasks:** If a task's priority changes after being assigned, `listUserTasks` sees the new priority immediately. This is correct but worth stating — there's no "snapshot at assignment time" semantics. If that's needed, store priority at assignment time.
- **State machine correctness:** The three states (active, completed, expired) are mutually exclusive. The `completed` flag gates both `isActive` and `isExpired`, so marking an already-expired assignment as completed is harmless — `isExpired` returns `false` for completed records regardless. Verify this invariant holds during `completeTask`.

### Common Interview Traps

- **Expiry boundary:** Active means `expiryTime > timestamp` (strict), expired means `expiryTime <= timestamp`. Confirm inclusive/exclusive with the interviewer — using `>=` vs `>` is the most common off-by-one.
- **`listExpiredTasks` vs `listUserTasks`:** These are almost identical loops with different classification predicates. Factor out a `classifyAssignments` helper to avoid duplicating the seen-set deduplication logic.
- **`completeTask` and multiple assignments:** If a user is assigned the same task twice (first assignment expired, then re-assigned), both records exist in the list. `completeTask` must target the *active* one, not the expired one. Filtering by `isActive` before selecting by `startTime` handles this correctly.
- **`addUser` deduplication:** `addUser` for an existing user should return `false`. Don't accidentally reset their quota or wipe their assignments.
- **Substring match is case-sensitive:** `name.contains(substr)` uses Java's case-sensitive `contains`. Confirm with the interviewer whether it should be case-insensitive.

### How to Push Forward as Staff+

- **Name the growth problem proactively:** "The assignment list grows unbounded. I'd split it into `activeAssignments` (bounded by quota) and `history` (append-only archive). Quota checks become O(quota) instead of O(all-time assignments)."
- **Propose a heap for priority queue operations:** "If `listTasks` is called frequently and tasks rarely change, I'd maintain a sorted structure (e.g., a `TreeSet` with a custom comparator) to avoid O(T log T) on each call. The tradeoff is O(log T) writes vs. O(T log T) reads."
- **Connect to Coinbase domain:** This system maps cleanly to Coinbase's trading infrastructure: tasks are open orders, users are traders, quota is position limits, TTL is order expiry (GTC vs. day orders), and `completeTask` is order fill. `listExpiredTasks` is the audit trail of unfilled orders — a regulatory requirement.
- **Distributed sharding:** "In production, I'd shard by `userId` — all assignments for a user live on one shard to avoid cross-shard quota checks. The `tasks` map is read-heavy and can be replicated to all shards or cached."
- **Observability:** "I'd track quota utilization per user as a histogram metric. A user consistently at 100% quota signals either too-low quota or tasks not completing — both worth alerting on."
