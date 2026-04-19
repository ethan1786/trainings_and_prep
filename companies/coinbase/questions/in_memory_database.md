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

```java
class InMemoryDB {
    void set(int timestamp, String key, String field, String value)
    // Upsert; clears any existing TTL on the field

    String get(int timestamp, String key, String field)
    // Returns "" if missing or expired

    boolean delete(int timestamp, String key, String field)
    // Returns false if missing or already expired

    boolean compareAndSet(int timestamp, String key, String field,
                          String expectedValue, String newValue)
    // Updates only if current value == expectedValue; false if missing/expired
}
```

### Level 2: Scan and Filter

```java
List<String> scan(int timestamp, String key)
// Returns ["field(value)", ...] sorted alphabetically by field; omits expired

List<String> scanWithPrefix(int timestamp, String key, String prefix)
// Same as scan but only fields starting with prefix
```

### Level 3: TTL

```java
void setWithTtl(int timestamp, String key, String field, String value, int ttl)
// Field expires at timestamp + ttl (expiry inclusive: expired when current >= expiry)

boolean compareAndSetWithTtl(int timestamp, String key, String field,
                              String expectedValue, String newValue, int ttl)
// CAS + sets new TTL on success; fails if field missing or expired
```

### Level 4: Backup and Restore

```java
void backup(int timestamp)
// Snapshot current live (non-expired) state including TTL metadata

void restore(int timestamp, int backupTimestamp)
// Restore from latest backup at or before backupTimestamp
// TTLs in the restored snapshot remain as originally set (not shifted)
```

---

## Solution Approach

### Level 1

**Core Idea:** Two parallel nested maps — one for values, one for expiry times.

**Data Structures:**
- `data: Map<String, Map<String, String>>` — `data[key][field] = value`
- `expiry: Map<String, Map<String, Integer>>` — `expiry[key][field] = expiryTimestamp`

```java
class InMemoryDB {
    private final Map<String, Map<String, String>> data = new HashMap<>();
    private final Map<String, Map<String, Integer>> expiry = new HashMap<>();

    private boolean isExpired(String key, String field, int ts) {
        Map<String, Integer> keyExpiry = expiry.get(key);
        if (keyExpiry == null) return false;
        Integer exp = keyExpiry.get(field);
        return exp != null && ts >= exp;
    }

    private void remove(String key, String field) {
        Map<String, String> keyData = data.get(key);
        if (keyData != null) {
            keyData.remove(field);
            if (keyData.isEmpty()) data.remove(key);
        }
        Map<String, Integer> keyExpiry = expiry.get(key);
        if (keyExpiry != null) {
            keyExpiry.remove(field);
            if (keyExpiry.isEmpty()) expiry.remove(key);
        }
    }

    public void set(int timestamp, String key, String field, String value) {
        data.computeIfAbsent(key, k -> new HashMap<>()).put(field, value);
        Map<String, Integer> keyExpiry = expiry.get(key);
        if (keyExpiry != null) keyExpiry.remove(field);
    }

    public String get(int timestamp, String key, String field) {
        Map<String, String> keyData = data.get(key);
        if (keyData == null || !keyData.containsKey(field)) return "";
        if (isExpired(key, field, timestamp)) {
            remove(key, field);
            return "";
        }
        return keyData.get(field);
    }

    public boolean delete(int timestamp, String key, String field) {
        Map<String, String> keyData = data.get(key);
        if (keyData == null || !keyData.containsKey(field)) return false;
        if (isExpired(key, field, timestamp)) {
            remove(key, field);
            return false;
        }
        remove(key, field);
        return true;
    }

    public boolean compareAndSet(int timestamp, String key, String field,
                                 String expectedValue, String newValue) {
        Map<String, String> keyData = data.get(key);
        if (keyData == null || !keyData.containsKey(field)) return false;
        if (isExpired(key, field, timestamp)) {
            remove(key, field);
            return false;
        }
        if (!keyData.get(field).equals(expectedValue)) return false;
        keyData.put(field, newValue);
        return true;
    }
}
```

**Complexity:** O(1) per operation

### Level 2

**Core Idea:** Sort fields at read time — writes are more frequent so we pay the sort cost on scan.

```java
public List<String> scan(int timestamp, String key) {
    Map<String, String> keyData = data.get(key);
    if (keyData == null) return Collections.emptyList();
    return keyData.entrySet().stream()
        .filter(e -> !isExpired(key, e.getKey(), timestamp))
        .sorted(Map.Entry.comparingByKey())
        .map(e -> e.getKey() + "(" + e.getValue() + ")")
        .collect(Collectors.toList());
}

public List<String> scanWithPrefix(int timestamp, String key, String prefix) {
    Map<String, String> keyData = data.get(key);
    if (keyData == null) return Collections.emptyList();
    return keyData.entrySet().stream()
        .filter(e -> e.getKey().startsWith(prefix) && !isExpired(key, e.getKey(), timestamp))
        .sorted(Map.Entry.comparingByKey())
        .map(e -> e.getKey() + "(" + e.getValue() + ")")
        .collect(Collectors.toList());
}
```

**Complexity:** O(F log F) where F = fields on the key

### Level 3

**Core Idea:** Lazy expiration — check and clean on access rather than running a background sweeper.

```java
public void setWithTtl(int timestamp, String key, String field, String value, int ttl) {
    data.computeIfAbsent(key, k -> new HashMap<>()).put(field, value);
    expiry.computeIfAbsent(key, k -> new HashMap<>()).put(field, timestamp + ttl);
}

public boolean compareAndSetWithTtl(int timestamp, String key, String field,
                                    String expectedValue, String newValue, int ttl) {
    Map<String, String> keyData = data.get(key);
    if (keyData == null || !keyData.containsKey(field)) return false;
    if (isExpired(key, field, timestamp)) {
        remove(key, field);
        return false;
    }
    if (!keyData.get(field).equals(expectedValue)) return false;
    keyData.put(field, newValue);
    expiry.computeIfAbsent(key, k -> new HashMap<>()).put(field, timestamp + ttl);
    return true;
}
```

**Complexity:** O(1) per operation

### Level 4

**Core Idea:** Store snapshots keyed by timestamp in a `TreeMap` for O(log B) lookup of latest backup at or before a given time. Use deep copies to prevent snapshot aliasing.

```java
// Additional fields in InMemoryDB:
private final TreeMap<Integer, Object[]> snapshots = new TreeMap<>();
// snapshots[ts] = [deepCopyOfData, deepCopyOfExpiry]

public void backup(int timestamp) {
    Map<String, Map<String, String>> dataSnap = new HashMap<>();
    Map<String, Map<String, Integer>> expirySnap = new HashMap<>();
    for (Map.Entry<String, Map<String, String>> entry : data.entrySet()) {
        String key = entry.getKey();
        Map<String, String> liveFields = new HashMap<>();
        for (Map.Entry<String, String> fe : entry.getValue().entrySet()) {
            if (!isExpired(key, fe.getKey(), timestamp)) {
                liveFields.put(fe.getKey(), fe.getValue());
            }
        }
        if (!liveFields.isEmpty()) {
            dataSnap.put(key, liveFields);
            Map<String, Integer> keyExpiry = expiry.get(key);
            if (keyExpiry != null) {
                Map<String, Integer> expSnap = new HashMap<>();
                for (String field : liveFields.keySet()) {
                    if (keyExpiry.containsKey(field)) expSnap.put(field, keyExpiry.get(field));
                }
                if (!expSnap.isEmpty()) expirySnap.put(key, expSnap);
            }
        }
    }
    snapshots.put(timestamp, new Object[]{dataSnap, expirySnap});
}

@SuppressWarnings("unchecked")
public void restore(int timestamp, int backupTimestamp) {
    Map.Entry<Integer, Object[]> entry = snapshots.floorEntry(backupTimestamp);
    if (entry == null) return;
    Object[] snap = entry.getValue();
    // Deep copy to avoid aliasing
    Map<String, Map<String, String>> dataSnap = (Map<String, Map<String, String>>) snap[0];
    Map<String, Map<String, Integer>> expirySnap = (Map<String, Map<String, Integer>>) snap[1];
    data.clear();
    expiry.clear();
    for (Map.Entry<String, Map<String, String>> e : dataSnap.entrySet())
        data.put(e.getKey(), new HashMap<>(e.getValue()));
    for (Map.Entry<String, Map<String, Integer>> e : expirySnap.entrySet())
        expiry.put(e.getKey(), new HashMap<>(e.getValue()));
}
```

**Complexity:** backup O(N), restore O(N + log B) where N = total fields, B = number of backups

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Lazy vs. eager expiration:** Lazy expiration (used here) means expired entries occupy memory until accessed. At Coinbase scale — millions of session tokens or short-lived API keys — this is a real memory leak. Production Redis uses both lazy expiration on access *and* a probabilistic background sweep that samples random keys to reap. The sweep rate is tunable to trade CPU for memory.
- **Snapshot memory cost:** Deep copying on every backup is O(N) memory. With frequent backups, you hold multiple full copies. Real systems use incremental snapshots (WAL/journal) or copy-on-write pages. Redis RDB vs AOF is the canonical tradeoff discussion.
- **CAS and atomicity:** `compareAndSet` is only safe in a single-threaded context. In a multi-threaded or distributed setting, two threads can both read the same `expectedValue` and both succeed the comparison before either writes. You need either a mutex per key or true atomic hardware CAS. This is the foundation of optimistic locking in distributed databases.
- **TTL precision:** The problem uses integer timestamps. Real-world TTL bugs often come from clock skew across nodes or from using wall-clock time vs. monotonic time. For a system tracking API rate limits or auth tokens at Coinbase, even 1-second skew can cause incorrect rejects or security gaps.
- **Binary search on backup timestamps:** `TreeMap.floorEntry(backupTimestamp)` correctly returns the latest backup at or before the requested time. Edge case: if `backupTimestamp` is before all backups, `floorEntry` returns `null` and we return early — make sure this is tested.

### Common Interview Traps

- `set()` must clear any existing TTL on the field — forgetting this means a `set()` after `setWithTtl()` will still expire, silently breaking the contract.
- `delete()` on an expired field should return `false`, not `true` — the field was already gone from the caller's perspective.
- `compareAndSet` on a missing key must return `false` — not throw a NullPointerException. Guard both key and field presence before comparing.
- Backup should exclude already-expired entries. If you copy the raw data map, you snapshot expired garbage that will incorrectly reappear after restore.
- After restore, the TTL absolute timestamps are preserved, not shifted. A field that expires at time 22 in the backup still expires at time 22 after restore — it's not re-anchored to the restore timestamp.

### How to Push Forward as Staff+

- **Name the tradeoffs proactively:** "Lazy expiration keeps the hot path fast but leaks memory. I'd add a bounded background sweeper — sample N random keys per second and evict expired ones — similar to Redis's approach."
- **Propose WAL for incremental backup:** "Full snapshots on every backup are expensive. I'd maintain a write-ahead log and take periodic checkpoints. Restore becomes: load last checkpoint + replay WAL entries up to the target timestamp."
- **Connect to Coinbase domain:** This pattern maps directly to how Coinbase likely manages API session tokens, OAuth credentials, and rate-limit counters — all of which need TTL, CAS for safe updates, and point-in-time restore for incident replay. A compliance team might need to restore to a specific timestamp during an audit.
- **Distributed extension:** "If this needs to scale across nodes, each node handles a shard of keys. CAS requires a quorum write to avoid split-brain. Backup becomes a distributed snapshot — coordinate with a global timestamp (Lamport clock or TrueTime) to get a consistent cut."
- **Observability:** "In production I'd add metrics: expired-key eviction rate, backup size histogram, CAS conflict rate. A spike in CAS conflicts points to a hot key under contention."
