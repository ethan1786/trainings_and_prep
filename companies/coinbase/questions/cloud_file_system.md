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

```python
class CloudFileSystem:
    def add_file(self, name: str, size: int) -> bool
    # Returns False if name already exists

    def get_file_size(self, name: str) -> int
    # Returns -1 if file does not exist

    def delete_file(self, name: str) -> bool
    # Returns False if file does not exist

    def copy_file(self, source: str, dest: str) -> bool
    # Returns False if source missing or dest already exists
```

### Part 2: Prefix Search

```python
def find_files(self, prefix: str, n: int) -> list[str]
# Returns up to N files whose names start with prefix
# Format: "name(size)", sorted by size DESC, then name ASC on ties
```

### Part 3: Users and Quotas

```python
def add_user(self, user_id: str, capacity: int) -> bool
# "admin" is reserved; files from add_file() belong to admin (unlimited)

def add_file_by(self, user_id: str, name: str, size: int) -> bool
# Fails if user missing, name taken, or would exceed capacity

def merge_user(self, user_id1: str, user_id2: str) -> bool
# user_id2's files and capacity transfer to user_id1; user_id2 is deleted
# admin cannot be merged (as source or target)
```

### Part 4: Backup and Restore

```python
def backup(self, user_id: str) -> int
# Snapshot user's files; returns count or -1 if user missing
# Overwrites any prior backup for this user

def restore(self, user_id: str) -> int
# Restore from backup; returns files restored or -1 if user missing
# If no backup exists: delete all user's files, return 0
# Skip files already owned by this user (keep current version)
# Skip files whose name is taken by another user
# Restore alphabetically; skip if capacity would be exceeded
# Clears backup after restore
```

---

## Solution Approach

### Part 1

**Core Idea:** Flat dict from filename to `(owner, size)`. All four operations are O(1) lookups.

**Data Structures:** `dict[str, tuple[str, int]]` — `files[name] = (owner, size)`

```python
class CloudFileSystem:
    def __init__(self):
        self.files = {}   # name -> (owner, size)
        self.users = {"admin": {"capacity": float("inf"), "used": 0}}
        self.backups = {}  # user_id -> {name: size}

    def add_file(self, name: str, size: int) -> bool:
        if name in self.files:
            return False
        self.files[name] = ("admin", size)
        return True

    def get_file_size(self, name: str) -> int:
        if name not in self.files:
            return -1
        return self.files[name][1]

    def delete_file(self, name: str) -> bool:
        if name not in self.files:
            return False
        owner, size = self.files.pop(name)
        if owner in self.users:
            self.users[owner]["used"] -= size
        return True

    def copy_file(self, source: str, dest: str) -> bool:
        if source not in self.files or dest in self.files:
            return False
        owner, size = self.files[source]
        self.files[dest] = (owner, size)
        if owner in self.users:
            self.users[owner]["used"] += size
        return True
```

**Complexity:** O(1) time per operation, O(N) space total

### Part 2

**Core Idea:** Linear scan with sorted output. No Trie needed at this scale.

```python
def find_files(self, prefix: str, n: int) -> list[str]:
    matches = [
        (name, size) for name, (_, size) in self.files.items()
        if name.startswith(prefix)
    ]
    matches.sort(key=lambda x: (-x[1], x[0]))
    return [f"{name}({size})" for name, size in matches[:n]]
```

**Complexity:** O(F log F) time where F = number of files, O(F) space

### Part 3

**Core Idea:** Track per-user `used` vs `capacity`. Merge just adds capacities and reassigns file ownership.

```python
def add_user(self, user_id: str, capacity: int) -> bool:
    if user_id == "admin" or user_id in self.users:
        return False
    self.users[user_id] = {"capacity": capacity, "used": 0}
    return True

def add_file_by(self, user_id: str, name: str, size: int) -> bool:
    if user_id not in self.users or name in self.files:
        return False
    u = self.users[user_id]
    if u["used"] + size > u["capacity"]:
        return False
    self.files[name] = (user_id, size)
    u["used"] += size
    return True

def merge_user(self, user_id1: str, user_id2: str) -> bool:
    if (user_id1 not in self.users or user_id2 not in self.users
            or user_id1 == user_id2
            or user_id1 == "admin" or user_id2 == "admin"):
        return False
    u1, u2 = self.users[user_id1], self.users[user_id2]
    u1["capacity"] += u2["capacity"]
    u1["used"] += u2["used"]
    for name, (owner, size) in self.files.items():
        if owner == user_id2:
            self.files[name] = (user_id1, size)
    del self.users[user_id2]
    return True
```

**Complexity:** merge_user is O(F) to retag files; others O(1)

### Part 4

**Core Idea:** Snapshot dict of `{name: size}` per user. Restore is a three-way reconciliation: keep existing, delete extras, add missing — subject to capacity and alphabetical ordering.

```python
def backup(self, user_id: str) -> int:
    if user_id not in self.users:
        return -1
    snapshot = {
        name: size for name, (owner, size) in self.files.items()
        if owner == user_id
    }
    self.backups[user_id] = snapshot
    return len(snapshot)

def restore(self, user_id: str) -> int:
    if user_id not in self.users:
        return -1

    snapshot = self.backups.pop(user_id, None)  # clears backup
    target_files = {
        name: size for name, (owner, size) in self.files.items()
        if owner == user_id
    }

    # Delete files not in snapshot
    for name in list(target_files):
        if snapshot is None or name not in snapshot:
            self.delete_file(name)

    if not snapshot:
        return 0

    u = self.users[user_id]
    restored = 0
    for name in sorted(snapshot):
        backed_size = snapshot[name]
        if name in self.files:
            # File still exists — only keep if owned by this user
            if self.files[name][0] == user_id:
                continue  # keep current version, don't count
            else:
                continue  # taken by another user, skip
        # File doesn't exist; try to restore it
        capacity = u["capacity"]
        if capacity != float("inf") and u["used"] + backed_size > capacity:
            continue
        self.files[name] = (user_id, backed_size)
        u["used"] += backed_size
        restored += 1

    return restored
```

**Complexity:** O(F log F) for restore (alphabetical iteration), O(S) space for snapshot where S = user's file count

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Concurrency:** `add_file_by` and capacity checks are a classic TOCTOU race — two concurrent requests can both pass the quota check and then both write. Needs per-user locking or optimistic CAS on `used`.
- **Merge atomicity:** `merge_user` must retag all files atomically. In a real system, this is a transaction across two user records and potentially millions of file metadata rows. Consider a two-phase approach or a background migration job with a "merging" state flag.
- **Backup storage:** Snapshots live in memory here. At Coinbase scale (wallets, transaction histories, compliance data), backups would land in object storage (S3 / GCS) with versioning, not RAM.
- **Restore ordering:** Alphabetical restore under capacity constraints is deterministic but may not be optimal — it could leave capacity unused by restoring many small files before failing on one large one. A knapsack-style approach would maximize files restored but is far more complex.
- **Capacity enforcement drift:** If files are deleted externally (admin force-delete) while a backup is in flight, `used` accounting can go negative. Always guard `used -= size` with `max(0, ...)` and add an audit reconciliation job.

### Common Interview Traps

- `copy_file` silently copies admin-owned files — should the copy also be owned by admin? Confirm the ownership semantics of copies before coding.
- `merge_user` doesn't recheck capacity for user_id1 after absorbing user_id2's files. This is correct (combined capacity >= combined used) but interviewers may probe it; have the math ready.
- `restore` has four distinct cases for each file in the snapshot — get them all: (1) exists, owned by this user → keep, (2) exists, owned by other → skip, (3) doesn't exist, fits → restore, (4) doesn't exist, doesn't fit → skip. Missing any one fails edge case tests.
- Off-by-one on capacity: `used + size > capacity` (strict) vs `>=`. Clarify whether capacity is inclusive.

### How to Push Forward as Staff+

- **Proactively name the TOCTOU:** "In production, the quota check + write needs to be atomic. I'd use a Redis INCR with a cap, or a DB row-level lock on the user record."
- **Question the restore semantics:** "Alphabetical restore under a capacity constraint is non-obvious — is the goal fairness, predictability, or maximizing recovery? I'd confirm with product before shipping."
- **Connect to Coinbase domain:** User storage quotas mirror account-level rate limits on the API — the same capacity enforcement pattern protects order submission rates, wallet creation limits, and compliance data retention budgets.
- **Audit trail:** "Any delete or restore operation on user files in a financial system should emit an immutable audit log. I'd add an append-only event stream alongside the state mutations."
- **Soft deletes:** "Before hard-deleting files on restore, I'd move them to a trash/recycle bin with a TTL. Accidental restores in production are hard to undo."
