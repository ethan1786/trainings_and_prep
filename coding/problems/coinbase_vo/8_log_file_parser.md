# Log File Parser

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 30-45 min
**Key Topics:** String parsing, HashMap, Sorted list, Binary Search (bisect), Streaming

---

## Problem Statement

Parse structured log lines and answer queries about thread activity. Log lines follow the format:

```
process_id:thread_id:timestamp:content
```

The `content` field may itself contain colons. Timestamps are integers. The system must support lookup by thread and time-window queries.

## Requirements

### Part 1: Parse and Group by Thread

```java
class LogParser {
    void ingest(List<String> lines)
    // Parse and store log lines
    // Skip lines that don't split into at least 4 colon-separated parts
    // Skip lines with non-integer timestamps

    List<Map<String, Object>> getLogsByThread(String threadId)
    // Returns list of maps sorted by timestamp ASC
    // Each map: {"process_id": String, "thread_id": String, "timestamp": int, "content": String}
    // Returns [] if thread not found
}
```

### Part 2: Count Active Threads in a Time Window

```java
int countActiveThreads(int start, int end)
// Count distinct threads with at least one log entry where start <= timestamp <= end
```

---

## Solution Approach

### Part 1

**Core Idea:** `split(":", 4)` with a limit preserves colons in content. Group entries by threadId into a map of lists. Sort on retrieval, not ingestion.

**Data Structures:** `HashMap<String, List<LogEntry>>` — `threadLogs[threadId] = [entry, ...]`

```java
class LogParser {
    private record LogEntry(String processId, String threadId, int timestamp, String content) {}

    private final Map<String, List<LogEntry>> threadLogs = new HashMap<>();
    private final Map<String, List<Integer>> threadTimestamps = new HashMap<>();
    private boolean dirty = false;

    public void ingest(List<String> lines) {
        for (String line : lines) {
            String[] parts = line.split(":", 4);
            if (parts.length < 4) continue;
            int timestamp;
            try {
                timestamp = Integer.parseInt(parts[2]);
            } catch (NumberFormatException e) {
                continue;
            }
            String threadId = parts[1];
            LogEntry entry = new LogEntry(parts[0], threadId, timestamp, parts[3]);
            threadLogs.computeIfAbsent(threadId, k -> new ArrayList<>()).add(entry);
            threadTimestamps.computeIfAbsent(threadId, k -> new ArrayList<>()).add(timestamp);
        }
        dirty = true;
    }

    public List<Map<String, Object>> getLogsByThread(String threadId) {
        List<LogEntry> entries = threadLogs.get(threadId);
        if (entries == null) return Collections.emptyList();
        return entries.stream()
            .sorted(Comparator.comparingInt(LogEntry::timestamp))
            .map(e -> {
                Map<String, Object> m = new LinkedHashMap<>();
                m.put("process_id", e.processId());
                m.put("thread_id", e.threadId());
                m.put("timestamp", e.timestamp());
                m.put("content", e.content());
                return m;
            })
            .collect(Collectors.toList());
    }
}
```

**Complexity:** ingest O(N), getLogsByThread O(K log K) where K = entries for that thread

### Part 2

**Core Idea:** For repeated range queries, maintain a sorted timestamp list per thread. Binary search to check if any timestamp falls in `[start, end]` in O(log K) per thread rather than O(K).

```java
private void ensureSorted() {
    if (dirty) {
        threadTimestamps.values().forEach(Collections::sort);
        dirty = false;
    }
}

public int countActiveThreads(int start, int end) {
    ensureSorted();
    int count = 0;
    for (Map.Entry<String, List<Integer>> entry : threadTimestamps.entrySet()) {
        List<Integer> timestamps = entry.getValue();
        int idx = Collections.binarySearch(timestamps, start);
        if (idx < 0) idx = -idx - 1;  // insertion point
        if (idx < timestamps.size() && timestamps.get(idx) <= end) count++;
    }
    return count;
}
```

**Complexity:** countActiveThreads O(T log K) where T = unique threads, K = max entries per thread. One-time sort cost O(N log N) amortized across calls.

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Streaming / large files:** This implementation loads all lines into RAM. For multi-GB log files, ingest should process line-by-line from a file handle or network stream, writing entries directly to disk-backed storage or a time-series DB (e.g., ClickHouse, Loki) rather than an in-memory map.
- **Out-of-order ingestion:** Logs from distributed systems arrive out of order. The `dirty` flag handles lazy re-sort, but if `ingest` is called frequently in small batches, `ensureSorted` triggers constant re-sorts. Better: insert into the sorted list using binary search at ingest time to maintain sorted order incrementally — O(K) per insert but eliminates re-sort on query.
- **Thread definition ambiguity:** The problem defines a thread as "active" if it has any log in the range. In production, "active" often means the thread's *execution span* overlaps the window (start of first log < window_end AND end of last log > window_start). This changes the data structure from a sorted timestamp list to tracking `(minTs, maxTs)` per thread.
- **Malformed lines:** `try/catch` on timestamp parsing is correct. But malformed lines should also be counted and surfaced as a metric — in production, a sudden spike in parse errors is a signal of a format change or upstream bug.
- **Memory:** `threadTimestamps` duplicates all timestamps already stored in `threadLogs`. This doubles memory for timestamps. You could compute timestamps on-demand from `threadLogs`, trading CPU for memory.

### Common Interview Traps

- **`split(":", 4)` vs `split(":")`:** Using plain `split(":")` breaks any content containing colons (e.g., `"DB query: result=OK"`). This is the most commonly missed detail in Part 1 — interviewers look for it.
- **Empty thread lookup:** Calling `getLogsByThread("missing")` should return an empty list without creating a spurious entry. Guard with a null check rather than `computeIfAbsent`.
- **Binary search boundary:** After `Collections.binarySearch` returns a negative insertion point, you still need `timestamps.get(idx) <= end` — don't forget the upper bound check.
- **Re-sort invalidation:** If `ingest` is called after `countActiveThreads` without resetting `dirty`, queries see stale sorted order. The `dirty` flag must be set on every `ingest` call.

### How to Push Forward as Staff+

- **Propose sorted insert proactively:** "I started with a lazy sort flag, but if we're ingesting continuously and querying frequently, I'd switch to inserting at the correct sorted position on each entry — keeps timestamps sorted at all times at O(K) insert cost, avoids the re-sort on every query batch."
- **Raise the streaming question early:** "Before I implement this, I want to clarify the scale. If lines come from a live log stream — which is typical at Coinbase for transaction logs or API traces — I'd design around a streaming ingest pipeline, not a batch load."
- **Connect to Coinbase domain:** At Coinbase, this pattern applies directly to transaction audit logs (each transaction has a process, thread/goroutine, timestamp, and event type). Counting active threads in a window maps to understanding concurrency levels during a trading spike or incident.
- **Extend to process-level queries:** "A natural next step is `countActiveProcesses(start, end)` or `getLogsByProcess`. I'd restructure storage to index by `(processId, threadId)` as a composite key, or maintain a separate `processLogs` map in parallel."
- **Observability angle:** "In a real system, the output of `countActiveThreads` over sliding windows is a useful real-time metric for thread pool saturation. I'd pipe this into a Prometheus gauge and alert when it approaches the thread pool limit."
