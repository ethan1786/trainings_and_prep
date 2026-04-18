# In-Memory Database

**Category:** Coding
**Difficulty:** Hard
**Time Estimate:** 45-60 min
**Key Topics:** HashMap, TTL/Lazy Expiration, Snapshot/Restore, Binary Search, Compare-and-Set (CAS)

---

## Problem Statement

Build an in-memory key-field-value store — think of it as a nested HashMap where each key holds a collection of field-value pairs. Every operation receives a monotonically increasing timestamp (no duplicates). Add TTL support, prefix scanning, and point-in-time backup/restore.

## Requirements

### Level 1: Basic Operations

```python
class InMemoryDB:
    def set(self, timestamp: int, key: str, field: str, value: str) -> None
    # Upsert; clears any existing TTL on the field

    def get(self, timestamp: int, key: str, field: str) -> str
    # Returns "" if missing or expired

    def delete(self, timestamp: int, key: str, field: str) -> bool
    # Returns False if missing or already expired

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected_value: str, new_value: str) -> bool
    # Updates only if current value == expected_value; False if missing/expired
```

### Level 2: Scan and Filter

```python
def scan(self, timestamp: int, key: str) -> list[str]
# Returns ["field(value)", ...] sorted alphabetically by field; omits expired

def scan_with_prefix(self, timestamp: int, key: str, prefix: str) -> list[str]
# Same as scan but only fields starting with prefix
```

### Level 3: TTL

```python
def set_with_ttl(self, timestamp: int, key: str, field: str,
                 value: str, ttl: int) -> None
# Field expires at timestamp + ttl (expiry inclusive: expired when current >= expiry)

def compare_and_set_with_ttl(self, timestamp: int, key: str, field: str,
                              expected_value: str, new_value: str, ttl: int) -> bool
# CAS + sets new TTL on success; fails if field missing or expired
```

### Level 4: Backup and Restore

```python
def backup(self, timestamp: int) -> None
# Snapshot current live (non-expired) state including TTL metadata

def restore(self, timestamp: int, backup_timestamp: int) -> None
# Restore from latest backup at or before backup_timestamp
# TTLs in the restored snapshot remain as originally set (not shifted)
```

---

## Solution Approach

### Level 1

**Core Idea:** Two parallel nested dicts — one for values, one for expiry times.

**Data Structures:**
- `data: dict[str, dict[str, str]]` — `data[key][field] = value`
- `expiry: dict[str, dict[str, int]]` — `expiry[key][field] = expiry_timestamp`

```python
class InMemoryDB:
    def __init__(self):
        self.data = {}
        self.expiry = {}

    def _is_expired(self, key: str, field: str, ts: int) -> bool:
        return (key in self.expiry
                and field in self.expiry[key]
                and ts >= self.expiry[key][field])

    def _remove(self, key: str, field: str):
        if key in self.data:
            self.data[key].pop(field, None)
            if not self.data[key]:
                del self.data[key]
        if key in self.expiry:
            self.expiry[key].pop(field, None)
            if not self.expiry[key]:
                del self.expiry[key]

    def set(self, timestamp: int, key: str, field: str, value: str) -> None:
        self.data.setdefault(key, {})[field] = value
        if key in self.expiry:
            self.expiry[key].pop(field, None)

    def get(self, timestamp: int, key: str, field: str) -> str:
        if key not in self.data or field not in self.data[key]:
            return ""
        if self._is_expired(key, field, timestamp):
            self._remove(key, field)
            return ""
        return self.data[key][field]

    def delete(self, timestamp: int, key: str, field: str) -> bool:
        if key not in self.data or field not in self.data[key]:
            return False
        if self._is_expired(key, field, timestamp):
            self._remove(key, field)
            return False
        self._remove(key, field)
        return True

    def compare_and_set(self, timestamp: int, key: str, field: str,
                        expected_value: str, new_value: str) -> bool:
        if key not in self.data or field not in self.data[key]:
            return False
        if self._is_expired(key, field, timestamp):
            self._remove(key, field)
            return False
        if self.data[key][field] != expected_value:
            return False
        self.data[key][field] = new_value
        return True
```

**Complexity:** O(1) per operation

### Level 2

**Core Idea:** Sort fields at read time — writes are more frequent so we pay the sort cost on scan.

```python
def scan(self, timestamp: int, key: str) -> list[str]:
    if key not in self.data:
        return []
    result = []
    for field, value in sorted(self.data[key].items()):
        if not self._is_expired(key, field, timestamp):
            result.append(f"{field}({value})")
    return result

def scan_with_prefix(self, timestamp: int, key: str, prefix: str) -> list[str]:
    if key not in self.data:
        return []
    return [
        f"{field}({value})"
        for field, value in sorted(self.data[key].items())
        if field.startswith(prefix) and not self._is_expired(key, field, timestamp)
    ]
```

**Complexity:** O(F log F) where F = fields on the key

### Level 3

**Core Idea:** Lazy expiration — check and clean on access rather than running a background sweeper.

```python
def set_with_ttl(self, timestamp: int, key: str, field: str,
                 value: str, ttl: int) -> None:
    self.data.setdefault(key, {})[field] = value
    self.expiry.setdefault(key, {})[field] = timestamp + ttl

def compare_and_set_with_ttl(self, timestamp: int, key: str, field: str,
                              expected_value: str, new_value: str, ttl: int) -> bool:
    if key not in self.data or field not in self.data[key]:
        return False
    if self._is_expired(key, field, timestamp):
        self._remove(key, field)
        return False
    if self.data[key][field] != expected_value:
        return False
    self.data[key][field] = new_value
    self.expiry.setdefault(key, {})[field] = timestamp + ttl
    return True
```

**Complexity:** O(1) per operation

### Level 4

**Core Idea:** Store snapshots keyed by timestamp; use `bisect` for O(log B) lookup of latest backup at or before a given time. Use `deepcopy` to prevent snapshot aliasing.

```python
import bisect
import copy

class InMemoryDB:
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.backup_times = []          # sorted list
        self.snapshots = {}             # ts -> (data_copy, expiry_copy)

    def backup(self, timestamp: int) -> None:
        data_snap, expiry_snap = {}, {}
        for key, fields in self.data.items():
            live = {f: v for f, v in fields.items()
                    if not self._is_expired(key, f, timestamp)}
            if live:
                data_snap[key] = live
                if key in self.expiry:
                    expiry_snap[key] = {
                        f: self.expiry[key][f]
                        for f in live if f in self.expiry.get(key, {})
                    }
        self.snapshots[timestamp] = (copy.deepcopy(data_snap),
                                     copy.deepcopy(expiry_snap))
        bisect.insort(self.backup_times, timestamp)

    def restore(self, timestamp: int, backup_timestamp: int) -> None:
        idx = bisect.bisect_right(self.backup_times, backup_timestamp) - 1
        if idx < 0:
            return
        ts = self.backup_times[idx]
        data_snap, expiry_snap = self.snapshots[ts]
        self.data = copy.deepcopy(data_snap)
        self.expiry = copy.deepcopy(expiry_snap)
```

**Complexity:** backup O(N), restore O(N + log B) where N = total fields, B = number of backups

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Lazy vs. eager expiration:** Lazy expiration (used here) means expired entries occupy memory until accessed. At Coinbase scale — millions of session tokens or short-lived API keys — this is a real memory leak. Production Redis uses both lazy expiration on access *and* a probabilistic background sweep that samples random keys to reap. The sweep rate is tunable to trade CPU for memory.
- **Snapshot memory cost:** `deepcopy` on every backup is O(N) memory. With frequent backups, you hold multiple full copies. Real systems use incremental snapshots (WAL/journal) or copy-on-write pages. Redis RDB vs AOF is the canonical tradeoff discussion.
- **CAS and atomicity:** `compare_and_set` is only safe in a single-threaded context. In a multi-threaded or distributed setting, two threads can both read the same `expected_value` and both succeed the comparison before either writes. You need either a mutex per key or true atomic hardware CAS. This is the foundation of optimistic locking in distributed databases.
- **TTL precision:** The problem uses integer timestamps. Real-world TTL bugs often come from clock skew across nodes or from using wall-clock time vs. monotonic time. For a system tracking API rate limits or auth tokens at Coinbase, even 1-second skew can cause incorrect rejects or security gaps.
- **Binary search on backup timestamps:** `bisect_right(...) - 1` correctly returns the latest backup at or before the requested time. Edge case: if `backup_timestamp` is before all backups, `idx = -1` and we return early — make sure this is tested.

### Common Interview Traps

- `set()` must clear any existing TTL on the field — forgetting this means a `set()` after `set_with_ttl()` will still expire, silently breaking the contract.
- `delete()` on an expired field should return `False`, not `True` — the field was already gone from the caller's perspective.
- `compare_and_set` on a missing key must return `False` — not raise a KeyError. Guard both key and field presence before comparing.
- Backup should exclude already-expired entries. If you `deepcopy` the raw data dict, you snapshot expired garbage that will incorrectly reappear after restore.
- After restore, the TTL absolute timestamps are preserved, not shifted. A field that expires at time 22 in the backup still expires at time 22 after restore — it's not re-anchored to the restore timestamp.

### How to Push Forward as Staff+

- **Name the tradeoffs proactively:** "Lazy expiration keeps the hot path fast but leaks memory. I'd add a bounded background sweeper — sample N random keys per second and evict expired ones — similar to Redis's approach."
- **Propose WAL for incremental backup:** "Full snapshots on every backup are expensive. I'd maintain a write-ahead log and take periodic checkpoints. Restore becomes: load last checkpoint + replay WAL entries up to the target timestamp."
- **Connect to Coinbase domain:** This pattern maps directly to how Coinbase likely manages API session tokens, OAuth credentials, and rate-limit counters — all of which need TTL, CAS for safe updates, and point-in-time restore for incident replay. A compliance team might need to restore to a specific timestamp during an audit.
- **Distributed extension:** "If this needs to scale across nodes, each node handles a shard of keys. CAS requires a quorum write to avoid split-brain. Backup becomes a distributed snapshot — coordinate with a global timestamp (Lamport clock or TrueTime) to get a consistent cut."
- **Observability:** "In production I'd add metrics: expired-key eviction rate, backup size histogram, CAS conflict rate. A spike in CAS conflicts points to a hot key under contention."
