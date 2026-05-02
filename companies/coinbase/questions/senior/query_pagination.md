# Query Pagination

**Category:** Coding — **VO #1 Most Frequent (10 occurrences in 2026 Q2 data)**
**Difficulty:** Medium
**Time Estimate:** 45-60 min
**Key Topics:** Builder Pattern, Method Chaining, Offset vs. Keyset Pagination, API Design

### Interview Intel (2026 Q2 Blog)
- **Highest frequency VO coding question** — appeared in 10 out of 47 coding interviews
- Interviewer deliberately **will not give function signatures** — expects you to design input/output OOD yourself
- Forward + backward pagination is a common follow-up — `prevCursor` is not optional
- Offset vs cursor distinction is tested explicitly — name it unprompted
- Looks simple but the OOD design aspect is where candidates get caught

---

## Problem Statement

Design a transaction query system for financial data. Given an in-memory list of transactions, build a clean API that supports composable filtering and paginated result retrieval. The interviewer will not specify the API shape — you must propose and justify it.

```java
List<Map<String, Object>> transactions = List.of(
    Map.of("time", 1,  "id", 11, "userId", 1, "currency", 1, "amount", 10),
    Map.of("time", 2,  "id", 12, "userId", 1, "currency", 3, "amount", 11),
    Map.of("time", 3,  "id", 13, "userId", 2, "currency", 2, "amount", -10),
    // ... (15 total rows, see full dataset in example below)
);
```

## Requirements

### Level 1: Filtering
Support composable filters: time range, user ID, currency, amount range. Filters combine with AND. Execution is deferred until `execute()` is called.

```java
TransactionQuery query = new TransactionQuery(transactions);
query.setUserId(1).setTimeRange(5, 10).setCurrency(1);
List<Map<String, Object>> results = query.execute();
```

### Level 2: Pagination
Add paginated access over filtered results. The caller receives an opaque cursor and passes it back to get the next page.

```java
query.setPageSize(3);
Page page1 = query.fetchPage(0);          // cursor defaults to 0
Page page2 = query.fetchPage(page1.nextCursor);
// page.nextCursor is -1 when no more results
// page.prevCursor allows going backward
```

---

## Solution Approach

### Level 1
**Core Idea:** Store filters in a map; apply them lazily in `execute()`. Each `set*` method returns `this` for method chaining. Adding a new filter type only requires adding a method and a `matches` check.

```java
import java.util.*;

class TransactionQuery {
    private final List<Map<String, Object>> transactions;
    private Integer userId, currency, timeStart, timeEnd;
    private Double amountMin, amountMax;

    TransactionQuery(List<Map<String, Object>> transactions) {
        this.transactions = transactions;
    }

    TransactionQuery setUserId(int userId) { this.userId = userId; return this; }

    TransactionQuery setCurrency(int currency) { this.currency = currency; return this; }

    TransactionQuery setTimeRange(int start, int end) {
        this.timeStart = start; this.timeEnd = end; return this;
    }

    TransactionQuery setAmountRange(double min, double max) {
        this.amountMin = min; this.amountMax = max; return this;
    }

    private boolean matches(Map<String, Object> txn) {
        if (userId != null && !txn.get("userId").equals(userId)) return false;
        if (currency != null && !txn.get("currency").equals(currency)) return false;
        int time = (int) txn.get("time");
        if (timeStart != null && time < timeStart) return false;
        if (timeEnd != null && time > timeEnd) return false;
        double amount = ((Number) txn.get("amount")).doubleValue();
        if (amountMin != null && amount < amountMin) return false;
        if (amountMax != null && amount > amountMax) return false;
        return true;
    }

    List<Map<String, Object>> execute() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> t : transactions) {
            if (matches(t)) result.add(t);
        }
        return result;
    }
}
```

**Complexity:** O(1) per `set*`, O(N) `execute`, O(R) space — N = total rows, R = matches

### Level 2
**Core Idea:** Use an integer offset as the cursor. `fetchPage` scans and skips `cursor` matching rows, then collects `pageSize` results. If any row remains after the page, emit a `nextCursor`.

```java
class Page {
    final List<Map<String, Object>> data;
    final int nextCursor;  // -1 if no more results
    final int prevCursor;  // -1 if at first page

    Page(List<Map<String, Object>> data, int nextCursor, int prevCursor) {
        this.data = data;
        this.nextCursor = nextCursor;
        this.prevCursor = prevCursor;
    }
}

class TransactionQuery {
    // ... (Level 1 code) ...
    private int pageSize = -1;

    TransactionQuery setPageSize(int size) { this.pageSize = size; return this; }

    Page fetchPage(int cursor) {
        if (pageSize < 0) throw new IllegalStateException("pageSize must be set before fetchPage");

        List<Map<String, Object>> matched = new ArrayList<>();
        int skipped = 0;
        boolean hasMore = false;

        for (Map<String, Object> txn : transactions) {
            if (!matches(txn)) continue;
            if (skipped < cursor) { skipped++; continue; }
            if (matched.size() < pageSize) {
                matched.add(txn);
            } else {
                hasMore = true;
                break;
            }
        }

        int nextCursor = hasMore ? cursor + matched.size() : -1;
        int prevCursor = cursor > 0 ? Math.max(0, cursor - pageSize) : -1;
        return new Page(matched, nextCursor, prevCursor);
    }
}
```

**Complexity:** O(cursor + P) per `fetchPage` — P = pageSize

**Example trace (userId=1, currency=1, pageSize=3):**
```
Matching IDs: 11(t=1), 15(t=5), 19(t=9), 20(t=10), 21(t=10), 22(t=11), 25(t=13)

fetchPage(cursor=0) -> data=[11,15,19], nextCursor=3, prevCursor=-1
fetchPage(cursor=3) -> data=[20,21,22], nextCursor=6, prevCursor=0
fetchPage(cursor=6) -> data=[25],       nextCursor=-1, prevCursor=3
```

---

## Follow-Up Discussion (Staff+ Depth)

### Production Concerns
- **Offset instability:** If a new transaction is inserted between page 1 and page 2 fetches, offset pagination will either skip a row or return a duplicate. This is a well-known hazard for financial data where new rows arrive continuously.
- **Keyset pagination:** Replace the integer offset with the last-seen `id` as the cursor: `WHERE id > :cursor ORDER BY id LIMIT :page_size`. O(log N) lookup via index, stable under concurrent inserts, no skips or duplicates.
- **Keyset tradeoff:** Keyset cannot "jump to page 10" by construction. For Coinbase's transaction history UI (scroll-based, not page-numbered), this is acceptable and preferred.
- **Composite sort key:** If sorting by `(time, id)` and two rows share a timestamp, the cursor must encode both fields: `WHERE (time, id) > (:last_time, :last_id)`. Encoding as an opaque base64 token hides implementation details from callers.
- **Deep pagination cost:** Offset pagination degrades to O(offset) even with DB indexes — scanning and discarding all prior rows. For deep history queries, time-range filtering (`time >= X`) should be applied to bound the scan before pagination.
- **Indexes:** For common query patterns (user_id + time range), a composite index on `(user_id, time)` makes filtering O(log N + R) instead of O(N).
- **Sharding:** Partition by `user_id` so a single user's transaction history lives on one shard. Cross-shard queries (e.g., all trades in a currency) become a scatter-gather operation.

### Common Interview Traps
- **Cursor as transparent state:** If the cursor is just an integer, callers can manipulate it. In production, encode as an opaque token (JWT, encrypted offset, or last-seen ID) so the implementation can change without breaking callers.
- **`prevCursor` off-by-one:** `prevCursor = cursor - pageSize` can go negative if the first page was smaller than `pageSize`. Clamp to 0.
- **`fetchPage` without `setPageSize`:** Should raise immediately, not silently return all results.
- **Re-executing filters on every page:** Each `fetchPage` call rescans from the beginning. Caching `execute()` results and slicing them is an optimization trade-off (memory vs. latency) worth discussing.

### How to Push Forward as Staff+
- **Open the API design conversation:** "I'm going to propose a builder pattern with method chaining — does that fit how callers will use this? The alternative is accepting a filter config object at construction time, which is more testable."
- **Name offset vs. keyset explicitly:** Don't wait to be asked. "I'll implement offset pagination for simplicity, but I want to note that for Coinbase's transaction history, keyset pagination keyed on transaction ID is strictly better — it's O(log N) per page and stable under concurrent writes."
- **Connect to SQL:** "Each `set*` method maps to a WHERE clause. `setTimeRange` maps to `time BETWEEN :start AND :end`. In production, I'd generate a parameterized SQL query from the filters rather than scanning a list."
- **Connect to Coinbase domain:** This is literally the Coinbase transaction history API. Users query their BTC/ETH/USD trades filtered by date range, currency pair, and amount. Pagination is essential — a user with 5 years of daily trades has thousands of rows.
- **Observability:** "In production I'd emit a metric on the filter combination being used — if 90% of queries are `userId + timeRange`, that drives index design and caching strategy."
