## Summary

Task system with users, quotas, TTL assignments, and completion tracking. 4 levels: task CRUD → list/filter with priority sort → users/quotas/TTL assignments → complete + list expired. Most relational-DB-like of all the questions — feels like day-to-day work but tricky under pressure.

## Design

**Data model:** Triple bookkeeping — assignments tracked on User, Task, AND a global PriorityQueue. Eager expiration via min-heap (vs. lazy expiration in the in_memory_database question).

**Maps / structures:**
- `tasks`: taskId → Task (name, priority, activeAssignments list)
- `users`: userId → User (quota, activeAssignments list)
- `activeAssignments`: PriorityQueue<Assignment> ordered by expiryTime (global, for eager expiration)
- `expiredAssignments`: Set<Assignment> (expired but not completed)

**Key pattern:** `expireTasks(timestamp)` called at the start of every Level 3/4 method — drains the heap of all expired assignments before any logic runs. Similar to bank_system's `checkAndExecutePayment`.

**Gotchas under pressure:**
- Triple bookkeeping: every assign/complete/expire must update ALL THREE structures (heap + user list + task list) — miss one and quota counts or duplicate checks break
- Expiry boundary: active while `expiryTime > timestamp` (strict), expired when `expiryTime <= timestamp` — off-by-one is the #1 trap
- `completeTask` targets the earliest active assignment — but since `assignTask` prevents duplicate active assignments of the same task to same user, there's at most one match
- `listExpiredTasks` needs dedup — a task can expire, be re-assigned, and expire again
- Don't modify a collection while iterating (same pattern as bank_system's `cancelAllByUser`)

---

```java
class TaskManager {
    private Map<String, Task> tasks = new HashMap<>();
    private Map<String, User> users = new HashMap<>();
    private PriorityQueue<Assignment> activeAssignments = new PriorityQueue<>((a,b) -> Integer.compare(a.ttl, b.ttl));
    private Set<Assignment> expiredAssignments = new HashSet<>();

    boolean createTask(String taskId, String name, int priority) {
        if (tasks.containsKey(taskId)) {
            return false;
        }
        tasks.put(taskId, new Task(taskId, name, priority));
        return true;
    }
    // Returns false if taskId already exists

    String getTask(String taskId) {
        if (!tasks.containsKey(taskId)) {
            return "";
        }
        Task task = tasks.get(taskId);
        return task.toString();
    }
    // Returns "taskId: name (priority P)" or "" if not found

    boolean updateTask(String taskId, String name, int priority) {
        if (!tasks.containsKey(taskId)) {
            return false;
        }
        Task task = tasks.get(taskId);
        task.name = name;
        task.priority = priority;
        return true;
    }
    // Returns false if taskId not found

    List<String> listTasks(int n, String substr) {
        return tasks.values().stream()
        .filter(t -> t.name.contains(substr))
        .sorted(Task::compareTo)
        .limit(n)
        .map(Task::toString)
        .toList();
    }
    // Top N tasks by priority DESC, then taskId ASC on ties
    // Filter to tasks whose name contains substr (case-sensitive)
    // Format: "taskId: name (priority P)"

    boolean addUser(String userId, int quota) {
        if (users.containsKey(userId)) {
            return false;
        }
        users.put(userId, new User(userId, quota));
        return true;
    }
    // Returns false if user already exists

    boolean assignTask(int timestamp, String userId, String taskId, int ttl) {
        expireTasks(timestamp);
        if (!users.containsKey(userId) || !tasks.containsKey(taskId)) {
            return false;
        }
        Task t = tasks.get(taskId);
        User u = users.get(userId);
        if (u.quota == u.activeAssignments.size()) {
            return false;
        }
        for (Assignment a: t.activeAssignments) {
            if (a.user.equals(u)) {
                return false;
            }
        }
        Assignment assignment = new Assignment(t, u, timestamp + ttl);
        activeAssignments.offer(assignment);
        u.activeAssignments.add(assignment);
        t.activeAssignments.add(assignment);
        return true;
    }
    // Assign task to user; expires at timestamp + ttl (exclusive: active while expiry > timestamp)
    // Fails if: user/task missing, quota reached, or task already actively assigned to user

    List<String> listUserTasks(int timestamp, String userId) {
        expireTasks(timestamp);
        if (!users.containsKey(userId)) {
            return List.of();
        }
        User u = users.get(userId);
        return u.activeAssignments.stream()
        .map(assignment -> assignment.task)
        .collect(Collectors.toSet()) // put into a set to dedup
        .stream()
        .sorted(Task::compareTo)
        .map(Task::toString)
        .toList();
    }
    // Active (non-expired, non-completed) assignments, sorted by priority DESC then taskId ASC

    boolean completeTask(int timestamp, String userId, String taskId) {
        expireTasks(timestamp);
        if (!users.containsKey(userId) || !tasks.containsKey(taskId)) {
            return false;
        }
        User u = users.get(userId);
        Task t = tasks.get(taskId);
        Optional<Assignment> firstActiveAssignment = u.activeAssignments.stream()
        .filter(assignment -> assignment.task.equals(t))
        .findFirst();
        if (firstActiveAssignment.isEmpty()) {
            return false;
        }
        activeAssignments.remove(firstActiveAssignment.get());
        u.activeAssignments.remove(firstActiveAssignment.get());
        t.activeAssignments.remove(firstActiveAssignment.get());
        return true;
    }
    // Marks the earliest active assignment of taskId for user as completed
    // Returns false if no active assignment exists

    List<String> listExpiredTasks(int timestamp, String userId) {
        expireTasks(timestamp);
        if (!users.containsKey(userId)) {
            return List.of();
        }

        return expiredAssignments.stream().filter(assignment -> assignment.user.id.equals(userId))
        .map(assignment -> assignment.task)
        .collect(Collectors.toSet()) // put into a set to dedup
        .stream()
        .sorted(Task::compareTo)
        .map(Task::toString)
        .toList();
    }
    // Tasks whose assignment expired (expiryTime <= timestamp) without completion
    // Sorted by priority DESC then taskId ASC


    void expireTasks(int timestamp) {
        while (!activeAssignments.isEmpty()) {
            Assignment curr = activeAssignments.peek();
            if (curr.ttl <= timestamp) {
                activeAssignments.poll();
                curr.user.activeAssignments.remove(curr);
                curr.task.activeAssignments.remove(curr);
                expiredAssignments.add(curr);
            } else {
                return;
            }
        }
    }

    private static class User {
        String id;
        int quota;
        List<Assignment> activeAssignments = new ArrayList<>();
        User(String userId, int q) {
            id = userId;
            quota = q;
        }
    }

    private static class Task {
        String id;
        String name;
        int priority;
        List<Assignment> activeAssignments = new ArrayList<>();
        Task (String taskId, String n, int p) {
            id = taskId;
            name = n;
            priority = p;
        }
        String toString() {
            return new StringBuilder().append(id).append(": ").append(name)
            .append(" (priority ").append(priority).append(")").toString();
        }
        int compareTo(Task b) {
            if (priority == b.priority) {
                return id.compareTo(b.id);
            }
            return b.priority - priority;
        }
    }
    private static class Assignment {
        Task task;
        User user;
        int ttl;
        Assignment(Task t, User u, int timestamp) {
            task = t;
            user = u;
            ttl = timestamp;
        }
    }
}