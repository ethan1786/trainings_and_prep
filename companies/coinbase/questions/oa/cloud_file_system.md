# Cloud File System

**Category:** Coding
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** HashMap, Multi-user ownership, Backup/Restore, Capacity constraints, Alphabetical ordering

---

## Problem Statement

Design an in-memory cloud file system. Files have a name and a size. The system supports multiple users with storage quotas, file ownership, backups, and restores. Build it incrementally across four parts.

## Requirements

### Part 1: Basic File Management

```java
class CloudFileSystem {
    boolean addFile(String name, int size)
    // Returns false if name already exists

    int getFileSize(String name)
    // Returns -1 if file does not exist

    boolean deleteFile(String name)
    // Returns false if file does not exist

    boolean copyFile(String source, String dest)
    // Returns false if source missing or dest already exists
}
```

### Part 2: Prefix Search

```java
List<String> findFiles(String prefix, int n)
// Returns up to N files whose names start with prefix
// Format: "name(size)", sorted by size DESC, then name ASC on ties
```

### Part 3: Users and Quotas

```java
boolean addUser(String userId, int capacity)
// "admin" is reserved; files from addFile() belong to admin (unlimited)

boolean addFileBy(String userId, String name, int size)
// Fails if user missing, name taken, or would exceed capacity

boolean mergeUser(String userId1, String userId2)
// userId2's files and capacity transfer to userId1; userId2 is deleted
// admin cannot be merged (as source or target)
```

### Part 4: Backup and Restore

```java
int backup(String userId)
// Snapshot user's files; returns count or -1 if user missing
// Overwrites any prior backup for this user

int restore(String userId)
// Restore from backup; returns files restored or -1 if user missing
// If no backup exists: delete all user's files, return 0
// Skip files already owned by this user (keep current version)
// Skip files whose name is taken by another user
// Restore alphabetically; skip if capacity would be exceeded
// Clears backup after restore
```

---

## Solution Approach

### Part 1

**Core Idea:** Flat map from filename to `(owner, size)`. All four operations are O(1) lookups.

**Data Structures:** `HashMap<String, long[]>` — `files[name] = [ownerId, size]` (or a small record class)

```java
class CloudFileSystem {
    // file entry: String owner, int size
    private record FileEntry(String owner, int size) {}
    private record UserEntry(long capacity, long used) {}

    private final Map<String, FileEntry> files = new HashMap<>();
    private final Map<String, long[]> users = new HashMap<>();
    // users[id] = [capacity, used]; Long.MAX_VALUE signals unlimited
    private final Map<String, Map<String, Integer>> backups = new HashMap<>();

    public CloudFileSystem() {
        users.put("admin", new long[]{Long.MAX_VALUE, 0});
    }

    public boolean addFile(String name, int size) {
        if (files.containsKey(name)) return false;
        files.put(name, new FileEntry("admin", size));
        return true;
    }

    public int getFileSize(String name) {
        FileEntry e = files.get(name);
        return e == null ? -1 : e.size();
    }

    public boolean deleteFile(String name) {
        FileEntry e = files.remove(name);
        if (e == null) return false;
        long[] u = users.get(e.owner());
        if (u != null) u[1] -= e.size();
        return true;
    }

    public boolean copyFile(String source, String dest) {
        if (!files.containsKey(source) || files.containsKey(dest)) return false;
        FileEntry e = files.get(source);
        files.put(dest, e);
        long[] u = users.get(e.owner());
        if (u != null) u[1] += e.size();
        return true;
    }
}
```

**Complexity:** O(1) time per operation, O(N) space total

### Part 2

**Core Idea:** Linear scan with sorted output. No Trie needed at this scale.

```java
public List<String> findFiles(String prefix, int n) {
    List<Map.Entry<String, FileEntry>> matches = new ArrayList<>();
    for (Map.Entry<String, FileEntry> e : files.entrySet()) {
        if (e.getKey().startsWith(prefix)) matches.add(e);
    }
    matches.sort((a, b) -> {
        int cmp = Integer.compare(b.getValue().size(), a.getValue().size());
        return cmp != 0 ? cmp : a.getKey().compareTo(b.getKey());
    });
    return matches.stream()
        .limit(n)
        .map(e -> e.getKey() + "(" + e.getValue().size() + ")")
        .collect(Collectors.toList());
}
```

**Complexity:** O(F log F) time where F = number of files, O(F) space

### Part 3

**Core Idea:** Track per-user `used` vs `capacity`. Merge just adds capacities and reassigns file ownership.

```java
public boolean addUser(String userId, int capacity) {
    if (userId.equals("admin") || users.containsKey(userId)) return false;
    users.put(userId, new long[]{capacity, 0});
    return true;
}

public boolean addFileBy(String userId, String name, int size) {
    if (!users.containsKey(userId) || files.containsKey(name)) return false;
    long[] u = users.get(userId);
    if (u[1] + size > u[0]) return false;
    files.put(name, new FileEntry(userId, size));
    u[1] += size;
    return true;
}

public boolean mergeUser(String userId1, String userId2) {
    if (!users.containsKey(userId1) || !users.containsKey(userId2)
            || userId1.equals(userId2)
            || userId1.equals("admin") || userId2.equals("admin")) return false;
    long[] u1 = users.get(userId1), u2 = users.get(userId2);
    u1[0] += u2[0];
    u1[1] += u2[1];
    for (Map.Entry<String, FileEntry> e : files.entrySet()) {
        if (e.getValue().owner().equals(userId2)) {
            e.setValue(new FileEntry(userId1, e.getValue().size()));
        }
    }
    users.remove(userId2);
    return true;
}
```

**Complexity:** mergeUser is O(F) to retag files; others O(1)

### Part 4

**Core Idea:** Snapshot map of `{name: size}` per user. Restore is a three-way reconciliation: keep existing, delete extras, add missing — subject to capacity and alphabetical ordering.

```java
public int backup(String userId) {
    if (!users.containsKey(userId)) return -1;
    Map<String, Integer> snapshot = new HashMap<>();
    for (Map.Entry<String, FileEntry> e : files.entrySet()) {
        if (e.getValue().owner().equals(userId)) {
            snapshot.put(e.getKey(), e.getValue().size());
        }
    }
    backups.put(userId, snapshot);
    return snapshot.size();
}

public int restore(String userId) {
    if (!users.containsKey(userId)) return -1;

    Map<String, Integer> snapshot = backups.remove(userId);  // clears backup

    // Collect files currently owned by this user
    List<String> currentFiles = new ArrayList<>();
    for (Map.Entry<String, FileEntry> e : files.entrySet()) {
        if (e.getValue().owner().equals(userId)) currentFiles.add(e.getKey());
    }

    // Delete files not in snapshot
    for (String name : currentFiles) {
        if (snapshot == null || !snapshot.containsKey(name)) deleteFile(name);
    }

    if (snapshot == null || snapshot.isEmpty()) return 0;

    long[] u = users.get(userId);
    int restored = 0;
    List<String> sortedNames = new ArrayList<>(snapshot.keySet());
    Collections.sort(sortedNames);

    for (String name : sortedNames) {
        int backedSize = snapshot.get(name);
        if (files.containsKey(name)) {
            // Either owned by this user (keep) or taken by another (skip)
            continue;
        }
        // File doesn't exist; try to restore it
        if (u[0] != Long.MAX_VALUE && u[1] + backedSize > u[0]) continue;
        files.put(name, new FileEntry(userId, backedSize));
        u[1] += backedSize;
        restored++;
    }

    return restored;
}
```

**Complexity:** O(F log F) for restore (alphabetical iteration), O(S) space for snapshot where S = user's file count

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Concurrency:** `addFileBy` and capacity checks are a classic TOCTOU race — two concurrent requests can both pass the quota check and then both write. Needs per-user locking or optimistic CAS on `used`.
- **Merge atomicity:** `mergeUser` must retag all files atomically. In a real system, this is a transaction across two user records and potentially millions of file metadata rows. Consider a two-phase approach or a background migration job with a "merging" state flag.
- **Backup storage:** Snapshots live in memory here. At Coinbase scale (wallets, transaction histories, compliance data), backups would land in object storage (S3 / GCS) with versioning, not RAM.
- **Restore ordering:** Alphabetical restore under capacity constraints is deterministic but may not be optimal — it could leave capacity unused by restoring many small files before failing on one large one. A knapsack-style approach would maximize files restored but is far more complex.
- **Capacity enforcement drift:** If files are deleted externally (admin force-delete) while a backup is in flight, `used` accounting can go negative. Always guard `used -= size` with `max(0, ...)` and add an audit reconciliation job.

### Common Interview Traps

- `copyFile` silently copies admin-owned files — should the copy also be owned by admin? Confirm the ownership semantics of copies before coding.
- `mergeUser` doesn't recheck capacity for userId1 after absorbing userId2's files. This is correct (combined capacity >= combined used) but interviewers may probe it; have the math ready.
- `restore` has four distinct cases for each file in the snapshot — get them all: (1) exists, owned by this user → keep, (2) exists, owned by other → skip, (3) doesn't exist, fits → restore, (4) doesn't exist, doesn't fit → skip. Missing any one fails edge case tests.
- Off-by-one on capacity: `used + size > capacity` (strict) vs `>=`. Clarify whether capacity is inclusive.

### How to Push Forward as Staff+

- **Proactively name the TOCTOU:** "In production, the quota check + write needs to be atomic. I'd use a Redis INCR with a cap, or a DB row-level lock on the user record."
- **Question the restore semantics:** "Alphabetical restore under a capacity constraint is non-obvious — is the goal fairness, predictability, or maximizing recovery? I'd confirm with product before shipping."
- **Connect to Coinbase domain:** User storage quotas mirror account-level rate limits on the API — the same capacity enforcement pattern protects order submission rates, wallet creation limits, and compliance data retention budgets.
- **Audit trail:** "Any delete or restore operation on user files in a financial system should emit an immutable audit log. I'd add an append-only event stream alongside the state mutations."
- **Soft deletes:** "Before hard-deleting files on restore, I'd move them to a trash/recycle bin with a TTL. Accidental restores in production are hard to undo."
