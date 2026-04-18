# Query Pagination

**Category:** Coding
**Difficulty:** Medium
**Time Estimate:** 45-60 min
**Key Topics:** Builder Pattern, Method Chaining, Offset vs. Keyset Pagination, API Design

---

## Problem Statement

Design a transaction query system for financial data. Given an in-memory list of transactions, build a clean API that supports composable filtering and paginated result retrieval. The interviewer will not specify the API shape — you must propose and justify it.

```python
transactions = [
    {"time": 1,  "id": 11, "user_id": 1, "currency": 1, "amount": 10},
    {"time": 2,  "id": 12, "user_id": 1, "currency": 3, "amount": 11},
    {"time": 3,  "id": 13, "user_id": 2, "currency": 2, "amount": -10},
    # ... (15 total rows, see full dataset in example below)
]
```

## Requirements

### Level 1: Filtering
Support composable filters: time range, user ID, currency, amount range. Filters combine with AND. Execution is deferred until `execute()` is called.

```python
query = TransactionQuery(transactions)
query.set_user_id(1).set_time_range(5, 10).set_currency(1)
results = query.execute()  # returns list of matching dicts
```

### Level 2: Pagination
Add paginated access over filtered results. The caller receives an opaque cursor and passes it back to get the next page.

```python
query.set_page_size(3)
page1 = query.fetch_page()           # cursor defaults to 0
page2 = query.fetch_page(cursor=page1.next_cursor)
# page.next_cursor is None when no more results
# page.prev_cursor allows going backward
```

---

## Solution Approach

### Level 1
**Core Idea:** Store filters in a dict; apply them lazily in `execute()`. Each `set_*` method returns `self` for method chaining. Adding a new filter type only requires adding a method and a `_matches` check.

```python
class TransactionQuery:
    def __init__(self, transactions: list):
        self.transactions = transactions
        self.filters = {}

    def set_user_id(self, user_id: int) -> 'TransactionQuery':
        self.filters['user_id'] = user_id
        return self

    def set_currency(self, currency: int) -> 'TransactionQuery':
        self.filters['currency'] = currency
        return self

    def set_time_range(self, start: int, end: int) -> 'TransactionQuery':
        self.filters['time_start'] = start
        self.filters['time_end'] = end
        return self

    def set_amount_range(self, min_amt: float, max_amt: float) -> 'TransactionQuery':
        self.filters['amount_min'] = min_amt
        self.filters['amount_max'] = max_amt
        return self

    def _matches(self, txn: dict) -> bool:
        f = self.filters
        if 'user_id' in f and txn['user_id'] != f['user_id']: return False
        if 'currency' in f and txn['currency'] != f['currency']: return False
        if 'time_start' in f and txn['time'] < f['time_start']: return False
        if 'time_end' in f and txn['time'] > f['time_end']: return False
        if 'amount_min' in f and txn['amount'] < f['amount_min']: return False
        if 'amount_max' in f and txn['amount'] > f['amount_max']: return False
        return True

    def execute(self) -> list:
        return [t for t in self.transactions if self._matches(t)]
```

**Complexity:** O(1) per `set_*`, O(N) `execute`, O(R) space — N = total rows, R = matches

### Level 2
**Core Idea:** Use an integer offset as the cursor. `fetch_page` scans and skips `cursor` matching rows, then collects `page_size` results. If any row remains after the page, emit a `next_cursor`.

```python
class Page:
    def __init__(self, data: list, next_cursor: int = None, prev_cursor: int = None):
        self.data = data
        self.next_cursor = next_cursor
        self.prev_cursor = prev_cursor

class TransactionQuery:
    # ... (Level 1 code) ...

    def set_page_size(self, size: int) -> 'TransactionQuery':
        self.page_size = size
        return self

    def fetch_page(self, cursor: int = 0) -> Page:
        if not hasattr(self, 'page_size') or self.page_size is None:
            raise ValueError("page_size must be set before calling fetch_page")

        matched, skipped, has_more = [], 0, False
        for txn in self.transactions:
            if not self._matches(txn):
                continue
            if skipped < cursor:
                skipped += 1
                continue
            if len(matched) < self.page_size:
                matched.append(txn)
            else:
                has_more = True
                break

        next_cursor = cursor + len(matched) if has_more else None
        prev_cursor = max(0, cursor - self.page_size) if cursor > 0 else None
        return Page(data=matched, next_cursor=next_cursor, prev_cursor=prev_cursor)
```

**Complexity:** O(cursor + P) per `fetch_page` — P = page_size

**Example trace (user_id=1, currency=1, page_size=3):**
```
Matching IDs: 11(t=1), 15(t=5), 19(t=9), 20(t=10), 21(t=10), 22(t=11), 25(t=13)

fetch_page(cursor=0) -> data=[11,15,19], next_cursor=3, prev_cursor=None
fetch_page(cursor=3) -> data=[20,21,22], next_cursor=6, prev_cursor=0
fetch_page(cursor=6) -> data=[25],       next_cursor=None, prev_cursor=3
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
- **`prev_cursor` off-by-one:** `prev_cursor = cursor - page_size` can go negative if the first page was smaller than `page_size`. Clamp to 0.
- **`fetch_page` without `set_page_size`:** Should raise immediately, not silently return all results.
- **Re-executing filters on every page:** Each `fetch_page` call rescans from the beginning. Caching `execute()` results and slicing them is an optimization trade-off (memory vs. latency) worth discussing.

### How to Push Forward as Staff+
- **Open the API design conversation:** "I'm going to propose a builder pattern with method chaining — does that fit how callers will use this? The alternative is accepting a filter config object at construction time, which is more testable."
- **Name offset vs. keyset explicitly:** Don't wait to be asked. "I'll implement offset pagination for simplicity, but I want to note that for Coinbase's transaction history, keyset pagination keyed on transaction ID is strictly better — it's O(log N) per page and stable under concurrent writes."
- **Connect to SQL:** "Each `set_*` method maps to a WHERE clause. `set_time_range` maps to `time BETWEEN :start AND :end`. In production, I'd generate a parameterized SQL query from the filters dict rather than scanning a list."
- **Connect to Coinbase domain:** This is literally the Coinbase transaction history API. Users query their BTC/ETH/USD trades filtered by date range, currency pair, and amount. Pagination is essential — a user with 5 years of daily trades has thousands of rows.
- **Observability:** "In production I'd emit a metric on the filter combination being used — if 90% of queries are `user_id + time_range`, that drives index design and caching strategy."
