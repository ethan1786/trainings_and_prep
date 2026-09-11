## Summary

Nested key-field-value store with TTL, prefix scan, and multi-backup/restore. 4 levels: basic CRUD + CAS → scan/scanWithPrefix → TTL (lazy expiration) → backup/restore with TreeMap for point-in-time lookup.

## Design

**Data model:** Single nested map with `ExpiryValue` wrapping value + optional TTL. Simpler than reference solution's parallel data/expiry maps.

**Maps / structures:**
- `db`: key → (field → ExpiryValue{value, ttl})
- `allbackups`: TreeMap<timestamp → deep copy of db> for O(log B) `floorEntry` lookup

**Key pattern:** Lazy expiration — writes never clean up, reads filter out expired entries. `backup` excludes expired fields; `restore` copies blindly and lets reads handle stale TTLs.

**Gotchas under pressure:**
- `set()` clears existing TTL (creates ExpiryValue without ttl); `setWithTtl()` sets it — don't mix up
- `compareAndSet` (Level 1) must preserve existing TTL when updating value — don't create new ExpiryValue without carrying ttl forward
- Deep copy in BOTH backup and restore — ExpiryValue objects are mutable, shallow copy causes aliasing where mutations to live db corrupt backups
- `restore` with no matching backup (`floorEntry` returns null) — guard against NPE
- Expired at boundary: `ttl <= timestamp` means expired (inclusive), confirm with interviewer

---

```java
class InMemoryDB {
    private Map<String, Map<String, ExpiryValue>> db = new HashMap<>();
    private TreeMap<Integer, Map<String, Map<String, ExpiryValue>>> allbackups = new TreeMap<>();
    void set(int timestamp, String key, String field, String value) {
        db.computeIfAbsent(key, k -> new HashMap<>()).put(field, new ExpiryValue(value));
    }
    // Upsert; clears any existing TTL on the field

    String get(int timestamp, String key, String field) {
        ExpiryValue data = db.getOrDefault(key, Map.of()).getOrDefault(field, null);
        if (data == null || (data.ttl != null && data.ttl.intValue() <= timestamp)) {
            return "";
        }
        return data.value;
    }
    // Returns "" if missing or expired

    boolean delete(int timestamp, String key, String field) {
        if (!db.containsKey(key)) {
            return false;
        }
        ExpiryValue data = db.getOrDefault(key, Map.of()).getOrDefault(field, null);
        if (data == null || (data.ttl != null && data.ttl.intValue() <= timestamp)) {
            return false;
        }
        db.get(key).remove(field);
        return true;
    }
    // Returns false if missing or already expired

    boolean compareAndSet(int timestamp, String key, String field,
                          String expectedValue, String newValue) {
        if (!db.containsKey(key)) {
            return false;
        }
        ExpiryValue data = db.getOrDefault(key, Map.of()).getOrDefault(field, null);
        if (data == null || (data.ttl != null && data.ttl.intValue() <= timestamp)) {
            return false;
        }
        if (data.value.equals(expectedValue)) {
            data.value = newValue;
            return true;
        }
        return false;
    }
    // Updates only if current value == expectedValue; false if missing/expired

    List<String> scan(int timestamp, String key) {
        if(!db.containsKey(key)) {
            return List.of();
        }
        Map<String, ExpiryValue> data = db.get(key);
        return data.entrySet().stream()
            .filter(entry -> entry.getValue().ttl == null || entry.getValue().ttl.intValue() > timestamp)
            .sorted((a, b) -> a.getKey().compareTo(b.getKey()))
            .map(entry -> new StringBuilder().append(entry.getKey()).append('(').append(entry.getValue().value).append(')').toString())
            .toList();
    }
    // Returns ["field(value)", ...] sorted alphabetically by field; omits expired

    List<String> scanWithPrefix(int timestamp, String key, String prefix) {
        if(!db.containsKey(key)) {
            return List.of();
        }
        Map<String, ExpiryValue> data = db.get(key);
        return data.entrySet().stream()
            .filter(entry -> entry.getKey().startsWith(prefix) && (entry.getValue().ttl == null || entry.getValue().ttl.intValue() > timestamp))
            .sorted((a, b) -> a.getKey().compareTo(b.getKey()))
            .map(entry -> new StringBuilder().append(entry.getKey()).append('(').append(entry.getValue().value).append(')').toString())
            .toList();
    }
    // Same as scan but only fields starting with prefix

    void setWithTtl(int timestamp, String key, String field, String value, int ttl) {
        db.computeIfAbsent(key, k -> new HashMap<>()).put(field, new ExpiryValue(value, timestamp + ttl));
    }
    // Field expires at timestamp + ttl (expiry inclusive: expired when current >= expiry)

    boolean compareAndSetWithTtl(int timestamp, String key, String field,
                                String expectedValue, String newValue, int ttl) {
        if (!db.containsKey(key)) {
            return false;
        }
        ExpiryValue data = db.getOrDefault(key, Map.of()).getOrDefault(field, null);
        if (data == null || (data.ttl != null && data.ttl.intValue() <= timestamp)) {
            return false;
        }
        if (db.get(key).get(field).value.equals(expectedValue)) {
            db.get(key).put(field, new ExpiryValue(newValue, timestamp + ttl));
            return true;
        }
        return false;
    }
    // CAS + sets new TTL on success; fails if field missing or expired

    void backup(int timestamp) {
        Map<String, Map<String, ExpiryValue>> backup = new HashMap<>();
        for (Map.Entry<String, Map<String, ExpiryValue>> dbEntry: db.entrySet()) {
            String key = dbEntry.getKey();
            Map<String, ExpiryValue> allFields = dbEntry.getValue();
            Map<String, ExpiryValue> backupFields = new HashMap<>();
            for (Map.Entry<String, ExpiryValue> fieldEntry: allFields.entrySet()) {
                ExpiryValue data = fieldEntry.getValue();
                if (data.ttl == null || data.ttl.intValue() > timestamp) {
                    backupFields.put(fieldEntry.getKey(), new ExpiryValue(data.value, data.ttl));
                }
            }
            if (!backupFields.isEmpty()) {
                backup.put(key, backupFields);
            }
        }
        allbackups.put(timestamp, backup);
    }
    // Snapshot current live (non-expired) state including TTL metadata

    void restore(int timestamp, int backupTimestamp) {
        Map.Entry<Integer, Map<String, Map<String, ExpiryValue>>> backupEntry = allbackups.floorEntry(backupTimestamp);
        db.clear();
        if (backupEntry != null) {
            backupEntry.getValue().entrySet().forEach(dbEntry -> {
                Map<String, ExpiryValue> fieldClone = new HashMap<>();
                dbEntry.getValue().entrySet().forEach(field -> {
                    fieldClone.put(field.getKey(), new ExpiryValue(field.getValue().value, field.getValue().ttl));
                });
                db.put(dbEntry.getKey(), fieldClone);
            });
        }
    }
    // Restore from latest backup at or before backupTimestamp
    // TTLs in the restored snapshot remain as originally set (not shifted)


    private static class ExpiryValue {
        String value;
        Integer ttl;
        ExpiryValue (String v, Integer t) {
            value = v;
            ttl = t;
        }
        ExpiryValue (String v) {
            value = v;
        }
    }
}