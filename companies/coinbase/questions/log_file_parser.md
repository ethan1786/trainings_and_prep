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

```python
class LogParser:
    def ingest(self, lines: list[str]) -> None
    # Parse and store log lines
    # Skip lines that don't split into at least 4 colon-separated parts
    # Skip lines with non-integer timestamps

    def get_logs_by_thread(self, thread_id: str) -> list[dict]
    # Returns list of dicts sorted by timestamp ASC
    # Each dict: {"process_id": str, "thread_id": str, "timestamp": int, "content": str}
    # Returns [] if thread not found
```

### Part 2: Count Active Threads in a Time Window

```python
def count_active_threads(self, start: int, end: int) -> int
# Count distinct threads with at least one log entry where start <= timestamp <= end
```

---

## Solution Approach

### Part 1

**Core Idea:** `split(":", 3)` preserves colons in content. Group entries by thread_id into a dict of lists. Sort on retrieval, not ingestion.

**Data Structures:** `defaultdict(list)` — `thread_logs[thread_id] = [entry, ...]`

```python
from collections import defaultdict

class LogParser:
    def __init__(self):
        self.thread_logs = defaultdict(list)
        self.thread_timestamps = defaultdict(list)  # for binary search
        self._dirty = False

    def ingest(self, lines: list[str]) -> None:
        for line in lines:
            parts = line.split(":", 3)
            if len(parts) < 4:
                continue
            process_id, thread_id, ts_str, content = parts
            try:
                timestamp = int(ts_str)
            except ValueError:
                continue
            entry = {
                "process_id": process_id,
                "thread_id": thread_id,
                "timestamp": timestamp,
                "content": content,
            }
            self.thread_logs[thread_id].append(entry)
            self.thread_timestamps[thread_id].append(timestamp)
        self._dirty = True

    def get_logs_by_thread(self, thread_id: str) -> list[dict]:
        return sorted(self.thread_logs[thread_id], key=lambda e: e["timestamp"])
```

**Complexity:** ingest O(N), get_logs_by_thread O(K log K) where K = entries for that thread

### Part 2

**Core Idea:** For repeated range queries, maintain a sorted timestamp list per thread. Binary search to check if any timestamp falls in `[start, end]` in O(log K) per thread rather than O(K).

```python
import bisect

def _ensure_sorted(self):
    if self._dirty:
        for thread_id in self.thread_timestamps:
            self.thread_timestamps[thread_id].sort()
        self._dirty = False

def count_active_threads(self, start: int, end: int) -> int:
    self._ensure_sorted()
    count = 0
    for thread_id, timestamps in self.thread_timestamps.items():
        idx = bisect.bisect_left(timestamps, start)
        if idx < len(timestamps) and timestamps[idx] <= end:
            count += 1
    return count
```

**Complexity:** count_active_threads O(T log K) where T = unique threads, K = max entries per thread. One-time sort cost O(N log N) amortized across calls.

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns

- **Streaming / large files:** This implementation loads all lines into RAM. For multi-GB log files, ingest should process line-by-line from a file handle or network stream, writing entries directly to disk-backed storage or a time-series DB (e.g., ClickHouse, Loki) rather than an in-memory dict.
- **Out-of-order ingestion:** Logs from distributed systems arrive out of order. The `_dirty` flag handles lazy re-sort, but if `ingest` is called frequently in small batches, `_ensure_sorted` triggers constant re-sorts. Better: use `bisect.insort` at ingest time to maintain sorted order incrementally — O(K) per insert but eliminates re-sort on query.
- **Thread definition ambiguity:** The problem defines a thread as "active" if it has any log in the range. In production, "active" often means the thread's *execution span* overlaps the window (start of first log < window_end AND end of last log > window_start). This changes the data structure from a sorted timestamp list to tracking `(min_ts, max_ts)` per thread.
- **Malformed lines:** `try/except` on timestamp parsing is correct. But malformed lines should also be counted and surfaced as a metric — in production, a sudden spike in parse errors is a signal of a format change or upstream bug.
- **Memory:** `thread_timestamps` duplicates all timestamps already stored in `thread_logs`. This doubles memory for timestamps. You could compute timestamps on-demand from `thread_logs`, trading CPU for memory.

### Common Interview Traps

- **`split(":", 3)` vs `split(":")`:** Using plain `split(":")` breaks any content containing colons (e.g., `"DB query: result=OK"`). This is the most commonly missed detail in Part 1 — interviewers look for it.
- **Empty thread lookup:** `defaultdict(list)` returns `[]` for missing keys without a key-existence check. Safe behavior, but calling `get_logs_by_thread("missing")` also *creates* an empty entry in the dict, which can inflate `thread_timestamps` during `count_active_threads`. Guard with `if thread_id in self.thread_logs`.
- **`bisect_left` boundary:** `bisect_left(timestamps, start)` gives the first index where `timestamps[idx] >= start`. You still need `timestamps[idx] <= end` — don't forget the upper bound check.
- **Re-sort invalidation:** If `ingest` is called after `count_active_threads` without resetting `_dirty`, queries see stale sorted order. The `_dirty` flag must be set on every `ingest` call.

### How to Push Forward as Staff+

- **Propose `bisect.insort` proactively:** "I started with a lazy sort flag, but if we're ingesting continuously and querying frequently, I'd switch to `bisect.insort` on each entry — keeps timestamps sorted at all times at O(K) insert cost, avoids the re-sort on every query batch."
- **Raise the streaming question early:** "Before I implement this, I want to clarify the scale. If lines come from a live log stream — which is typical at Coinbase for transaction logs or API traces — I'd design around a streaming ingest pipeline, not a batch load."
- **Connect to Coinbase domain:** At Coinbase, this pattern applies directly to transaction audit logs (each transaction has a process, thread/goroutine, timestamp, and event type). Counting active threads in a window maps to understanding concurrency levels during a trading spike or incident.
- **Extend to process-level queries:** "A natural next step is `count_active_processes(start, end)` or `get_logs_by_process`. I'd restructure storage to index by `(process_id, thread_id)` as a composite key, or maintain a separate `process_logs` dict in parallel."
- **Observability angle:** "In a real system, the output of `count_active_threads` over sliding windows is a useful real-time metric for thread pool saturation. I'd pipe this into a Prometheus gauge and alert when it approaches the thread pool limit."
